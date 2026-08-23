# products.py
PRODUCTS = {
    'cheese': {
        'id': 'cheese',
        'name': 'Pop\'y Crunch – Cheese Flavour',
        'slug': 'cheese-flavour',
        'price': 12.50,
        'currency': 'RM',
        'description': 'Crispy mini popia coated with a rich and savoury cheese flavour.',
        'short_description': 'Crispy and savoury cheese goodness',
        'image': 'cheese.jpg',
        'category': 'snacks'
    },
    'salted_egg': {
        'id': 'salted_egg',
        'name': 'Pop\'y Crunch – Salted Egg Flavour',
        'slug': 'salted-egg-flavour',
        'price': 12.50,
        'currency': 'RM',
        'description': 'Crispy mini popia with a savoury salted egg flavour for a satisfying snack.',
        'short_description': 'Savoury salted egg delight',
        'image': 'salted_egg.jpg',
        'category': 'snacks'
    }
}

def get_all_products():
    """Return all products as a list"""
    return list(PRODUCTS.values())

def get_product(product_id):
    """Get a single product by ID"""
    return PRODUCTS.get(product_id)

def calculate_subtotal(cart_items):
    """Calculate subtotal for cart items"""
    total = 0
    for item in cart_items:
        product = get_product(item['id'])
        if product:
            total += product['price'] * item['quantity']
    return round(total, 2)

def calculate_delivery_fee(total):
    """Calculate delivery fee"""
    if total > 0:
        return 3.00  # Fixed delivery fee for Malaysia
    return 0.00

def calculate_total(cart_items):
    """Calculate total including delivery"""
    subtotal = calculate_subtotal(cart_items)
    delivery = calculate_delivery_fee(subtotal)
    return round(subtotal + delivery, 2)
