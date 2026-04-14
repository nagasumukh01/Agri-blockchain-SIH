from flask import Flask, render_template, request, redirect, url_for, jsonify
import qrcode, os
from blockchain import Blockchain
from price_model import PriceModel
from weather import WeatherService
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
blockchain = Blockchain()
price_model = PriceModel()

# Function to get base URL for QR codes
def get_base_url():
    """Get the base URL for QR codes"""
    try:
        # Try to get the base URL from the current request
        from flask import request
        if request and hasattr(request, 'host'):
            scheme = request.scheme or 'http'
            host = request.host
            if host and 'localhost' not in host and '127.0.0.1' not in host:
                return f"{scheme}://{host}"
    except:
        pass

    # Fallback: try to detect the current network IP
    import socket
    try:
        # Get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to Google DNS
        local_ip = s.getsockname()[0]
        s.close()
        return f"http://{local_ip}:5000"
    except:
        pass

    # Final fallback to localhost
    return "http://127.0.0.1:5000"

# Supply chain stages for tracking
STAGES = ['Farmer', 'Distributor', 'Retailer', 'Consumer']

# ---------------------------
# Home Page
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------------------
# Farmer Page
# ---------------------------
@app.route("/farmer", methods=["GET", "POST"])
def farmer():
    if request.method == "POST":
        crop = request.form["crop"]
        quantity = float(request.form["quantity"])
        quality = request.form.get("quality", "B")
        location = request.form.get("location", "rural")
        city = request.form.get("city", "")
        
        # Calculate price using the price model with weather data
        price_per_kg, pricing_details = price_model.calculate_price(crop, quality, location, quantity, city, 'farmer')
        total_price = price_per_kg * quantity if price_per_kg else 0
        
        details = {
            "crop": crop,
            "quantity": quantity,
            "quality": quality,
            "location": location,
            "city": city
        }
        
        price_info = {
            "price_per_kg": price_per_kg,
            "total_price": total_price,
            "weather_impact": pricing_details.get("weather_data", {}),
            "pricing_factors": price_model.get_price_factors(),
            "calculation_details": pricing_details
        }
        
        # Create new blockchain entry
        block_index = blockchain.new_data("Farmer", details, price_info)
        block = blockchain.new_block()
        
        # Get the product ID for this transaction
        product_id = block["transactions"][-1]["product_id"]
        
        # Generate QR data for dynamic tracking
        qr_data = f"{get_base_url()}/track?id={product_id}"
        
        return render_template("transaction_success.html", 
                             qr_data=qr_data,
                             product_id=product_id,
                             stage="Farmer",
                             details=details,
                             price_info=price_info)
    return render_template("farmer.html")

# ---------------------------
# Distributor Page
# ---------------------------
@app.route("/distributor", methods=["GET", "POST"])
def distributor():
    if request.method == "POST":
        transport = request.form["transport"]
        warehouse = request.form["warehouse"]
        location = request.form.get("location", "urban")
        product_id = request.form["product_id"]
        
        # Get product history from blockchain
        product_history = blockchain.get_product_journey(product_id)
        if not product_history:
            return render_template("distributor.html", error="Product not found. Please check the Product ID.")
            
        # Get the farmer's entry to get crop details
        farmer_entry = None
        for entry in product_history:
            if entry['role'] == 'Farmer':
                farmer_entry = entry
                break
                
        if not farmer_entry or not farmer_entry.get('details') or not farmer_entry.get('price_info'):
            return render_template("distributor.html", error="Invalid farmer data. Please check the Product ID.")
            
        # Get crop details from farmer's entry
        farmer_details = farmer_entry['details']
        crop = farmer_details['crop']
        quality = farmer_details['quality']
        quantity = farmer_details['quantity']
        
        # Calculate new price with distributor markup
        price_per_kg, pricing_details = price_model.calculate_price(
            crop_name=crop,
            quality=quality,
            location=location,
            quantity=quantity,
            stage='distributor',
            prev_price=farmer_entry['price_info']['price_per_kg']
        )
        
        # Calculate total costs and markup
        transport_cost = 2.0 * quantity  # Transport cost per kg
        storage_cost = 1.0 * quantity    # Storage cost per kg
        handling_cost = 0.5 * quantity   # Handling cost per kg
        total_costs = transport_cost + storage_cost + handling_cost
        
        details = {
            "transport_type": transport,
            "warehouse": warehouse,
            "location": location,
            "original_crop": crop,
            "quantity": quantity,
            "quality": quality
        }
        
        price_info = {
            "original_price": farmer_entry['price_info']['price_per_kg'],
            "price_per_kg": price_per_kg,
            "total_price": price_per_kg * quantity,
            "markup_details": pricing_details.get('markup_details', {}),
            "transport_cost": transport_cost,
            "storage_cost": storage_cost,
            "handling_cost": handling_cost,
            "total_costs": total_costs,
            "market_factors": pricing_details.get('market_factors', {}),
            "calculation_details": pricing_details
        }
        
        # Create blockchain entry
        blockchain.new_data("Distributor", details, price_info, prev_product_id=product_id)
        block = blockchain.new_block()
        
        # Generate QR data for dynamic tracking
        qr_data = f"{get_base_url()}/track?id={product_id}"
        
        return render_template("transaction_success.html", 
                             qr_data=qr_data,
                             product_id=product_id,
                             stage="Distributor",
                             details=details,
                             price_info=price_info)
    return render_template("distributor.html")

