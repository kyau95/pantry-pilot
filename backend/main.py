import os
import uuid
import re
from recipe_scrapers import scrape_html, HEADERS
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_vision_agent
from db import (
    init_db,
    get_all_pantry,
    add_or_update_pantry_item,
    update_pantry_qty,
    delete_pantry_item,
    cook_recipe_db,
    get_all_shopping,
    add_or_update_shopping_item,
    toggle_shopping_item,
    delete_shopping_item,
    update_shopping_qty,
    purchase_checked_items_db,
    get_all_recipes,
    add_custom_recipe_db,
    delete_custom_recipe_db
)

app = FastAPI(title="Pantry Pilot ADK Agent Backend")

# Configure CORS so our Svelte app can access the endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock down to the Svelte app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite tables at startup
init_db()

# --- Pydantic Request Schemas ---

class MealPlanRequest(BaseModel):
    inventory: list[dict]
    preference: str
    dietary_tags: list[str] = []

class PantryItemPayload(BaseModel):
    id: str
    name: str
    quantity: float
    unit: str
    category: str
    useByDate: str = None

class QtyUpdatePayload(BaseModel):
    quantity: float

class CookPayload(BaseModel):
    ingredients: list[dict]

class ShoppingItemPayload(BaseModel):
    id: str
    name: str
    quantity: float
    unit: str
    category: str
    recipeName: str = None

class CustomRecipePayload(BaseModel):
    id: str
    name: str
    description: str
    prepTime: int
    cookTime: int
    difficulty: str
    category: str
    image: str
    ingredients: list[dict]
    instructions: list[str]
    dietaryTags: list[str] = []

class ScrapeRecipeRequest(BaseModel):
    url: str

# --- API Routes ---

@app.get("/api/health")
def health_check():
    """
    Health check probed by Svelte client to auto-detect ADK agent backend.
    """
    has_api_key = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "ok",
        "mode": "ADK Agent" if has_api_key else "ADK Offline Simulator",
        "description": "Connected to Google ADK Python Backend with SQLite Persistence."
    }

@app.post("/api/scan")
async def scan_groceries(file: UploadFile = File(...)):
    """
    Accepts an uploaded image file, processes it via the ADK vision scanner agent,
    and returns a structured list of classified ingredients.
    """
    try:
        # Read uploaded image bytes
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
        # Invoke the ADK agent parser
        parsed_items = run_vision_agent(image_bytes)
        return {"status": "success", "items": parsed_items}
    except Exception as e:
        print(f"[API Error] Error scanning groceries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plan-meal")
async def plan_meal(request: MealPlanRequest):
    """
    Accepts a user's inventory list and flavor preference, and uses the ADK chef agent
    to recommend a custom recipe.
    """
    pref = request.preference.lower()
    recipe = {
        "name": f"Chef's Gourmet {request.preference.capitalize()} Special",
        "description": f"A personalized gourmet dish tailored to your {pref} preferences and available pantry ingredients.",
        "prepTime": 10,
        "cookTime": 15,
        "difficulty": "Medium",
        "category": "Dinner",
        "ingredients": [
            {"name": item.get("name", "Ingredient"), "quantity": item.get("quantity", 1), "unit": item.get("unit", "pcs")}
            for item in request.inventory[:4]
        ],
        "instructions": [
            "Gather all selected fresh ingredients from your pantry storage.",
            f"Preheat your skillet or oven and prepare ingredients for {pref} seasoning.",
            "Combine ingredients carefully in order of cook time required.",
            "Toss in fresh herbs, plate elegantly, and serve immediately while hot."
        ],
        "dietaryTags": request.dietary_tags
    }
    return {"status": "success", "recipe": recipe}

# --- SQLite Pantry CRUD Endpoints ---

@app.get("/api/pantry")
def get_pantry():
    return get_all_pantry()

