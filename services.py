"""
services.py - Service / Business Logic Layer
Contains all classes and business logic for StoreHQ.
This module sits between the UI (app.py) and the data layer (data.py).
"""

from datetime import datetime
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import hashlib
import data


def hash_password(password):
    """Hash a password using SHA-256 before storing it."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password, hashed_password):
    """Check if a plain-text password matches a stored hash."""
    return hash_password(plain_password) == hashed_password


class User:
    """Represents an authenticated user with a role."""

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def is_owner(self):
        """Returns True if the user is a Shop Owner."""
        return self.role == "Shop Owner"

    def is_employee(self):
        """Returns True if the user is an Employee."""
        return self.role == "Employee"

    def can_access_page(self, required_role):
        """Returns True if the user's role matches the required role for a page."""
        return self.role == required_role

    def to_dict(self):
        """Convert the User object to a dictionary for JSON storage. Password is stored as a hash."""
        return {"username": self.username, "password": hash_password(self.password), "role": self.role}


class InventoryItem:
    """Represents a single product in the store inventory."""

    def __init__(self, id, name, category, price, stock):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock

    def is_low_stock(self):
        """Returns True if stock is greater than 0 but less than 5."""
        return 0 < self.stock < 5

    def is_out_of_stock(self):
        """Returns True if stock is 0."""
        return self.stock == 0

    def to_dict(self):
        """Convert the InventoryItem object to a dictionary for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock
        }


class AIAssistant:
    """Handles communication with the OpenAI API for inventory-related queries."""

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def get_response(self, user_message, inventory):
        """
        Send a user message to OpenAI along with the current inventory as context.
        Returns a response string or a clear error message if the request fails.
        """
        inventory_summary = "\n".join(
            f"- {item['name']} ({item['category']}): ${item['price']:.2f}, Stock: {item['stock']}"
            for item in inventory
        )
        system_prompt = (
            "You are a helpful inventory assistant for StoreHQ, a small retail store. "
            "You help employees check stock levels, find products, and get business insights. "
            "Here is the current inventory:\n\n"
            f"{inventory_summary}\n\n"
            "Answer questions about the inventory clearly and concisely. "
            "Do not discuss topics unrelated to the store or its inventory."
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except AuthenticationError:
            return "Error: Invalid API key. Please disconnect and enter a valid OpenAI API key."
        except RateLimitError:
            return "Error: OpenAI rate limit reached. Please wait a moment and try again."
        except APIConnectionError:
            return "Error: Could not connect to OpenAI. Please check your internet connection."
        except Exception as e:
            return f"Error: Something went wrong — {str(e)}"


# AUTH FUNCTIONS

def validate_login(username, password):
    """
    Check username and password against stored users.
    Supports both plain-text passwords (legacy) and hashed passwords.
    Returns a User object if valid, or None if not found.
    """
    users = data.load_users()
    hashed = hash_password(password)
    for u in users:
        if u["username"] == username:
            stored = u["password"]
            if stored == hashed or stored == password:
                return User(u["username"], u["password"], u["role"])
    return None


def register_user(username, password, role):
    """
    Register a new user if the username is not already taken.
    Returns (True, success message) or (False, error message).
    """
    if not username or not password:
        return False, "Username and password are required."
    users = data.load_users()
    for u in users:
        if u["username"] == username:
            return False, "Username already taken."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    new_user = User(username, password, role)
    users.append(new_user.to_dict())
    data.save_users(users)
    return True, "Account created successfully."


# INVENTORY FUNCTIONS

def get_next_id():
    """Return the next available product ID based on current inventory."""
    inventory = data.load_inventory()
    if not inventory:
        return 1
    return max(i["id"] for i in inventory) + 1


def add_product(name, category, price, stock):
    """
    Add a new product to the inventory.
    Returns the new InventoryItem object.
    """
    inventory = data.load_inventory()
    new_item = InventoryItem(get_next_id(), name.strip(), category.strip(), round(price, 2), int(stock))
    inventory.append(new_item.to_dict())
    data.save_inventory(inventory)
    return new_item


def update_product(product_id, name, category, price, stock):
    """Update an existing product's details by its ID."""
    inventory = data.load_inventory()
    for item in inventory:
        if item["id"] == product_id:
            item["name"] = name.strip()
            item["category"] = category.strip()
            item["price"] = round(price, 2)
            item["stock"] = int(stock)
            break
    data.save_inventory(inventory)


def delete_product(product_id):
    """Remove a product from inventory by its ID."""
    inventory = data.load_inventory()
    inventory = [i for i in inventory if i["id"] != product_id]
    data.save_inventory(inventory)


def get_low_stock_items():
    """Return a list of items with stock between 1 and 4 (inclusive)."""
    return [i for i in data.load_inventory() if 0 < i["stock"] < 5]


def get_out_of_stock_items():
    """Return a list of items with stock equal to 0."""
    return [i for i in data.load_inventory() if i["stock"] == 0]


# SALES FUNCTIONS

def record_sale(product_id, product_name, price, qty, logged_by):
    """
    Deduct sold quantity from inventory and append a sale record.
    Returns the sale record dictionary.
    """
    inventory = data.load_inventory()
    for item in inventory:
        if item["id"] == product_id:
            item["stock"] -= int(qty)
            break
    data.save_inventory(inventory)

    sales = data.load_sales()
    sale_record = {
        "product_id": product_id,
        "product_name": product_name,
        "qty_sold": int(qty),
        "price_each": price,
        "total": round(price * qty, 2),
        "logged_by": logged_by,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    sales.append(sale_record)
    data.save_sales(sales)
    return sale_record
