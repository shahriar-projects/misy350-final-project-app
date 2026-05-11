"""
data.py - Data Layer
Handles all JSON file reads and writes for StoreHQ.
This module is the only place in the app that directly touches the JSON files.
"""

import json
import os
import shutil

USERS_FILE = "data/users.json"
INVENTORY_FILE = "data/inventory.json"
SALES_FILE = "data/sales.json"

DEFAULT_USERS = [
    {"username": "owner1", "password": "owner123", "role": "Shop Owner"},
    {"username": "employee1", "password": "emp123", "role": "Employee"}
]

DEFAULT_INVENTORY = [
    {"id": 1, "name": "Laptop Stand", "category": "Electronics", "price": 29.99, "stock": 12},
    {"id": 2, "name": "Wireless Mouse", "category": "Electronics", "price": 19.99, "stock": 3},
    {"id": 3, "name": "Notebook (5-pack)", "category": "Stationery", "price": 8.49, "stock": 25},
    {"id": 4, "name": "Blue Pens (10-pack)", "category": "Stationery", "price": 4.99, "stock": 2},
    {"id": 5, "name": "Desk Lamp", "category": "Furniture", "price": 34.99, "stock": 7},
    {"id": 6, "name": "Stapler", "category": "Stationery", "price": 9.99, "stock": 0},
    {"id": 7, "name": "USB-C Hub", "category": "Electronics", "price": 45.99, "stock": 1},
    {"id": 8, "name": "Whiteboard Markers", "category": "Stationery", "price": 6.99, "stock": 14}
]


def init_data_files():
    """Create the data directory and default JSON files if they do not exist."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, DEFAULT_USERS)
    if not os.path.exists(INVENTORY_FILE):
        save_json(INVENTORY_FILE, DEFAULT_INVENTORY)
    if not os.path.exists(SALES_FILE):
        save_json(SALES_FILE, [])


def load_json(filepath):
    """
    Load and return data from a JSON file.
    Returns an empty list if the file does not exist or is corrupted.
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_json(filepath, data):
    """
    Save data to a JSON file using a safe write pattern.
    Writes to a temporary file first, then replaces the original
    to avoid data corruption if the write is interrupted.
    """
    tmp_path = filepath + ".tmp"
    try:
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        shutil.move(tmp_path, filepath)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e


def load_users():
    """Load and return the list of all users from users.json."""
    return load_json(USERS_FILE)


def save_users(users):
    """Save the updated users list to users.json."""
    save_json(USERS_FILE, users)


def load_inventory():
    """Load and return the list of all inventory items from inventory.json."""
    return load_json(INVENTORY_FILE)


def save_inventory(inventory):
    """Save the updated inventory list to inventory.json."""
    save_json(INVENTORY_FILE, inventory)


def load_sales():
    """Load and return the list of all sales records from sales.json."""
    return load_json(SALES_FILE)


def save_sales(sales):
    """Save the updated sales list to sales.json."""
    save_json(SALES_FILE, sales)
