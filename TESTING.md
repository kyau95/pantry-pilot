# Pantry Pilot - Testing Guide & Test Plan 🧪

This document describes the test plan, manual validation suite, and automated test harness used to verify the correctness of Pantry Pilot's features, with a focus on the new **Use-by Date Expiration Tracking**, **Dietary Filter Toggles**, and **Simulated Barcode Scanner**.

---

## 🤖 1. Automated Test Harness

We have written a comprehensive, lightweight automated test harness inside the [`tests/test_backend.py`](file://wsl.localhost/Ubuntu-24.04/home/keyau/pantry-pilot/tests/test_backend.py) file. This test suite validates:
1. **Pydantic Model Schema**: Checks that the FastAPI server accepts `dietary_tags: list[str] = []` correctly and handles missing values.
2. **ADK Tool & Runner Logic**: Direct unit testing of `analyze_grocery_image` tool and `run_vision_agent` fallback pipeline.
3. **Live API Integration**: Auto-detects if the FastAPI server is running on `http://localhost:8000`. If active, it dispatches HTTP queries to `/api/health`, `/api/plan-meal` (with dietary parameters), and `/api/scan` (with file upload streaming) to verify responses match expected contracts.

### How to Run Automated Tests:

Ensure your backend virtual environment is active, then execute:

```bash
# Run unit tests
backend/venv/bin/python3 tests/test_backend.py
```

If you start the backend server beforehand (using `./start.sh` or `python backend/main.py`), the test harness will automatically upgrade to run live integration tests alongside the unit tests!

---

## 🧑‍💻 2. Manual Test Suite

Follow these step-by-step test cases to manually verify the frontend UI components and their integration with the local stores.

### Test Case A: "Use By" Date Expiration Tracker
* **Objective**: Ensure that expiration tracking badge colors function correctly and items are sorted properly.
* **Steps**:
  1. Navigate to the **Pantry** tab.
  2. Locate the "Add Item Manually" form.
  3. Enter a mock item:
     * Name: `Expiring Bread`
     * Quantity: `1`
     * Unit: `pieces`
     * Expiration Date: Select a date exactly **2 days in the future**. Click **Add Item**.
  4. Verify the item appears in the list with an **Expiring Soon** (orange) badge.
  5. Add another item:
     * Name: `Fresh Spinach`
     * Quantity: `2`
     * Unit: `bags`
     * Expiration Date: Select a date **10 days in the future**. Click **Add Item**.
  6. Verify the item appears with a **Fresh** (green) badge.
  7. Add a third item:
     * Name: `Expired Milk`
     * Quantity: `1`
     * Unit: `bottle`
     * Expiration Date: Select **yesterday's date** or earlier. Click **Add Item**.
  8. Verify the item appears with an **Expired** (red) badge.
  9. **Sort Verification**: Check that `Expired Milk` is at the very top of the list, followed by `Expiring Bread`, and then `Fresh Spinach` at the bottom.

---

### Test Case B: Dietary Filter Toggles
* **Objective**: Ensure dietary tags filter recipes accurately and correctly send preferences to the backend.
* **Steps**:
  1. Navigate to the **Cookbook** tab.
  2. Observe the default recipe grid. You should see all 8 curated recipes.
  3. Click the **Vegetarian** filter pill in the filters bar.
  4. Verify that non-vegetarian recipes (like *Garlic Butter Chicken Skillet* and *Garlic Chicken & Spinach Stir-Fry*) disappear, while *Creamy Tomato Basil Pasta*, *Caprese Salad*, and others remain.
  5. Click the **Gluten-Free** pill as well (both `Vegetarian` and `Gluten-Free` active).
  6. Verify that only recipes matching *both* tags (e.g., *Caprese Salad* and *Spinach & Cheese Fluffy Omelet*) remain visible.
  7. Uncheck all dietary pills to restore the full grid.

---

### Test Case C: Simulated Barcode Scanner
* **Objective**: Verify that simulated barcode codes are successfully mapped to preset products, decoded with correct expiration dates, and added to the pantry.
* **Steps**:
  1. Navigate to the **Scan Groceries** tab.
  2. Toggle the scanner mode to **Barcode Reader** (right side button).
  3. Note the retro grid overlay, custom red laser animation line, and input field.
  4. In the simulated code input, enter `501004` (representing a Cheddar Cheese Block).
  5. Click **Simulate Scan**.
  6. Verify that:
     * The item `Cheddar Cheese` is successfully added to the review queue list below the viewport.
     * The category is correctly identified as `Dairy`.
     * The quantity is set to `200g`.
     * The expiration date is automatically calculated to be exactly **14 days in the future**.
  6. Click **Add Items to Pantry**.
  7. Navigate back to the **Pantry** tab and confirm `Cheddar Cheese` is now listed under the Dairy category with the correct quantity and a `Fresh` badge.

---

### Test Case D: Recipe Link Importing & Staged Verification Feedback Loop
* **Objective**: Ensure that scraping an external recipe URL loads a "Verify & Normalize" staged screen inside the modal displaying raw text helpers, and final confirmation adds the custom recipe to SQLite database.
* **Steps**:
  1. Navigate to the **Cookbook** tab.
  2. Click the **Import from Link** button in the header.
  3. Paste a recipe URL (e.g., `https://www.allrecipes.com/recipe/20144/challah/`).
  4. Click **Import Recipe**.
  5. Verify that:
     * The modal does *not* close, but transitions into the **Verify & Normalize Recipe** grid view.
     * The scraped recipe name, prep time, cook time, and instructions steps are populated.
     * Staged ingredients are listed with inputs for Name, Qty, Unit, and Category.
     * Underneath each ingredient row, a helper message shows the original text (e.g. `Original: "2 tablespoons active dry yeast"`).
  6. Modify any ingredients (e.g. adjust quantities or units) and click **Save to Cookbook**.
  7. Confirm a toast notification shows success, the recipe details close, and the new recipe is visible in the recipe grid.
  8. Click the new card and check that the recipe details match your edited values.
  9. Click **Delete Recipe** in the footer of the details modal, confirm the dialog warning, and verify the recipe is removed from the grid.

---

### Test Case E: Multi-Batch Pantry Grouping & Expiration Dashboard Warnings
* **Objective**: Verify that adding multiple batches of the same item preserves individual dates, collapses them under a single master card, and triggers the dashboard alert banner.
* **Steps**:
  1. Navigate to the **Pantry** tab.
  2. Click **Add Item** to open the manual entry form. Add a mock item:
     * Name: `Basil`
     * Quantity: `1`
     * Unit: `bunch`
     * Expiration Date: Select exactly **2 days in the future** (Expiring status).
     * Click **Add to Inventory**.
  3. Open the form again and add the second batch:
     * Name: `Basil`
     * Quantity: `1`
     * Unit: `bunch`
     * Expiration Date: Select exactly **10 days in the future** (Fresh status).
     * Click **Add to Inventory**.
  4. Verify that:
     * An orange **1 Item(s) Expiring Soon!** warning banner appears at the top of the pantry.
     * The pantry grid contains a single `Basil` card showing **Total Qty: 2 bunch** with an `Expires in 2d` status badge.
  5. Click the `Basil` card header. Verify it expands to show two rows:
     * Batch 1: Expires in 2 days (orange status badge).
     * Batch 2: Fresh (green status badge).
  6. Click the `-` decrement button on the expiring batch to change its quantity to `0`.
  7. Verify that:
     * The expiring batch row disappears.
     * The master card updates to `Total Qty: 1 bunch` with a `Fresh` status badge.
     * The top alert warning banner disappears (since the expiring batch was used up/discarded).
     * The parent card remains in the list representing the second (fresh) batch.

