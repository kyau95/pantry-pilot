import os
import sys
import unittest
import json
import base64
import urllib.request
import urllib.error

# Ensure backend directory is in the system path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import MealPlanRequest
from agent import analyze_grocery_image, run_vision_agent

class TestPantryPilotBackend(unittest.TestCase):

    def test_meal_plan_request_pydantic_validation(self):
        """
        Validate that the MealPlanRequest pydantic model enforces correct types
        and handles the new dietary_tags field correctly.
        """
        # Test valid request
        data = {
            "inventory": [{"name": "Tomato", "quantity": 2, "unit": "pieces"}],
            "preference": "Spicy",
            "dietary_tags": ["Vegetarian", "Gluten-Free"]
        }
        request = MealPlanRequest(**data)
        self.assertEqual(request.preference, "Spicy")
        self.assertEqual(request.dietary_tags, ["Vegetarian", "Gluten-Free"])
        self.assertEqual(len(request.inventory), 1)

        # Test request with missing optional dietary_tags (should default to empty list)
        data_no_tags = {
            "inventory": [{"name": "Tomato", "quantity": 2, "unit": "pieces"}],
            "preference": "Spicy"
        }
        request_no_tags = MealPlanRequest(**data_no_tags)
        self.assertEqual(request_no_tags.dietary_tags, [])

    def test_vision_agent_tool(self):
        """
        Validate that the analyze_grocery_image tool decodes input base64
        and returns the correct structured list of mock items.
        """
        # Encode a small mock image byte payload
        mock_bytes = b"fake-image-bytes"
        b64_data = base64.b64encode(mock_bytes).decode('utf-8')
        
        # Invoke the tool directly
        result_str = analyze_grocery_image(b64_data)
        result = json.loads(result_str)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["name"], "Tomato")
        self.assertIn("category", result[0])
        self.assertIn("quantity", result[0])

    def test_vision_agent_fallback_runner(self):
        """
        Validate that run_vision_agent returns valid classifications.
        """
        mock_bytes = b"fake-image-bytes"
        result = run_vision_agent(mock_bytes)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["name"], "Tomato")

    def test_live_server_endpoints(self):
        """
        Check if the backend server is running on http://localhost:8000.
        If it is running, perform live integration tests on API endpoints.
        If it is not running, skip HTTP integration checks.
        """
        server_url = "http://localhost:8000"
        
        # Probe health endpoint to check if server is active
        try:
            req = urllib.request.Request(f"{server_url}/api/health", method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as response:
                health_data = json.loads(response.read().decode('utf-8'))
        except (urllib.error.URLError, ConnectionError):
            print("\n⚠️  [SKIPPED] Live integration tests skipped because no running server was detected at http://localhost:8000.")
            return

        print(f"\n✅ [RUNNING] Live server detected at {server_url}. Running HTTP integration tests...")

        # 1. Verify health check schema
        self.assertEqual(health_data["status"], "ok")
        self.assertIn("mode", health_data)

        # 2. Verify /api/plan-meal with dietary tags
        meal_data = {
            "inventory": [
                {"name": "Pasta", "quantity": 1, "unit": "pack"},
                {"name": "Tomato", "quantity": 3, "unit": "pcs"}
            ],
            "preference": "Italian",
            "dietary_tags": ["Vegetarian"]
        }
        
        req_meal = urllib.request.Request(
            f"{server_url}/api/plan-meal",
            data=json.dumps(meal_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req_meal) as response:
            meal_response = json.loads(response.read().decode('utf-8'))
            
        self.assertEqual(meal_response["status"], "success")
        self.assertIn("recipe", meal_response)
        recipe = meal_response["recipe"]
        self.assertEqual(recipe["dietaryTags"], ["Vegetarian"])
        self.assertIn("prepTime", recipe)
        self.assertIn("ingredients", recipe)
        self.assertIn("instructions", recipe)

        # 3. Verify /api/scan with multipart/form-data upload
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="test.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
            f"dummy-image-content\r\n"
            f"--{boundary}--\r\n"
        ).encode('utf-8')

        req_scan = urllib.request.Request(
            f"{server_url}/api/scan",
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            },
            method="POST"
        )

        with urllib.request.urlopen(req_scan) as response:
            scan_response = json.loads(response.read().decode('utf-8'))
            
        self.assertEqual(scan_response["status"], "success")
        self.assertIsInstance(scan_response["items"], list)
        self.assertGreater(len(scan_response["items"]), 0)


if __name__ == '__main__':
    unittest.main()
