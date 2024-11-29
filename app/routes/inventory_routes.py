from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.menu import Ingredient
from app.forms.inventory_forms import InventoryItemForm, InventoryTransactionForm
from datetime import datetime
from app.decorators import permission_required, manager_required

inventory = Blueprint('inventory', __name__)

@inventory.route('/inventory')
@inventory.route('/inventory/<int:return_menu_item_id>')
@login_required
@permission_required('view_inventory')
def inventory_list(return_menu_item_id=None):
    """Display list of inventory items"""
    inventory_items = InventoryItem.query.filter_by(user_id=current_user.id).all()
    low_stock_items = [item for item in inventory_items if item.needs_restock()]
    return render_template('inventory/list.html', 
                         inventory_items=inventory_items,
                         low_stock_items=low_stock_items,
                         return_menu_item_id=return_menu_item_id)

@inventory.route('/inventory/setup/<int:ingredient_id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_inventory')
def setup_inventory(ingredient_id):
    """Create a new inventory item"""
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    form = InventoryItemForm()
    
    if form.validate_on_submit():
        try:
            inventory_item = InventoryItem(
                user_id=current_user.id,
                ingredient_id=ingredient.id,
                minimum_stock=form.minimum_stock.data
            )
            db.session.add(inventory_item)
            db.session.commit()
            flash('Inventory tracking set up successfully!')
            return redirect(url_for('inventory.inventory_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error setting up inventory: {str(e)}')
    
    return render_template('inventory/setup.html', form=form, ingredient=ingredient)

@inventory.route('/inventory/<int:inventory_id>/transaction', methods=['GET', 'POST'])
@login_required
@permission_required('manage_inventory')
def add_transaction(inventory_id):
    """Create a new inventory transaction"""
    inventory_item = InventoryItem.query.filter_by(id=inventory_id, user_id=current_user.id).first_or_404()
    form = InventoryTransactionForm()
    
    if form.validate_on_submit():
        try:
            transaction = InventoryTransaction(
                user_id=current_user.id,
                inventory_item_id=inventory_item.id,
                transaction_type=form.transaction_type.data,
                quantity=form.quantity.data,
                unit_cost=form.unit_cost.data if form.transaction_type.data == 'restock' else None,
                notes=form.notes.data
            )
            
            # Update inventory quantity
            if form.transaction_type.data == 'restock':
                inventory_item.quantity += form.quantity.data
                inventory_item.last_restock_date = datetime.utcnow()
            else:  # usage
                if inventory_item.quantity < form.quantity.data:
                    flash('Error: Not enough stock available!')
                    return redirect(url_for('inventory.add_transaction', inventory_id=inventory_id))
                inventory_item.quantity -= form.quantity.data
            
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction recorded successfully!')
            return redirect(url_for('inventory.inventory_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording transaction: {str(e)}')
    
    return render_template('inventory/transaction.html', 
                         form=form, 
                         inventory_item=inventory_item)

@inventory.route('/inventory/cost-analysis')
@inventory.route('/inventory/cost-analysis/<int:return_menu_item_id>')
@login_required
@permission_required('view_inventory')
def cost_analysis(return_menu_item_id=None):
    """Display cost analysis of inventory items"""
    inventory_items = InventoryItem.query.filter_by(user_id=current_user.id).all()
    total_cost = sum(item.quantity * item.ingredient.cost_per_unit for item in inventory_items)
    return render_template('inventory/cost_analysis.html', 
                         inventory_items=inventory_items,
                         total_cost=total_cost,
                         return_menu_item_id=return_menu_item_id)
