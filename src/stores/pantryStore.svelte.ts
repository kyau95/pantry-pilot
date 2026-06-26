import { recipes as defaultRecipes, type Recipe } from '../utils/recipeData';

export interface PantryItem {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  category: string;
  createdAt: string;
  useByDate: string;
}

export interface ShoppingItem {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  category: string;
  checked: boolean;
  recipeName?: string;
}

const API_URL = 'http://localhost:8000/api';

class PantryStore {
  pantryItems = $state<PantryItem[]>([]);
  shoppingList = $state<ShoppingItem[]>([]);
  recipes = $state<Recipe[]>([]);
  isSynced = $state(false);

  constructor() {
    // Only load if window is defined (browser environment)
    if (typeof window !== 'undefined') {
      this.load();
    }
  }

  async load() {
    // 1. Load optimistic local state from localStorage first (offline-first)
    try {
      const savedPantry = localStorage.getItem('pp_pantry');
      const savedShopping = localStorage.getItem('pp_shopping');
      const savedRecipes = localStorage.getItem('pp_recipes');
      
      if (savedPantry) {
        const items = JSON.parse(savedPantry);
        this.pantryItems = items.map((item: any) => {
          if (!item.useByDate) {
            const date = new Date(item.createdAt || new Date());
            date.setDate(date.getDate() + 7);
            return { ...item, useByDate: date.toISOString() };
          }
          return item;
        });
      } else {
        // Seed default pantry items for initial load if nothing is saved
        const now = new Date();
        const getFutureDate = (days: number) => {
          const d = new Date(now);
          d.setDate(d.getDate() + days);
          return d.toISOString();
        };
        this.pantryItems = [
          { id: '1', name: 'Eggs', quantity: 6, unit: 'pieces', category: 'Meats & Proteins', createdAt: now.toISOString(), useByDate: getFutureDate(5) },
          { id: '2', name: 'Bread', quantity: 6, unit: 'slices', category: 'Grains', createdAt: now.toISOString(), useByDate: getFutureDate(3) },
          { id: '3', name: 'Butter', quantity: 4, unit: 'tbsp', category: 'Dairy', createdAt: now.toISOString(), useByDate: getFutureDate(14) },
          { id: '4', name: 'Tomato', quantity: 2, unit: 'pieces', category: 'Vegetables', createdAt: now.toISOString(), useByDate: getFutureDate(2) }
        ];
        this.saveLocal();
      }
      
      if (savedShopping) {
        this.shoppingList = JSON.parse(savedShopping);
      } else {
        this.shoppingList = [];
      }

      if (savedRecipes) {
        this.recipes = JSON.parse(savedRecipes);
      } else {
        this.recipes = defaultRecipes;
      }
    } catch (e) {
      console.error('Failed to load pantry data from localStorage', e);
    }

    // 2. Asynchronously sync with SQLite database backend
    try {
      console.log('[SQLite Store] Probing backend for SQLite database synchronization...');
      
      const pantryRes = await fetch(`${API_URL}/pantry`);
      if (!pantryRes.ok) throw new Error('Failed to fetch pantry from backend');
      const dbPantry = await pantryRes.json();
      
      const shoppingRes = await fetch(`${API_URL}/shopping`);
      if (!shoppingRes.ok) throw new Error('Failed to fetch shopping list from backend');
      const dbShopping = await shoppingRes.json();

      const recipesRes = await fetch(`${API_URL}/recipes`);
      if (!recipesRes.ok) throw new Error('Failed to fetch recipes from backend');
      const dbRecipes = await recipesRes.json();
      
      // Update state with backend data
      this.pantryItems = dbPantry;
      this.shoppingList = dbShopping;
      this.recipes = dbRecipes;
      this.isSynced = true;
      this.saveLocal();
      console.log('[SQLite Store] Sync completed successfully. Loaded data from SQLite.');
    } catch (err) {
      console.warn('[SQLite Store Sync Offline] FastAPI SQLite backend offline or unreachable. Using localStorage.', err);
      this.isSynced = false;
    }
  }

