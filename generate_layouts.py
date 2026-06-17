import re

template = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{PAGE_TITLE} - The Healthy Lab</title>
<!-- Tailwind CSS CDN -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<!-- Google Fonts for Serif/Sans-serif combo -->
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&amp;family=Inter:wght@300;400;500;600&amp;display=swap" rel="stylesheet"/>
<style data-purpose="typography">
    body {
      font-family: 'Inter', sans-serif;
      background-color: #fcfcfc;
      color: #333;
    }
    h1, h2, .serif-font {
      font-family: 'Libre+Baskerville', serif;
    }
  </style>
<style data-purpose="layout-custom">
    .card-shadow {
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }
    .active-tab {
      border-bottom: 2px solid #1a3c2f;
      color: #1a3c2f;
      font-weight: 600;
    }
    .ingredient-card {
      transition: all 0.2s ease-in-out;
      border: 1px solid #f0f0f0;
    }
    .ingredient-card:hover {
      border-color: #1a3c2f;
      transform: translateY(-2px);
    }
    .ingredient-card.selected {
      border-color: #1a3c2f;
      background-color: #f4fbf8;
    }
    .sidebar-sticky {
      position: sticky;
      top: 2rem;
    }
  </style>
</head>
<body class="min-h-screen">
<!-- BEGIN: MainHeader -->
<header class="bg-white border-b border-gray-100 py-6 px-8 md:px-16 flex justify-between items-center sticky top-0 z-50">
<div class="logo">
<h1 class="text-2xl font-bold text-gray-900">The Healthy Lab</h1>
</div>
<nav>
<ul class="flex space-x-8 text-xs tracking-widest text-gray-600 font-medium uppercase">
<li><a class="hover:text-black" href="index.html">HOME</a></li>
<li><a class="hover:text-black" href="#">ABOUT US</a></li>
<li><a class="hover:text-black" href="#">SHOP</a></li>
<li><a class="hover:text-black" href="#">LOGIN</a></li>
<li><a class="hover:text-black" href="#">REGISTER</a></li>
<li><a class="hover:text-black" href="#">CART (0)</a></li>
</ul>
</nav>
</header>
<!-- END: MainHeader -->
<main class="max-w-7xl mx-auto px-8 md:px-16 py-12">
<div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
<!-- BEGIN: CustomizerSection -->
<section class="lg:col-span-8" data-purpose="customizer-controls">
<header class="mb-10">
<p class="text-sm text-gray-500 mb-2">Interactive Meal Builder</p>
<h2 class="text-5xl mb-4 text-gray-900 serif-font">{HERO_TITLE}</h2>
<p class="text-lg text-gray-400">{HERO_DESC}</p>
</header>
<!-- BEGIN: NavigationTabs -->
<nav class="flex space-x-8 border-b border-gray-200 mb-12 text-sm text-gray-400 font-medium" data-purpose="category-navigation">
{TABS}
</nav>
<!-- END: NavigationTabs -->
{STEPS_HTML}
</section>
<!-- END: CustomizerSection -->
<!-- BEGIN: NutritionSidebar -->
<aside class="lg:col-span-4" data-purpose="order-summary-sidebar">
<div class="bg-white rounded-3xl p-10 card-shadow sidebar-sticky">
<h2 class="text-2xl mb-8 serif-font">Your Nutrition</h2>
<!-- Nutrition Grid -->
<div class="grid grid-cols-2 gap-y-10 gap-x-8 mb-12 border-b border-gray-100 pb-12">
<div>
<p class="text-4xl font-semibold mb-1">0</p>
<p class="text-[10px] uppercase tracking-widest text-gray-400 font-bold">Calories</p>
</div>
<div>
<p class="text-4xl font-semibold mb-1">0g</p>
<p class="text-[10px] uppercase tracking-widest text-gray-400 font-bold">Protein</p>
</div>
<div>
<p class="text-4xl font-semibold mb-1">0g</p>
<p class="text-[10px] uppercase tracking-widest text-gray-400 font-bold">Carbs</p>
</div>
<div>
<p class="text-4xl font-semibold mb-1">0g</p>
<p class="text-[10px] uppercase tracking-widest text-gray-400 font-bold">Fats</p>
</div>
</div>
<!-- Composition -->
<div class="mb-10">
<h4 class="text-xs uppercase tracking-wider text-gray-400 font-bold mb-3">Composition</h4>
<p class="text-sm text-gray-600 leading-relaxed">Start selecting ingredients...</p>
</div>
<!-- Price & CTA -->
<div class="mt-auto">
<div class="flex items-center mb-8">
<span class="text-2xl text-gray-900 mr-2 font-bold">Total Price:</span>
<span class="text-3xl font-bold text-gray-900" id="val-price">${BASE_PRICE}</span>
</div>
<button data-purpose="add-to-cart-button" class="w-full bg-[#1a3c2f] hover:bg-[#122b22] text-white py-5 rounded-lg flex items-center justify-center font-semibold transition-colors duration-200">
<svg class="h-5 w-5 mr-3" fill="none" stroke="currentColor" viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
</svg>
              Add to Cart
            </button>
