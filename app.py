from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_session import Session
import os, uuid
from datetime import datetime
from products import get_all_products, get_product, calculate_subtotal, calculate_delivery_fee, calculate_total

app = Flask(__name__)
app.config['SECRET_KEY'] = 'popy_secret_2026'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
Session(app)

@app.route('/')
def index():
    return render_template('index.html', products=get_all_products(), cart_count=get_cart_count())

@app.route('/shop')
def shop():
    return render_template('shop.html', products=get_all_products(), cart_count=get_cart_count())

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    if not isinstance(cart_items, list):
        cart_items = []
    
    enriched = []
    for item in cart_items:
        if isinstance(item, dict):
            p = get_product(item.get('id'))
            if p:
                enriched.append({
                    'id': item.get('id'),
                    'quantity': item.get('quantity', 1),
                    'name': p['name'], 
                    'price': p['price'], 
                    'image': p['image'],
                    'currency': p['currency'],
                    'subtotal': round(p['price'] * item.get('quantity', 1), 2)
                })
    
    subtotal = calculate_subtotal(cart_items)
    return render_template('cart.html', 
                         cart_items=enriched, 
                         subtotal=subtotal, 
                         delivery=calculate_delivery_fee(subtotal), 
                         total=calculate_total(cart_items),
                         cart_count=get_cart_count())

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))
    cart = session.get('cart', [])
    
    if not isinstance(cart, list):
        cart = []
    
    found = False
    for item in cart:
        if isinstance(item, dict) and item.get('id') == product_id:
            item['quantity'] = item.get('quantity', 0) + quantity
            found = True
            break
    
    if not found:
        cart.append({'id': product_id, 'quantity': quantity})
    
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart_count': get_cart_count()})

@app.route('/update-cart', methods=['POST'])
def update_cart():
    product_id = request.json.get('product_id')
    action = request.json.get('action')
    cart = session.get('cart', [])
    
    if not isinstance(cart, list):
        cart = []
    
    for i, item in enumerate(cart):
        if isinstance(item, dict) and item.get('id') == product_id:
            if action == 'increase':
                item['quantity'] = item.get('quantity', 0) + 1
            elif action == 'decrease':
                item['quantity'] = item.get('quantity', 0) - 1
                if item['quantity'] <= 0:
                    cart.pop(i)
            elif action == 'remove':
                cart.pop(i)
            break
    
    session['cart'] = cart
    session.modified = True
    subtotal = calculate_subtotal(cart)
    return jsonify({'success': True, 'cart_count': get_cart_count(), 
                   'subtotal': subtotal, 
                   'delivery': calculate_delivery_fee(subtotal),
                   'total': calculate_total(cart)})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        cart_items = session.get('cart', [])
        
        if not isinstance(cart_items, list):
            cart_items = []
        
        # Filter hanya yang valid
        valid_items = []
        for item in cart_items:
            if isinstance(item, dict) and item.get('id'):
                valid_items.append({
                    'id': item.get('id'),
                    'quantity': item.get('quantity', 1)
                })
        
        order = {
            'order_id': f'PC{datetime.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}',
            'customer_name': request.form.get('full_name', 'Customer'),
            'phone': request.form.get('phone', ''),
            'email': request.form.get('email', ''),
            'address': request.form.get('address', ''),
            'delivery_method': request.form.get('delivery_method', 'delivery'),
            'items': valid_items,
            'total': calculate_total(valid_items)
        }
        
        session['order'] = order
        session['cart'] = []
        session.modified = True
        return redirect(url_for('order_confirmation'))
    
    cart_items = session.get('cart', [])
    if not isinstance(cart_items, list):
        cart_items = []
    
    if not cart_items:
        return redirect(url_for('cart'))
    
    enriched = []
    for item in cart_items:
        if isinstance(item, dict):
            p = get_product(item.get('id'))
            if p:
                enriched.append({
                    'id': item.get('id'),
                    'quantity': item.get('quantity', 1),
                    'name': p['name'],
                    'price': p['price'],
                    'currency': p['currency'],
                    'subtotal': round(p['price'] * item.get('quantity', 1), 2)
                })
    
    subtotal = calculate_subtotal(cart_items)
    delivery = calculate_delivery_fee(subtotal)
    total = calculate_total(cart_items)
    
    return render_template('checkout.html', 
                         cart_items=enriched,
                         subtotal=subtotal,
                         delivery=delivery,
                         total=total,
                         cart_count=get_cart_count())

@app.route('/order-confirmation')
def order_confirmation():
    order = session.get('order')
    
    if not order:
        return redirect(url_for('index'))
    
    # Pastikan items adalah list
    items = order.get('items', [])
    if not isinstance(items, list):
        items = []
    
    # Pastikan setiap item adalah dict
    valid_items = []
    for item in items:
        if isinstance(item, dict):
            valid_items.append(item)
    
    order['items'] = valid_items
    
    return render_template('order_confirmation.html', order=order, cart_count=get_cart_count())

@app.route('/about')
def about():
    return render_template('about.html', cart_count=get_cart_count())

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message_sent = False
    if request.method == 'POST':
        message_sent = True
    return render_template('contact.html', cart_count=get_cart_count(), message_sent=message_sent)

def get_cart_count():
    cart = session.get('cart', [])
    if not isinstance(cart, list):
        return 0
    total = 0
    for item in cart:
        if isinstance(item, dict):
            total += item.get('quantity', 0)
    return total

if __name__ == '__main__':
    os.makedirs('flask_session', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    app.run(debug=True, port=5000)
