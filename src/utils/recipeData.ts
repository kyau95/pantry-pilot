export interface RecipeIngredient {
  name: string;
  quantity: number;
  unit: string;
  category: string;
  originalText?: string;
}

export interface Recipe {
  id: string;
  name: string;
  description: string;
  prepTime: number;
  cookTime: number;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  category: 'Breakfast' | 'Lunch' | 'Dinner' | 'Snack';
  image: string;
  ingredients: RecipeIngredient[];
  instructions: string[];
  dietaryTags: string[];
  isCustom?: boolean;
}

export const recipes: Recipe[] = [
  {
    id: 'creamy-tomato-pasta',
    name: 'Creamy Tomato Basil Pasta',
    description: 'A comforting, rich Italian pasta tossed in a creamy tomato sauce and finished with fresh basil.',
    prepTime: 10,
    cookTime: 15,
    difficulty: 'Easy',
    category: 'Dinner',
    image: 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    ingredients: [
      { name: 'Pasta', quantity: 250, unit: 'g', category: 'Grains' },
      { name: 'Tomato', quantity: 3, unit: 'pieces', category: 'Vegetables' },
      { name: 'Garlic', quantity: 3, unit: 'cloves', category: 'Pantry Staples' },
      { name: 'Onion', quantity: 1, unit: 'piece', category: 'Vegetables' },
      { name: 'Milk', quantity: 150, unit: 'ml', category: 'Dairy' },
      { name: 'Butter', quantity: 2, unit: 'tbsp', category: 'Dairy' },
      { name: 'Olive Oil', quantity: 1, unit: 'tbsp', category: 'Pantry Staples' },
      { name: 'Basil', quantity: 5, unit: 'leaves', category: 'Vegetables' }
    ],
    instructions: [
      'Boil pasta in salted water according to package instructions until al dente.',
      'Finely dice the onion and mince the garlic.',
      'Heat olive oil and melt butter in a large pan over medium heat. Sauté onion and garlic until soft and fragrant (about 3 mins).',
      'Chop tomatoes and add them to the pan. Cook until they break down and form a sauce (about 7 mins).',
      'Stir in the milk and let it simmer gently for 2 minutes to thicken.',
      'Drain pasta and toss it directly into the sauce. Tear fresh basil leaves and fold them in just before serving.'
    ],
    dietaryTags: ['Vegetarian']
  },
  {
    id: 'avocado-toast-egg',
    name: 'Gourmet Avocado Toast with Poached Egg',
    description: 'Crispy toasted sourdough topped with creamy mashed avocado, chili flakes, and a perfectly poached egg.',
    prepTime: 5,
    cookTime: 5,
    difficulty: 'Easy',
    category: 'Breakfast',
    image: 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    ingredients: [
      { name: 'Bread', quantity: 2, unit: 'slices', category: 'Grains' },
      { name: 'Avocado', quantity: 1, unit: 'piece', category: 'Fruits' },
      { name: 'Eggs', quantity: 1, unit: 'piece', category: 'Meats & Proteins' },
      { name: 'Olive Oil', quantity: 1, unit: 'tsp', category: 'Pantry Staples' }
    ],
    instructions: [
      'Toast your slices of bread until golden brown and crispy.',
      'Cut the avocado, scoop the flesh into a bowl, and mash with a fork. Season with a pinch of salt, pepper, and a drop of olive oil.',
      'Poach or fry the egg to your liking (a runny yolk is recommended).',
      'Spread the mashed avocado evenly over the toasted bread.',
      'Top with the cooked egg and optionally sprinkle with red pepper flakes or sesame seeds.'
    ],
    dietaryTags: ['Vegetarian']
  },
  {
    id: 'garlic-butter-chicken',
    name: 'Garlic Butter Chicken Skillet',
    description: 'Tender pan-seared chicken breasts coated in a rich garlic butter sauce, cooked in a single skillet.',
    prepTime: 10,
    cookTime: 15,
    difficulty: 'Medium',
    category: 'Dinner',
    image: 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    ingredients: [
      { name: 'Chicken Breast', quantity: 400, unit: 'g', category: 'Meats & Proteins' },
      { name: 'Garlic', quantity: 4, unit: 'cloves', category: 'Pantry Staples' },
      { name: 'Butter', quantity: 3, unit: 'tbsp', category: 'Dairy' },
      { name: 'Olive Oil', quantity: 1, unit: 'tbsp', category: 'Pantry Staples' },
      { name: 'Spinach', quantity: 100, unit: 'g', category: 'Vegetables' }
    ],
    instructions: [
      'Cut chicken breast into bite-sized cubes. Season with salt, pepper, and paprika.',
      'Heat olive oil and 1 tablespoon of butter in a large skillet over medium-high heat.',
      'Add chicken cubes in a single layer and sear until golden brown and cooked through (about 6-8 minutes). Remove chicken from the pan.',
      'Reduce heat to medium. Add remaining butter and minced garlic to the skillet. Cook for 1 minute until fragrant.',
      'Add baby spinach and cook until wilted (about 2 minutes).',
      'Return chicken to the skillet, toss in the garlic butter sauce, and serve hot.'
    ],
    dietaryTags: ['Gluten-Free']
  },
  {
    id: 'caprese-salad',
    name: 'Classic Caprese Salad',
    description: 'A simple and elegant Italian salad featuring fresh mozzarella, vine-ripened tomatoes, and sweet basil leaves.',
    prepTime: 5,
    cookTime: 0,
    difficulty: 'Easy',
    category: 'Lunch',
    image: 'https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600&auto=format&fit=crop&q=60',
    ingredients: [
      { name: 'Tomato', quantity: 2, unit: 'pieces', category: 'Vegetables' },
      { name: 'Mozzarella', quantity: 150, unit: 'g', category: 'Dairy' },
      { name: 'Basil', quantity: 10, unit: 'leaves', category: 'Vegetables' },
      { name: 'Olive Oil', quantity: 2, unit: 'tbsp', category: 'Pantry Staples' }
    ],
    instructions: [
      'Slice the fresh tomatoes and mozzarella cheese into 1/4-inch-thick rounds.',
      'Alternate layering tomato slices and mozzarella slices on a serving platter.',
      'Tuck whole fresh basil leaves between the tomato and cheese slices.',
      'Drizzle generously with extra virgin olive oil and season with sea salt and cracked black pepper.'
    ],
    dietaryTags: ['Vegetarian', 'Gluten-Free']
  },
  {
    id: 'spinach-cheese-omelet',
    name: 'Spinach & Cheese Fluffy Omelet',
    description: 'A light and fluffy 2-egg omelet loaded with fresh baby spinach and melted cheddar cheese.',
    prepTime: 5,
    cookTime: 5,
    difficulty: 'Easy',
    category: 'Breakfast',
    image: 'https://images.unsplash.com/photo-1494597564530-871f2b93ac55?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    ingredients: [
      { name: 'Eggs', quantity: 2, unit: 'pieces', category: 'Meats & Proteins' },
      { name: 'Spinach', quantity: 50, unit: 'g', category: 'Vegetables' },
      { name: 'Cheese', quantity: 50, unit: 'g', category: 'Dairy' },
      { name: 'Butter', quantity: 1, unit: 'tbsp', category: 'Dairy' }
    ],
    instructions: [
      'Crack eggs into a bowl, add a splash of water/milk, and whisk vigorously with a fork until frothy.',
      'Melt butter in a non-stick skillet over medium-low heat.',
      'Pour in the eggs. Let them cook slightly, then use a spatula to push the cooked edges toward the center.',
      'Once the eggs are mostly set but still slightly wet on top, scatter the baby spinach and shredded cheese over one half.',
      'Fold the omelet in half, cook for 1 more minute until cheese melts, and slide onto a plate.'
    ],
    dietaryTags: ['Vegetarian', 'Gluten-Free']
  },
  {
    id: 'french-toast',
    name: 'Classic Golden French Toast',
    description: 'Thick bread slices soaked in a rich custard of eggs and milk, pan-fried to golden-brown perfection.',
    prepTime: 5,
    cookTime: 10,
    difficulty: 'Easy',
    category: 'Breakfast',
    image: 'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    ingredients: [
      { name: 'Bread', quantity: 4, unit: 'slices', category: 'Grains' },
      { name: 'Eggs', quantity: 2, unit: 'pieces', category: 'Meats & Proteins' },
      { name: 'Milk', quantity: 100, unit: 'ml', category: 'Dairy' },
      { name: 'Butter', quantity: 2, unit: 'tbsp', category: 'Dairy' }
    ],
    instructions: [
      'In a wide, shallow bowl, whisk together the eggs and milk until fully combined.',
      'Melt 1 tablespoon of butter in a skillet over medium heat.',
      'Dip a slice of bread into the egg mixture for 10 seconds per side, allowing it to soak up the liquid.',
      'Place in the hot skillet and cook for 2-3 minutes per side until golden brown.',
      'Repeat with remaining slices, adding more butter as needed. Serve with honey, syrup, or fruit.'
    ],
    dietaryTags: ['Vegetarian']
  },
  {
    id: 'chicken-spinach-stir-fry',
    name: 'Garlic Chicken & Spinach Stir-Fry',
    description: 'A quick, healthy stir-fry combining tender chicken, sweet onions, and fresh wilted spinach.',
    prepTime: 10,
    cookTime: 10,
    difficulty: 'Easy',
    category: 'Lunch',
    image: 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    ingredients: [
      { name: 'Chicken Breast', quantity: 300, unit: 'g', category: 'Meats & Proteins' },
      { name: 'Spinach', quantity: 150, unit: 'g', category: 'Vegetables' },
      { name: 'Onion', quantity: 1, unit: 'piece', category: 'Vegetables' },
      { name: 'Garlic', quantity: 2, unit: 'cloves', category: 'Pantry Staples' },
      { name: 'Olive Oil', quantity: 1, unit: 'tbsp', category: 'Pantry Staples' }
    ],
    instructions: [
      'Slice the chicken breast into thin strips. Thinly slice the onion and mince the garlic.',
      'Heat olive oil in a wok or large skillet over high heat.',
      'Add chicken strips and stir-fry until cooked through and slightly browned (about 5 mins). Remove from wok.',
      'Add onion and garlic to the wok, stir-frying for 2 minutes until tender.',
      'Add spinach and return chicken to the wok. Toss continuously until the spinach is wilted and chicken is heated through (about 2 mins).'
    ],
    dietaryTags: ['Gluten-Free', 'Dairy-Free']
  },
  {
    id: 'simple-grilled-cheese',
    name: 'Ultimate Crispy Grilled Cheese',
    description: 'Crispy, butter-toasted bread oozing with thick layers of warm, melted cheese.',
    prepTime: 2,
    cookTime: 6,
    difficulty: 'Easy',
    category: 'Snack',
    image: 'https://images.unsplash.com/photo-1476887334197-56adbf254e1a?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    ingredients: [
      { name: 'Bread', quantity: 2, unit: 'slices', category: 'Grains' },
      { name: 'Cheese', quantity: 80, unit: 'g', category: 'Dairy' },
      { name: 'Butter', quantity: 1, unit: 'tbsp', category: 'Dairy' }
    ],
    instructions: [
      'Spread butter evenly on one side of each slice of bread.',
      'Place one slice of bread, buttered-side down, in a cold skillet.',
      'Lay the cheese slices evenly on top of the bread, then top with the second slice of bread, buttered-side up.',
      'Turn the heat to medium-low. Cook for 3-4 minutes until the bottom is golden brown and cheese begins to melt.',
      'Flip carefully and cook the other side for another 3 minutes until crispy and golden and cheese is completely melted.'
    ],
    dietaryTags: ['Vegetarian']
  }
];