  saveLocal() {
    try {
      localStorage.setItem('pp_pantry', JSON.stringify(this.pantryItems));
      localStorage.setItem('pp_shopping', JSON.stringify(this.shoppingList));
      localStorage.setItem('pp_recipes', JSON.stringify(this.recipes));
    } catch (e) {
      console.error('Failed to save pantry data to localStorage', e);
    }
  }

  // Helper to dispatch async background API requests
  private async apiCall(path: string, method: string, body?: any) {
    try {
      const options: RequestInit = {
        method,
        headers: body ? { 'Content-Type': 'application/json' } : undefined,
        body: body ? JSON.stringify(body) : undefined
      };
      const res = await fetch(`${API_URL}${path}`, options);
      if (!res.ok) {
        console.warn(`[SQLite Store Sync] API call to ${path} failed: ${res.statusText}`);
      }
    } catch (err) {
      console.warn(`[SQLite Store Sync Offline] Failed to sync ${method} ${path} to backend SQLite. App remains functional locally.`, err);
    }
  }

  // --- Pantry Actions ---
  addPantryItem(name: string, quantity: number, unit: string, category: string, useByDate?: string) {
    if (!name.trim()) return;
    
    const existingIndex = this.pantryItems.findIndex(
      i => i.name.toLowerCase() === name.trim().toLowerCase() && i.unit.toLowerCase() === unit.trim().toLowerCase()
    );

    // Default expiration date: 7 days from now
    let expiry = useByDate;
    if (!expiry) {
      const d = new Date();
      d.setDate(d.getDate() + 7);
      expiry = d.toISOString();
    }

    let itemId = Math.random().toString(36).substring(2, 9);

    if (existingIndex > -1) {
      this.pantryItems[existingIndex].quantity += quantity;
      // Keep the earlier expiration date
      if (new Date(expiry) < new Date(this.pantryItems[existingIndex].useByDate)) {
        this.pantryItems[existingIndex].useByDate = expiry;
      }
      itemId = this.pantryItems[existingIndex].id;
      expiry = this.pantryItems[existingIndex].useByDate;
    } else {
      this.pantryItems.push({
        id: itemId,
        name: name.trim(),
        quantity,
        unit: unit.trim(),
        category: category.trim(),
        createdAt: new Date().toISOString(),
        useByDate: expiry
      });
    }
    
    this.saveLocal();
    
    // Sync to SQLite in the background
    this.apiCall('/pantry', 'POST', {
      id: itemId,
      name: name.trim(),
      quantity,
      unit: unit.trim(),
      category: category.trim(),
      useByDate: expiry
    });
  }

  updatePantryQuantity(id: string, newQuantity: number) {
    const item = this.pantryItems.find(i => i.id === id);
    if (item) {
      const qty = Math.max(0, newQuantity);
      item.quantity = qty;
      if (qty === 0) {
        this.pantryItems = this.pantryItems.filter(i => i.id !== id);
        this.saveLocal();
        this.apiCall(`/pantry/${id}`, 'DELETE');
      } else {
        this.saveLocal();
        this.apiCall(`/pantry/${id}`, 'PUT', { quantity: qty });
      }
    }
  }

  deletePantryItem(id: string) {
    this.pantryItems = this.pantryItems.filter(i => i.id !== id);
    this.saveLocal();
    
    // Sync to SQLite in the background
    this.apiCall(`/pantry/${id}`, 'DELETE');
  }

  // Cook a recipe: Deduct ingredients from pantry
  cookRecipe(recipeId: string) {
    const recipe = this.recipes.find(r => r.id === recipeId);
    if (!recipe) return;

    recipe.ingredients.forEach(reqIng => {
      // Find matching items in pantry (case insensitive)
      const matchingItems = this.pantryItems.filter(
        p => p.name.toLowerCase() === reqIng.name.toLowerCase()
      );

      let needed = reqIng.quantity;
      for (const pItem of matchingItems) {
        if (needed <= 0) break;
        if (pItem.quantity >= needed) {
          pItem.quantity -= needed;
          needed = 0;
        } else {
          needed -= pItem.quantity;
          pItem.quantity = 0;
        }
      }
    });

    // Remove any items that reached 0 quantity
    this.pantryItems = this.pantryItems.filter(p => p.quantity > 0);
    this.saveLocal();

    // Sync to SQLite in the background
    this.apiCall('/pantry/cook', 'POST', {
      ingredients: recipe.ingredients
    });
  }

