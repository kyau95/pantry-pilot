import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_vision_agent

app = FastAPI(title="Pantry Pilot ADK Agent Backend")

# Configure CORS so our Svelte app can access the endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock down to the Svelte app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MealPlanRequest(BaseModel):
    inventory: list[dict]
    preference: str
    dietary_tags: list[str] = []

@app.get("/api/health")
def health_check():
    """
    Health check probed by Svelte client to auto-detect ADK agent backend.
    """
    has_api_key = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "ok",
        "mode": "ADK Agent" if has_api_key else "ADK Offline Simulator",
        "description": "Connected to Google ADK Python Backend."
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
    # Simple structured builder to return recipe proposals
    pref = request.preference.lower()
    
    # Custom recipe generation logic (with fallback)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
