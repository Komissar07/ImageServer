// 1. Считаем параметр "page" из текущего URL
const urlParams = new URLSearchParams(window.location.search);
const page = parseInt(urlParams.get('page')) || 1;


// 2. Загружаем данные с нужной страницы
fetch(`/api/get-data?page=${page}`)
    .then(response => response.json())
    .then(data => {
        const total_pages = Math.ceil(data.total / 10);
        const container = document.querySelector('.images-container');
        if (data && typeof data.total === 'number' && data.total > 0) {
            container.innerHTML = "";
        }
        const body = document.createElement('div');
        body.className = 'images-container-body';

        // 3. Отрисовываем записи
        if (data.total) {
            body.innerHTML += `
            <div class="images-container-header">
                <div class="column1">Name</div>
                <div class="column2">Original Name</div>
                <div class="column3">Size, kB</div>
                <div class="column4">Uploaded at</div>
                <div class="column5">Type</div>
                <div class="column6">Delete</div>
            </div`
            data.items.forEach(img => {
                body.innerHTML += `
                <div class="images-container-body-line">
                    <div class="images-container-body-item column1">
                        <img src="/images/${img.name}" width="16" height="16" alt="img">
                        <a href="/images/${img.name}">${img.name}</a>
                    </div>
                    <div class="images-container-body-item column2">${img.original_name}</div>
                    <div class="images-container-body-item column3">${img.size}</div>
                    <div class="images-container-body-item column4">${img.uploaded_at}</div>
                    <div class="images-container-body-item column5">${img.type}</div>
                    <div class="images-container-body-item column6">
                        <a href="#" class="delete-image" data-id="${img.id}">
                            <img src="/static/img/delete.svg" width="30" height="30" alt="img">
                        </a>
                    </div>
                </div>`;
            });
        }
        container.appendChild(body);

        // 4. Управление пагинацией

        const btnPrev = document.getElementById('btn-prev')
        if (page > 1) {
            btnPrev.href = `?page=${page - 1}`;
            btnPrev.classList.remove('disabled');  // если есть класс для стилизации недоступной кнопки
            btnPrev.removeAttribute('aria-disabled'); // на всякий случай
        } else {
            btnPrev.href = '#';                      // или просто убрать href
            btnPrev.classList.add('disabled');      // добавить класс для визуального эффекта
            btnPrev.setAttribute('aria-disabled', 'true');  // для доступности
        }
        const pageNumber = document.getElementById('page-number');
        pageNumber.innerHTML = String(page);

        const totalPages = document.getElementById('total-pages');
        totalPages.innerHTML = `(total ${total_pages})`;

        const btnNext = document.getElementById('btn-next');
        if (page < total_pages) {
            btnNext.href = `?page=${page + 1}`;
            btnNext.classList.remove('disabled');  // если есть класс для стилизации недоступной кнопки
            btnNext.removeAttribute('aria-disabled'); // на всякий случай
        } else {
            btnNext.href = '#';                      // или просто убрать href
            btnNext.classList.add('disabled');      // добавить класс для визуального эффекта
            btnNext.setAttribute('aria-disabled', 'true');  // для доступности
        }
        console.log('page:', page, 'total_pages', total_pages);
    });


document.addEventListener('click', function (e) {
    if (e.target.closest('.delete-image')) {
        e.preventDefault();

        const link = e.target.closest('.delete-image');
        const imageId = link.dataset.id;
        console.log('id for deleting: ', imageId)
        const containerLine = link.closest('.images-container-body-line');

        if (!imageId) return;

        if (!confirm('Delete image?')) return;

        fetch(`/delete/${imageId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (response.ok) {
                    containerLine.remove();
                } else {
                    return response.text().then(text => {
                        throw new Error(text || 'Ошибка удаления');
                    });
                }
            })
            .catch(error => {
                alert(`Ошибка: ${error.message}`);
            });
    }
});
