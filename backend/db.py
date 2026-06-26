import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "pantry_pilot.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create pantry_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pantry_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        category TEXT NOT NULL,
        created_at TEXT NOT NULL,
        use_by_date TEXT NOT NULL
    )
    """)
    
    # Create shopping_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shopping_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        category TEXT NOT NULL,
        checked INTEGER NOT NULL DEFAULT 0,
        recipe_name TEXT
    )
    """)
    
    conn.commit()
    conn.close()

# --- Pantry DB Operations ---

def get_all_pantry():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pantry_items")
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "name": r["name"],
            "quantity": r["quantity"],
            "unit": r["unit"],
            "category": r["category"],
            "createdAt": r["created_at"],
            "useByDate": r["use_by_date"]
        })
    return items

def add_or_update_pantry_item(item_id, name, quantity, unit, category, use_by_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clean inputs
    name_clean = name.strip()
    unit_clean = unit.strip()
    category_clean = category.strip()
    
    # Default expiration: 7 days
    if not use_by_date:
        use_by_date = (datetime.now() + timedelta(days=7)).isoformat()
        
    created_at = datetime.now().isoformat()
    
    # Check if item with same name (case-insensitive) and same unit exists
    cursor.execute(
        "SELECT id, quantity, use_by_date FROM pantry_items WHERE LOWER(name) = ? AND LOWER(unit) = ?", 
        (name_clean.lower(), unit_clean.lower())
    )
    existing = cursor.fetchone()
    
    if existing:
        new_qty = existing["quantity"] + quantity
        # Keep earlier expiration date
        existing_expiry = existing["use_by_date"]
        final_expiry = existing_expiry
        try:
            if datetime.fromisoformat(use_by_date) < datetime.fromisoformat(existing_expiry):
                final_expiry = use_by_date
        except Exception:
            pass
            
        cursor.execute(
            "UPDATE pantry_items SET quantity = ?, use_by_date = ? WHERE id = ?",
            (new_qty, final_expiry, existing["id"])
        )
    else:
        cursor.execute(
            "INSERT INTO pantry_items (id, name, quantity, unit, category, created_at, use_by_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item_id, name_clean, quantity, unit_clean, category_clean, created_at, use_by_date)
        )
        
    conn.commit()
    conn.close()

def update_pantry_qty(item_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    qty = max(0.0, quantity)
    if qty == 0.0:
        cursor.execute("DELETE FROM pantry_items WHERE id = ?", (item_id,))
    else:
        cursor.execute("UPDATE pantry_items SET quantity = ? WHERE id = ?", (qty, item_id))
        
    conn.commit()
    conn.close()

def delete_pantry_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pantry_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def cook_recipe_db(ingredients_req):
    """
    Deducts required ingredients from the pantry items database.
    ingredients_req: list of dicts with 'name' and 'quantity'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for req in ingredients_req:
            req_name = req.get("name", "").strip().lower()
            req_qty = req.get("quantity", 0.0)
            
            # Find matching items in pantry (ordered by useByDate ascending to use oldest first)
            cursor.execute(
                "SELECT id, quantity FROM pantry_items WHERE LOWER(name) = ? ORDER BY use_by_date ASC",
                (req_name,)
            )
            matches = cursor.fetchall()
            
            needed = req_qty
            for m in matches:
                if needed <= 0.0:
                    break
                p_id = m["id"]
                p_qty = m["quantity"]
                
                if p_qty >= needed:
                    new_qty = p_qty - needed
                    needed = 0.0
                    if new_qty == 0.0:
                        cursor.execute("DELETE FROM pantry_items WHERE id = ?", (p_id,))
                    else:
                        cursor.execute("UPDATE pantry_items SET quantity = ? WHERE id = ?", (new_qty, p_id))
                else:
                    needed -= p_qty
                    cursor.execute("DELETE FROM pantry_items WHERE id = ?", (p_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# --- Shopping DB Operations ---

def get_all_shopping():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shopping_items")
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "name": r["name"],
            "quantity": r["quantity"],
            "unit": r["unit"],
            "category": r["category"],
            "checked": bool(r["checked"]),
            "recipeName": r["recipe_name"]
        })
    return items

def add_or_update_shopping_item(item_id, name, quantity, unit, category, recipe_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    name_clean = name.strip()
    unit_clean = unit.strip()
    category_clean = category.strip()
    
    cursor.execute(
        "SELECT id, quantity FROM shopping_items WHERE LOWER(name) = ? AND LOWER(unit) = ?",
        (name_clean.lower(), unit_clean.lower())
    )
    existing = cursor.fetchone()
    
    if existing:
        new_qty = existing["quantity"] + quantity
        cursor.execute(
            "UPDATE shopping_items SET quantity = ?, checked = 0 WHERE id = ?",
            (new_qty, existing["id"])
        )
    else:
        cursor.execute(
            "INSERT INTO shopping_items (id, name, quantity, unit, category, checked, recipe_name) VALUES (?, ?, ?, ?, ?, 0, ?)",
            (item_id, name_clean, quantity, unit_clean, category_clean, recipe_name)
        )
        
    conn.commit()
    conn.close()

def toggle_shopping_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE shopping_items SET checked = 1 - checked WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def delete_shopping_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def purchase_checked_items_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get checked items
        cursor.execute("SELECT * FROM shopping_items WHERE checked = 1")
        checked_rows = cursor.fetchall()
        
        now_str = datetime.now().isoformat()
        default_expiry = (datetime.now() + timedelta(days=7)).isoformat()
        
        for r in checked_rows:
            name_clean = r["name"].strip()
            unit_clean = r["unit"].strip()
            qty = r["quantity"]
            cat = r["category"]
            
            # Try to add to pantry
            cursor.execute(
                "SELECT id, quantity, use_by_date FROM pantry_items WHERE LOWER(name) = ? AND LOWER(unit) = ?", 
                (name_clean.lower(), unit_clean.lower())
            )
            existing_pantry = cursor.fetchone()
            
            if existing_pantry:
                new_qty = existing_pantry["quantity"] + qty
                cursor.execute(
                    "UPDATE pantry_items SET quantity = ? WHERE id = ?",
                    (new_qty, existing_pantry["id"])
                )
            else:
                import uuid
                item_id = str(uuid.uuid4())[:8]
                cursor.execute(
                    "INSERT INTO pantry_items (id, name, quantity, unit, category, created_at, use_by_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (item_id, name_clean, qty, unit_clean, cat, now_str, default_expiry)
                )
        
        # Delete checked shopping items
        cursor.execute("DELETE FROM shopping_items WHERE checked = 1")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
