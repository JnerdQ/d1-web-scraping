from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Product
from .forms import ProductForm
from scraper.d1_scraper import D1Scraper

# Vista de la pagina principal
def home(request):
  
    # Obtener productos recientes
    products = Product.objects.all().order_by("-created_at")[:8]
    return render(
        request, "home.html", {"products": products, "title": "Inicio - D1 Scraper"}
    )

 # Vista de busqueda de productos 
def search(request):
 
    query = request.GET.get("q", "")
    products = []

    if query:
        # Buscar primero en la base de datos
        products = Product.objects.filter(name__icontains=query)

        # Si hay menos de 3 resultados, ejecutar el scraper
        if products.count() < 3:
            scraper = D1Scraper()
            # Pasamos save_to_db=True explicitamente
            scraper.search_products(query, save_to_db=True)
            # Actualizar los resultados de la base de datos
            products = Product.objects.filter(name__icontains=query)

    return render(
        request,
        "search.html",
        {
            "query": query,
            "products": products,
            "title": f"Búsqueda: {query} - D1 Scraper",
        },
    )


def product_list(request):
    # Lista de productos 
    products = Product.objects.all().order_by("-created_at")
    return render(
        request,
        "product_list.html",
        {"products": products, "title": "Administrar Productos"},
    )


def product_detail(request, pk):
    # Detalle de un producto
    product = get_object_or_404(Product, pk=pk)
    return render(
        request,
        "product_detail.html",
        {"product": product, "title": f"Detalle: {product.name}"},
    )


def product_create(request):
    # Crear un nuevo producto
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(
                request, f"El producto {product.name} ha sido creado exitosamente."
            )
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(
        request,
        "product_form.html",
        {"form": form, "title": "Crear Producto", "action": "Crear"},
    )


def product_update(request, pk):
    # Actualizar un producto existente
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(
                request, f"El producto {product.name} ha sido actualizado exitosamente."
            )
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "product_form.html",
        {
            "form": form,
            "product": product,
            "title": f"Editar: {product.name}",
            "action": "Actualizar",
        },
    )


def product_delete(request, pk):
    # Eliminar un producto
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product_name = product.name
        product.delete()
        messages.success(
            request, f"El producto {product_name} ha sido eliminado exitosamente."
        )
        return redirect("product_list")

    return render(
        request,
        "product_confirm_delete.html",
        {"product": product, "title": f"Eliminar: {product.name}"},
    )


def run_scraper_view(request):
    # Vista para ejecutar el scraper manualmente
    term = request.GET.get("term", "")

    if term:
        scraper = D1Scraper()
        products = scraper.search_products(term)

        return JsonResponse(
            {
                "success": True,
                "message": f'Se encontraron {len(products)} productos para "{term}"',
                "count": len(products),
            }
        )

    return JsonResponse(
        {"success": False, "message": "No se especificó un término de búsqueda"}
    )