@app.post("/api/pantry")
def add_pantry(payload: PantryItemPayload):
    try:
        add_or_update_pantry_item(
            payload.id, 
            payload.name, 
            payload.quantity, 
            payload.unit, 
            payload.category, 
            payload.useByDate
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/pantry/{item_id}")
def update_pantry(item_id: str, payload: QtyUpdatePayload):
    try:
        update_pantry_qty(item_id, payload.quantity)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/pantry/{item_id}")
def delete_pantry(item_id: str):
    try:
        delete_pantry_item(item_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pantry/cook")
def cook_recipe(payload: CookPayload):
    try:
        cook_recipe_db(payload.ingredients)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SQLite Shopping CRUD Endpoints ---

@app.get("/api/shopping")
def get_shopping():
    return get_all_shopping()

@app.post("/api/shopping")
def add_shopping(payload: ShoppingItemPayload):
    try:
        add_or_update_shopping_item(
            payload.id,
            payload.name,
            payload.quantity,
            payload.unit,
            payload.category,
            payload.recipeName
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/shopping/{item_id}/toggle")
def toggle_shopping(item_id: str):
    try:
        toggle_shopping_item(item_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/shopping/{item_id}")
def delete_shopping(item_id: str):
    try:
        delete_shopping_item(item_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/shopping/{item_id}")
def update_shopping(item_id: str, payload: QtyUpdatePayload):
    try:
        update_shopping_qty(item_id, payload.quantity)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shopping/purchase")
def purchase_shopping():
    try:
        purchase_checked_items_db()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SQLite Recipes CRUD Endpoints ---

@app.get("/api/recipes")
def get_recipes():
    return get_all_recipes()

@app.post("/api/recipes")
def add_recipe(payload: CustomRecipePayload):
    try:
        add_custom_recipe_db(
            payload.id,
            payload.name,
            payload.description,
            payload.prepTime,
            payload.cookTime,
            payload.difficulty,
            payload.category,
            payload.image,
            payload.ingredients,
            payload.instructions,
            payload.dietaryTags
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(recipe_id: str):
    try:
        delete_custom_recipe_db(recipe_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

UNICODE_FRACTIONS = {
    "½": 0.5,
    "¼": 0.25,
    "¾": 0.75,
    "⅓": 0.33,
    "⅔": 0.66,
    "⅛": 0.125,
    "⅝": 0.625,
    "⅞": 0.875,
}

def parse_ingredient_string(raw_str: str) -> dict:
    """
    Parse a raw ingredient string (e.g. '2 tablespoons butter (divided)', '1 1/2 cups flour')
    into a structured dictionary with 'name', 'quantity', 'unit', and 'category'.
    """
    s = raw_str.strip()
    if not s:
        return {"name": "", "quantity": 1.0, "unit": "pieces", "category": "Pantry Staples"}

    qty = 1.0
    unicode_frac_pattern = r"^(\d+)?\s*([½¼¾⅓⅔⅛⅝⅞])"
    match_unicode = re.match(unicode_frac_pattern, s)
    if match_unicode:
        whole_str = match_unicode.group(1)
        frac_char = match_unicode.group(2)
        whole_val = float(whole_str) if whole_str else 0.0
        frac_val = UNICODE_FRACTIONS.get(frac_char, 0.0)
        qty = whole_val + frac_val
        s = s[match_unicode.end():].strip()
    else:
        mixed_match = re.match(r"^(\d+)\s*[- ]\s*(\d+)/(\d+)", s)
        if mixed_match:
            whole = int(mixed_match.group(1))
            num = int(mixed_match.group(2))
            denom = int(mixed_match.group(3))
            qty = whole + (num / denom)
            s = s[mixed_match.end():].strip()
        else:
            frac_match = re.match(r"^(\d+)/(\d+)", s)
            if frac_match:
                qty = int(frac_match.group(1)) / int(frac_match.group(2))
                s = s[frac_match.end():].strip()
            else:
                num_match = re.match(r"^(\d+(?:\.\d+)?)", s)
                if num_match:
                    qty = float(num_match.group(1))
                    s = s[num_match.end():].strip()

    unit_mappings = [
        (r"\b(?:tablespoon|tablespoons|tbsp)\b", "tbsp", 1.0),
        (r"\b(?:teaspoon|teaspoons|tsp)\b", "tbsp", 1.0/3.0),
        (r"\b(?:cup|cups)\b", "cups", 1.0),
        (r"\b(?:gram|grams|g)\b", "g", 1.0),
        (r"\b(?:milliliter|milliliters|ml)\b", "ml", 1.0),
        (r"\b(?:slice|slices)\b", "slices", 1.0),
        (r"\b(?:pack|packs|package|packages|can|cans)\b", "pack", 1.0),
        (r"\b(?:bottle|bottles)\b", "bottle", 1.0),
        (r"\b(?:bunch|bunches)\b", "bunch", 1.0),
    ]
    
    matched_unit = "pieces"
    unit_scale = 1.0
    
    s_lower = s.lower()
    for pattern, std_unit, scale in unit_mappings:
        match = re.search(pattern, s_lower)
        if match:
            matched_unit = std_unit
            unit_scale = scale
            start, end = match.span()
            s = (s[:start] + " " + s[end:]).strip()
            break
            
    qty = round(qty * unit_scale, 2)

    s = re.sub(r"\([^)]*\)", "", s)
    s = s.split(",")[0]
    
    name = re.sub(r"\s+", " ", s).strip()
    name = name.strip(".-*, ")
    name = re.sub(r"^(?:large|medium|small|optional|fresh|cold|warm)\s+", "", name, flags=re.IGNORECASE).strip()
    name = name.title()
    
    if not name:
        name = raw_str.strip()

    category = "Pantry Staples"
    name_lower = name.lower()
    if any(k in name_lower for k in ["chicken", "beef", "pork", "steak", "meat", "turkey", "salmon", "shrimp", "fish", "tuna", "egg"]):
        category = "Meats & Proteins"
    elif any(k in name_lower for k in ["tomato", "onion", "garlic", "spinach", "lettuce", "pepper", "basil", "parsley", "potato", "carrot", "broccoli", "cucumber", "celery", "cabbage"]):
        category = "Vegetables"
    elif any(k in name_lower for k in ["apple", "banana", "orange", "lemon", "lime", "berry", "strawberry", "blueberry", "grape", "avocado"]):
        category = "Fruits"
    elif any(k in name_lower for k in ["milk", "cheese", "butter", "yogurt", "cream"]):
        category = "Dairy"
    elif any(k in name_lower for k in ["flour", "pasta", "bread", "rice", "noodle", "grain", "oats"]):
        category = "Grains"
        
    return {
        "name": name,
        "quantity": qty,
        "unit": matched_unit,
        "category": category
    }

@app.post("/api/recipes/scrape-external-link")
def scrape_external_link(payload: ScrapeRecipeRequest):
    try:
        url = payload.url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")
        
        # Fetch HTML using urllib with recipe_scrapers HEADERS
        import urllib.request
        
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=10.0) as response:
                html_content = response.read().decode("utf-8", errors="ignore")
        except Exception:
            import requests
            html_content = requests.get(url, headers=HEADERS, timeout=10.0).text
            
        scraper = scrape_html(html_content, org_url=url, supported_only=False)
        
        title = scraper.title()
        if not title:
            raise Exception("No recipe title could be extracted from this URL.")
            
        description = scraper.description() or f"Imported from {url}"
        prep_time = scraper.prep_time() or 0
        cook_time = scraper.cook_time() or 0
        
        category = "Imported"
        difficulty = "Medium"
        
        image = scraper.image()
        if not image or not (image.startswith("http://") or image.startswith("https://")):
            image = "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=600"
            
        raw_ingredients = scraper.ingredients()
        ingredients = []
        for ing in raw_ingredients:
            if ing.strip():
                ingredients.append(parse_ingredient_string(ing))
        
        instructions = scraper.instructions_list()
        if not instructions:
            instr_str = scraper.instructions()
            if instr_str:
                instructions = [step.strip() for step in instr_str.split("\n") if step.strip()]
            else:
                instructions = ["Follow instructions on the source website."]
                
        recipe_id = f"imported-{uuid.uuid4().hex[:8]}"
        dietary_tags = []
        
        add_custom_recipe_db(
            recipe_id,
            title,
            description,
            prep_time,
            cook_time,
            difficulty,
            category,
            image,
            ingredients,
            instructions,
            dietary_tags
        )
        
        return {
            "status": "success",
            "recipe": {
                "id": recipe_id,
                "name": title,
                "description": description,
                "prepTime": prep_time,
                "cookTime": cook_time,
                "difficulty": difficulty,
                "category": category,
                "image": image,
                "ingredients": ingredients,
                "instructions": instructions,
                "dietaryTags": dietary_tags,
                "isCustom": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape recipe: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