  // --- Shopping List Actions ---
  addShoppingItem(name: string, quantity: number, unit: string, category: string, recipeName?: string) {
    if (!name.trim()) return;

    const existingIndex = this.shoppingList.findIndex(
      i => i.name.toLowerCase() === name.trim().toLowerCase() && i.unit.toLowerCase() === unit.trim().toLowerCase()
    );

    let itemId = Math.random().toString(36).substring(2, 9);

    if (existingIndex > -1) {
      this.shoppingList[existingIndex].quantity += quantity;
      this.shoppingList[existingIndex].checked = false;
      itemId = this.shoppingList[existingIndex].id;
    } else {
      this.shoppingList.push({
        id: itemId,
        name: name.trim(),
        quantity,
        unit: unit.trim(),
        category: category.trim(),
        checked: false,
        recipeName
      });
    }
    
    this.saveLocal();

    // Sync to SQLite in the background
    this.apiCall('/shopping', 'POST', {
      id: itemId,
      name: name.trim(),
      quantity,
      unit: unit.trim(),
      category: category.trim(),
      recipeName
    });
  }

  toggleShoppingItem(id: string) {
    const item = this.shoppingList.find(i => i.id === id);
    if (item) {
      item.checked = !item.checked;
      this.saveLocal();

      // Sync to SQLite in the background
      this.apiCall(`/shopping/${id}/toggle`, 'PUT');
    }
  }

  updateShoppingQuantity(id: string, newQuantity: number) {
    const item = this.shoppingList.find(i => i.id === id);
    if (item) {
      const qty = Math.max(0, newQuantity);
      item.quantity = qty;
      if (qty === 0) {
        this.shoppingList = this.shoppingList.filter(i => i.id !== id);
        this.saveLocal();
        this.apiCall(`/shopping/${id}`, 'DELETE');
      } else {
        this.saveLocal();
        this.apiCall(`/shopping/${id}`, 'PUT', { quantity: qty });
      }
    }
  }

  deleteShoppingItem(id: string) {
    this.shoppingList = this.shoppingList.filter(i => i.id !== id);
    this.saveLocal();

    // Sync to SQLite in the background
    this.apiCall(`/shopping/${id}`, 'DELETE');
  }

  // Move checked shopping items to pantry
  purchaseCheckedItems() {
    const checkedItems = this.shoppingList.filter(i => i.checked);
    
    // Perform local changes
    checkedItems.forEach(item => {
      this.addPantryItem(item.name, item.quantity, item.unit, item.category);
    });
    this.shoppingList = this.shoppingList.filter(i => !i.checked);
    this.saveLocal();

    // Sync to SQLite in the background (moves items from shopping to pantry on DB)
    this.apiCall('/shopping/purchase', 'POST');
  }

  // --- Custom Recipe Actions ---
  addCustomRecipe(recipe: Recipe) {
    this.recipes.push(recipe);
    this.saveLocal();

    // Sync to SQLite in the background
    this.apiCall('/recipes', 'POST', {
      id: recipe.id,
      name: recipe.name,
      description: recipe.description,
      prepTime: recipe.prepTime,
      cookTime: recipe.cookTime,
      difficulty: recipe.difficulty,
      category: recipe.category,
      image: recipe.image,
      ingredients: recipe.ingredients,
      instructions: recipe.instructions,
      dietaryTags: recipe.dietaryTags
    });
  }

  deleteCustomRecipe(id: string) {
    this.recipes = this.recipes.filter(r => r.id !== id);
    this.saveLocal();

    // Sync to SQLite in the background
    this.apiCall(`/recipes/${id}`, 'DELETE');
  }
}

export const pantryStore = new PantryStore();
