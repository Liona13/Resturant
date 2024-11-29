from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models.menu import MenuItem, Ingredient
from app.models.audit_log import AuditLog
from app.forms.menu_forms import MenuItemForm, IngredientForm
from app.services.price_calculator import PriceCalculator
from app.decorators import permission_required, manager_required

menu = Blueprint('menu', __name__)

@menu.route('/menu')
@login_required
def menu_list():
    """Display list of menu items"""
    menu_items = MenuItem.query.filter_by(user_id=current_user.id).order_by(MenuItem.category).all()
    return render_template('menu/list.html', title='Menu Items', menu_items=menu_items)

@menu.route('/menu/add', methods=['GET', 'POST'])
@login_required
@permission_required('manage_menu')
def add_menu_item():
    """Create a new menu item"""
    form = MenuItemForm()
    if form.validate_on_submit():
        menu_item = MenuItem(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            cost=form.cost.data,
            category=form.category.data
        )
        menu_item.profit_margin = menu_item.calculate_profit_margin()
        
        db.session.add(menu_item)
        try:
            db.session.commit()
            # Log menu item creation
            AuditLog.log_action(
                user=current_user,
                action='create_menu_item',
                details={
                    'name': menu_item.name,
                    'category': menu_item.category,
                    'price': str(menu_item.price),
                    'cost': str(menu_item.cost)
                },
                ip_address=request.remote_addr,
                target_type='menu_item',
                target_id=menu_item.id
            )
            flash('Menu item added successfully!', 'success')
            return redirect(url_for('menu.menu_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding menu item: {str(e)}', 'error')
    
    return render_template('menu/add_edit.html', title='Add Menu Item', form=form)

@menu.route('/menu/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_menu')
def edit_menu_item(id):
    """Edit an existing menu item"""
    menu_item = MenuItem.query.get_or_404(id)
    
    # Check if user has permission to edit this menu item
    if menu_item.user_id != current_user.id:
        flash('You do not have permission to edit this menu item.', 'danger')
        return redirect(url_for('menu.menu_list'))
    
    form = MenuItemForm(obj=menu_item)
    if form.validate_on_submit():
        menu_item.name = form.name.data
        menu_item.description = form.description.data
        menu_item.price = form.price.data
        menu_item.cost = form.cost.data
        menu_item.category = form.category.data
        menu_item.profit_margin = menu_item.calculate_profit_margin()  # Recalculate profit margin
        
        try:
            db.session.commit()
            # Log menu item update
            AuditLog.log_action(
                user=current_user,
                action='update_menu_item',
                details={
                    'name': menu_item.name,
                    'category': menu_item.category,
                    'price': str(menu_item.price),
                    'cost': str(menu_item.cost)
                },
                ip_address=request.remote_addr,
                target_type='menu_item',
                target_id=menu_item.id
            )
            flash('Menu item has been updated.', 'success')
            return redirect(url_for('menu.menu_list'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the menu item.', 'danger')
            return redirect(url_for('menu.menu_list'))
    
    return render_template('menu/edit.html', title='Edit Menu Item', form=form, menu_item=menu_item)

@menu.route('/menu/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('manage_menu')
def delete_menu_item(id):
    """Delete a menu item"""
    menu_item = MenuItem.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    try:
        # Store item details before deletion for audit log
        item_details = {
            'name': menu_item.name,
            'category': menu_item.category,
            'price': str(menu_item.price)
        }
        
        db.session.delete(menu_item)
        db.session.commit()
        
        # Log menu item deletion
        AuditLog.log_action(
            user=current_user,
            action='delete_menu_item',
            details=item_details,
            ip_address=request.remote_addr,
            target_type='menu_item',
            target_id=id
        )
        flash('Menu item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting menu item: {str(e)}', 'error')
    
    return redirect(url_for('menu.menu_list'))

# Ingredient routes
@menu.route('/ingredients')
@login_required
@permission_required('manage_menu')
def ingredient_list():
    """Display list of ingredients"""
    ingredients = Ingredient.query.filter_by(user_id=current_user.id).all()
    return render_template('menu/ingredients.html', title='Ingredients', ingredients=ingredients)

@menu.route('/ingredients/add', methods=['GET', 'POST'])
@login_required
@permission_required('manage_menu')
def add_ingredient():
    """Add a new ingredient"""
    form = IngredientForm()
    if form.validate_on_submit():
        ingredient = Ingredient(
            user_id=current_user.id,
            name=form.name.data,
            unit=form.unit.data,
            cost_per_unit=form.cost_per_unit.data
        )
        db.session.add(ingredient)
        try:
            db.session.commit()
            # Log ingredient creation
            AuditLog.log_action(
                user=current_user,
                action='create_ingredient',
                details={
                    'name': ingredient.name,
                    'unit': ingredient.unit,
                    'cost_per_unit': str(ingredient.cost_per_unit)
                },
                ip_address=request.remote_addr,
                target_type='ingredient',
                target_id=ingredient.id
            )
            flash('Ingredient added successfully!', 'success')
            return redirect(url_for('menu.ingredient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding ingredient: {str(e)}', 'error')
    
    return render_template('menu/add_edit_ingredient.html', title='Add Ingredient', form=form)

@menu.route('/ingredients/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_menu')
def edit_ingredient(id):
    """Edit an existing ingredient"""
    ingredient = Ingredient.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = IngredientForm(obj=ingredient)
    
    if form.validate_on_submit():
        # Store old values for audit log
        old_values = {
            'name': ingredient.name,
            'unit': ingredient.unit,
            'cost_per_unit': str(ingredient.cost_per_unit)
        }
        
        # Update ingredient
        ingredient.name = form.name.data
        ingredient.unit = form.unit.data
        ingredient.cost_per_unit = form.cost_per_unit.data
        
        try:
            db.session.commit()
            # Log ingredient update
            AuditLog.log_action(
                user=current_user,
                action='edit_ingredient',
                details={
                    'old_values': old_values,
                    'new_values': {
                        'name': ingredient.name,
                        'unit': ingredient.unit,
                        'cost_per_unit': str(ingredient.cost_per_unit)
                    }
                },
                ip_address=request.remote_addr,
                target_type='ingredient',
                target_id=ingredient.id
            )
            flash('Ingredient updated successfully!', 'success')
            return redirect(url_for('menu.ingredient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating ingredient: {str(e)}', 'error')
    
    return render_template('menu/add_edit_ingredient.html', title='Edit Ingredient', form=form)

@menu.route('/ingredients/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('manage_menu')
def delete_ingredient(id):
    """Delete an ingredient"""
    ingredient = Ingredient.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    try:
        # Store item details before deletion for audit log
        item_details = {
            'name': ingredient.name,
            'unit': ingredient.unit,
            'cost_per_unit': str(ingredient.cost_per_unit)
        }
        
        db.session.delete(ingredient)
        db.session.commit()
        
        # Log ingredient deletion
        AuditLog.log_action(
            user=current_user,
            action='delete_ingredient',
            details=item_details,
            ip_address=request.remote_addr,
            target_type='ingredient',
            target_id=id
        )
        flash('Ingredient deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting ingredient: {str(e)}', 'error')
    
    return redirect(url_for('menu.ingredient_list'))
