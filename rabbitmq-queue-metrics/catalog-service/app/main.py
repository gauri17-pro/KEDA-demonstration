from fastapi import FastAPI

app = FastAPI(title="catalog-service", version="0.1.0")

# In-memory demo catalog (good enough for autoscaling demos)
PRODUCTS = [
    {"sku": "sku-1", "name": "KEDA Sticker Pack", "price_cents": 499},
    {"sku": "sku-2", "name": "Autoscaling T-Shirt", "price_cents": 2499},
    {"sku": "sku-3", "name": "Queue Depth Mug", "price_cents": 1599},
]


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/products")
def list_products():
    return {"items": PRODUCTS}


@app.get("/products/{sku}")
def get_product(sku: str):
    for p in PRODUCTS:
        if p["sku"] == sku:
            return p
    return {"error": "not_found", "sku": sku}

