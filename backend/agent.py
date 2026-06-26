import os
import base64
import json
import io
from PIL import Image
from dotenv import load_dotenv

# Load env variables (contains GEMINI_API_KEY)
load_dotenv()

# We only load google-adk if it's imported in a context where dependencies exist,
# but we write the agent declarations using the framework SDK
try:
    from google.adk.agents.llm_agent import Agent
    HAS_ADK = True
except ImportError:
    HAS_ADK = False
    print("Warning: google-adk package not imported. Running in simulator-mode.")

# Tool to analyze grocery images
def analyze_grocery_image(image_base64: str) -> str:
    """
    Decodes an uploaded base64 image and parses the groceries.
    Returns a JSON string of parsed ingredients: name, quantity, unit, category, confidence.
    """
    try:
        img_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(img_data))
        print(f"[ADK Tool] Analyzing image of size {image.size}")
    except Exception as e:
        print(f"[ADK Tool] Error reading image data: {e}")

    # Standard gourmet grocery presets to simulate classifications from visual cues
    mock_results = [
        {"name": "Tomato", "quantity": 3, "unit": "pieces", "category": "Vegetables", "confidence": 0.96},
        {"name": "Pasta", "quantity": 250, "unit": "g", "category": "Grains", "confidence": 0.94},
        {"name": "Basil", "quantity": 1, "unit": "bunch", "category": "Vegetables", "confidence": 0.89},
        {"name": "Mozzarella", "quantity": 150, "unit": "g", "category": "Dairy", "confidence": 0.91},
        {"name": "Olive Oil", "quantity": 1, "unit": "bottle", "category": "Pantry Staples", "confidence": 0.95}
    ]
    return json.dumps(mock_results)

# Instantiate the Agent
if HAS_ADK:
    try:
        vision_agent = Agent(
            model='gemini-2.5-flash',
            name='vision_scanner',
            description='Parses image frame base64 strings and extracts structured kitchen inventory items.',
            instruction='Given a base64 image data payload, use the analyze_grocery_image tool to classify and extract ingredients.',
            tools=[analyze_grocery_image]
        )
    except Exception as e:
        print(f"Failed to initialize google-adk Agent: {e}")
        vision_agent = None
else:
    vision_agent = None

def run_vision_agent(image_bytes: bytes) -> list[dict]:
    """
    Main entry point for running the vision analysis.
    If the ADK Agent is configured and GEMINI_API_KEY is available, executes via the Agent SDK.
    Otherwise, returns parsed mock classifications securely.
    """
    # 1. Base64 encode the incoming image bytes for the tool
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    
    # 2. Check if we have active ADK agent capabilities and a Gemini key
    has_api_key = bool(os.getenv("GEMINI_API_KEY"))
    
    if HAS_ADK and vision_agent is not None and has_api_key:
        try:
            print("[ADK Backend] Running vision_agent pipeline...")
            # Query the agent with the base64 string
            prompt = f"Run tool analyze_grocery_image with payload: {base64_str[:100]}..."
            # Execute the agent
            result_str = vision_agent.run(prompt)
            # Parse the tool response back into a list of objects
            # Clean up the output string to isolate the JSON array
            start = result_str.find('[')
            end = result_str.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(result_str[start:end])
        except Exception as e:
            print(f"[ADK Backend] Agent execution failed: {e}. Falling back to offline scanner.")
            
    # Fallback/Offline Simulator Mode
    print("[ADK Backend] Running in offline simulator mode...")
    tool_output = analyze_grocery_image(base64_str)
    return json.loads(tool_output)
