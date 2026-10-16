from collections import Counter
from typing import Optional
from fastapi import FastAPI, HTTPException

app = FastAPI(title="TechStore API")

# --- Base de datos falsa (en memoria) ---
productos = [
    {
        "id": 1,
        "nombre": "Laptop Pro",
        "categoria": "computadoras",
        "precio": 1200,
        "stock": 5,
    },
    {
        "id": 2,
        "nombre": "Smartphone X",
        "categoria": "telefonia",
        "precio": 850,
        "stock": 12,
    },
    {
        "id": 3,
        "nombre": "Auriculares Inalámbricos",
        "categoria": "audio",
        "precio": 150,
        "stock": 25,
    },
    {
        "id": 4,
        "nombre": 'Monitor UltraWide 34"',
        "categoria": "monitores",
        "precio": 450,
        "stock": 8,
    },
    {
        "id": 5,
        "nombre": "Teclado Mecánico RGB",
        "categoria": "accesorios",
        "precio": 90,
        "stock": 15,
    },
    {
        "id": 6,
        "nombre": "Mouse Ergonómico",
        "categoria": "accesorios",
        "precio": 45,
        "stock": 30,
    },
    {
        "id": 7,
        "nombre": "Tablet Air",
        "categoria": "tablets",
        "precio": 600,
        "stock": 10,
    },
]

# ---------- Base de datos de pedidos (en memoria) ----------
pedidos = [
    {
        "id": 101,
        "cliente_id": 1,
        "producto": "Laptop Pro",
        "total": 1200,
        "estado": "completado",
    },
    {
        "id": 102,
        "cliente_id": 1,
        "producto": "Mouse Inalámbrico",
        "total": 25,
        "estado": "pendiente",
    },
    {
        "id": 103,
        "cliente_id": 1,
        "producto": 'Monitor 27"',
        "total": 300,
        "estado": "completado",
    },
    {
        "id": 104,
        "cliente_id": 2,
        "producto": "Audífonos BT",
        "total": 60,
        "estado": "pendiente",
    },
    {
        "id": 105,
        "cliente_id": 2,
        "producto": 'Tablet 10"',
        "total": 250,
        "estado": "completado",
    },
]


# --- Endpoint de Bienvenida ---
@app.get("/")
async def inicio():
    return {
        "mensaje": "Bienvenido a TechStore :)",
        "total_productos": len(productos),
    }


# ==========================================
# SECCIÓN DE PRODUCTOS
# ==========================================

# ⚠️ IMPORTANTE (Reto 2): Las rutas estáticas (/mas-caro, /buscar)
# deben ir SIEMPRE ANTES de la ruta dinámica (/productos/{producto_id})


@app.get("/productos/mas-caro")
def obtener_producto_mas_caro():  # [Reto 2]
    if not productos:
        raise HTTPException(
            status_code=404, detail="No hay productos registrados"
        )
    return max(productos, key=lambda p: p["precio"])


@app.get("/productos/buscar")
def buscar_productos(q: str = ""):  # [Reto 5]
    busqueda = q.lower()
    return [p for p in productos if busqueda in p["nombre"].lower()]


@app.get("/productos/{producto_id}")
async def obtener_producto(producto_id: int):
    for producto in productos:
        if producto["id"] == producto_id:
            return producto

    raise HTTPException(
        status_code=404,
        detail=f"El producto con el id {producto_id} no existe",
    )


@app.get("/productos")
async def listar_productos(
    categoria: str | None = None,
    max_precio: float | None = None,
    min_precio: float | None = None,  # [Reto 3] Añadido
    solo_disponible: bool = False,
    orden: str = "id",
    pagina: int = 1,
    tamano: int = 3,
):
    resultado = productos.copy()

    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]

    # [Reto 3] Filtros de rango de precio
    if min_precio is not None:
        resultado = [p for p in resultado if p["precio"] >= min_precio]

    if max_precio is not None:
        resultado = [p for p in resultado if p["precio"] <= max_precio]

    if solo_disponible:
        resultado = [p for p in resultado if p["stock"] > 0]

    # Ordenamiento (Corregido el error de duplicidad en 'precio_asc')
    if orden == "precio_asc":
        resultado.sort(key=lambda p: p["precio"])
    elif orden == "precio_desc":
        resultado.sort(key=lambda p: p["precio"], reverse=True)

    # Paginación
    inicio = (pagina - 1) * tamano
    fin = inicio + tamano
    pagina_resultados = resultado[inicio:fin]

    return {
        "total_encontrados": len(resultado),
        "pagina": pagina,
        "tamano": tamano,
        "productos": pagina_resultados,
    }


# ==========================================
# SECCIÓN DE CATEGORÍAS Y CLIENTES / PEDIDOS
# ==========================================


@app.get("/categorias")
def obtener_contador_categorias():  # [Reto 1]
    categorias = [p["categoria"] for p in productos]
    return dict(Counter(categorias))


@app.get("/clientes/{cliente_id}/pedidos")
async def pedidos_del_cliente(
    cliente_id: int, estado: str | None = None, orden: str = "id"
):
    mis_pedidos = [p for p in pedidos if p["cliente_id"] == cliente_id]

    if not mis_pedidos:
        raise HTTPException(
            status_code=404,
            detail=f"El cliente {cliente_id} no tiene pedidos 🤷",
        )

    if estado:
        mis_pedidos = [p for p in mis_pedidos if p["estado"] == estado]

    if orden == "total_desc":
        mis_pedidos.sort(key=lambda p: p["total"], reverse=True)

    gasto_total = sum(p["total"] for p in mis_pedidos)

    # [Reto 4] Estadísticas adicionales del cliente
    pedido_mas_caro = max(mis_pedidos, key=lambda p: p["total"])
    promedio_gasto = gasto_total / len(mis_pedidos)

    return {
        "cliente_id": cliente_id,
        "cantidad_pedidos": len(mis_pedidos),
        "gasto_total": gasto_total,
        "promedio_gasto": round(promedio_gasto, 2),
        "pedido_mas_caro": pedido_mas_caro,
        "pedidos": mis_pedidos,
    }