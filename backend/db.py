import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "pantry_pilot.db"))

# Default recipes list to seed the SQLite database if it's empty
SEED_RECIPES = [
    {
        "id": "creamy-tomato-pasta",
        "name": "Creamy Tomato Basil Pasta",
        "description": "A comforting, rich Italian pasta tossed in a creamy tomato sauce and finished with fresh basil.",
        "prepTime": 10,
        "cookTime": 15,
        "difficulty": "Easy",
        "category": "Dinner",
        "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Pasta", "quantity": 250, "unit": "g", "category": "Grains"},
            {"name": "Tomato", "quantity": 3, "unit": "pieces", "category": "Vegetables"},
            {"name": "Garlic", "quantity": 3, "unit": "cloves", "category": "Pantry Staples"},
            {"name": "Onion", "quantity": 1, "unit": "piece", "category": "Vegetables"},
            {"name": "Milk", "quantity": 150, "unit": "ml", "category": "Dairy"},
            {"name": "Butter", "quantity": 2, "unit": "tbsp", "category": "Dairy"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp", "category": "Pantry Staples"},
            {"name": "Basil", "quantity": 5, "unit": "leaves", "category": "Vegetables"}
        ],
        "instructions": [
            "Boil pasta in salted water according to package instructions until al dente.",
            "Finely dice the onion and mince the garlic.",
            "Heat olive oil and melt butter in a large pan over medium heat. Sauté onion and garlic until soft and fragrant (about 3 mins).",
            "Chop tomatoes and add them to the pan. Cook until they break down and form a sauce (about 7 mins).",
            "Stir in the milk and let it simmer gently for 2 minutes to thicken.",
            "Drain pasta and toss it directly into the sauce. Tear fresh basil leaves and fold them in just before serving."
        ],
        "dietaryTags": ["Vegetarian"]
    },
    {
        "id": "avocado-toast-egg",
        "name": "Gourmet Avocado Toast with Poached Egg",
        "description": "Crispy toasted sourdough topped with creamy mashed avocado, chili flakes, and a perfectly poached egg.",
        "prepTime": 5,
        "cookTime": 5,
        "difficulty": "Easy",
        "category": "Breakfast",
        "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Bread", "quantity": 2, "unit": "slices", "category": "Grains"},
            {"name": "Avocado", "quantity": 1, "unit": "piece", "category": "Fruits"},
            {"name": "Eggs", "quantity": 1, "unit": "piece", "category": "Meats & Proteins"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp", "category": "Pantry Staples"}
        ],
        "instructions": [
            "Toast your slices of bread until golden brown and crispy.",
            "Cut the avocado, scoop the flesh into a bowl, and mash with a fork. Season with a pinch of salt, pepper, and a drop of olive oil.",
            "Poach or fry the egg to your liking (a runny yolk is recommended).",
            "Spread the mashed avocado evenly over the toasted bread.",
            "Top with the cooked egg and optionally sprinkle with red pepper flakes or sesame seeds."
        ],
        "dietaryTags": ["Vegetarian"]
    },
    {
        "id": "garlic-butter-chicken",
        "name": "Garlic Butter Chicken Skillet",
        "description": "Tender pan-seared chicken breasts coated in a rich garlic butter sauce, cooked in a single skillet.",
        "prepTime": 10,
        "cookTime": 15,
        "difficulty": "Medium",
        "category": "Dinner",
        "image": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 400, "unit": "g", "category": "Meats & Proteins"},
            {"name": "Garlic", "quantity": 4, "unit": "cloves", "category": "Pantry Staples"},
            {"name": "Butter", "quantity": 3, "unit": "tbsp", "category": "Dairy"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp", "category": "Pantry Staples"},
            {"name": "Spinach", "quantity": 100, "unit": "g", "category": "Vegetables"}
        ],
        "instructions": [
            "Cut chicken breast into bite-sized cubes. Season with salt, pepper, and paprika.",
            "Heat olive oil and 1 tablespoon of butter in a large skillet over medium-high heat.",
            "Add chicken cubes in a single layer and sear until golden brown and cooked through (about 6-8 minutes). Remove chicken from the pan.",
            "Reduce heat to medium. Add remaining butter and minced garlic to the skillet. Cook for 1 minute until fragrant.",
            "Add baby spinach and cook until wilted (about 2 minutes).",
            "Return chicken to the skillet, toss in the garlic butter sauce, and serve hot."
        ],
        "dietaryTags": ["Gluten-Free"]
    },
    {
        "id": "caprese-salad",
        "name": "Classic Caprese Salad",
        "description": "A simple and elegant Italian salad featuring fresh mozzarella, vine-ripened tomatoes, and sweet basil leaves.",
        "prepTime": 5,
        "cookTime": 0,
        "difficulty": "Easy",
        "category": "Lunch",
        "image": "https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Tomato", "quantity": 2, "unit": "pieces", "category": "Vegetables"},
            {"name": "Mozzarella", "quantity": 150, "unit": "g", "category": "Dairy"},
            {"name": "Basil", "quantity": 10, "unit": "leaves", "category": "Vegetables"},
            {"name": "Olive Oil", "quantity": 2, "unit": "tbsp", "category": "Pantry Staples"}
        ],
        "instructions": [
            "Slice the fresh tomatoes and mozzarella cheese into 1/4-inch-thick rounds.",
            "Alternate layering tomato slices and mozzarella slices on a serving platter.",
            "Tuck whole fresh basil leaves between the tomato and cheese slices.",
            "Drizzle generously with extra virgin olive oil and season with sea salt and cracked black pepper."
        ],
        "dietaryTags": ["Vegetarian", "Gluten-Free"]
    },
    {
        "id": "spinach-cheese-omelet",
        "name": "Spinach & Cheese Fluffy Omelet",
        "description": "A light and fluffy 2-egg omelet loaded with fresh baby spinach and melted cheddar cheese.",
        "prepTime": 5,
        "cookTime": 5,
        "difficulty": "Easy",
        "category": "Breakfast",
        "image": "https://images.unsplash.com/photo-1494597564530-871f2b93ac55?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Eggs", "quantity": 2, "unit": "pieces", "category": "Meats & Proteins"},
            {"name": "Spinach", "quantity": 50, "unit": "g", "category": "Vegetables"},
            {"name": "Cheese", "quantity": 50, "unit": "g", "category": "Dairy"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp", "category": "Dairy"}
        ],
        "instructions": [
            "Crack eggs into a bowl, add a splash of water/milk, and whisk vigorously with a fork until frothy.",
            "Melt butter in a non-stick skillet over medium-low heat.",
            "Pour in the eggs. Let them cook slightly, then use a spatula to push the cooked edges toward the center.",
            "Once the eggs are mostly set but still slightly wet on top, scatter the baby spinach and shredded cheese over one half.",
            "Fold the omelet in half, cook for 1 more minute until cheese melts, and slide onto a plate."
        ],
        "dietaryTags": ["Vegetarian", "Gluten-Free"]
    },
    {
        "id": "french-toast",
        "name": "Classic Golden French Toast",
        "description": "Thick bread slices soaked in a rich custard of eggs and milk, pan-fried to golden-brown perfection.",
        "prepTime": 5,
        "cookTime": 10,
        "difficulty": "Easy",
        "category": "Breakfast",
        "image": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Bread", "quantity": 4, "unit": "slices", "category": "Grains"},
            {"name": "Eggs", "quantity": 2, "unit": "pieces", "category": "Meats & Proteins"},
            {"name": "Milk", "quantity": 100, "unit": "ml", "category": "Dairy"},
            {"name": "Butter", "quantity": 2, "unit": "tbsp", "category": "Dairy"}
        ],
        "instructions": [
            "In a wide, shallow bowl, whisk together the eggs and milk until fully combined.",
            "Melt 1 tablespoon of butter in a skillet over medium heat.",
            "Dip a slice of bread into the egg mixture for 10 seconds per side, allowing it to soak up the liquid.",
            "Place in the hot skillet and cook for 2-3 minutes per side until golden brown.",
            "Repeat with remaining slices, adding more butter as needed. Serve with honey, syrup, or fruit."
        ],
        "dietaryTags": ["Vegetarian"]
    },
    {
        "id": "chicken-spinach-stir-fry",
        "name": "Garlic Chicken & Spinach Stir-Fry",
        "description": "A quick, healthy stir-fry combining tender chicken, sweet onions, and fresh wilted spinach.",
        "prepTime": 10,
        "cookTime": 10,
        "difficulty": "Easy",
        "category": "Lunch",
        "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 300, "unit": "g", "category": "Meats & Proteins"},
            {"name": "Spinach", "quantity": 150, "unit": "g", "category": "Vegetables"},
            {"name": "Onion", "quantity": 1, "unit": "piece", "category": "Vegetables"},
            {"name": "Garlic", "quantity": 2, "unit": "cloves", "category": "Pantry Staples"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp", "category": "Pantry Staples"}
        ],
        "instructions": [
            "Slice the chicken breast into thin strips. Thinly slice the onion and mince the garlic.",
            "Heat olive oil in a wok or large skillet over high heat.",
            "Add chicken strips and stir-fry until cooked through and slightly browned (about 5 mins). Remove from wok.",
            "Add onion and garlic to the wok, stir-frying for 2 minutes until tender.",
            "Add spinach and return chicken to the wok. Toss continuously until the spinach is wilted and chicken is heated through (about 2 mins)."
        ],
        "dietaryTags": ["Gluten-Free", "Dairy-Free"]
    },
    {
        "id": "simple-grilled-cheese",
        "name": "Ultimate Crispy Grilled Cheese",
        "description": "Crispy, butter-toasted bread oozing with thick layers of warm, melted cheese.",
        "prepTime": 2,
        "cookTime": 6,
        "difficulty": "Easy",
        "category": "Snack",
        "image": "https://images.unsplash.com/photo-1476887334197-56adbf254e1a?w=600&auto=format&fit=crop&q=60",
        "ingredients": [
            {"name": "Bread", "quantity": 2, "unit": "slices", "category": "Grains"},
            {"name": "Cheese", "quantity": 80, "unit": "g", "category": "Dairy"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp", "category": "Dairy"}
        ],
        "instructions": [
            "Spread butter evenly on one side of each slice of bread.",
            "Place one slice of bread, buttered-side down, in a cold skillet.",
            "Lay the cheese slices evenly on top of the bread, then top with the second slice of bread, buttered-side up.",
            "Turn the heat to medium-low. Cook for 3-4 minutes until the bottom is golden brown and cheese begins to melt.",
            "Flip carefully and cook the other side for another 3 minutes until crispy and golden and cheese is completely melted."
        ],
        "dietaryTags": ["Vegetarian"]
    }
]

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
    
    # Create recipes table (with JSON text fields)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        prep_time INTEGER NOT NULL,
        cook_time INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        category TEXT NOT NULL,
        image TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        dietary_tags TEXT NOT NULL,
        is_custom INTEGER NOT NULL DEFAULT 0
    )
    """)
    
    conn.commit()
    
    # Seed recipes table if empty
    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]
    if count == 0:
        print("[SQLite DB] Seeding 8 default gourmet recipes into SQLite database...")
        for r in SEED_RECIPES:
            cursor.execute(
                """
                INSERT INTO recipes (id, name, description, prep_time, cook_time, difficulty, category, image, ingredients, instructions, dietary_tags, is_custom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    r["id"],
                    r["name"],
                    r["description"],
                    r["prepTime"],
                    r["cookTime"],
                    r["difficulty"],
                    r["category"],
                    r["image"],
                    json.dumps(r["ingredients"]),
                    json.dumps(r["instructions"]),
                    json.dumps(r["dietaryTags"])
                )
            )
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
    
    name_clean = name.strip()
    unit_clean = unit.strip()
    category_clean = category.strip()
    
    if not use_by_date:
        use_by_date = (datetime.now() + timedelta(days=7)).isoformat()
        
    created_at = datetime.now().isoformat()
    
    cursor.execute(
        "SELECT id, quantity, use_by_date FROM pantry_items WHERE LOWER(name) = ? AND LOWER(unit) = ?", 
        (name_clean.lower(), unit_clean.lower())
    )
    existing = cursor.fetchone()
    
    if existing:
        new_qty = existing["quantity"] + quantity
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for req in ingredients_req:
            req_name = req.get("name", "").strip().lower()
            req_qty = req.get("quantity", 0.0)
            
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

