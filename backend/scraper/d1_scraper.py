import time
import csv
import logging
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configuracion basica de logging para seguimiento de errores y eventos
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="d1_scraper.log",
)


class D1Scraper:
    def __init__(self):
        self.base_url = "https://domicilios.tiendasd1.com"
        self.search_url = f"{self.base_url}/search?name="
        self.products = (
            []
        )  # Almacena todos los productos extraidos de todas las busquedas
        self.setup_driver()

    def setup_driver(self):
        # Configuracion del navegador Chrome en modo headless para ejecucion sin interfaz
        options = Options()
        options.add_argument("--headless")  # Ejecuta Chrome sin abrir ventana grafica
        options.add_argument("--no-sandbox")  # Mejora la estabilidad en entornos CI/CD
        options.add_argument("--disable-dev-shm-usage")  # Reduce problemas de memoria

        # Instalacion automatica del ChromeDriver mediante webdriver_manager
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def search_products(self, query, save_to_db=True):
        # Metodo principal para buscar y extraer productos de la tienda D1
        encoded_query = quote(
            query
        )  # Codifica parametros URL para caracteres especiales
        search_url = f"{self.search_url}{encoded_query}"

        logging.info(f"Buscando productos con la consulta: {query}")
        print(f"URL de busqueda: {search_url}")

        try:
            # Navegacion a la pagina de resultados
            self.driver.get(search_url)
            time.sleep(
                4
            )  # Espera necesaria para carga de contenido dinamico mediante JS

            # Identifica todas las tarjetas de productos mediante su selector CSS
            product_cards = self.driver.find_elements(
                By.CSS_SELECTOR, "div.card-product-vertical"
            )
            print(f"Encontrados {len(product_cards)} productos con Selenium")

            products_found = []

            for i, card in enumerate(product_cards):
                try:
                    # Inicializacion del diccionario para cada producto
                    product_data = {"id": i + 1}

                    # EXTRACCION DEL NOMBRE: intenta multiples selectores en orden descendente de preferencia
                    try:
                        name_element = card.find_element(By.CSS_SELECTOR, ".prod__name")
                        product_data["name"] = name_element.text
                    except:
                        # Selector alternativo para casos donde cambia la estructura HTML
                        try:
                            name_element = card.find_element(
                                By.CSS_SELECTOR, "p[class*='CardName']"
                            )
                            product_data["name"] = name_element.text
                        except:
                            # Estrategia heuristica: busca parrafos con texto largo sin simbolo de precio
                            paragraphs = card.find_elements(By.TAG_NAME, "p")
                            for p in paragraphs:
                                text = p.text.strip()
                                if text and "$" not in text and len(text) > 5:
                                    product_data["name"] = text
                                    break

                    # EXTRACCION DEL PRECIO: intenta varios selectores con estrategia fallback
                    try:
                        price_element = card.find_element(
                            By.CSS_SELECTOR, ".base__price"
                        )
                        price_text = price_element.text
                    except:
                        try:
                            price_element = card.find_element(
                                By.CSS_SELECTOR, "p[class*='CardBasePrice']"
                            )
                            price_text = price_element.text
                        except:
                            # Busqueda heuristica por simbolo peso en cualquier parrafo
                            paragraphs = card.find_elements(By.TAG_NAME, "p")
                            for p in paragraphs:
                                if "$" in p.text:
                                    price_text = p.text
                                    break
                            else:
                                price_text = "0"

                    # Conversion del precio: elimina simbolos y formatos para obtener solo digitos
                    if price_text:
                        # Elimina puntos de miles y extrae solo digitos
                        price_num = "".join(
                            filter(str.isdigit, price_text.replace(".", ""))
                        )
                        try:
                            product_data["price"] = float(price_num)
                        except:
                            product_data["price"] = 0
                    else:
                        product_data["price"] = 0

                    # EXTRACCION DE CANTIDAD/MEDIDA: busca unidades como ml, g, kg, etc.
                    product_data["quantity"] = ""
                    try:
                        # Lista de selectores probables para unidades de medida
                        selectors = [
                            ".styles__PumStyles span",
                            "p[class*='CardPum'] span",
                            "span[class*='Pum']",
                        ]

                        # Intenta cada selector hasta encontrar uno valido
                        for selector in selectors:
                            try:
                                qty_element = card.find_element(
                                    By.CSS_SELECTOR, selector
                                )
                                product_data["quantity"] = qty_element.text.strip()
                                break
                            except:
                                continue

                        # Si los selectores fallan, busca spans con unidades de medida conocidas
                        if not product_data["quantity"]:
                            spans = card.find_elements(By.TAG_NAME, "span")
                            for span in spans:
                                text = span.text.strip()
                                # Detecta unidades comunes en productos alimenticios
                                if any(
                                    unit in text.lower()
                                    for unit in ["ml", "g", "kg", "l", "oz"]
                                ):
                                    product_data["quantity"] = text
                                    break
                    except Exception as e:
                        print(f"Error al obtener cantidad: {e}")

                    # EXTRACCION DE IMAGEN: busca tag img dentro de la tarjeta
                    product_data["image_url"] = ""
                    try:
                        img = card.find_element(By.TAG_NAME, "img")
                        if img:
                            src = img.get_attribute("src")
                            if src:
                                product_data["image_url"] = src
                    except Exception as e:
                        print(f"Error al obtener imagen: {e}")

                    # VALIDACION: solo agrega productos con nombre y precio validos
                    if "name" in product_data and product_data.get("price", 0) > 0:
                        product_data["source"] = "D1"  # Marca la fuente del producto
                        # Campos adicionales para compatibilidad con el modelo de datos
                        product_data["category"] = ""
                        product_data["description"] = ""

                        products_found.append(product_data)

                        # Muestra informacion del producto extraido en consola
                        print(
                            f"Producto {i+1}: {product_data.get('name')}, "
                            f"Precio: {product_data.get('price')}, "
                            f"Cantidad: {product_data.get('quantity', '')}"
                        )

                        # ALMACENAMIENTO EN BASE DE DATOS DJANGO
                        if save_to_db:
                            try:
                                # Importaciones Django realizadas aqui para evitar dependencias iniciales
                                import os
                                import django

                                # Configuracion del entorno Django si no esta inicializado
                                if not os.environ.get("DJANGO_SETTINGS_MODULE"):
                                    os.environ.setdefault(
                                        "DJANGO_SETTINGS_MODULE", "d1_scraper.settings"
                                    )
                                    django.setup()

                                # Importacion del modelo de producto despues de configurar Django
                                from products.models import Product

                                # Operacion upsert: crea nuevo o actualiza existente si ya existe
                                product, created = Product.objects.update_or_create(
                                    name=product_data[
                                        "name"
                                    ],  # Campo clave para buscar duplicados
                                    defaults={
                                        "price": product_data["price"],
                                        "image_url": product_data.get("image_url", ""),
                                        "quantity": product_data.get("quantity", ""),
                                        "category": product_data.get("category", ""),
                                        "description": product_data.get(
                                            "description", ""
                                        ),
                                        "source": product_data.get("source", "D1"),
                                    },
                                )

                                # Feedback sobre la operacion en DB
                                if created:
                                    print(
                                        f"✅ Producto CREADO en DB: {product_data['name']}"
                                    )
                                else:
                                    print(
                                        f"✅ Producto ACTUALIZADO en DB: {product_data['name']}"
                                    )

                            except Exception as e:
                                logging.error(f"Error al guardar en DB: {e}")
                                print(f"❌ Error al guardar en DB: {e}")
                                import traceback

                                # Muestra traza completa para facilitar debugging de errores DB
                                traceback.print_exc()

                except Exception as e:
                    logging.error(f"Error al procesar producto {i+1}: {e}")
                    print(f"Error al procesar producto {i+1}: {e}")

            # Agrega productos encontrados a la lista principal del scraper
            self.products.extend(products_found)
            return products_found

        except Exception as e:
            logging.error(f"Error al buscar productos: {e}")
            print(f"Error al buscar productos: {e}")
            return []

    def save_to_csv(self, filename="d1_products.csv"):
        # Exporta todos los productos recolectados a un archivo CSV
        if not self.products:
            logging.warning("No hay productos para guardar en CSV")
            return

        try:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                # Usa las claves del primer producto para definir las columnas del CSV
                fieldnames = self.products[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()  # Escribe fila de encabezados
                writer.writerows(self.products)  # Escribe datos de productos

            logging.info(f"Productos guardados en {filename}")
            return True
        except Exception as e:
            logging.error(f"Error al guardar CSV: {e}")
            return False

    def __del__(self):
        # Metodo destructor: cierra el navegador y libera recursos al finalizar
        if hasattr(self, "driver"):
            self.driver.quit()


# Funcion principal para ejecutar el proceso completo de scraping
def run_scraper(search_terms=None):
    # Crea instancia del scraper
    scraper = D1Scraper()

    # Si no se proporcionan terminos, usa esta lista por defecto de productos basicos
    if search_terms is None:
        search_terms = [
            "leche",
            "arroz",
            "aceite",
            "azucar",
            "cafe",
        ]

    all_products = []

    # Itera sobre cada termino de busqueda
    for term in search_terms:
        products = scraper.search_products(term)
        all_products.extend(products)
        print(f"Se encontraron {len(products)} productos para '{term}'")
        time.sleep(1)  # Pausa de 1 segundo entre busquedas para evitar bloqueos IP

    # Guarda todos los productos recolectados en un archivo CSV
    scraper.save_to_csv()

    print(f"Proceso completado. Se encontraron {len(all_products)} productos en total.")
    return all_products
