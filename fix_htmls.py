import os

files = ['food-lab.html', 'food-lab-salad.html', 'food-lab-wrap.html', 'food-lab-smoothie.html']

cart_html = """
<!-- TOAST NOTIFICATION -->
<div id="toast-container" style="position: fixed; bottom: 30px; right: 30px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;"></div>

<!-- CART MODAL AS SIDEBAR -->
<div id="cart-modal" class="modal-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 10000; opacity: 0; visibility: hidden; transition: all 0.3s ease;">
<div class="cart-sidebar-content" style="background: white; width: 400px; height: 100%; position: absolute; right: 0; top: 0; display: flex; flex-direction: column; padding: 20px; box-shadow: -4px 0 15px rgba(0,0,0,0.1);">
  <div class="flex justify-between items-center border-b pb-4 mb-4">
    <h2 class="text-2xl font-bold serif-title text-green-900">Your Cart</h2>
    <button id="close-cart" class="text-2xl text-gray-500">&times;</button>
  </div>
  <div id="cart-items" class="flex-1 overflow-y-auto"></div>
  <div class="border-t pt-4 mt-auto">
    <div class="flex justify-between items-center mb-4">
      <span class="font-bold">Total</span>
      <span id="cart-total-price" class="text-2xl font-bold text-green-900">$0.00</span>
    </div>
    <button class="checkout-proceed-btn w-full bg-green-900 text-white py-3 rounded-lg font-bold">Proceed to Checkout</button>
  </div>
</div>
</div>

<script src="./assets/js/api.js"></script>
<script src="./assets/js/auth.js?v=5"></script>
<script src="./assets/js/cart.js"></script>
<script src="./assets/js/customizer-static.js"></script>
</body></html>
"""

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # Remove old scripts if present
    content = content.replace('<script src="./assets/js/food-lab.js"></script>', '')
    content = content.replace('<script src="./assets/js/api.js"></script>', '')
    content = content.replace('<script src="./assets/js/auth.js?v=5"></script>', '')
    content = content.replace('<script src="./assets/js/cart.js"></script>', '')
    content = content.replace('<script src="./assets/js/customizer-static.js"></script>', '')
    
    # Remove old modals if present
    if 'id="toast-container"' in content:
        content = content.split('<!-- TOAST NOTIFICATION -->')[0]
    else:
        content = content.replace('</body></html>', '')
        
    content = content.strip() + '\n' + cart_html
    
    with open(f, 'w') as file:
        file.write(content)

print("Updated HTML files.")
