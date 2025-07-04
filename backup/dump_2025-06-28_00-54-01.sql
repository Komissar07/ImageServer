--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Debian 17.5-1.pgdg120+1)
-- Dumped by pg_dump version 17.5 (Debian 17.5-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    filename text NOT NULL,
    original_name text NOT NULL,
    size integer NOT NULL,
    upload_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    file_type text NOT NULL
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.images_id_seq OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.images (id, filename, original_name, size, upload_time, file_type) FROM stdin;
2	dgnGiopG4wI1.png	python-logo-3840x2160-22914.png	71	2025-06-27 21:44:23.231481	png
3	i5Ai0Qliaobz.png	Desktop image.png	565	2025-06-27 21:44:31.47402	png
4	7mdIbZEaLA2G.gif	true2.gif	2081	2025-06-27 21:44:34.76818	gif
5	dI1ABnF2qaCs.jpg	wallpaperflare.com_wallpaper.jpg	22	2025-06-27 21:44:49.862288	jpg
6	2ApSF8zcRFjZ.png	Desktop image.png	565	2025-06-27 21:44:56.521105	png
7	ZSZEHWiPVwUQ.gif	true2.gif	2081	2025-06-27 21:45:00.230048	gif
8	AqXGJv0qgaaq.png	python-logo-3840x2160-22914.png	71	2025-06-27 21:45:05.912876	png
9	XZSL6V3O7g0z.jpg	wallpaperflare.com_wallpaper.jpg	22	2025-06-27 21:45:11.064842	jpg
10	B8W86UmSV301.png	Desktop image.png	565	2025-06-27 21:45:19.502538	png
11	jnqz43tRuB44.png	python-logo-3840x2160-22914.png	71	2025-06-27 21:45:22.662733	png
12	VoOaNx16mr0o.gif	true2.gif	2081	2025-06-27 21:45:25.111605	gif
13	3rnL4Rivq3QH.png	Desktop image.png	565	2025-06-27 21:45:37.645921	png
\.


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.images_id_seq', 13, true);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

