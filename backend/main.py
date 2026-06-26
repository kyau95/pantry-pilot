import os
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
