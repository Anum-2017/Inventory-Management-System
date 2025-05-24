import streamlit as st 
from abc import ABC, abstractmethod
import json
from datetime import datetime

# ----------------------- Product Base Class -----------------------
class Product(ABC):
    def __init__(self, product_id, name, price, quantity_in_stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock

    @abstractmethod
    def __str__(self):
        pass

    def restock(self, amount):
        if amount < 1:
            raise ValueError("Restock amount must be at least 1")
        self._quantity_in_stock += amount

    def sell(self, quantity):
        if quantity < 1:
            raise ValueError("Sell quantity must be at least 1")
        if quantity > self._quantity_in_stock:
            raise Exception("Not enough stock to sell")
        self._quantity_in_stock -= quantity

    def get_total_value(self):
        return self._price * self._quantity_in_stock

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "quantity_in_stock": self._quantity_in_stock,
        }

# ----------------------- Subclasses -----------------------
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, brand, warranty_years):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.brand = brand
        self.warranty_years = warranty_years

    def __str__(self):
        return f"🔌 Electronics: {self._name}, Brand: {self.brand}, Warranty: {self.warranty_years} years, Stock: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"brand": self.brand, "warranty_years": self.warranty_years})
        return data

class Grocery(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, expiry_date):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.expiry_date = expiry_date

    def is_expired(self):
        return datetime.strptime(self.expiry_date, "%Y-%m-%d") < datetime.today()

    def __str__(self):
        return f"🍎 Grocery: {self._name}, Expiry: {self.expiry_date}, Stock: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"expiry_date": self.expiry_date})
        return data

class Clothing(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, size, material):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.size = size
        self.material = material

    def __str__(self):
        return f"👕 Clothing: {self._name}, Size: {self.size}, Material: {self.material}, Stock: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"size": self.size, "material": self.material})
        return data

