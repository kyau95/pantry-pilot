import { recipes } from '../utils/recipeData';

export interface PantryItem {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  category: string;
  createdAt: string;
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

class PantryStore {
  pantryItems = $state<PantryItem[]>([]);
  shoppingList = $state<ShoppingItem[]>([]);

  constructor() {
    // Only load if window is defined (browser environment)
    if (typeof window !== 'undefined') {
      this.load();
    }
  }

  load() {
    try {
      const savedPantry = localStorage.getItem('pp_pantry');
      const savedShopping = localStorage.getItem('pp_shopping');
      
      if (savedPantry) {
        this.pantryItems = JSON.parse(savedPantry);
      } else {
        // Seed default pantry items for initial load
        this.pantryItems = [
          { id: '1', name: 'Eggs', quantity: 6, unit: 'pieces', category: 'Meats & Proteins', createdAt: new Date().toISOString() },
          { id: '2', name: 'Bread', quantity: 6, unit: 'slices', category: 'Grains', createdAt: new Date().toISOString() },
          { id: '3', name: 'Butter', quantity: 4, unit: 'tbsp', category: 'Dairy', createdAt: new Date().toISOString() },
          { id: '4', name: 'Tomato', quantity: 2, unit: 'pieces', category: 'Vegetables', createdAt: new Date().toISOString() }
        ];
        this.save();
      }
      
      if (savedShopping) {
        this.shoppingList = JSON.parse(savedShopping);
      } else {
        this.shoppingList = [];
      }
    } catch (e) {
      console.error('Failed to load pantry data from localStorage', e);
    }
  }

  save() {
    try {
      localStorage.setItem('pp_pantry', JSON.stringify(this.pantryItems));
      localStorage.setItem('pp_shopping', JSON.stringify(this.shoppingList));
    } catch (e) {
      console.error('Failed to save pantry data to localStorage', e);
    }
  }

  // --- Pantry Actions ---
  addPantryItem(name: string, quantity: number, unit: string, category: string) {
    if (!name.trim()) return;
    
    const existingIndex = this.pantryItems.findIndex(
      i => i.name.toLowerCase() === name.trim().toLowerCase() && i.unit.toLowerCase() === unit.trim().toLowerCase()
    );

    if (existingIndex > -1) {
      this.pantryItems[existingIndex].quantity += quantity;
    } else {
      this.pantryItems.push({
        id: Math.random().toString(36).substring(2, 9),
        name: name.trim(),
        quantity,
        unit: unit.trim(),
        category: category.trim(),
        createdAt: new Date().toISOString()
      });
    }
    this.save();
  }

  updatePantryQuantity(id: string, newQuantity: number) {
    const item = this.pantryItems.find(i => i.id === id);
    if (item) {
      item.quantity = Math.max(0, newQuantity);
      if (item.quantity === 0) {
        this.pantryItems = this.pantryItems.filter(i => i.id !== id);
      }
      this.save();
    }
  }

  deletePantryItem(id: string) {
    this.pantryItems = this.pantryItems.filter(i => i.id !== id);
    this.save();
  }

  // --- Shopping List Actions ---
  addShoppingItem(name: string, quantity: number, unit: string, category: string, recipeName?: string) {
    if (!name.trim()) return;

    const existingIndex = this.shoppingList.findIndex(
      i => i.name.toLowerCase() === name.trim().toLowerCase() && i.unit.toLowerCase() === unit.trim().toLowerCase()
    );

    if (existingIndex > -1) {
      this.shoppingList[existingIndex].quantity += quantity;
      // If previously checked, uncheck it since we are adding more
      this.shoppingList[existingIndex].checked = false;
    } else {
      this.shoppingList.push({
        id: Math.random().toString(36).substring(2, 9),
        name: name.trim(),
        quantity,
        unit: unit.trim(),
        category: category.trim(),
        checked: false,
        recipeName
      });
    }
    this.save();
  }

  toggleShoppingItem(id: string) {
    const item = this.shoppingList.find(i => i.id === id);
    if (item) {
      item.checked = !item.checked;
      this.save();
    }
  }

  deleteShoppingItem(id: string) {
    this.shoppingList = this.shoppingList.filter(i => i.id !== id);
    this.save();
  }

  // Cook a recipe: Deduct ingredients from pantry
  cookRecipe(recipeId: string) {
    const recipe = recipes.find(r => r.id === recipeId);
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
    this.save();
  }

  // Move checked shopping items to pantry
  purchaseCheckedItems() {
    const checkedItems = this.shoppingList.filter(i => i.checked);
    checkedItems.forEach(item => {
      this.addPantryItem(item.name, item.quantity, item.unit, item.category);
    });

    // Remove checked items from shopping list
    this.shoppingList = this.shoppingList.filter(i => !i.checked);
    this.save();
  }
}

export const pantryStore = new PantryStore();
