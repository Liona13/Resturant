from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.menu import MenuItem, Ingredient
from app.models.recipe import Recipe
from app.forms.recipe_forms import RecipeItemForm
from app.forms.inventory_forms import RecipeScalingForm
from dataclasses import dataclass

recipe = Blueprint('recipe', __name__)

@dataclass
class ScaledRecipeItem:
    ingredient: Ingredient
    original_quantity: float
    scaled_quantity: float
    unit: str

@recipe.route('/menu/<int:menu_item_id>/recipe', methods=['GET'])
@login_required
def view_recipe(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    scaling_form = RecipeScalingForm()
    return render_template('recipe/view.html', 
                         menu_item=menu_item,
                         scaling_form=scaling_form)

@recipe.route('/menu/<int:menu_item_id>/recipe/scale', methods=['POST'])
@login_required
def scale_recipe(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    scaling_form = RecipeScalingForm()
    
    if scaling_form.validate_on_submit():
        servings = scaling_form.servings.data
        scaled_recipe = []
        
        for recipe_item in menu_item.recipe_items:
            scaled_quantity = recipe_item.quantity * servings
            scaled_recipe.append(ScaledRecipeItem(
                ingredient=recipe_item.ingredient,
                original_quantity=recipe_item.quantity,
                scaled_quantity=scaled_quantity,
                unit=recipe_item.unit
            ))
        
        return render_template('recipe/view.html', 
                             menu_item=menu_item,
                             scaling_form=scaling_form,
                             scaled_recipe=scaled_recipe,
                             scaled_servings=servings)
    
    flash('Invalid form data. Please try again.', 'error')
    return redirect(url_for('recipe.view_recipe', menu_item_id=menu_item.id))

@recipe.route('/menu/<int:menu_item_id>/recipe/add', methods=['GET', 'POST'])
@login_required
def add_recipe_item(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    form = RecipeItemForm()
    
    # Populate ingredient choices
    ingredients = Ingredient.query.all()
    form.ingredient_id.choices = [(i.id, f"{i.name} (${i.cost_per_unit:.2f}/{i.unit})") for i in ingredients]
    
    if form.validate_on_submit():
        recipe_item = Recipe(
            menu_item_id=menu_item.id,
            ingredient_id=form.ingredient_id.data,
            quantity=form.quantity.data,
            unit=form.unit.data
        )
        db.session.add(recipe_item)
        
        # Update menu item cost
        try:
            db.session.commit()
            menu_item.update_cost_from_recipe()
            db.session.commit()
            flash('Recipe item added successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding recipe item: {str(e)}')
        
        return redirect(url_for('recipe.view_recipe', menu_item_id=menu_item.id))
    
    return render_template('recipe/add_edit.html', form=form, menu_item=menu_item)

@recipe.route('/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe_item(recipe_id):
    recipe_item = Recipe.query.get_or_404(recipe_id)
    menu_item = recipe_item.menu_item
    
    try:
        db.session.delete(recipe_item)
        db.session.commit()
        
        # Update menu item cost
        menu_item.update_cost_from_recipe()
        db.session.commit()
        flash('Recipe item deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting recipe item: {str(e)}')
    
    return redirect(url_for('recipe.view_recipe', menu_item_id=menu_item.id))