# ---------------------------
# Retailer Page
# ---------------------------
@app.route("/retailer", methods=["GET", "POST"])
def retailer():
    if request.method == "POST":
        shop = request.form["shop"]
        price = request.form["price"]
        location = request.form.get("location", "urban")
        product_id = request.form["product_id"]
        
        # Get the product's price history
        product_history = blockchain.get_product_journey(product_id)
        if not product_history:
            return render_template("retailer.html", error="Product not found. Please check the Product ID.")
            
        # Get the distributor's entry to get product details
        distributor_entry = None
        for entry in product_history:
            if entry['role'] == 'Distributor':
                distributor_entry = entry
                break
                
        if not distributor_entry:
            return render_template("retailer.html", error="No distributor data found. Product must go through distributor first.")
        
        original_price = distributor_entry['price_info']['price_per_kg']
        product_details = distributor_entry['details']
        
        # Calculate retail markup and costs
        retail_markup = 0.40  # 40% retail markup
        additional_costs = 2.8  # Fixed costs per kg (storage, handling, etc.)
        retail_price = original_price * (1 + retail_markup) + additional_costs
        
        details = {
            "shop_name": shop,
            "location": location,
            "original_crop": product_details['original_crop'],
            "quantity": product_details['quantity'],
            "quality": product_details['quality']
        }
        
        price_info = {
            "original_price": original_price,
            "price_per_kg": retail_price,
            "markup_percentage": retail_markup * 100,
            "additional_costs": additional_costs,
            "total_price": float(price)
        }
        
        # Create blockchain entry
        blockchain.new_data("Retailer", details, price_info, prev_product_id=product_id)
        block = blockchain.new_block()
        
        # Generate QR data for dynamic tracking
        qr_data = f"{get_base_url()}/track?id={product_id}"
        
        return render_template("transaction_success.html", 
                             qr_data=qr_data,
                             product_id=product_id,
                             stage="Retailer",
                             details=details,
                             price_info=price_info)
    return render_template("retailer.html")

# ---------------------------
# Product Tracking Routes
# ---------------------------
@app.route("/track")
def track():
    """Show product tracking page"""
    product_id = request.args.get('id')
    if product_id:
        journey = blockchain.get_product_journey(product_id)
        return render_template("track.html", stages=STAGES, product_id=product_id, journey=journey)
    return render_template("track.html", stages=STAGES)

@app.route("/api/track/<product_id>")
def track_product(product_id):
    """API endpoint for tracking a product's journey"""
    journey = blockchain.get_product_journey(product_id)
    if journey:
        return jsonify({
            "success": True,
            "product_id": product_id,
            "journey": journey,
            "stages": STAGES
        })
    return jsonify({
        "success": False,
        "error": "Product not found"
    })

# ---------------------------
# Blockchain View
# ---------------------------
@app.route("/chain")
def view_chain():
    """View the entire blockchain"""
    chain_data = blockchain.chain
    base_url = get_base_url()
    return render_template("view_chain.html", 
                         chain=chain_data, 
                         base_url=base_url)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")