// Pop'y Crunch - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Quantity Selector Buttons
    document.querySelectorAll('.qty-plus').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.product;
            const input = document.getElementById(`qty-${productId}`);
            if (input) {
                let value = parseInt(input.value) || 1;
                if (value < 10) {
                    input.value = value + 1;
                }
            }
        });
    });
    
    document.querySelectorAll('.qty-minus').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.product;
            const input = document.getElementById(`qty-${productId}`);
            if (input) {
                let value = parseInt(input.value) || 1;
                if (value > 1) {
                    input.value = value - 1;
                }
            }
        });
    });
    
    // Add to Cart Functionality
    document.querySelectorAll('.btn-add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.product;
            const quantityInput = document.getElementById(`qty-${productId}`);
            const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
            
            addToCart(productId, quantity);
        });
    });
    
    // Cart Quantity Updates
    document.querySelectorAll('.cart-qty').forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.dataset.product;
            const quantity = parseInt(this.value) || 1;
            
            if (quantity < 1) {
                this.value = 1;
                return;
            }
            
            updateCartItem(productId, 'update', quantity);
        });
    });
    
    document.querySelectorAll('.cart-item .qty-plus').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.product;
            const input = document.querySelector(`.cart-qty[data-product="${productId}"]`);
            if (input) {
                let value = parseInt(input.value) || 1;
                if (value < 10) {
                    input.value = value + 1;
                    updateCartItem(productId, 'increase');
                }
            }
        });
    });
    
    document.querySelectorAll('.cart-item .qty-minus').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.product;
            const input = document.querySelector(`.cart-qty[data-product="${productId}"]`);
            if (input) {
                let value = parseInt(input.value) || 1;
                if (value > 1) {
                    input.value = value - 1;
                    updateCartItem(productId, 'decrease');
                }
            }
        });
    });
    
    document.querySelectorAll('.cart-item-remove').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.product;
            updateCartItem(productId, 'remove');
        });
    });
});

// Add to Cart Function
function addToCart(productId, quantity) {
    fetch('/add-to-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart badge
            updateCartBadge(data.cart_count);
            
            // Show toast notification
            showToast(data.message);
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

// Update Cart Item Function
function updateCartItem(productId, action, quantity = null) {
    const data = {
        product_id: productId,
        action: action
    };
    
    if (quantity && action === 'update') {
        data.quantity = quantity;
    }
    
    fetch('/update-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart badge
            updateCartBadge(data.cart_count);
            
            // Update cart totals
            updateCartTotals(data);
            
            // Update cart items display if cart is empty
            if (data.cart_items && data.cart_items.length === 0) {
                location.reload(); // Reload to show empty cart
            }
        } else {
            showToast('Error updating cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

// Update Cart Badge
function updateCartBadge(count) {
    const cartLinks = document.querySelectorAll('.nav-menu a[href*="cart"]');
    cartLinks.forEach(link => {
        const badge = link.querySelector('.cart-badge');
        if (count > 0) {
            if (badge) {
                badge.textContent = count;
            } else {
                const newBadge = document.createElement('span');
                newBadge.className = 'cart-badge';
                newBadge.textContent = count;
                link.appendChild(newBadge);
            }
        } else {
            if (badge) {
                badge.remove();
            }
        }
    });
}

// Update Cart Totals
function updateCartTotals(data) {
    const subtotalElement = document.getElementById('subtotal');
    const deliveryElement = document.getElementById('delivery');
    const totalElement = document.getElementById('total');
    
    if (subtotalElement) subtotalElement.textContent = data.subtotal.toFixed(2);
    if (deliveryElement) deliveryElement.textContent = data.delivery.toFixed(2);
    if (totalElement) totalElement.textContent = data.total.toFixed(2);
    
    // Update item subtotals
    if (data.cart_items) {
        data.cart_items.forEach(item => {
            const itemElement = document.querySelector(`.cart-item[data-product="${item.id}"]`);
            if (itemElement) {
                const subtotalElement = itemElement.querySelector('.cart-item-subtotal p');
                if (subtotalElement) {
                    subtotalElement.textContent = `RM ${item.subtotal.toFixed(2)}`;
                }
                
                const qtyInput = itemElement.querySelector('.cart-qty');
                if (qtyInput) {
                    qtyInput.value = item.quantity;
                }
            }
        });
    }
}

// Toast Notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = toast.querySelector('i');
    
    if (toast && toastMessage) {
        toastMessage.textContent = message;
        
        if (type === 'error') {
            toastIcon.className = 'fas fa-exclamation-circle';
            toast.style.background = '#d32f2f';
        } else {
            toastIcon.className = 'fas fa-check-circle';
            toast.style.background = '#2d1b0e';
        }
        
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Form Validation (Contact & Checkout)
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const requiredFields = this.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#d32f2f';
                isValid = false;
            } else {
                field.style.borderColor = '#ddd';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showToast('Please fill in all required fields.', 'error');
        }
    });
});