# ----------------------- Inventory Class -----------------------
class Inventory:
    def __init__(self):
        self._products = {}

    def add_product(self, product):
        if not product._product_id:
            raise ValueError("Product ID cannot be empty")
        if product._product_id in self._products:
            raise Exception("Duplicate product ID")
        self._products[product._product_id] = product

    def remove_product(self, product_id):
        if product_id in self._products:
            del self._products[product_id]
        else:
            raise Exception("Product ID not found")

    def list_all_products(self):
        return [str(p) for p in self._products.values()]

    def search_by_name(self, name):
        return [p for p in self._products.values() if name.lower() in p._name.lower()]

    def search_by_type(self, product_type):
        return [p for p in self._products.values() if p.__class__.__name__.lower() == product_type.lower()]

    def sell_product(self, product_id, quantity):
        if product_id not in self._products:
            raise Exception("Product ID not found")
        self._products[product_id].sell(quantity)

    def restock_product(self, product_id, quantity):
        if product_id not in self._products:
            raise Exception("Product ID not found")
        self._products[product_id].restock(quantity)

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())

    def remove_expired_products(self):
        expired = [pid for pid, p in self._products.items() if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired:
            del self._products[pid]

    def save_to_file(self, filename):
        data = [p.to_dict() for p in self._products.values()]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        self._products.clear() 
        for item in data:
            ptype = item["type"]
            if ptype == "Electronics":
                p = Electronics(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["brand"], item["warranty_years"])
            elif ptype == "Grocery":
                p = Grocery(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["expiry_date"])
            elif ptype == "Clothing":
                p = Clothing(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["size"], item["material"])
            else:
                continue
            self._products[p._product_id] = p

# ----------------------- Streamlit UI -----------------------
st.set_page_config(page_title="🌟 Inventory System", layout="centered")

# Enhanced CSS for Mobile Compatibility
st.markdown("""
<style>
    /* Force dark text on all devices */
    .stApp, .stApp * {
        color: #262730 !important;
    }

    /* Background */
    .stApp {
        background: linear-gradient(to right, #e3f2fd, #f0f4f8) !important;
        font-family: 'Segoe UI', sans-serif !important;
    }

    /* Headers - Force dark color */
    h1, h2, h3, .stSubheader, .stHeader {
        color: #0d47a1 !important;
        font-weight: bold !important;
    }

    /* Main title */
    .main-title {
        color: #0d47a1 !important;
        text-align: center !important;
        font-weight: bold !important;
        margin-bottom: 2rem !important;
    }

    /* Tab labels */
    .stTabs [data-baseweb="tab-list"] button {
        color: #262730 !important;
        font-weight: 600 !important;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #0d47a1 !important;
    }

    /* Form labels */
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
        color: #262730 !important;
        font-weight: 600 !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input,
    .stSelectbox > div > div {
        
        background-color: #ffffff !important;
        border: 2px solid #90caf9 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    /* Number input spinner buttons */
    .stNumberInput button {
        background-color: #2196f3 !important;
        color: #ffffff !important;
    }

    /* Fix number input container */
    .stNumberInput > div > div {
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Select box options */
    .stSelectbox div[data-baseweb="select"] > div {
        color: #262730 !important;
        background-color: #ffffff !important;
    }

    /* Buttons - Enhanced for Mobile */
    .stButton > button {
        background-color: #2196f3 !important;
        color: #ffffff !important;
        border: 2px solid #1976d2 !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: all 0.3s ease-in-out !important;
        cursor: pointer !important;
        min-height: 48px !important;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stButton > button:hover {
        background-color: #1565c0 !important;
        color: #ffffff !important;
        border-color: #0d47a1 !important;
        transform: scale(1.03) !important;
        box-shadow: 0 4px 12px rgba(13, 71, 161, 0.4) !important;
    }

    .stButton > button:active {
        background-color: #0d47a1 !important;
        color: #ffffff !important;
        transform: scale(0.98) !important;
    }

    .stButton > button:focus {
        outline: 3px solid #90caf9 !important;
        outline-offset: 2px !important;
    }

    /* Success/Error/Info messages */
    .stSuccess, .stError, .stInfo, .stWarning {
        color: #262730 !important;
    }

    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #1976d2 !important;
        color: white !important;
        text-align: center !important;
        padding: 10px !important;
        font-weight: bold !important;
        border-top: 2px solid #0d47a1 !important;
        z-index: 1000;
    }

    /* Mobile-specific adjustments */
    @media only screen and (max-width: 768px) {
        .stApp {
            color: #262730 !important;
            background: linear-gradient(to bottom, #e3f2fd, #f0f4f8) !important;
        }
        
        h1, h2, h3 {
            color: #0d47a1 !important;
            font-size: 1.5rem !important;
        }
        
        .stSelectbox, .stTextInput, .stNumberInput, .stDateInput {
            color: #262730 !important;
        }
        
        .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
            color: #262730 !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        
        /* Enhanced Mobile Buttons */
        .stButton > button {
            width: 100% !important;
            margin: 8px 0 !important;
            background-color: #2196f3 !important;
            color: #ffffff !important;
            border: 3px solid #1976d2 !important;
            border-radius: 15px !important;
            padding: 15px 20px !important;
            font-weight: bold !important;
            font-size: 18px !important;
            min-height: 55px !important;
            box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4) !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            appearance: none !important;
        }
        
        .stButton > button:hover, .stButton > button:active, .stButton > button:focus {
            background-color: #1565c0 !important;
            color: #ffffff !important;
            border-color: #0d47a1 !important;
            box-shadow: 0 6px 16px rgba(13, 71, 161, 0.5) !important;
        }
        
        /* Ensure button text is always visible */
        .stButton > button span {
            color: #ffffff !important;
            font-weight: bold !important;
        }

        /* Mobile number input fixes */
        .stNumberInput button {
            background-color: #2196f3 !important;
            color: #ffffff !important;
            border: 2px solid #1976d2 !important;
            min-width: 40px !important;
            min-height: 40px !important;
        }

        .stNumberInput button:hover {
            background-color: #1565c0 !important;
        }

        .stNumberInput > div > div {
            border-radius: 10px !important;
            overflow: hidden !important;
            border: 2px solid #90caf9 !important;
        }

        /* Input field mobile adjustments */
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stDateInput input {
            font-size: 16px !important;
            padding: 12px !important;
            min-height: 48px !important;
        }
        
        .footer {
            position: relative !important;
            margin-top: 2rem !important;
        }
    }

    /* Hide default Streamlit footer */
    footer {
        visibility: hidden !important;
    }

    /* Ensure readability on all backgrounds */
    .stMarkdown, .stText, p, div {
        color: #262730 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 class="main-title">⚙️ Inventory Management System</h1>
""", unsafe_allow_html=True)

# Session State Setup
if 'inventory' not in st.session_state:
    st.session_state.inventory = Inventory()
    try:
        st.session_state.inventory.load_from_file("inventory.json")
    except FileNotFoundError:
        pass
    except Exception as e:
        st.error(f"Error loading inventory: {e}")

inv = st.session_state.inventory

# Tabs as the menu
tabs = st.tabs(["Add Product", "View Inventory", "Sell Product", "Restock Product", "Save", "Load", "Remove Expired"])

with tabs[0]:  # Add Product
    st.header("➕ Add New Product")
    ptype = st.selectbox("Select Product Type", ["Electronics", "Grocery", "Clothing"])
    pid = st.text_input("Product ID").strip()
    name = st.text_input("Product Name").strip()
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    quantity = st.number_input("Quantity", min_value=0, step=1)

    if ptype == "Electronics":
        brand = st.text_input("Brand").strip()
        warranty = st.number_input("Warranty (Years)", min_value=0, step=1)
        if st.button("Add Electronics"):
            if not all([pid, name, brand]):
                st.error("Please fill in all fields.")
            elif price <= 0 or quantity <= 0:
                st.error("Price and Quantity must be greater than 0.")
            else:
                try:
                    e = Electronics(pid, name, price, quantity, brand, warranty)
                    inv.add_product(e)
                    st.success(f"Electronics product '{name}' added successfully!")
                except Exception as e:
                    st.error(str(e))

    elif ptype == "Grocery":
        expiry_date = st.date_input("Expiry Date").strftime("%Y-%m-%d")
        if st.button("Add Grocery"):
            if not all([pid, name, expiry_date]):
                st.error("Please fill in all fields.")
            elif price <= 0 or quantity <= 0:
                st.error("Price and Quantity must be greater than 0.")
            else:
                try:
                    g = Grocery(pid, name, price, quantity, expiry_date)
                    inv.add_product(g)
                    st.success(f"Grocery product '{name}' added successfully!")
                except Exception as e:
                    st.error(str(e))

    elif ptype == "Clothing":
        size = st.text_input("Size (e.g. M, L, XL)").strip()
        material = st.text_input("Material").strip()
        if st.button("Add Clothing"):
            if not all([pid, name, size, material]):
                st.error("Please fill in all fields.")
            elif price <= 0 or quantity <= 0:
                st.error("Price and Quantity must be greater than 0.")
            else:
                try:
                    c = Clothing(pid, name, price, quantity, size, material)
                    inv.add_product(c)
                    st.success(f"Clothing product '{name}' added successfully!")
                except Exception as e:
                    st.error(str(e))

with tabs[1]:  # View Inventory
    st.header("📋 Current Inventory")
    products = inv.list_all_products()
    if products:
        for p in products:
            st.write("- ", p)
    else:
        st.info("No products in inventory.")
    st.info(f"💰 **Total Inventory Value:** ${inv.total_inventory_value():,.2f}")

with tabs[2]:  # Sell Product
    st.header("🛒 Sell Product")
    sell_pid = st.text_input("Product ID to Sell").strip()
    sell_qty = st.number_input("Quantity to Sell", min_value=1, step=1)
    if st.button("Sell"):
        if not sell_pid:
            st.error("Enter a Product ID.")
        else:
            try:
                inv.sell_product(sell_pid, sell_qty)
                st.success(f"✅ Sold {sell_qty} unit(s) of product ID {sell_pid}.")
            except Exception as e:
                st.error(str(e))

with tabs[3]:  # Restock Product
    st.header("🔄 Restock Product")
    restock_pid = st.text_input("Product ID to Restock").strip()
    restock_qty = st.number_input("Quantity to Restock", min_value=1, step=1)
    if st.button("Restock"):
        if not restock_pid:
            st.error("Enter a Product ID.")
        else:
            try:
                inv.restock_product(restock_pid, restock_qty)
                st.success(f"✅ Restocked {restock_qty} unit(s) of product ID {restock_pid}.")
            except Exception as e:
                st.error(str(e))

with tabs[4]:  # Save
    st.header("💾 Save Inventory to File")
    filename_save = st.text_input("Filename to save (e.g., inventory.json)", value="inventory.json")
    if st.button("Save"):
        try:
            inv.save_to_file(filename_save)
            st.success(f"Inventory saved to {filename_save}")
        except Exception as e:
            st.error(str(e))

with tabs[5]:  # Load
    st.header("📂 Load Inventory from File")
    filename_load = st.text_input("Filename to load (e.g., inventory.json)", value="inventory.json")
    if st.button("Load"):
        try:
            inv.load_from_file(filename_load)
            st.success(f"Inventory loaded from {filename_load}")
        except FileNotFoundError:
            st.error(f"File '{filename_load}' not found.")
        except Exception as e:
            st.error(str(e))

with tabs[6]:  # Remove Expired Products
    st.header("🗑️ Remove Expired Grocery Products")
    if st.button("Remove Expired"):
        try:
            inv.remove_expired_products()
            st.success("Expired grocery products removed successfully.")
        except Exception as e:
            st.error(str(e))

# Footer
st.markdown("""
<div class="footer">
    Inventory Management System &nbsp;|&nbsp; Made with ❤️ by Anum Kamal
</div>
""", unsafe_allow_html=True)
