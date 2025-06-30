import cgi
import json
import logging
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse

from db_manager import PostgresManager, postgres_config
from PIL import Image

# Configuration
HOST = '0.0.0.0'
PORT = 8000
UPLOAD_FOLDER = '/app/images'
LOG_FILE = '/logs/app.log'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ImageServer(BaseHTTPRequestHandler):
    db: Optional[PostgresManager] = None

    def do_GET(self):

        # для пагинации меняем self.path (путь с параметрами) на path ("чистый" путь)
        parsed_url = urlparse(self.path)  # /api/images?page=2
        path = parsed_url.path  # например, /api/images
        query_params = parse_qs(parsed_url.query)
        page = int(query_params.get('page', [1])[0])  # если ?page=2 → 2, иначе 1

        if path == '/':
            self.serve_file('index.html', 'text/html')
            logging.info('Main page accessed')
        elif path == '/upload':
            self.serve_file('upload.html', 'text/html')
            logging.info('Upload page accessed')
        elif path == '/images-list':
            self.serve_file('images.html', 'text/html')

        # добавляем ссылку для запроса по AJAX:
        elif path == '/api/get-data':
            total, data = ImageServer.db.get_page_by_page_num(page, is_print=False)
            print("total:", total, "data:", data)
            json_data = {
                "items": [
                    {
                        "id": row[0],
                        "name": row[1],
                        "original_name": row[2],
                        "size": row[3],
                        "uploaded_at": row[4].strftime('%Y-%m-%d %H:%M:%S'),
                        "type": row[5]
                    }
                    for row in data
                ],
                "total": total,
                "page": page,
            }

            print('==================== json_data: ===================')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(json_data).encode('utf-8'))

        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        if self.path == '/upload':
            try:
                # Parse multipart form data
                content_type = self.headers.get('content-type')
                if not content_type or 'multipart/form-data' not in content_type:
                    self.send_error_response(400, 'Invalid content type')
                    logging.error('Invalid content type')
                    return

                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )

                if 'file' not in form:
                    self.send_error_response(400, 'No file part')
                    logging.error('No file part in request')
                    return

                file_item = form['file']
                if not file_item.filename:
                    self.send_error_response(400, 'No selected file')
                    logging.error('No selected file')
                    return

                if not allowed_file(file_item.filename):
                    self.send_error_response(400, 'Unsupported file format')
                    logging.error(f'Unsupported file format: {file_item.filename}')
                    return

                # Check file size
                file_data = file_item.file.read()
                if len(file_data) > MAX_FILE_SIZE:
                    self.send_error_response(400, 'File too large')
                    logging.error(f'File too large: {len(file_data)} bytes')
                    return

                # Generate random filename
                filename = ImageServer.db.random_filename(file_item.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                # Save file
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                    os.chmod(filepath, 0o664)  # Ensure readable by Nginx
                logging.info(f'File saved to: {filepath}')  # Debug log

                # Save to db
                ImageServer.db.add_file(file_item.filename, filename)

                # Verify image
                try:
                    Image.open(filepath).verify()
                except Exception:
                    os.remove(filepath)
                    self.send_error_response(400, 'Invalid image file')
                    logging.error(f'Invalid image file: {filename}')
                    return

                image_url = f"/images/{filename}"
                logging.info(f'Success: image {filename} uploaded')

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'message': 'File uploaded successfully',
                    'filename': filename,
                    'url': image_url
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                self.send_error_response(500, f'Error saving file: {str(e)}')
                logging.error(f'Error saving file: {str(e)}')


        elif self.path.startswith("/delete/"):
            match = re.match(r"^/delete/(\d+)$", self.path)
            print("Есть совпадение!")
            if match:
                image_id = match.group(1)
                print(f"Удаление изображения с ID {image_id}")

                # Например, удалим файл по ID (предположим, что имя совпадает)
                try:
                    # 1. Находим имя по id
                    filename = ImageServer.db.get_id_by_filename(image_id)
                    print(f'Файл {filename} по ID {image_id}  успешно найден!')

                    # 2. Удаляем файл из папки
                    file_path = f"/app/images/{filename}"
                    os.remove(file_path)
                    print(f'Файл {file_path} успешно удалён!')

                    # 3. Удаляем запись из базы
                    ImageServer.db.delete_by_id(image_id)
                    print(f'Файл c ID {image_id} успешно удалён из БД!')

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Deleted")
                except FileNotFoundError:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"File not found")
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(f"Error: {e}".encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not found")

        else:
            self.send_error(404, '...Not Found...')

    def serve_file(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, 'Not Found')

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))


def run(db_object):
    ImageServer.db = db_object
    """
    Класс HTTPServer сам создаёт экземпляры ImageServer, 
    передавая только аргументы, которые ему нужны. 
    Мы не можете напрямую изменить __init__ в ImageServer, чтобы передать туда pm, 
    потому что HTTPServer этого не поддерживает.
    
    Поэтому создаём промежуточный класс-наследник CustomHandler,
    куда передаём объект подключения в качестве class attribute
    (атрибута класса, а не экземпляра класса)
    """

    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ImageServer)
    logging.info('Starting server...')
    httpd.serve_forever()


if __name__ == '__main__':
    with PostgresManager(postgres_config) as pm:
        pm.create_table()
        run(pm)
