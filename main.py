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

st.markdown("""
<style>
    /* General App Styling */
    .stApp, .stApp * {
        color: #262730 !important;
    }
    .stApp {
        background: linear-gradient(to right, #e3f2fd, #f0f4f8) !important;
        font-family: 'Segoe UI', sans-serif !important;
        padding: 1rem !important;
    }

    /* Headings */
    h1, h2, h3, .stSubheader, .stHeader {
        color: #0d47a1 !important;
        font-weight: bold !important;
    }

    .main-title {
        color: #0d47a1 !important;
        text-align: center !important;
        font-weight: bold !important;
        margin-bottom: 2rem !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] button {
        color: #262730 !important;
        font-weight: 600 !important;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #0d47a1 !important;
        border-bottom: 2px solid #0d47a1 !important;
    }

    /* Labels */
    label {
        color: #262730 !important;
        font-weight: 600 !important;
    }

    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input,
    .stSelectbox > div > div {
        color: #262730 !important;
        background-color: #ffffff !important;
        border: 2px solid #90caf9 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-size: 1rem !important;
    }

    /* Number Input Buttons */
    .stNumberInput button {
        background-color: #2196f3 !important;
        color: #000000 !important;
        border: none !important;
        min-width: 40px !important;
        min-height: 40px !important;
        cursor: pointer !important;
        transition: background-color 0.3s ease !important;
    }
    .stNumberInput button:hover {
        background-color: #1565c0 !important;
    }
    .stNumberInput > div > div {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 2px solid #90caf9 !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Selectbox (Dropdown) Styling */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        color: #262730 !important;
    }

    /* Selected value styling */
    .stSelectbox div[data-baseweb="select"] div[role="button"] {
        color: #262730 !important;
        background-color: #ffffff !important;
        font-size: 1rem !important;
        border: none !important;
        padding: 10px !important;
    }

    /* Remove text cursor from selectbox */
    .stSelectbox div[data-baseweb="select"] input {
        display: none !important;
    }

    /* Dropdown arrow */
    .stSelectbox div[data-baseweb="select"] svg {
        color: #262730 !important;
    }

    /* Dropdown menu items */
    .stSelectbox div[role="listbox"] div[role="option"] {
        color: #262730 !important;
        background-color: #ffffff !important;
        padding: 10px !important;
    }

    .stSelectbox div[role="listbox"] div[role="option"]:hover {
        background-color: #e3f2fd !important;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #2196f3 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: background-color 0.3s ease !important;
        width: 100% !important; /* Full-width buttons for mobile */
        margin-top: 10px !important;
    }
    .stButton > button:hover {
        background-color: #1976d2 !important;
    }

    /* Dark mode override */
    @media (prefers-color-scheme: dark) {
        .stApp, .stSelectbox, .stSelectbox * {
            background-color: #ffffff !important;
            color: #262730 !important;
        }
    }

    /* Mobile Responsive Styling */
    @media only screen and (max-width: 600px) {
        .stApp {
            padding: 0.5rem !important;
        }
        .stTextInput, .stNumberInput, .stDateInput, .stSelectbox, .stButton {
            width: 100% !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
        }
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
    price = st.number_input("Price", min_value=0.01, format="%.2f")
    quantity = st.number_input("Quantity", min_value=1, step=1, format="%d")  # integer quantity, min 1

    # Specific inputs per product type
    if ptype == "Electronics":
        brand = st.text_input("Brand").strip()
        warranty = st.number_input("Warranty (Years)", min_value=0, step=1)

    elif ptype == "Grocery":
        expiry_date = st.date_input("Expiry Date")

    elif ptype == "Clothing":
        size = st.text_input("Size (e.g. M, L, XL)").strip()
        material = st.text_input("Material").strip()

    if st.button(f"Add {ptype}"):
        # Basic validation
        if not pid:
            st.error("Product ID cannot be empty.")
        elif not name:
            st.error("Product Name cannot be empty.")
        elif price <= 0:
            st.error("Price must be greater than 0.")
        elif quantity <= 0:
            st.error("Quantity must be greater than 0.")
        else:
            try:
                if ptype == "Electronics":
                    if not brand:
                        st.error("Brand cannot be empty.")
                    else:
                        product = Electronics(pid, name, price, quantity, brand, warranty)
                        inv.add_product(product)
                        st.success(f"Electronics product '{name}' added successfully!")

                elif ptype == "Grocery":
                    # Format expiry_date to string
                    expiry_str = expiry_date.strftime("%Y-%m-%d")
                    product = Grocery(pid, name, price, quantity, expiry_str)
                    inv.add_product(product)
                    st.success(f"Grocery product '{name}' added successfully!")

                elif ptype == "Clothing":
                    if not size or not material:
                        st.error("Size and Material cannot be empty.")
                    else:
                        product = Clothing(pid, name, price, quantity, size, material)
                        inv.add_product(product)
                        st.success(f"Clothing product '{name}' added successfully!")

            except Exception as e:
                st.error(f"Error adding product: {e}")

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
