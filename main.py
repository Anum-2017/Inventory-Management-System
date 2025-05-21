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

# Custom CSS for Stylish UI
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(to right, #e3f2fd, #f0f4f8);
        color: #333;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Titles and headers */
    h1, h2, h3, .stSubheader {
        color: #0d47a1;
    }

    /* Buttons */
    .stButton > button {
        background-color: #2196f3;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        cursor: pointer;
    }

    .stButton > button:hover {
        background-color: #1565c0;
        transform: scale(1.03);
    }

    /* Input boxes */
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input {
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #90caf9;
    }

    /* Footer */
    footer {
        visibility: hidden;
    }

    .footer {
        bottom: 0;
        width: 100%;
        background-color: #1976d2;
        color: white;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-top: 2px solid #0d47a1;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align: center; color: #0d47a1;'>⚙️ Inventory Management System</h1>
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

