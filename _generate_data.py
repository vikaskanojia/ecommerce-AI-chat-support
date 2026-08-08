import pandas as pd
import random
import json

random.seed(42)

categories = {
    "Electronics": {"brands": ["Voltix", "Nexara", "Pulseon", "Kryon", "Aerowave"],
        "types": [
            ("Wireless Earbuds", "In-ear Bluetooth earbuds with active noise cancellation and {hrs}h battery life."),
            ("Bluetooth Speaker", "Portable speaker with {hrs}h playtime and IPX7 waterproof rating."),
            ("Smartwatch", "Fitness smartwatch with heart-rate tracking, GPS, and {hrs}h battery life."),
            ("Laptop Stand", "Adjustable aluminum laptop stand, compatible with 11-17 inch laptops."),
            ("USB-C Hub", "7-in-1 USB-C hub with HDMI, SD card reader, and 100W power delivery."),
            ("Mechanical Keyboard", "Hot-swappable mechanical keyboard with RGB backlighting."),
            ("Wireless Charger", "15W fast wireless charging pad, compatible with Qi-enabled devices."),
            ("Webcam", "1080p HD webcam with autofocus and built-in noise-canceling mic."),
            ("Power Bank", "{cap}mAh portable power bank with dual USB-C fast charging."),
            ("Noise Cancelling Headphones", "Over-ear headphones with active noise cancellation and {hrs}h battery life.")],
        "price_range": (14.99, 249.99)},
    "Home & Kitchen": {"brands": ["Homely", "Kitchura", "Nestwell", "Brewpoint", "Fresca"],
        "types": [
            ("Stainless Steel Knife Set", "6-piece kitchen knife set with ergonomic handles and storage block."),
            ("Air Fryer", "{cap}L digital air fryer with 8 preset cooking programs."),
            ("Coffee Maker", "12-cup programmable drip coffee maker with reusable filter."),
            ("Non-Stick Frying Pan", "10-inch non-stick frying pan, oven-safe up to 450F."),
            ("Electric Kettle", "1.7L stainless steel electric kettle with auto shut-off."),
            ("Food Storage Containers", "Set of 10 airtight glass food storage containers with lids."),
            ("Cutting Board Set", "3-piece bamboo cutting board set with juice grooves."),
            ("Stand Mixer", "{cap}L stand mixer with 6 speed settings and dough hook attachment."),
            ("Ceramic Dinnerware Set", "16-piece ceramic dinnerware set, microwave and dishwasher safe."),
            ("Throw Blanket", "Soft fleece throw blanket, {size} inches, machine washable.")],
        "price_range": (9.99, 199.99)},
    "Fashion": {"brands": ["Urbane", "Driftwood", "Solstice", "Maren & Co", "Ridgeline"],
        "types": [
            ("Cotton T-Shirt", "Classic fit crewneck t-shirt, 100% combed cotton."),
            ("Denim Jacket", "Classic washed denim jacket with button front closure."),
            ("Running Shoes", "Lightweight running shoes with breathable mesh upper."),
            ("Leather Wallet", "Slim bifold leather wallet with RFID-blocking lining."),
            ("Wool Beanie", "Ribbed knit beanie, one size fits most, available in multiple colors."),
            ("Canvas Backpack", "{cap}L canvas backpack with padded laptop sleeve."),
            ("Polarized Sunglasses", "UV400 polarized sunglasses with lightweight aluminum frame."),
            ("Yoga Leggings", "High-waisted yoga leggings with four-way stretch fabric."),
            ("Chino Pants", "Slim fit chino pants, wrinkle-resistant stretch cotton blend."),
            ("Wool Scarf", "Soft wool-blend scarf, {size} inches, available in multiple colors.")],
        "price_range": (7.99, 129.99)},
    "Sports & Outdoors": {"brands": ["Trailhead", "Summit Gear", "Rapidflow", "Ironloop", "Basecamp"],
        "types": [
            ("Yoga Mat", "6mm non-slip yoga mat with carrying strap."),
            ("Adjustable Dumbbells", "Adjustable dumbbell set, {cap}lb per dumbbell, space-saving design."),
            ("Camping Tent", "{cap}-person waterproof camping tent with easy 10-minute setup."),
            ("Insulated Water Bottle", "32oz vacuum-insulated stainless steel water bottle, keeps drinks cold 24h."),
            ("Resistance Bands Set", "5-piece resistance band set with varying resistance levels."),
            ("Hiking Backpack", "{cap}L hiking backpack with hydration bladder compartment."),
            ("Foam Roller", "High-density foam roller for muscle recovery and deep tissue massage."),
            ("Cycling Helmet", "Lightweight cycling helmet with adjustable fit dial and 18 vents."),
            ("Jump Rope", "Speed jump rope with ball-bearing swivels and adjustable length."),
            ("Sleeping Bag", "3-season sleeping bag rated to {temp}F, compression sack included.")],
        "price_range": (11.99, 179.99)},
    "Beauty & Personal Care": {"brands": ["Lumina", "Pure & Bloom", "Velveska", "Aurelle", "Cascade Beauty"],
        "types": [
            ("Vitamin C Serum", "Brightening vitamin C serum with hyaluronic acid, {size}ml."),
            ("Electric Toothbrush", "Rechargeable electric toothbrush with 5 cleaning modes."),
            ("Hair Dryer", "Ionic hair dryer with 3 heat settings and cool shot button."),
            ("Facial Cleanser", "Gentle foaming facial cleanser for all skin types, {size}ml."),
            ("Moisturizing Body Lotion", "24h hydrating body lotion with shea butter, {size}ml."),
            ("Makeup Brush Set", "12-piece makeup brush set with synthetic bristles and travel case."),
            ("Beard Trimmer", "Cordless beard trimmer with 20 length settings and USB charging."),
            ("Sunscreen SPF 50", "Broad-spectrum SPF 50 sunscreen lotion, lightweight and non-greasy, {size}ml."),
            ("Hair Straightener", "Ceramic flat iron hair straightener with adjustable temperature."),
            ("Essential Oil Diffuser", "Ultrasonic essential oil diffuser with 7 LED light colors.")],
        "price_range": (6.99, 89.99)},
    "Toys & Games": {"brands": ["Playforge", "Wonderkind", "Brickwork", "Funloop", "Tinkerbots"],
        "types": [
            ("Building Block Set", "{cap}-piece building block set, compatible with major brick brands."),
            ("Remote Control Car", "Off-road remote control car with rechargeable battery, {mph}mph top speed."),
            ("Board Game", "Strategy board game for 2-6 players, ages 10 and up."),
            ("Puzzle 1000 Piece", "1000-piece jigsaw puzzle with premium matte finish."),
            ("Plush Toy", "Soft plush toy, {size} inches, machine washable."),
            ("Art Supply Kit", "50-piece art supply kit with markers, crayons, and colored pencils."),
            ("Drone with Camera", "Mini drone with HD camera and one-touch takeoff/landing."),
            ("Card Game", "Fast-paced card game for 2-8 players, 15 minute playtime."),
            ("Building Robot Kit", "STEM robot building kit with programmable motors."),
            ("Kids Tablet", "{size}-inch kids tablet with parental controls and protective case.")],
        "price_range": (5.99, 149.99)},
    "Grocery": {"brands": ["Harvestly", "Golden Fields", "Rootside", "Pantry Co", "Wholegrain Market"],
        "types": [
            ("Organic Coffee Beans", "{size}oz whole bean organic coffee, medium roast."),
            ("Extra Virgin Olive Oil", "{size}ml cold-pressed extra virgin olive oil."),
            ("Almond Butter", "{size}oz creamy almond butter, no added sugar."),
            ("Green Tea Bags", "Box of 100 organic green tea bags."),
            ("Protein Powder", "{size}lb whey protein powder, chocolate flavor, 24g protein per serving."),
            ("Granola Mix", "{size}oz honey oat granola with mixed nuts and dried fruit."),
            ("Raw Honey", "{size}oz raw unfiltered wildflower honey."),
            ("Quinoa", "{size}lb organic tri-color quinoa, gluten-free."),
            ("Dark Chocolate Bars", "Pack of 6 70% cacao dark chocolate bars."),
            ("Sparkling Water", "Pack of 12 naturally flavored sparkling water cans.")],
        "price_range": (3.99, 49.99)},
    "Books": {"brands": ["Northgate Press", "Lantern & Ink", "Ferngrove Books", "Cobblestone", "Meridian House"],
        "types": [
            ("Mystery Novel", "Gripping mystery novel, paperback, {pages} pages."),
            ("Cookbook", "Illustrated cookbook with {recipes}+ recipes for home cooks."),
            ("Self-Help Guide", "Practical self-help guide on building better daily habits."),
            ("Science Fiction Novel", "Award-winning science fiction novel, paperback, {pages} pages."),
            ("Children's Picture Book", "Illustrated picture book for ages 3-7, hardcover."),
            ("Business Strategy Book", "Bestselling book on business strategy and leadership."),
            ("Poetry Collection", "Collection of contemporary poetry, hardcover, {pages} pages."),
            ("History Book", "Narrative history book covering major 20th century events."),
            ("Journal Notebook", "Dot-grid journal notebook, {pages} pages, hardcover."),
            ("Fantasy Novel", "Epic fantasy novel, first in a trilogy, paperback, {pages} pages.")],
        "price_range": (6.99, 34.99)},
}

