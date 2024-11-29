from app import create_app, db
from app.models.menu import MenuItem, Ingredient
from app.models.recipe import Recipe

app = create_app()

def add_sample_recipes():
    with app.app_context():
        # Get menu items
        chicken_biryani = MenuItem.query.filter_by(name='Chicken Biryani').first()
        pasta_alfredo = MenuItem.query.filter_by(name='Pasta Alfredo').first()
        garlic_bread = MenuItem.query.filter_by(name='Garlic Bread').first()
        tomato_soup = MenuItem.query.filter_by(name='Tomato Soup').first()

        # Get ingredients
        rice = Ingredient.query.filter_by(name='Rice').first()
        chicken = Ingredient.query.filter_by(name='Chicken').first()
        tomatoes = Ingredient.query.filter_by(name='Tomatoes').first()
        onions = Ingredient.query.filter_by(name='Onions').first()
        garlic = Ingredient.query.filter_by(name='Garlic').first()
        olive_oil = Ingredient.query.filter_by(name='Olive Oil').first()
        pasta = Ingredient.query.filter_by(name='Pasta').first()
        cheese = Ingredient.query.filter_by(name='Cheese').first()

        # Recipe for Chicken Biryani
        if chicken_biryani:
            recipes = [
                Recipe(menu_item=chicken_biryani, ingredient=rice, quantity=0.25, unit='kg'),
                Recipe(menu_item=chicken_biryani, ingredient=chicken, quantity=0.3, unit='kg'),
                Recipe(menu_item=chicken_biryani, ingredient=onions, quantity=0.1, unit='kg'),
                Recipe(menu_item=chicken_biryani, ingredient=garlic, quantity=0.02, unit='kg'),
                Recipe(menu_item=chicken_biryani, ingredient=olive_oil, quantity=0.05, unit='l')
            ]
            for recipe in recipes:
                db.session.add(recipe)

        # Recipe for Pasta Alfredo
        if pasta_alfredo:
            recipes = [
                Recipe(menu_item=pasta_alfredo, ingredient=pasta, quantity=0.2, unit='kg'),
                Recipe(menu_item=pasta_alfredo, ingredient=cheese, quantity=0.1, unit='kg'),
                Recipe(menu_item=pasta_alfredo, ingredient=garlic, quantity=0.02, unit='kg'),
                Recipe(menu_item=pasta_alfredo, ingredient=olive_oil, quantity=0.03, unit='l')
            ]
            for recipe in recipes:
                db.session.add(recipe)

        # Recipe for Garlic Bread
        if garlic_bread:
            recipes = [
                Recipe(menu_item=garlic_bread, ingredient=garlic, quantity=0.03, unit='kg'),
                Recipe(menu_item=garlic_bread, ingredient=olive_oil, quantity=0.02, unit='l'),
                Recipe(menu_item=garlic_bread, ingredient=cheese, quantity=0.05, unit='kg')
            ]
            for recipe in recipes:
                db.session.add(recipe)

        # Recipe for Tomato Soup
        if tomato_soup:
            recipes = [
                Recipe(menu_item=tomato_soup, ingredient=tomatoes, quantity=0.3, unit='kg'),
                Recipe(menu_item=tomato_soup, ingredient=onions, quantity=0.1, unit='kg'),
                Recipe(menu_item=tomato_soup, ingredient=garlic, quantity=0.02, unit='kg'),
                Recipe(menu_item=tomato_soup, ingredient=olive_oil, quantity=0.02, unit='l')
            ]
            for recipe in recipes:
                db.session.add(recipe)

        try:
            # Update menu item costs based on recipes
            for menu_item in [chicken_biryani, pasta_alfredo, garlic_bread, tomato_soup]:
                if menu_item:
                    menu_item.update_cost_from_recipe()
            
            db.session.commit()
            print("Sample recipes added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sample recipes: {str(e)}")

if __name__ == '__main__':
    add_sample_recipes()
