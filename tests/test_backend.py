import os
import sys
import unittest
import unittest.mock
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
        # Initialize test DB tables and seed default recipes
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
        # Clear pantry and shopping list tables before each test
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pantry_items")
        cursor.execute("DELETE FROM shopping_items")
        # Remove only custom recipes to keep seeded recipes intact
        cursor.execute("DELETE FROM recipes WHERE is_custom = 1")
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
        db.add_or_update_pantry_item("item-123", "Chicken Breast", 2.0, "pack", "Meats & Proteins")
        items = db.get_all_pantry()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Chicken Breast")

        db.add_or_update_pantry_item("item-456", "Chicken Breast", 3.0, "pack", "Meats & Proteins")
        items = db.get_all_pantry()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 5.0)

        db.update_pantry_qty(items[0]["id"], 4.5)
        items = db.get_all_pantry()
        self.assertEqual(items[0]["quantity"], 4.5)

        db.delete_pantry_item(items[0]["id"])
        items = db.get_all_pantry()
        self.assertEqual(len(items), 0)

    def test_sqlite_cooking_deductions(self):
        """
        Test that cooking a recipe correctly deducts pantry items.
        """
        db.add_or_update_pantry_item("item-pasta", "Pasta", 300.0, "g", "Grains")
        db.add_or_update_pantry_item("item-tomato", "Tomato", 3.0, "pieces", "Vegetables")

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
        db.add_or_update_shopping_item("shop-1", "Basil", 1.0, "bunch", "Vegetables")
        db.add_or_update_shopping_item("shop-2", "Cheese", 200.0, "g", "Dairy")

        items = db.get_all_shopping()
        self.assertEqual(len(items), 2)

        # Test clear shopping list database helper
        db.clear_shopping_list_db()
        self.assertEqual(len(db.get_all_shopping()), 0)

        # Re-add items for remaining assertions
        db.add_or_update_shopping_item("shop-1", "Basil", 1.0, "bunch", "Vegetables")
        db.add_or_update_shopping_item("shop-2", "Cheese", 200.0, "g", "Dairy")

        items = db.get_all_shopping()
        self.assertEqual(len(items), 2)

        # Test updating quantity
        db.update_shopping_qty("shop-2", 250.0)
        items = db.get_all_shopping()
        cheese = next(i for i in items if i["id"] == "shop-2")
        self.assertEqual(cheese["quantity"], 250.0)

        # Test updating quantity to 0 deletes the item
        db.update_shopping_qty("shop-2", 0)
        items = db.get_all_shopping()
        self.assertEqual(len(items), 1)
        self.assertTrue(all(i["id"] != "shop-2" for i in items))

        db.toggle_shopping_item("shop-1")
        items = db.get_all_shopping()
        basil = next(i for i in items if i["id"] == "shop-1")
        self.assertTrue(basil["checked"])

        db.purchase_checked_items_db()
        
        shopping_items = db.get_all_shopping()
        self.assertEqual(len(shopping_items), 0)

        pantry_items = db.get_all_pantry()
        self.assertEqual(len(pantry_items), 1)

    def test_sqlite_recipe_seeding_and_custom_crud(self):
        """
        Test that default recipes are seeded and that custom recipes can be created and deleted.
        """
        # 1. Verify default recipes are seeded
        recipes = db.get_all_recipes()
        self.assertGreaterEqual(len(recipes), 8)
        self.assertTrue(any(r["id"] == "creamy-tomato-pasta" for r in recipes))
        caprese = next(r for r in recipes if r["id"] == "caprese-salad")
        self.assertEqual(caprese["image"], "https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600&auto=format&fit=crop&q=60")

        # 2. Add custom recipe
        db.add_custom_recipe_db(
            "custom-egg",
            "Scrambled Eggs Special",
            "A fast scrambled eggs recipe",
            5,
            5,
            "Easy",
            "Breakfast",
            "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600",
            [{"name": "Eggs", "quantity": 2, "unit": "pieces", "category": "Meats & Proteins"}],
            ["Crack eggs", "Scramble in skillet"],
            ["Gluten-Free"]
        )

        recipes = db.get_all_recipes()
        self.assertEqual(len(recipes), 9)
        custom = next(r for r in recipes if r["id"] == "custom-egg")
        self.assertEqual(custom["name"], "Scrambled Eggs Special")
        self.assertTrue(custom["isCustom"])
        self.assertEqual(custom["dietaryTags"], ["Gluten-Free"])

        # 3. Delete custom recipe
        db.delete_custom_recipe_db("custom-egg")
        recipes = db.get_all_recipes()
        self.assertEqual(len(recipes), 8)

    @unittest.mock.patch('urllib.request.urlopen')
    @unittest.mock.patch('main.scrape_html')
    def test_scrape_external_link_endpoint(self, mock_scrape_html, mock_urlopen):
        """
        Test the scrape_external_link endpoint with a mocked scraper.
        """
        mock_scraper = unittest.mock.MagicMock()
        mock_scraper.title.return_value = "Mocked Lasagna"
        mock_scraper.description.return_value = "Tasty lasagna"
        mock_scraper.prep_time.return_value = 15
        mock_scraper.cook_time.return_value = 45
        mock_scraper.image.return_value = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600"
        mock_scraper.ingredients.return_value = ["1 cup Ricotta", "2 sheets Pasta"]
        mock_scraper.instructions_list.return_value = ["Boil pasta", "Bake lasagna"]
        
        mock_scrape_html.return_value = mock_scraper
        
        from main import scrape_external_link, ScrapeRecipeRequest
        payload = ScrapeRecipeRequest(url="https://www.example.com/recipe/lasagna")
        response = scrape_external_link(payload)
        
        self.assertEqual(response["status"], "success")
        recipe = response["recipe"]
        self.assertEqual(recipe["name"], "Mocked Lasagna")
        self.assertEqual(recipe["prepTime"], 15)
        self.assertEqual(recipe["cookTime"], 45)
        self.assertEqual(len(recipe["ingredients"]), 2)
        self.assertEqual(recipe["ingredients"][0]["name"], "Ricotta")
        self.assertEqual(recipe["ingredients"][0]["quantity"], 1.0)
        self.assertEqual(recipe["ingredients"][0]["unit"], "cups")
        self.assertEqual(recipe["ingredients"][0]["originalText"], "1 cup Ricotta")
        self.assertEqual(recipe["ingredients"][1]["name"], "Sheets Pasta")
        self.assertEqual(recipe["ingredients"][1]["quantity"], 2.0)
        self.assertEqual(recipe["ingredients"][1]["unit"], "pieces")
        self.assertEqual(recipe["ingredients"][1]["originalText"], "2 sheets Pasta")
        self.assertEqual(recipe["instructions"], ["Boil pasta", "Bake lasagna"])

    def test_ingredient_string_parser(self):
        """
        Verify that parse_ingredient_string correctly extracts quantities, standard units,
        clean title-cased names, and preserves originalText.
        """
        from main import parse_ingredient_string
        
        res1 = parse_ingredient_string("2 tablespoons butter (divided)")
        self.assertEqual(res1["quantity"], 2.0)
        self.assertEqual(res1["unit"], "tbsp")
        self.assertEqual(res1["name"], "Butter")
        self.assertEqual(res1["category"], "Dairy")
        self.assertEqual(res1["originalText"], "2 tablespoons butter (divided)")
        
        res2 = parse_ingredient_string("1 ½ cups all-purpose flour")
        self.assertEqual(res2["quantity"], 1.5)
        self.assertEqual(res2["unit"], "cups")
        self.assertEqual(res2["name"], "All-Purpose Flour")
        self.assertEqual(res2["category"], "Grains")
        self.assertEqual(res2["originalText"], "1 ½ cups all-purpose flour")
        
        res3 = parse_ingredient_string("3 teaspoons white sugar")
        self.assertEqual(res3["quantity"], 1.0)
        self.assertEqual(res3["unit"], "tbsp")
        self.assertEqual(res3["name"], "White Sugar")
        self.assertEqual(res3["category"], "Pantry Staples")
        self.assertEqual(res3["originalText"], "3 teaspoons white sugar")
        
        res4 = parse_ingredient_string("1 large chicken breast (about ¾ lb.)")
        self.assertEqual(res4["quantity"], 1.0)
        self.assertEqual(res4["unit"], "pieces")
        self.assertEqual(res4["name"], "Chicken Breast")
        self.assertEqual(res4["category"], "Meats & Proteins")
        self.assertEqual(res4["originalText"], "1 large chicken breast (about ¾ lb.)")

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
                health_data = response.read()
        except (urllib.error.URLError, ConnectionError):
            print("\n⚠️  [SKIPPED] Live integration tests skipped because no running server was detected at http://localhost:8000.")
            return

        print(f"\n✅ [RUNNING] Live server detected at {server_url}. Running HTTP integration tests...")

        # Verify /api/recipes endpoint returns list
        req_recipes = urllib.request.Request(f"{server_url}/api/recipes", method="GET")
        with urllib.request.urlopen(req_recipes) as resp:
            recipes = json.loads(resp.read().decode('utf-8'))
            self.assertIsInstance(recipes, list)
            self.assertGreaterEqual(len(recipes), 8)

        # Test adding custom recipe via POST
        custom_payload = {
            "id": "live-custom-recipe",
            "name": "Live Custom Salad",
            "description": "A fresh custom salad",
            "prepTime": 5,
            "cookTime": 0,
            "difficulty": "Easy",
            "category": "Lunch",
            "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600",
            "ingredients": [{"name": "Lettuce", "quantity": 1, "unit": "head", "category": "Vegetables"}],
            "instructions": ["Chop lettuce", "Toss in bowl"],
            "dietaryTags": ["Vegetarian"]
        }
        req_post = urllib.request.Request(
            f"{server_url}/api/recipes",
            data=json.dumps(custom_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_post) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # Test deleting it
        req_del = urllib.request.Request(
            f"{server_url}/api/recipes/live-custom-recipe",
            method="DELETE"
        )
        with urllib.request.urlopen(req_del) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # Test adding, updating quantity, and deleting a shopping item via live API
        shop_payload = {
            "id": "live-shop-item",
            "name": "Live Milk",
            "quantity": 1.0,
            "unit": "bottle",
            "category": "Dairy"
        }
        req_shop_post = urllib.request.Request(
            f"{server_url}/api/shopping",
            data=json.dumps(shop_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_shop_post) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # Update shopping quantity to 5
        qty_payload = {
            "quantity": 5.0
        }
        req_shop_put = urllib.request.Request(
            f"{server_url}/api/shopping/live-shop-item",
            data=json.dumps(qty_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req_shop_put) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # Verify change in get_all
        req_get_shop = urllib.request.Request(f"{server_url}/api/shopping", method="GET")
        with urllib.request.urlopen(req_get_shop) as resp:
            shop_items = json.loads(resp.read().decode('utf-8'))
            live_item = next(i for i in shop_items if i["id"] == "live-shop-item")
            self.assertEqual(live_item["quantity"], 5.0)

        # Delete the shopping item
        req_shop_del = urllib.request.Request(
            f"{server_url}/api/shopping/live-shop-item",
            method="DELETE"
        )
        with urllib.request.urlopen(req_shop_del) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # Test bulk clear endpoint on live API
        # 1. Re-add item
        with urllib.request.urlopen(req_shop_post) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # 2. Call bulk clear DELETE /api/shopping
        req_bulk_del = urllib.request.Request(
            f"{server_url}/api/shopping",
            method="DELETE"
        )
        with urllib.request.urlopen(req_bulk_del) as resp:
            self.assertEqual(json.loads(resp.read().decode('utf-8'))["status"], "success")

        # 3. Verify the shopping list is now empty
        with urllib.request.urlopen(req_get_shop) as resp:
            shop_items = json.loads(resp.read().decode('utf-8'))
            self.assertEqual(len(shop_items), 0)

if __name__ == '__main__':
    unittest.main()
