# d1-web-scraping
Este proyecto consiste en un sistema de web scraping para la tienda D1 en Colombia, que extrae información de productos y la almacena en una base de datos. La aplicación incluye una interfaz web construida con Django para visualizar los productos extraídos.

# Tecnologías Utilizadas

Python 3.12: Lenguaje de programación principal
Django 5.2: Framework web pdjango ara backend y frontend
Selenium: Automatización de navegador para web scraping
PostgreSQL/SQLite: Base de datos
Requests: Cliente HTTP para solicitudes web
WebDriver Manager: Gestión de controladores para Selenium

# Guía  para D1 Web Scraping

## Preparación del Entorno


1. Clonar el repositorio

git clone https://github.com/JnerdQ/d1-web-scraping.git
cd d1-web-scraping

2. Crear un entorno virtual

python -m venv venv

3. Activar el entorno virtual

En Windows:
venv\Scripts\activate

En macOS/Linux
source venv/bin/activate

4. Instalar las dependencias

cd backend
pip install -r requirements.txt

5. Configurar la base de datos

python manage.py migrate

6. Iniciar el servidor de desarrollo

python manage.py runserver