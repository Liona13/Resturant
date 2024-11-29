from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem, OrderStatus, DailySales, PaymentMethod
from app.models.menu import MenuItem
from app.forms.order_forms import OrderForm, OrderItemForm
from datetime import datetime, date
import random
import string

orders = Blueprint('orders', __name__)

def generate_order_number():
    """Generate a unique order number"""
    prefix = ''.join(random.choices(string.ascii_uppercase, k=2))
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{suffix}"

@orders.route('/orders')
@login_required
def order_list():
    """Display list of orders"""
    print("Fetching orders...")  # Debug log
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    print(f"Found {len(orders)} orders")  # Debug log
    return render_template('orders/list.html', orders=orders)

@orders.route('/orders/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """Create a new order"""
    form = OrderForm()
    print(f"Form submitted: {request.method == 'POST'}")  # Debug log
    print(f"Form validation: {form.validate_on_submit() if request.method == 'POST' else 'Not submitted'}")  # Debug log
    
    if form.validate_on_submit():
        try:
            order = Order(
                user_id=current_user.id,
                order_number=generate_order_number(),
                table_number=form.table_number.data,
                server_name=form.server_name.data,
                status=OrderStatus.PENDING,  # Always start as pending
                notes=form.notes.data,
                created_at=datetime.utcnow()
            )
            print(f"Creating order: {order.order_number}")  # Debug log
            db.session.add(order)
            db.session.commit()
            print(f"Order created with ID: {order.id}")  # Debug log
            flash('New order created successfully!')
            return redirect(url_for('orders.edit_order', order_id=order.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error creating order: {str(e)}")  # Debug log
            flash(f'Error creating order: {str(e)}')
    elif request.method == 'POST':
        print("Form validation errors:", form.errors)  # Debug log
        
    return render_template('orders/new.html', form=form)

@orders.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Edit an existing order"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    form = OrderForm(obj=order)
    item_form = OrderItemForm()
    
    # Update item_form choices to only show current user's menu items
    menu_items = MenuItem.query.filter_by(user_id=current_user.id).all()
    item_form.menu_item_id.choices = [(item.id, f"{item.name} - ${item.price:.2f}") 
                                    for item in menu_items]
    
    if form.validate_on_submit():
        try:
            order.table_number = form.table_number.data
            order.server_name = form.server_name.data
            order.status = OrderStatus(form.status.data)
            order.notes = form.notes.data
            
            # Update payment details
            if form.payment_method.data:
                order.payment_method = PaymentMethod(form.payment_method.data)
            order.tax_amount = form.tax_amount.data
            order.tip_amount = form.tip_amount.data
            
            # Recalculate total
            order.calculate_total()
            
            if form.status.data == OrderStatus.COMPLETED.value and not order.completed_at:
                order.completed_at = datetime.utcnow()
                order.update_inventory()
                
                # Update daily sales
                daily_sales = DailySales.query.filter_by(
                    user_id=current_user.id,
                    date=date.today()
                ).first()
                
                if not daily_sales:
                    daily_sales = DailySales(
                        user_id=current_user.id,
                        date=date.today()
                    )
                    db.session.add(daily_sales)
                
                # Only get completed orders for current user
                completed_orders = Order.query.filter(
                    Order.user_id == current_user.id,
                    Order.status == OrderStatus.COMPLETED,
                    db.func.date(Order.completed_at) == date.today()
                ).all()
                
                daily_sales.update_from_orders(completed_orders)
            
            db.session.commit()
            flash('Order updated successfully!')
            return redirect(url_for('orders.order_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating order: {str(e)}')
            print(f"Error updating order: {str(e)}")  # Debug log
    
    return render_template('orders/edit.html', 
                         form=form, 
                         item_form=item_form, 
                         order=order)

@orders.route('/orders/<int:order_id>/add_item', methods=['POST'])
@login_required
def add_order_item(order_id):
    """Add an item to an order"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    form = OrderItemForm()
    
    # Update form choices to only show current user's menu items
    menu_items = MenuItem.query.filter_by(user_id=current_user.id).all()
    form.menu_item_id.choices = [(item.id, f"{item.name} - ${item.price:.2f}") 
                                for item in menu_items]
    
    if form.validate_on_submit():
        try:
            menu_item = MenuItem.query.filter_by(
                id=form.menu_item_id.data,
                user_id=current_user.id
            ).first_or_404()
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=form.quantity.data,
                unit_price=menu_item.price,
                special_instructions=form.special_instructions.data
            )
            
            db.session.add(order_item)
            order.calculate_total()
            db.session.commit()
            
            flash('Item added to order successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item to order: {str(e)}')
    
    return redirect(url_for('orders.edit_order', order_id=order.id))

@orders.route('/orders/<int:order_id>/remove_item/<int:item_id>', methods=['POST'])
@login_required
def remove_order_item(order_id, item_id):
    """Remove an item from an order"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    order_item = OrderItem.query.filter_by(id=item_id, order_id=order.id).first_or_404()
    
    try:
        db.session.delete(order_item)
        order.calculate_total()
        db.session.commit()
        flash('Item removed from order successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing item from order: {str(e)}')
    
    return redirect(url_for('orders.edit_order', order_id=order.id))

@orders.route('/orders/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    """Mark an order as completed"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    order.status = OrderStatus.COMPLETED
    order.completed_at = datetime.utcnow()
    order.update_inventory()
    db.session.commit()
    
    # Update daily sales
    daily_sales = DailySales.query.filter_by(
        user_id=current_user.id,
        date=date.today()
    ).first()
    
    if not daily_sales:
        daily_sales = DailySales(
            user_id=current_user.id,
            date=date.today()
        )
        db.session.add(daily_sales)
    
    # Only get completed orders for current user
    completed_orders = Order.query.filter(
        Order.user_id == current_user.id,
        Order.status == OrderStatus.COMPLETED,
        db.func.date(Order.completed_at) == date.today()
    ).all()
    
    daily_sales.update_from_orders(completed_orders)
    db.session.commit()
    
    flash('Order completed successfully!')
    return redirect(url_for('orders.order_list'))

@orders.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel an order"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    order.status = OrderStatus.CANCELLED
    db.session.commit()
    flash('Order cancelled successfully!')
    return redirect(url_for('orders.order_list'))
