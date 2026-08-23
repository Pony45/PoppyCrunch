# app.py
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_session import Session
import os
import json
import uuid
from datetime import datetime
from products import get_all_products, get_product, calculate_subtotal, calculate_delivery_fee, calculate_total

app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = 'pop_y_crunch_secret_key_2026'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './flask_session'

Session(app)

# Route: Home
@app.route('/')
def index():
    products = get_all_products()
    cart_count = get_cart_count()
    return render_template('index.html', 
                         products=products, 
                         cart_count=cart_count,
                         title='Pop\'y Crunch - Home')

# Route: Shop
@app.route('/shop')
def shop():
    products = get_all_products()
    cart_count = get_cart_count()
    return render_template('shop.html', 
                         products=products, 
                         cart_count=cart_count,
                         title='Shop Pop\'y Crunch')

# Route: Cart
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    subtotal = calculate_subtotal(cart_items)
    delivery = calculate_delivery_fee(subtotal)
    total = subtotal + delivery
    cart_count = get_cart_count()
    
    # Enrich cart items with product details
    enriched_cart = []
    for item in cart_items:
        product = get_product(item['id'])
        if product:
            enriched_cart.append({
                **item,
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'subtotal': round(product['price'] * item['quantity'], 2)
            })
    
    return render_template('cart.html',
                         cart_items=enriched_cart,
                         subtotal=subtotal,
                         delivery=delivery,
                         total=total,
                         cart_count=cart_count,
                         title='Your Cart')

# Route: Add to Cart (AJAX)
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))
    
    if not product_id:
        return jsonify({'error': 'Product ID required'}), 400
    
    product = get_product(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get current cart from session
    cart = session.get('cart', [])
    
    # Check if product already in cart
    found = False
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'id': product_id,
            'quantity': quantity
        })
    
    session['cart'] = cart
    session.modified = True
    
    cart_count = get_cart_count()
    
    return jsonify({
        'success': True,
        'message': f'{product["name"]} added to cart!',
        'cart_count': cart_count
    })

# Route: Update Cart (AJAX)
@app.route('/update-cart', methods=['POST'])
def update_cart():
    product_id = request.json.get('product_id')
    action = request.json.get('action')  # 'increase', 'decrease', 'remove'
    
    cart = session.get('cart', [])
    
    for i, item in enumerate(cart):
        if item['id'] == product_id:
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease':
                item['quantity'] -= 1
                if item['quantity'] <= 0:
                    cart.pop(i)
            elif action == 'remove':
                cart.pop(i)
            break
    
    session['cart'] = cart
    session.modified = True
    
    # Calculate new totals
    subtotal = calculate_subtotal(cart)
    delivery = calculate_delivery_fee(subtotal)
    total = subtotal + delivery
    
    # Get updated cart items with details
    enriched_cart = []
    for item in cart:
        product = get_product(item['id'])
        if product:
            enriched_cart.append({
                **item,
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'subtotal': round(product['price'] * item['quantity'], 2)
            })
    
    return jsonify({
        'success': True,
        'cart_count': get_cart_count(),
        'subtotal': round(subtotal, 2),
        'delivery': round(delivery, 2),
        'total': round(total, 2),
        'cart_items': enriched_cart
    })

# Route: Checkout
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = session.get('cart', [])
    
    if not cart_items:
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        # Process order
        order_data = {
            'order_id': f'PC{datetime.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}',
            'customer_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'notes': request.form.get('notes'),
            'delivery_method': request.form.get('delivery_method'),
            'items': cart_items.copy(),
            'subtotal': calculate_subtotal(cart_items),
            'delivery_fee': calculate_delivery_fee(calculate_subtotal(cart_items)),
            'total': calculate_total(cart_items),
            'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store order in session for confirmation
        session['order'] = order_data
        session['cart'] = []  # Clear cart
        session.modified = True
        
        return redirect(url_for('order_confirmation'))
    
    subtotal = calculate_subtotal(cart_items)
    delivery = calculate_delivery_fee(subtotal)
    total = subtotal + delivery
    cart_count = get_cart_count()
    
    # Enrich cart items
    enriched_cart = []
    for item in cart_items:
        product = get_product(item['id'])
        if product:
            enriched_cart.append({
                **item,
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'subtotal': round(product['price'] * item['quantity'], 2)
            })
    
    return render_template('checkout.html',
                         cart_items=enriched_cart,
                         subtotal=subtotal,
                         delivery=delivery,
                         total=total,
                         cart_count=cart_count,
                         title='Checkout')

# Route: Order Confirmation
@app.route('/order-confirmation')
def order_confirmation():
    order = session.get('order')
    if not order:
        return redirect(url_for('index'))
    
    cart_count = get_cart_count()
    return render_template('order_confirmation.html',
                         order=order,
                         cart_count=cart_count,
                         title='Order Confirmed!')

# Route: About
@app.route('/about')
def about():
    cart_count = get_cart_count()
    return render_template('about.html',
                         cart_count=cart_count,
                         title='About Pop\'y Crunch')

# Route: Contact
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    cart_count = get_cart_count()
    message_sent = False
    
    if request.method == 'POST':
        # In a real application, you'd send an email or store the message
        message_sent = True
        # You could store the message in a database here
    
    return render_template('contact.html',
                         cart_count=cart_count,
                         message_sent=message_sent,
                         title='Contact Us')

# Helper function
def get_cart_count():
    cart = session.get('cart', [])
    return sum(item['quantity'] for item in cart)

# Context processor for all templates
@app.context_processor
def utility_processor():
    def get_cart_count_from_session():
        cart = session.get('cart', [])
        return sum(item['quantity'] for item in cart)
    
    return dict(get_cart_count=get_cart_count_from_session)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('flask_session', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