colors = ["Black", "White", "Gray", "Navy", "Red", "Green", "Beige", "Blue", "Pink", "Silver"]
rows, product_id, all_combos = [], 1001, []
for cat, info in categories.items():
    for brand in info["brands"]:
        for type_name, desc_template in info["types"]:
            all_combos.append((cat, brand, type_name, desc_template, info["price_range"]))
random.shuffle(all_combos)

for cat, brand, type_name, desc_template, price_range in all_combos[:100]:
    desc = desc_template.format(
        hrs=random.choice([6, 8, 10, 12, 20, 24, 30]),
        cap=random.choice([4, 5, 6, 8, 10, 20, 30, 40, 50, 65, 500, 1000, 10000, 20000]),
        size=random.choice([30, 50, 60, 100, 150, 200, 250, 8, 16, 32]),
        mph=random.choice([15, 20, 25, 30]), temp=random.choice([20, 30, 40]),
        pages=random.choice([224, 288, 320, 352, 416]), recipes=random.choice([75, 100, 125, 150]))
    price = round(random.uniform(*price_range), 2)
    rows.append({"product_id": product_id, "product_name": f"{brand} {type_name}", "category": cat,
        "brand": brand, "price_usd": price, "rating": round(random.uniform(3.2, 5.0), 1),
        "num_reviews": random.randint(8, 4200), "stock_quantity": random.randint(0, 500),
        "color": random.choice(colors), "description": desc})
    product_id += 1