def update_shopping_qty(item_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    qty = max(0.0, quantity)
    if qty == 0.0:
        cursor.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
    else:
        cursor.execute("UPDATE shopping_items SET quantity = ? WHERE id = ?", (qty, item_id))
        
    conn.commit()
    conn.close()

def purchase_checked_items_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM shopping_items WHERE checked = 1")
        checked_rows = cursor.fetchall()
        
        now_str = datetime.now().isoformat()
        default_expiry = (datetime.now() + timedelta(days=7)).isoformat()
        
        for r in checked_rows:
            name_clean = r["name"].strip()
            unit_clean = r["unit"].strip()
            qty = r["quantity"]
            cat = r["category"]
            
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
        
        cursor.execute("DELETE FROM shopping_items WHERE checked = 1")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# --- Recipes DB Operations ---

def get_all_recipes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes")
    rows = cursor.fetchall()
    conn.close()
    
    recipes_list = []
    for r in rows:
        recipes_list.append({
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "prepTime": r["prep_time"],
            "cookTime": r["cook_time"],
            "difficulty": r["difficulty"],
            "category": r["category"],
            "image": r["image"],
            "ingredients": json.loads(r["ingredients"]),
            "instructions": json.loads(r["instructions"]),
            "dietaryTags": json.loads(r["dietary_tags"]),
            "isCustom": bool(r["is_custom"])
        })
    return recipes_list

def add_custom_recipe_db(recipe_id, name, description, prep_time, cook_time, difficulty, category, image, ingredients, instructions, dietary_tags):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Store lists as serialized JSON strings
    ingredients_str = json.dumps(ingredients)
    instructions_str = json.dumps(instructions)
    tags_str = json.dumps(dietary_tags)
    
    cursor.execute(
        """
        INSERT INTO recipes (id, name, description, prep_time, cook_time, difficulty, category, image, ingredients, instructions, dietary_tags, is_custom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            recipe_id,
            name.strip(),
            description.strip(),
            prep_time,
            cook_time,
            difficulty.strip(),
            category.strip(),
            image.strip() or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=60", # default placeholder food image
            ingredients_str,
            instructions_str,
            tags_str
        )
    )
    conn.commit()
    conn.close()

def delete_custom_recipe_db(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only allow deleting custom recipes
    cursor.execute("DELETE FROM recipes WHERE id = ? AND is_custom = 1", (recipe_id,))
    conn.commit()
    conn.close()
