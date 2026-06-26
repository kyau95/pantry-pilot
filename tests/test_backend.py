import os
import sys
import unittest
import json
import base64
import urllib.request
import urllib.error

# Ensure backend directory is in system path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import db
from main import MealPlanRequest

class TestPantryPilotBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Point SQLite DB to a test db file during tests
        cls.orig_db_path = db.DB_PATH
        db.DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "test_pantry_pilot.db"))
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        # Clean up test DB file and restore original path
        db.DB_PATH = cls.orig_db_path
        test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "test_pantry_pilot.db"))
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except Exception:
                pass

    def setUp(self):
        # Clear tables before each test
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pantry_items")
        cursor.execute("DELETE FROM shopping_items")
        conn.commit()
        conn.close()

    def test_meal_plan_request_pydantic_validation(self):
        """
        Validate that the MealPlanRequest pydantic model enforces correct types
        and handles the new dietary_tags field correctly.
        """
        data = {
            "inventory": [{"name": "Tomato", "quantity": 2, "unit": "pieces"}],
            "preference": "Spicy",
            "dietary_tags": ["Vegetarian", "Gluten-Free"]
        }
        request = MealPlanRequest(**data)
        self.assertEqual(request.preference, "Spicy")
        self.assertEqual(request.dietary_tags, ["Vegetarian", "Gluten-Free"])
        self.assertEqual(len(request.inventory), 1)

    def test_sqlite_pantry_crud_operations(self):
        """
        Test direct SQLite database helper operations for the Pantry inventory.
        """
        # 1. Add item
        db.add_or_update_pantry_item("item-123", "Chicken Breast", 2.0, "pack", "Meats & Proteins")
        items = db.get_all_pantry()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Chicken Breast")
        self.assertEqual(items[0]["quantity"], 2.0)
        self.assertEqual(items[0]["unit"], "pack")

        # 2. Update quantity (increment existing item)
        db.add_or_update_pantry_item("item-456", "Chicken Breast", 3.0, "pack", "Meats & Proteins")
        items = db.get_all_pantry()
        self.assertEqual(len(items), 1) # Should merge with existing item
        self.assertEqual(items[0]["quantity"], 5.0)

        # 3. Direct qty update
        db.update_pantry_qty(items[0]["id"], 4.5)
        items = db.get_all_pantry()
        self.assertEqual(items[0]["quantity"], 4.5)

        # 4. Direct delete
        db.delete_pantry_item(items[0]["id"])
        items = db.get_all_pantry()
        self.assertEqual(len(items), 0)

    def test_sqlite_cooking_deductions(self):
        """
        Test that cooking a recipe correctly deducts pantry items.
        """
        db.add_or_update_pantry_item("item-pasta", "Pasta", 300.0, "g", "Grains")
        db.add_or_update_pantry_item("item-tomato", "Tomato", 3.0, "pieces", "Vegetables")

        # Cook recipe requiring 250g Pasta and 2 Tomatoes
        req_ingredients = [
            {"name": "Pasta", "quantity": 250.0},
            {"name": "Tomato", "quantity": 2.0}
        ]
        db.cook_recipe_db(req_ingredients)

        items = db.get_all_pantry()
        pasta = next(i for i in items if i["name"] == "Pasta")
        tomato = next(i for i in items if i["name"] == "Tomato")

        self.assertEqual(pasta["quantity"], 50.0)
        self.assertEqual(tomato["quantity"], 1.0)

    def test_sqlite_shopping_operations(self):
        """
        Test SQLite database CRUD operations for the Shopping List checklist.
        """
        # 1. Add shopping items
        db.add_or_update_shopping_item("shop-1", "Basil", 1.0, "bunch", "Vegetables")
        db.add_or_update_shopping_item("shop-2", "Cheese", 200.0, "g", "Dairy")

        items = db.get_all_shopping()
        self.assertEqual(len(items), 2)
        self.assertFalse(items[0]["checked"])

        # 2. Toggle checked status
        db.toggle_shopping_item("shop-1")
        items = db.get_all_shopping()
        basil = next(i for i in items if i["id"] == "shop-1")
        self.assertTrue(basil["checked"])

        # 3. Bulk purchase checked items
        db.purchase_checked_items_db()
        
        # Basil should move to pantry, Cheese stays in shopping list
        shopping_items = db.get_all_shopping()
        self.assertEqual(len(shopping_items), 1)
        self.assertEqual(shopping_items[0]["name"], "Cheese")

        pantry_items = db.get_all_pantry()
        self.assertEqual(len(pantry_items), 1)
        self.assertEqual(pantry_items[0]["name"], "Basil")

    def test_live_server_endpoints(self):
        """
        Check if the backend server is running on http://localhost:8000.
        If it is running, perform live integration tests on API endpoints.
        If it is not running, skip HTTP integration checks.
        """
        server_url = "http://localhost:8000"
        
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
        self.assertIn("SQLite Persistence", health_data["description"])

        # 2. Verify /api/pantry CRUD
        # Clear remote pantry for testing (careful: this alters running server state)
        pantry_payload = {
            "id": "live-test-item",
            "name": "Live Test Tomato",
            "quantity": 3.0,
            "unit": "pieces",
            "category": "Vegetables"
        }
        req_add = urllib.request.Request(
            f"{server_url}/api/pantry",
            data=json.dumps(pantry_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_add) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # Verify it was added
        req_get = urllib.request.Request(f"{server_url}/api/pantry", method="GET")
        with urllib.request.urlopen(req_get) as resp:
            items = json.loads(resp.read().decode('utf-8'))
            self.assertTrue(any(i["id"] == "live-test-item" for i in items))

        # Update quantity
        qty_payload = {"quantity": 5.0}
        req_update = urllib.request.Request(
            f"{server_url}/api/pantry/live-test-item",
            data=json.dumps(qty_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req_update) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # Delete it
        req_del = urllib.request.Request(
            f"{server_url}/api/pantry/live-test-item",
            method="DELETE"
        )
        with urllib.request.urlopen(req_del) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

if __name__ == '__main__':
    unittest.main()