</div>
</div>
</aside>
<!-- END: NutritionSidebar -->
</div>
</main>

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
</body></html>"""

def get_tabs(active_name):
    tabs = [
        "Signature Bowl",
        "Artisan Wrap",
        "Fresh Salad",
        "Smoothies",
        "Fresh Juices"
    ]
    html = ""
    for t in tabs:
        if t == active_name:
            html += f'<button class="pb-4 active-tab">{t}</button>\n'
        else:
            html += f'<button class="pb-4 hover:text-gray-600">{t}</button>\n'
    return html

def build_card(img, name, cal_text, is_vertical=False):
    if is_vertical:
        return f"""<!-- Card -->
<div class="ingredient-card bg-white p-4 rounded-xl flex flex-col items-center text-center cursor-pointer">
<img alt="{name}" class="w-16 h-16 mb-4 object-contain" src="{img}"/>
<p class="font-bold text-sm leading-tight">{name}</p>
<p class="text-[10px] text-gray-400 mt-1">{cal_text}</p>
</div>"""
    else:
        return f"""<!-- Card -->
<div class="ingredient-card bg-white p-4 rounded-xl flex items-center space-x-4 cursor-pointer">
<img alt="{name}" class="w-16 h-16 rounded-full object-cover" src="{img}"/>
<div>
<p class="font-bold text-sm leading-tight">{name}</p>
<p class="text-xs text-gray-400">{cal_text}</p>
</div>
</div>"""

def build_step(step_idx, title, subtitle, items, is_vertical=False):
    grid_class = "grid grid-cols-1 md:grid-cols-4 lg:grid-cols-4 gap-4" if is_vertical else "grid grid-cols-1 md:grid-cols-3 gap-4"
    html = f"""<div class="mb-14" data-purpose="step-{step_idx}">