products_df = pd.DataFrame(rows).sort_values("category").reset_index(drop=True)
products_df.to_csv("data/ecommerce_products.csv", index=False)
print(f"Wrote data/ecommerce_products.csv: {len(products_df)} products")

FAQ_DOCS = [
    {"id": "faq_shipping_time", "question": "How long does shipping take?",
     "answer": "Standard shipping takes 4-6 business days. Express shipping takes 1-2 business days and is available at checkout for an extra fee."},
    {"id": "faq_shipping_intl", "question": "Do you ship internationally?",
     "answer": "Yes, we ship to over 30 countries. International orders typically take 7-14 business days and may be subject to customs fees charged by your country."},
    {"id": "faq_return_policy", "question": "What is your return policy?",
     "answer": "Items can be returned within 30 days of delivery if unused and in original packaging. Some categories (e.g. opened beauty products) are final sale."},
    {"id": "faq_return_start", "question": "How do I start a return?",
     "answer": "Go to Order History, select the item, and click 'Start a Return'. You'll receive a prepaid shipping label by email within a few minutes."},
    {"id": "faq_refund_time", "question": "How long do refunds take?",
     "answer": "Refunds are issued to your original payment method within 5-7 business days after we receive the returned item."},
    {"id": "faq_payment_methods", "question": "What payment methods do you accept?",
     "answer": "We accept all major credit and debit cards, PayPal, and store gift cards. We do not currently accept cryptocurrency."},
    {"id": "faq_order_tracking", "question": "How do I track my order?",
     "answer": "A tracking link is emailed once your order ships. You can also find it under Order History on your account page."},
    {"id": "faq_order_cancel", "question": "Can I cancel an order after placing it?",
     "answer": "Orders can be cancelled within 1 hour of placing them, before they enter processing. After that, please use the return process once it arrives."},
    {"id": "faq_warranty", "question": "Do products come with a warranty?",
     "answer": "Electronics carry a 1-year manufacturer warranty against defects. Other categories vary by brand -- check the individual product description for details."},
    {"id": "faq_coupon", "question": "How do I apply a coupon or promo code?",
     "answer": "Enter your code in the 'Promo Code' field at checkout before payment. Only one code can be applied per order."},
    {"id": "faq_password_reset", "question": "How do I reset my account password?",
     "answer": "Click 'Forgot password' on the login page and enter your email. A reset link will arrive within a few minutes -- check your spam folder if it doesn't."},
    {"id": "faq_privacy", "question": "How is my personal data used?",
     "answer": "We use your data only to process orders, provide support, and (with consent) send marketing emails. We never sell personal data to third parties."},
    {"id": "faq_price_match", "question": "Do you price match other retailers?",
     "answer": "We price match identical in-stock items from major retailers within 7 days of purchase. Contact support with a link to the lower price to request a match."},
    {"id": "faq_gift_cards", "question": "Do you sell gift cards?",
     "answer": "Yes, digital gift cards from $10 to $200 are available and delivered by email within minutes of purchase. Gift cards do not expire."},
    {"id": "faq_loyalty", "question": "Is there a rewards or loyalty program?",
     "answer": "Yes -- you earn 1 point per dollar spent, redeemable for discounts once you reach 500 points. Enrollment is free from your account page."},
    {"id": "faq_contact_support", "question": "How do I contact customer support?",
     "answer": "Live chat is available 9am-9pm ET on our website, or email support@example-store.com. Typical response time is under 4 hours."},
]

with open("data/faq.json", "w") as f:
    json.dump(FAQ_DOCS, f, indent=2)
print(f"Wrote data/faq.json: {len(FAQ_DOCS)} entries")
