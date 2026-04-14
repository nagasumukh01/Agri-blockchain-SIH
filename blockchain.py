import hashlib
import json
import os
from datetime import datetime
from uuid import uuid4

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_data = []
        self.product_tracking = {}  # Track products through supply chain
        self.data_file = "blockchain_data.json"
        self.load_data()  # Load existing data if available
        
        if not self.chain:  # Only create genesis block if chain is empty
            self.new_block(previous_hash="1")  # Genesis block
            
    def load_data(self):
        """Load blockchain data from file if it exists"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.chain = data.get('chain', [])
                    self.product_tracking = data.get('product_tracking', {})
        except Exception as e:
            print(f"Error loading blockchain data: {e}")
            
    def save_data(self):
        """Save blockchain data to file"""
        try:
            data = {
                'chain': self.chain,
                'product_tracking': self.product_tracking
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving blockchain data: {e}")

    def new_block(self, previous_hash=None):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # readable date
            "transactions": self.current_data,  # renamed from 'data' → clearer
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        block["hash"] = self.hash(block)
        self.current_data = []  # reset current data
        self.chain.append(block)
        self.save_data()  # Save after adding new block
        return block

    def new_data(self, role, details, price_info=None, prev_product_id=None):
        """Add a new transaction to the list of current transactions"""
        # Generate a unique product ID for farmer's initial entry
        if role == "Farmer":
            product_id = str(uuid4())
        else:
            product_id = prev_product_id
            
        if not product_id:
            raise ValueError("Product ID is required for non-farmer roles")
            
        # Calculate estimated delivery time based on role and location
        est_delivery = self._calculate_delivery_time(role, details.get("location", ""))
        
        transaction = {
            "product_id": product_id,
            "role": role,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_delivery": est_delivery
        }
        
        if price_info:
            transaction["price_info"] = price_info
            
        # Track product through supply chain
        if product_id not in self.product_tracking:
            self.product_tracking[product_id] = []
        self.product_tracking[product_id].append({
            "role": role,
            "timestamp": transaction["timestamp"],
            "estimated_delivery": est_delivery
        })
            
        self.current_data.append(transaction)
        self.save_data()  # Save after adding new transaction
        return self.last_block["index"] + 1
        
    def _calculate_delivery_time(self, role, location):
        """Calculate estimated delivery time based on role and location"""
        base_times = {
            "Farmer": {
                "urban": 1,      # 1 day to local distribution
                "suburban": 2,   # 2 days to local distribution
                "rural": 3       # 3 days to local distribution
            },
            "Distributor": {
                "urban": 1,      # 1 day to retailers
                "suburban": 2,    # 2 days to retailers
                "rural": 3       # 3 days to retailers
            },
            "Retailer": {
                "urban": 0.5,    # 12 hours to consumer
                "suburban": 1,   # 1 day to consumer
                "rural": 2       # 2 days to consumer
            }
        }
        
        # Get base delivery time for role and location
        role_times = base_times.get(role, {})
        delivery_time = role_times.get(location.lower(), 1)  # Default 1 day if not specified
        
        return {
            "days": delivery_time,
            "hours": delivery_time * 24
        }
        
    def get_product_journey(self, product_id):
        """Get the complete journey of a product through the supply chain"""
        return self.product_tracking.get(product_id, [])

    @staticmethod
    def hash(block):
        """Generate SHA-256 hash of a block"""
        # Convert dict to JSON string (ignore hash key itself to avoid recursion)
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