<h3 class="text-xl font-bold mb-6">{step_idx}. {title} <span class="text-sm font-normal text-gray-400 ml-2">({subtitle})</span></h3>
<div class="{grid_class}">
"""
    for item in items:
        html += build_card(item['img'], item['name'], item['cals'], is_vertical) + "\n"
    html += "</div></div>\n"
    return html

pages = [
    {
        "file": "food-lab-salad.html",
        "title": "Fresh Salad Customizer",
        "hero_title": "Fresh Salad Customizer",
        "hero_desc": "Interactive Meal Builder for Fresh Salads at 'The Healthy Lab'.",
        "active_tab": "Fresh Salad",
        "base_price": "8.99",
        "steps": [
            {
                "title": "Choose Your Greens", "subtitle": "Select up to 2", "is_vertical": False,
                "items": [
                    {"name": "Mixed Field Greens", "cals": "10 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrz3sj8k8FjvPy9UgMrSSDn_Q60skSIxvJ-bQTQ0mRv4_vGApIjePepDgaeWLHat0_leKDSEXb0n4xqX3mVKX1TmJb-F-C6epq4S2zKpM-S4Li-Rza0_RQb37hxGX5oQFt9WoUkoCYpZIkFnER0IHvsCVXxsFqjc830EqiAEeS0UpeW1BhhhgtmAMk5d4Z2bewgLp8p2zRAEE1czyFjr1NWepJ6417PT5PL1ZXdBHVIG8W-VmbNjAfpyeZvpRRr-YmmPVowQfgAkgH"},
                    {"name": "Baby Spinach", "cals": "7 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBS7LDZoWvlwzx08c5FAKcl8kp6lE76qKWmrtYF-9kEzFrkcTsH17osYuC2mQS074KAqUG6lcuCSiKcL4h88_jvv9lGin23OsEkEmZn1pkbHRmN2RlJZYvDH6ucpBgqe6-J04Vs7yWgqAfHkmoFawtb_5syY-0oDdqK4djqnOoz6-en_hnkyQylEKc4j-ydMvimYN2bzR7wURHFX0sBchp7CyntWsdxWwXzpFbNEtrXIJrugdj0SqP8wSs07D9GreT-DZ9HRBKNq7iO"},
                    {"name": "Romaine", "cals": "8 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBrgqvhWsAvXBmqvWTbOiwqOWzMFF6ntTSiedtZC1cm2OVRVECLknAJUxKf4HXTJYzPDn_qCaR6PNzd9Bq54wPw192fRbbGBY9rrZKxA2dZAMxQjKQHxrUh5kh1xDRYrHeIcBL9CVOpSXaZ-LDBT1dQ0WDCLwfPuOR0b2opSpbdpEXpl5qGo81AADq-6PBnfb1Tn0xX39VMFgZfTSLu_M9Mcu0TEyXyvXk3Ap-aOAT8Jqy__sYiwXMTDuzShx6uciiV_IpUgJlCcVSr"}
                ]
            },
            {
                "title": "Select a Protein Boost", "subtitle": "Select 1", "is_vertical": False,
                "items": [
                    {"name": "Poached Egg", "cals": "78 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuAUqauihIfbMiRomrF3CX-oeCNUCGTjzX3endlN0Ip9FRBbZXNygHfI4qGjWHXKJgyR0SEMtehuviGL1BB-zEu14ur2k0aDwRSfzoghxihgBmyJBUNAcVnFXvvXiO7HHES8z10b2ugVdpjqk3Ekf6iKlIqatsNkScePdAr4w2xVmRzFpFAIDzBYH-vWhnbL2m78lnNBW1y5t2TSnA0f1cbfP1-Ila1YemR9heJZ7rMedCaK9jwRARyQydQfGHJElgdHGXvOnv5LjOaH"},
                    {"name": "Grilled Steak Strips", "cals": "160 cal, +$4.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuD9bz9h3wTENrfLKjdum6-gMHstMN5-5CaJatevNWTi6SSb5onoz8ZYqH0Xewopnpuu2KUxD3-1pclEPawGOoTZzrRImzuHu1kb5_hDdx9_PxiHjxN6eSfyAfmpa7bY49c_o2QCQ4zsM2ARvNkAQKeSKHOpOZn6t5szlOe9ew-h0t-G7MNvsASHZOKeSI3ImJvnYGpJfIjT97RoEm9Ug3aI7GoMaZG_LY31EsQkD_FM8-E_mtm_xg3ReCiAeL60d3oL6TVhdU49NSYr"},
                    {"name": "Tempeh", "cals": "140 cal, +$2.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuA5eNNGX80ZiMprvI-YrVLJda-IlK_ypp4vOuXwpdBOGL-9Y0bQ3By_BKMTCfMNsdcZUd2nUcHKkQN2_W51SchZJKK7HBxaQVdjivXHK1DObB2ATODyL_7B4gNsbGlPukGRLC8fLa-pau6bQ5a0wm5GoCt2HzHQczPTcVDV2rga0QTUqBQNVdsf1tE448ocQQ8zSG5V8w-hDT2pKE4I4rnIKmFO9LQXBL6HJVcTyBi7rllF-07JlR2jObNUZsXnG4EN98N2h3KnXzA3"}
                ]
            },
            {
                "title": "Pick Your Crunch & Dressings", "subtitle": "Select up to 3", "is_vertical": True,
                "items": [
                    {"name": "Sunflower Seeds", "cals": "170 cal, +$1.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBdSTVNpFAV956j5Sdo3n4hR7CGe_ONbUfD8udDQtslvPQHiL7vJ4DKA9ckqIWaIO3GCF0M0WkEQ7WuWZ4P67BetFoqzArQ3RR0MPAzpGdU_6Umt-7S05j_HmaEi_h78BZXZ-Fd-pj_63pi2Lm3zk6isCeCaFigRXirlxeBYInhwGB4QNkzc6Ku3p--GQ7CJzE2a8MLMRNcBaGHsFrCQPBl-RsZUfXfsD_ynmmFuMS5jK9CO2gRHtoW1-nSK2fsmYtaBHRbOh2GvwRr"},
                    {"name": "Lemon Tahini", "cals": "120 cal, +$1.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuCCDPeM-5zYIeQOwczGTFsVyJzVQiisgvlWmStPGmCMkC30K1IE_im5gjqLUPv6-fz9O252KqmgxSg1NGl84KJwetGPBgvdifXq_ubDHTxjAQw4E55Zhb3Aq1rIKtetDTYIwVZuTGpftguSFQrLIBRxnP_gKTjTmRIg5pkxOUSgAxEQnwgx7ewb5xGkMOEp8sk6EmT29UtqfhtUFgK6nqaBXt1jUHMIvQSSGcpX7IZGzu0cEzOH8v3mcJwy-O_n1YcGTFd5hlYms3Tv"},
                    {"name": "Balsamic Glaze", "cals": "60 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDxxdrdcYEejKWI2WBji-x3UEnQHNZ_P6VzZ7I90BcSpKof_321OFiaM_SNVJqyrbk3MkRkp1oRwvsQv1BEff2NtySufOxNbHxYD-bRDGl4MEnqoeF_0wB8riA13doaLpVtI8k_TGV-9_OTjE6NaBr4xBO7swxVgrmmbN3we7kgiTXmabowI-JvmF5KIjN4bdDe9VGAnW0-UJg3y2AYtE3mynQ3s__KUztZzFWkXqHmEsDKlhc0iCj3fd8Q2kEC2ynxbQVkLRb9A8g1"}
                ]
            }
        ]
    },
    {
        "file": "food-lab.html",
        "title": "Signature Bowl Customizer",
        "hero_title": "Signature Bowl Customizer",
        "hero_desc": "Interactive Meal Builder for Signature Bowls at 'The Healthy Lab'.",
        "active_tab": "Signature Bowl",
        "base_price": "9.99",
        "steps": [
            {
                "title": "Pick Your Base", "subtitle": "Select up to 2", "is_vertical": False,
                "items": [
                    {"name": "Quinoa", "cals": "220 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrdx2R3YxK8qM2pB1w6hWwPzM_Z_1Xy_J_L_vP9H8O_J4K_Wc2QvE2I_P9z3U_N_K4z1P0L_T8A_Z0z3D_Y5P_L_J9W_D2K1O"},
                    {"name": "Brown Rice", "cals": "210 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrdx2R3YxK8qM2pB1w6hWwPzM_Z_1Xy_J_L_vP9H8O_J4K_Wc2QvE2I_P9z3U_N_K4z1P0L_T8A_Z0z3D_Y5P_L_J9W_D2K1O"},
                    {"name": "Baby Kale", "cals": "15 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBS7LDZoWvlwzx08c5FAKcl8kp6lE76qKWmrtYF-9kEzFrkcTsH17osYuC2mQS074KAqUG6lcuCSiKcL4h88_jvv9lGin23OsEkEmZn1pkbHRmN2RlJZYvDH6ucpBgqe6-J04Vs7yWgqAfHkmoFawtb_5syY-0oDdqK4djqnOoz6-en_hnkyQylEKc4j-ydMvimYN2bzR7wURHFX0sBchp7CyntWsdxWwXzpFbNEtrXIJrugdj0SqP8wSs07D9GreT-DZ9HRBKNq7iO"},
                    {"name": "Edamame Mix", "cals": "120 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrdx2R3YxK8qM2pB1w6hWwPzM_Z_1Xy_J_L_vP9H8O_J4K_Wc2QvE2I_P9z3U_N_K4z1P0L_T8A_Z0z3D_Y5P_L_J9W_D2K1O"}
                ]
            },
            {
                "title": "Select a Protein", "subtitle": "Select 1", "is_vertical": False,
                "items": [
                    {"name": "Grilled Salmon", "cals": "280 cal, +$4.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrdx2R3YxK8qM2pB1w6hWwPzM_Z_1Xy_J_L_vP9H8O_J4K_Wc2QvE2I_P9z3U_N_K4z1P0L_T8A_Z0z3D_Y5P_L_J9W_D2K1O"},
                    {"name": "Herbed Chicken", "cals": "180 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrdx2R3YxK8qM2pB1w6hWwPzM_Z_1Xy_J_L_vP9H8O_J4K_Wc2QvE2I_P9z3U_N_K4z1P0L_T8A_Z0z3D_Y5P_L_J9W_D2K1O"},
                    {"name": "Smoked Tofu", "cals": "160 cal, +$2.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuA5eNNGX80ZiMprvI-YrVLJda-IlK_ypp4vOuXwpdBOGL-9Y0bQ3By_BKMTCfMNsdcZUd2nUcHKkQN2_W51SchZJKK7HBxaQVdjivXHK1DObB2ATODyL_7B4gNsbGlPukGRLC8fLa-pau6bQ5a0wm5GoCt2HzHQczPTcVDV2rga0QTUqBQNVdsf1tE448ocQQ8zSG5V8w-hDT2pKE4I4rnIKmFO9LQXBL6HJVcTyBi7rllF-07JlR2jObNUZsXnG4EN98N2h3KnXzA3"},
                    {"name": "Crispy Falafel", "cals": "180 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrdx2R3YxK8qM2pB1w6hWwPzM_Z_1Xy_J_L_vP9H8O_J4K_Wc2QvE2I_P9z3U_N_K4z1P0L_T8A_Z0z3D_Y5P_L_J9W_D2K1O"}
                ]
            },
            {
                "title": "Add Accents", "subtitle": "Select up to 4", "is_vertical": True,
                "items": [
                    {"name": "Avocado", "cals": "160 cal, +$2.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuA5QIfGgIX5ckzLosGwXaZaokkDQUn5lMfyUt5ygnYsURl-kFY0RSEROTOyGyP31vWlQt6R2_S2H_ue0MN1mZhqMvewAq7zCqFQ4PATJD7S3JgiV-lDc4q3Esvfk_SWPiJzhDtzMAjrkQHm4PokF8DUV_c3hRMSxKHrs-VyZJ_sKGQdTijyZDe7fHYrHr8sFy_eT_60Ker9cozRxnjQiPClpwLtfJm0ppZ633zBlgP_H0i3fZJ1jKwrfBty8TUELMpr715QMLtCcRZh"},
                    {"name": "Hemp Seeds", "cals": "50 cal, +$0.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBdSTVNpFAV956j5Sdo3n4hR7CGe_ONbUfD8udDQtslvPQHiL7vJ4DKA9ckqIWaIO3GCF0M0WkEQ7WuWZ4P67BetFoqzArQ3RR0MPAzpGdU_6Umt-7S05j_HmaEi_h78BZXZ-Fd-pj_63pi2Lm3zk6isCeCaFigRXirlxeBYInhwGB4QNkzc6Ku3p--GQ7CJzE2a8MLMRNcBaGHsFrCQPBl-RsZUfXfsD_ynmmFuMS5jK9CO2gRHtoW1-nSK2fsmYtaBHRbOh2GvwRr"},
                    {"name": "Pumpkin Seeds", "cals": "60 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBdSTVNpFAV956j5Sdo3n4hR7CGe_ONbUfD8udDQtslvPQHiL7vJ4DKA9ckqIWaIO3GCF0M0WkEQ7WuWZ4P67BetFoqzArQ3RR0MPAzpGdU_6Umt-7S05j_HmaEi_h78BZXZ-Fd-pj_63pi2Lm3zk6isCeCaFigRXirlxeBYInhwGB4QNkzc6Ku3p--GQ7CJzE2a8MLMRNcBaGHsFrCQPBl-RsZUfXfsD_ynmmFuMS5jK9CO2gRHtoW1-nSK2fsmYtaBHRbOh2GvwRr"},
                    {"name": "Sweet Potato", "cals": "90 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDrdx2R3YxK8qM2pB1w6hWwPzM_Z_1Xy_J_L_vP9H8O_J4K_Wc2QvE2I_P9z3U_N_K4z1P0L_T8A_Z0z3D_Y5P_L_J9W_D2K1O"}
                ]
            }
        ]
    },
    {
        "file": "food-lab-wrap.html",
        "title": "Artisan Wrap Customizer",
        "hero_title": "Artisan Wrap Customizer",
        "hero_desc": "Interactive Meal Builder for Artisan Wraps at 'The Healthy Lab'.",
        "active_tab": "Artisan Wrap",
        "base_price": "8.50",
        "steps": [
            {
                "title": "Choose Your Wrap Type", "subtitle": "Select 1", "is_vertical": False,
                "items": [
                    {"name": "Whole Wheat Wrap", "cals": "180 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDjiktRx4wOMH5inb6kSekYBIMm15yGfbpu5d8e-4qxsojEDG_9hmmCnJgPL608arRDOXNGslEOP8Wbu0FfBybB8S7dVVHgagfU1uiyWJoj4cK6UxzGAw2QUVvdtpBnOeDjzVnwLA0BSyR_1a3CzWhhb1HWw_JOpJn4jMalL6KE4d6cFYz0KvJ_hzMDDVJG3ia7VsVqg9c-Nq87Cx4wVc_ysIkITUftux2W-_H-aohpbDBzDehRrI4UGYzKQCvyialFf1pvJiz3kKbH"},
                    {"name": "Spinach Wrap", "cals": "160 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuAzEU4gxdsQ0DxEh62GHJTA7NtacwwWsS_wXHCqx3zvDfCdWPq3lTU7Q-TZwZ__yxGRUBeOJtXKdAxA5_bEhM5D4SF6H45KxoQFi2nt6gC6YlH7Wvv891j4jIaRCjQEvBxviDq27nRl3zjsIlhc30pO3jcO-q69IJr1XIkbV2PHU17Kx-CgAemjLZ15vQPecSzLWBw2VCHybNVTCKbSxtKeSF9v8e1g2Ohp96A_V3gfDId-4TzbKXT5_A_NFjY2KXcGMWZscSCTkrwA"},
                    {"name": "Gluten-Free Teff Wrap", "cals": "180 cal, +$1.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDRd8a2ussHmReIYGzyWjYyNzQ1nZG_kItFScGtQJRw6hEkvn-jbWshB-IWKt0Q4NTeAhGXVfPAoenBro2TUbbF_w2lYKQkNl5hfLkC-U8ypLfR6vPXRm1uKtjBoEIX3EH4PpPeI_5zCM5k1CBnBSd1-GDITnl19mY0RK74vlSoKIo-YNmRs_io2DyL7rhB5JS--42IPUzpKFn7i7K9FfNu4JfunLDaBlVfs_djnan6QR2GjkoGiXifxy7iV3dEhhTegGhxcnfEovzc"}
                ]
            },
            {
                "title": "Select a Main Filling", "subtitle": "Select 1", "is_vertical": False,
                "items": [
                    {"name": "Grilled Halloumi", "cals": "220 cal, +$4.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuAn3hq-LlkAzHVZbske006k40FDIB9A7rDdncMP1eZSqksRVgQ8_WeG7njOPp5m_pkSy2HS9iTxtBDzqT0jDqLdMisL4agGu-fFCVSiVVUMlamLUG-yIcbMk2NWubvv042mmXEsDVCqNSnAG4Wx24JX20m-Re2l49zqF4PqWoNs60r__tYVOF0RtoL9wzQVY0_01VUy4rpiWCC-U1Qq-nifzrnLgvvGGlEBFFHVwOOwnH63q3I85zYjQTFoLAghagL2slOvDpOUaW37"},
                    {"name": "Roasted Turkey", "cals": "180 cal, +$3.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuClAOBqJOjpilzai-1jSLJtU3mxNvjOyAs40stQKnTbiSU9JyBoEgMEIszHXlPuGEHqZThiqhQqH2pwDYeKsOwI7PGUIyrrOWh4wfNUzGgIVmQWaKfqZZrQDWQpDuop_y9B7bjnNJBn2hs-rEHdUEfN8VP6vubowuAk22ESlsIk1_WluUrP2uq9TD9RJ4V9eVbBNZ9--rAxlkSOE5S-poR4_6gji-eP7zOcq3kRXJsKzFjgBLt1ZyesRpgMb0w4AaexnBwqiB6fxRgm"},
                    {"name": "Spicy Chickpeas", "cals": "180 cal, +$2.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuA4mTCSsW5N42WZjlV20iVT0OG0mYW4HwDETH57NO3EZeXgy7EOGvv9Qa6RldkNzMlJK3ZxPyTlf4NWe5ULh1eJKlUY9OO1CvrkInKLjEJn8pkFjHkAbpZlVzvSSGxqzlGGqAlaOX1BfZU2GEz2CSZEXTlzaLLdJsLNshzzX2KqSM6cdb3-e4bmqIfzpElo5LXmpk3g6D6SNwLz2g5xmwpYOVOQeBY3CZAKngzgjwTPh40W6GK6iHv412bNnlWtSPR3gYu6hIeex8nw"}
                ]
            },
            {
                "title": "Add Toppings & Spreads", "subtitle": "Select up to 3", "is_vertical": True,
                "items": [
                    {"name": "Hummus", "cals": "90 cal, +$1.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDqHFpwkom_1HdxTC9oIFGWk11IDZMeRRf5sgARkxLAKfIcDPJd1nfynxAAtnYSpFTAWr00gk3aPKldccPvVWgIpxSlKvpgWddj7W1B8OjcOhtqZoY-zPboPl0c2ohj72Fq_0iDdifsaFUu-Xo1wIHr9PyRBgmJNL0mk9AtzgoCQQNGp9KtqxaaLUTHITWy3EM0Cby-VtGIcXIS3LDV3L_MpPa2ZizK99JjedPOAMjweMRrZ-JgkgIVAsUChtHcJVaLJ1fwPCbcy2s2"},
                    {"name": "Roasted Peppers", "cals": "45 cal, +$1.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDZ_EYunPI8QRXdUSpW9-idSxHKHJDR1pOn5jkawLwWt0r0ARXrNTDZQOp06oi86zzQEgHMoNBNfmDbrq8gyw3ZqfvyHwQRNBl9hIvp1B3duhe2OW50xGbgDW02cb2tDnCxxvGJ7ZMsHJ1Ojcsn9mSbwICHUQjSBiH8HHEkhuy1QkTQzeq-o1W_0MYw4cSJp9RlrOGWk3yDDSlEl9QlOoYIgGH_78eDUHTt-1AfupxaLFaEWCIaAHXzS0BX4fzUfcSTOGzpSGMBCk00"},
                    {"name": "Arugula", "cals": "10 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuAMlHM5qtFzdH0fFqfdzgSZ4f-Vf-s8qyTKGXNfMNbGw6p80IQebpn04iI1rSM5cySfEqi8D5_RvWZOYeMZilFaQrH7wMAHFvPngMkX5WKzk2dX5pfjUp4S-VZN--OtS-QIJYPHM8m2WRyz4bL3wwo_NrCsrzC8AgOIjHOIHrQVha3hTBF2SvLSgvuA3n5IxlF-OjEjWsAUOfjAD2vPXgGyWAHGZO0NTDYmwqAiX9bYIvPhW7faaJS7Z4JqZG2z7g_CKHrnLneQpp8H"},
                    {"name": "Tzatziki", "cals": "70 cal, +$1.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuCCvVkYK7yBEzCMFnQ53TK93m63GxW0s3cF2xBtLf40LSRMlNV-s6eS9W29IqzmJmAOC5KJUFvQXsVYYjpA6dQcXiTncfaHaz3XX92B7GOkbW0VK0X7yCblMAXqgJ_9gKwi698VoQErM9_BaFzoO9fA7P6EEMqmOyrLohAvnEx8jk0eHdh1A41l8iQTCN6HJciJU4oFzs4h6myZwqF96-fZz7E337OuoXCYaLPMW-MtpO9aFyeT18YdwAacrnN6YJO3CsbQuq1nUpsJ"}
                ]
            }
        ]
    },
    {
        "file": "food-lab-smoothie.html",
        "title": "Smoothie Customizer",
        "hero_title": "Smoothie Customizer",
        "hero_desc": "Interactive Builder for Smoothies at 'The Healthy Lab'.",
        "active_tab": "Smoothies",
        "base_price": "6.99",
        "steps": [
            {
                "title": "Pick Your Base", "subtitle": "Select up to 2", "is_vertical": False,
                "items": [
                    {"name": "Almond Milk", "cals": "60 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBzCYINsTDWaH9XRP1onNk_1d-O25DltSKSq8_Uc_N5d3a1kq5MjxKCq5FjNgdiQ0i5tOxiDKgxFshgGZXWOnXa4jcJPaNOdW9VUh74yWMExGSUrA3wPoOyeC0SwEhyM7b2oNujOVRjtA0klvOTuD4OaEPwM5wDGlZQUEHbR0zPD-eCtGIKX7hsMADPbeSKGwPRQnrn49dqB6GpVKr98xG4LZzMcHVNzXi3Ux8CW0sTzp-jiPU3656v_XULQ1hfDJZ7W9bYQsYac6PA"},
                    {"name": "Coconut Water", "cals": "45 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDvVLbXgMmi6JvgP5cTcSLB0g_O7BjBlxrt6oORjqYbRLSXFdEz7xuzwpSTTkASXlSvvXnONDdykn6mVJxjzqHXL6Fi4P5ETkDEhzmMMlSoZBxJbydS_s3-vcqOCbw83e7XIFT_gU0TnstXi9oIb9AvZ3i8SXrtfEZwf-gopn5JrZV_EOYVBXOIb5TCrw7Ri9KRMGrhHISJZUxvVkxco9V_RzGW5fUmR5EMmJi-78WaFbhxQqbnwEv7r5MWlihhABG7XfpZhd8jpMBJ"},
                    {"name": "Cold-Pressed Apple Juice", "cals": "110 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBlT6imaytRM-eN54bI1OjcMa94K82RtCB1Tg_kE_1KKCIZKx2fMD3TKNEtjMS0bfReJF1crtlkX-thJbGdF492GK31yL0rtRtaS3Y9NiGYYCAck366bRzyRN1BPPtmEsASILPsODv5CEwY1N2Hu0QaemFQDLKKsH7GflIyrpUmbdhmCH8XuvfDAaBvqviPAtE9VLGwIj2h4eQJnq7nC8lVcKz4utrU5j-941JLsb11sz_FAIMFWSsKraLfjI_N60ImL0a0aPGvl53o"}
                ]
            },
            {
                "title": "Select Fruits & Veggies", "subtitle": "Select up to 3", "is_vertical": False,
                "items": [
                    {"name": "Dragonfruit", "cals": "60 cal, +$2.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBAtqJ5NkztttiScLe87TYuBAXY_3gdF2RTSToBJMFGtdQ3JgApl8aZbDCAK8O_I7hQnq2MhDKe_OC1FcuQ0fv3tdlyI26yBuj_BSAswAsu4vbISiy0DYxgFymZaf2ViMgshXS-MuPunguYhIQpEw85axal1ZSCgOv0QNpKXojLY2BJtIpEorcIyoj97KUZgee0b7ZsqJRSJYyX9sJt4TzYWkdahYMfrXLa6paoTSri3stZfx-yq4EaupMu2YMQlB1evLO8j1YSqNTA"},
                    {"name": "Kale", "cals": "33 cal, +$1.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuBbxSd0YxnK5Y3WzTXqqzUVr827lBNP1dEMpagsNCJJHHRCa9mE2qQ4ZeUDX_GyGP0dsdJvtjq5KHpycz9s3Wm9hJhMVRu-E5TgG6TIXHHuxr1I0xKSOPR4AJFbkT24maqpxaFBAgUP3KHYwLST7Ic898xyk-SXdKINU1VPrPSVQ5kwmWfXndvWXCQcLthiHoBI-YrDfvpyNQUm04EHC4qw4I_MIVxYAvHp46b8WPBy9JOkIVLbUdMfEcL-Qq64Gua5H-t1qdDsmAPI"},
                    {"name": "Ginger", "cals": "5 cal, +$0.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDFsDGJ7GVt0xa58RzPh3aJmN5_gXJorRHxsnOuCDxAQ9jC7Bqc4UCJ2hL4HLuu_cQoqRK4wY2aSCXuZLuOH7Mf17OMmALsp-rzJN2eUqRwbMrBknnkCGel1okIATwZM7UtCinWGk9zXByRAkI-bHO-1nRKmPsIVxuNhT9Shm3boBGjllmGRuA0voUzMpI2KN2t_RUyCChHs0J7KHesgGpvtLw0Z82UHVFboIRG9JeFaAUBx2WgIZ65kTH2RQ8qCxnLIah5IMn-5ghD"}
                ]
            },
            {
                "title": "Superfood Add-ins", "subtitle": "Select up to 2", "is_vertical": True,
                "items": [
                    {"name": "Chia Seeds", "cals": "55 cal, +$1.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuA97soSU6N-DteeaXq2QESnhVhrmZrxq8AkMrYpHoWFFvUI96a4MJngr4Cfu51wopuIf1AJ2cGhwWVHWlHTFM-e19YVpha1ZVPzhJh4_w1nchPTCLHnRu4q_KPGGVtWVMDBtMPCQAHnRf2GX1YCkXKZiZQu4cWzTIK-FbZemNmvK4X0yO5J1wqdQXa-UeWYa3wow8xBYuMtcb-kGcKMeE1nHqTWkziXj3Z1VvtH0SuoByPgon2sotje_vXOJ04OiXVjwN0k_RUTqST0"},
                    {"name": "Ashwagandha", "cals": "10 cal, +$2.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuCBlhsA9ahAODMuMUmj4gf18gFT-CpXKIrUrpf8mlz9RlVBOJY9DbU-HKhmfC0xcaosor29m4kUrDH1QFm6Fawwjw8sp9P8CaDuMH01lZ9uKPpQENx_NfxZ3tgNM7PW3R9QdSzFIb8AO8LTvchOFRzTSxnjrvE2P08hWV58yO65Qlg_DKX-wzdz-huEzR2a4E1kzxcq0s6fjw-E8asP-BTDZ48sU6Qpl2DQDO84rYW11ZaiprQz3A_GRvtzhqG3ZKpgnoajO58yfN8Q"},
                    {"name": "Spirulina", "cals": "20 cal, +$2.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuCN1SrpbKnBmEelAt9D9p3sovvoKiHy9o6CnDBO4YkBRHLUQmbitWKjgyoPIieSG-ICNa_eHBd6PvIjIxc2R6pjKCM8zardohsAKCN8oOJX9nmYtYq1UGK4d0eP_56eQQrpMFrodeiot8r5HPbdrlOrV7jTy0kyo0JkdvH-A_uPbq2Vxhov6173H1kwehWqFHGtXZJFFAet3XlqfBMzXdocIDu0qLwscsA_sPcadOmCvtYn_IcIGR6KVsPz6GOJkKQkN6PRt0P1IKFS"}
                ]
            }
        ]
    },
    {
        "file": "food-lab-juice.html",
        "title": "Fresh Juice Customizer",
        "hero_title": "Fresh Juice Customizer",
        "hero_desc": "Interactive Builder for Fresh Juices at 'The Healthy Lab'.",
        "active_tab": "Fresh Juices",
        "base_price": "5.99",
        "steps": [
            {
                "title": "Pick Your Base Juice", "subtitle": "Select 1", "is_vertical": False,
                "items": [
                    {"name": "Cold-Pressed Apple", "cals": "110 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDizw1bgbx5DK3cKqiU_cgfB4MD8cnBLHrHEip6kEtmbO8yes8lh3cCf7YLvO9dJfAEEnfmlvyIWt4GVvatGLP2zJK8rAmZ0b2m_qeVZXijjctrvLpKrMKNwy0SZQ5wF_8NcCLyEf6OdhtmF_Y7-B3PcF0frysdhacdAnl43kdZEgl2GYhN0pQbE3uf9mGapbGwbxDb7eDDAxyg7JzZ7wsiyi9SpjcSsc9QaRy8MPhFRF-vND65Wrnnqzfx5JVEZDeyK5-ObES-8zwp"},
                    {"name": "Carrot Juice", "cals": "95 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDOUDK9K65mymhpAW7ZfhPBPhAkIYbzCLW52WbQCXX99uRMZJeA0ik2IbNHQn-DrmbQlolQnsE5gyxtOdNP5IuXhNzeqeivRdXlHnAjVxxvcNNsCjrKnq5fTHKfXOcVLLwmZ9EK9g5TxgzJJMK5LuGxWMFM3Nw9-oTuuFRVz8n-DeeKch_sIm5yHxsdiW7jMiMzKShDGdlIwblMCaJ8IBqv4grH_wPxEM6pZMapczRtAswHrG0Sn9uA5mAP1xVP1e5tt2mc8otyF-up"},
                    {"name": "Celery Juice", "cals": "40 cal", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuB7Bi88URFNVSTj9tHN1LjTk3nJuaIzrRc7PV_Q1F3vBgO44MSGBwNkHMz9siCRe9_pP9aNuwN094G72vmIEqYGTvcz2suSDby91bm3BzbsbxDxRr2P6FMPks56QOYdF_xk_kGM5QWrgzSbmflb1C5DWc30Bm_4sEJO90bZhiNsmUKQpPW5OqXe4MGhRB0e_WdpGjysPbdX9HZBtu_zrS_tM-ETmQ9ianhGSsuBBDsrlh5Ewrwq0MxhjvHz8P_PnvreYGOhtljT2BXM"}
                ]
            },
            {
                "title": "Flavor Enhancers", "subtitle": "Select up to 3", "is_vertical": False,
                "items": [
                    {"name": "Ginger", "cals": "5 cal, +$0.50", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDn-evyudR24VNLm8SywZ9LeanEhf2OOQe2Y_OrtmnwHQiaB6VYIODzElJscG4EZB6ggruaj95d2qikaHabiAI05KskWK-SV6pzFmcTKa8m3YxuA9SL_ASbxXZCHgPxKItP1AWomo3-0PX1CAwnOKH4qvZn4HRtvOeswBoVi_GAp2X3j4dpAB5f3QlzxD4TWqghrKRzopYcWbpNnKsIdKzVsWjFeopTGOeHiAWqIuU0qo4osuIjVORy3LcPM1KZAS58aBj5Apx_9a2w"},
                    {"name": "Turmeric", "cals": "10 cal, +$1.00", "img": "https://lh3.googleusercontent.com/aida-public/AB6AXuDxmxqaH_b75eOFH5cZPYfCNCfWuPxgUenzwEFk5BSEiumFXKo87iI0m_W2TmvcLd7IYUBeywZBOfvSmwBjNrCLhxRYloqPERohMS91wxAGRLpuvSJYphzVmI03sbi2RIxw0HvzEj5ACEgge3iirfg16qaVXn10HcwdZ37cQhJmIor-cjKn-HL2lUujluxzYcpw6gtGR816rY0zGGMAv6iCQjJOUeqCyYdxTtWZMfDDrAngwxO5QgF-S_vL3yWL64x0zdXnzqRB7kan"},
                    {"name": "Lemon", "cals": "10 cal, +$0.50", "img": "https://www.gstatic.com/labs-code/stitch/stitch-placeholder-300x300.svg"}
                ]
            },
            {
                "title": "Wellness Boosts", "subtitle": "Select up to 2", "is_vertical": True,
                "items": [
                    {"name": "Wheatgrass Shot", "cals": "15 cal, +$2.50", "img": "https://www.gstatic.com/labs-code/stitch/stitch-placeholder-300x300.svg"},
                    {"name": "Activated Charcoal", "cals": "0 cal, +$1.50", "img": "https://www.gstatic.com/labs-code/stitch/stitch-placeholder-300x300.svg"},
                    {"name": "Aloe Vera", "cals": "15 cal, +$2.00", "img": "https://www.gstatic.com/labs-code/stitch/stitch-placeholder-300x300.svg"}
                ]
            }
        ]
    }
]

for p in pages:
    tabs_html = get_tabs(p['active_tab'])
    
    steps_html = ""
    for idx, step in enumerate(p['steps']):
        steps_html += build_step(idx + 1, step['title'], step['subtitle'], step['items'], step['is_vertical'])
        
    final_html = template.replace("{PAGE_TITLE}", p['title']) \
                         .replace("{HERO_TITLE}", p['hero_title']) \
                         .replace("{HERO_DESC}", p['hero_desc']) \
                         .replace("{BASE_PRICE}", p['base_price']) \
                         .replace("{TABS}", tabs_html) \
                         .replace("{STEPS_HTML}", steps_html)
                         
    with open(p['file'], 'w') as f:
        f.write(final_html)

print("Generated ALL pages including Salad successfully!")
