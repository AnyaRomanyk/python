from flask import Flask, request, jsonify
import csv, uuid, os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data/inventory.csv"
FIELDS = ['id','name','category','quantity','price','location','created_at']

def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()

def load_items():
    ensure_data_file()
    items = []
    with open(DATA_FILE, 'r', newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            items.append(row)
    return items

def save_items(items):
    ensure_data_file()
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i in items:
            w.writerow(i)

def validate_item(data, require_id=False):
    if not isinstance(data, dict):
        return None, "Invalid JSON body"

    out = {}

    if require_id:
        if not data.get("id"):
            return None, "Missing id"
        out["id"] = str(data["id"])
    else:
        out["id"] = str(uuid.uuid4())

    name = str(data.get("name","")).strip()
    if not name:
        return None, "Invalid name"
    out["name"] = name

    category = str(data.get("category","")).strip()
    if not category:
        return None, "Invalid category"
    out["category"] = category

    try:
        q = int(data.get("quantity",0))
        if q < 0:
            raise ValueError
        out["quantity"] = str(q)
    except:
        return None, "Quantity must be integer >= 0"

    try:
        p = float(str(data.get("price", "0")).replace(',', '.'))
        if p < 0:
            raise ValueError
        out["price"] = f"{p:.2f}"
    except:
        return None, "Price must be number >= 0"

    out["location"] = str(data.get("location",""))

    out["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return out, None

@app.get("/items")
def api_get_items():
    return jsonify(load_items()), 200

@app.post("/items")
def api_post_item():
    data = request.get_json()
    item, err = validate_item(data)
    if err:
        return jsonify({"error": err}), 400
    items = load_items()
    items.append(item)
    save_items(items)
    return jsonify(item), 201

@app.put("/items/<item_id>")
def api_put_item(item_id):
    data = request.get_json() or {}
    data["id"] = item_id
    item, err = validate_item(data, require_id=True)
    if err:
        return jsonify({"error": err}), 400
    items = load_items()
    found = False
    for i, it in enumerate(items):
        if it["id"] == item_id:
            item["created_at"] = it.get("created_at", item["created_at"])
            items[i] = item
            found = True
            break
    if not found:
        return jsonify({"error": "Item not found"}), 404
    save_items(items)
    return jsonify(item), 200

@app.delete("/items/<item_id>")
def api_delete_item(item_id):
    items = load_items()
    new_items = [i for i in items if i["id"] != item_id]
    if len(new_items) == len(items):
        return jsonify({"error": "Item not found"}), 404
    save_items(new_items)
    return jsonify({"status": "deleted"}), 200

@app.get("/export")
def api_export():
    ensure_data_file()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = f.read()
    return data, 200, {"Content-Type": "text/csv; charset=utf-8"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
