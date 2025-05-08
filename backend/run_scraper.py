import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "d1_scraper.settings")
django.setup()

from scraper.d1_scraper import run_scraper

if __name__ == "__main__":
    # Verificar si se proporcionaron términos de búsqueda como argumentos
    search_terms = sys.argv[1:] if len(sys.argv) > 1 else None

    print("Iniciando el scraper de productos D1...")
    products = run_scraper(search_terms)
    print(f"Proceso completado. Se encontraron {len(products)} productos en total.")
