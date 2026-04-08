import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="StoreHQ - Inventory Manager", page_icon="🏪", layout="wide")

#SESSION STATE INITIALIZATION

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# JSON FILE PATHS

USERS_FILE = "data/users.json"
INVENTORY_FILE = "data/inventory.json"
SALES_FILE = "data/sales.json"

# JSON LOADING & SAVING

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([
            {"username": "owner1", "password": "owner123", "role": "Shop Owner"},
            {"username": "employee1", "password": "emp123", "role": "Employee"}
        ], f, indent=2)

if not os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "w") as f:
        json.dump([
            {"id": 1, "name": "Laptop Stand", "category": "Electronics", "price": 29.99, "stock": 12},
            {"id": 2, "name": "Wireless Mouse", "category": "Electronics", "price": 19.99, "stock": 3},
            {"id": 3, "name": "Notebook (5-pack)", "category": "Stationery", "price": 8.49, "stock": 25},
            {"id": 4, "name": "Blue Pens (10-pack)", "category": "Stationery", "price": 4.99, "stock": 2},
            {"id": 5, "name": "Desk Lamp", "category": "Furniture", "price": 34.99, "stock": 7},
            {"id": 6, "name": "Stapler", "category": "Stationery", "price": 9.99, "stock": 0},
            {"id": 7, "name": "USB-C Hub", "category": "Electronics", "price": 45.99, "stock": 1},
            {"id": 8, "name": "Whiteboard Markers", "category": "Stationery", "price": 6.99, "stock": 14}
        ], f, indent=2)

if not os.path.exists(SALES_FILE):
    with open(SALES_FILE, "w") as f:
        json.dump([], f, indent=2)

with open(USERS_FILE, "r") as f:
    users_data = json.load(f)

with open(INVENTORY_FILE, "r") as f:
    inventory_data = json.load(f)

with open(SALES_FILE, "r") as f:
    sales_data = json.load(f)

# LOGIN PAGE

if st.session_state.page == "login":
    st.title("🏪 StoreHQ")
    st.subheader("Inventory Management System")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True, type="primary", key="login_btn"):
            if login_username and login_password:
                matched_user = None
                for u in users_data:
                    if u["username"] == login_username and u["password"] == login_password:
                        matched_user = u
                        break
                if matched_user:
                    st.session_state.logged_in = True
                    st.session_state.user = matched_user
                    if matched_user["role"] == "Shop Owner":
                        st.session_state.page = "owner_dashboard"
                    else:
                        st.session_state.page = "employee_dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
            else:
                st.warning("⚠️ Please enter both username and password.")

        st.markdown("---")
        if st.button("Don't have an account? Register here", use_container_width=True, key="go_register_btn"):
            st.session_state.page = "register"
            st.rerun()

        st.caption("**Demo Accounts:**")
        st.caption("Shop Owner → `owner1` / `owner123`")
        st.caption("Employee → `employee1` / `emp123`")


# REGISTRATION PAGE

elif st.session_state.page == "register":
    st.title("🏪 StoreHQ")
    st.subheader("Create a New Account")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Register")
        reg_username = st.text_input("Choose a Username", key="reg_username")
        reg_password = st.text_input("Choose a Password", type="password", key="reg_password")
        reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2")
        reg_role = st.selectbox("Role", ["Employee", "Shop Owner"], key="reg_role")

        if st.button("Create Account", use_container_width=True, type="primary", key="register_btn"):
            if not reg_username or not reg_password or not reg_password2:
                st.error("❌ All fields are required.")
            elif reg_password != reg_password2:
                st.error("❌ Passwords do not match.")
            elif len(reg_password) < 4:
                st.error("❌ Password must be at least 4 characters.")
            else:
                duplicate = False
                for u in users_data:
                    if u["username"] == reg_username:
                        duplicate = True
                        break
                if duplicate:
                    st.error("❌ That username is already taken. Please choose another.")
                else:
                    new_user = {"username": reg_username, "password": reg_password, "role": reg_role}
                    users_data.append(new_user)
                    with open(USERS_FILE, "w") as f:
                        json.dump(users_data, f, indent=2)
                    st.success(f"✅ Account created! You can now log in as **{reg_username}**.")

        st.markdown("---")
        if st.button("← Back to Login", use_container_width=True, key="back_login_btn"):
            st.session_state.page = "login"
            st.rerun()

# OWNER DASHBOARD

elif st.session_state.page == "owner_dashboard":

    if not st.session_state.logged_in or st.session_state.user["role"] != "Shop Owner":
        st.error("Access denied.")
        st.stop()

    #Sidebar
    with st.sidebar:
        st.title("🏪 StoreHQ")
        st.markdown(f"👤 **{st.session_state.user['username']}**")
        st.markdown(f"🔑 Role: `Shop Owner`")
        st.markdown("---")
        st.markdown("### Navigation")
        if st.button("📦 Inventory", use_container_width=True, key="nav_inventory"):
            st.session_state.page = "owner_dashboard"
            st.rerun()
        if st.button("➕ Add Product", use_container_width=True, key="nav_add"):
            st.session_state.page = "owner_add"
            st.rerun()
        if st.button("✏️ Edit / Delete", use_container_width=True, key="nav_edit"):
            st.session_state.page = "owner_edit"
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="owner_logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    #Main Content
    st.title("🛠️ Owner Dashboard")
    st.markdown("View and manage your full store inventory.")
    st.markdown("---")

    #Summary metrics
    total_items = len(inventory_data)
    low_stock_items = [i for i in inventory_data if 0 < i["stock"] < 5]
    out_of_stock_items = [i for i in inventory_data if i["stock"] == 0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", total_items)
    c2.metric("🟡 Low Stock", len(low_stock_items))
    c3.metric("🔴 Out of Stock", len(out_of_stock_items))
    st.markdown("---")

    #Category filter
    categories = ["All"] + sorted(set(i["category"] for i in inventory_data))
    selected_cat = st.selectbox("Filter by Category", categories, key="owner_cat_filter")
    filtered = inventory_data if selected_cat == "All" else [i for i in inventory_data if i["category"] == selected_cat]

    for item in filtered:
        stock_icon = "🔴" if item["stock"] == 0 else ("🟡" if item["stock"] < 5 else "🟢")
        with st.expander(f"{stock_icon} **{item['name']}** | {item['category']} | ${item['price']:.2f} | Stock: {item['stock']}"):
            col_a, col_b = st.columns(2)
            col_a.write(f"**ID:** {item['id']}")
            col_a.write(f"**Category:** {item['category']}")
            col_b.write(f"**Price:** ${item['price']:.2f}")
            col_b.write(f"**Stock:** {item['stock']} units")
            if item["stock"] == 0:
                st.error("⚠️ Out of stock!")
            elif item["stock"] < 5:
                st.warning("⚠️ Low stock — consider restocking soon.")

# OWNER ADD PRODUCT PAGE

elif st.session_state.page == "owner_add":

    if not st.session_state.logged_in or st.session_state.user["role"] != "Shop Owner":
        st.error("Access denied.")
        st.stop()

    with st.sidebar:
        st.title("🏪 StoreHQ")
        st.markdown(f"👤 **{st.session_state.user['username']}**")
        st.markdown(f"🔑 Role: `Shop Owner`")
        st.markdown("---")
        st.markdown("### Navigation")
        if st.button("📦 Inventory", use_container_width=True, key="nav_inv2"):
            st.session_state.page = "owner_dashboard"
            st.rerun()
        if st.button("➕ Add Product", use_container_width=True, key="nav_add2"):
            st.session_state.page = "owner_add"
            st.rerun()
        if st.button("✏️ Edit / Delete", use_container_width=True, key="nav_edit2"):
            st.session_state.page = "owner_edit"
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="owner_logout2"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    st.title("➕ Add New Product")
    st.markdown("---")

    add_name = st.text_input("Product Name", key="add_name")
    add_category = st.text_input("Category (e.g. Electronics, Stationery, Furniture)", key="add_category")
    add_price = st.number_input("Price ($)", min_value=0.01, step=0.01, format="%.2f", key="add_price")
    add_stock = st.number_input("Initial Stock", min_value=0, step=1, key="add_stock")

    if st.button("✅ Add Product", type="primary", key="add_product_btn"):
        if not add_name or not add_category:
            st.error("❌ Product name and category are required.")
        else:
            new_id = 1 if not inventory_data else max(i["id"] for i in inventory_data) + 1
            new_product = {
                "id": new_id,
                "name": add_name.strip(),
                "category": add_category.strip(),
                "price": round(add_price, 2),
                "stock": int(add_stock)
            }
            inventory_data.append(new_product)
            with open(INVENTORY_FILE, "w") as f:
                json.dump(inventory_data, f, indent=2)
            st.success(f"✅ **{add_name}** added to inventory!")

# OWNER EDIT / DELETE PAGE

elif st.session_state.page == "owner_edit":

    if not st.session_state.logged_in or st.session_state.user["role"] != "Shop Owner":
        st.error("Access denied.")
        st.stop()

    with st.sidebar:
        st.title("🏪 StoreHQ")
        st.markdown(f"👤 **{st.session_state.user['username']}**")
        st.markdown(f"🔑 Role: `Shop Owner`")
        st.markdown("---")
        st.markdown("### Navigation")
        if st.button("📦 Inventory", use_container_width=True, key="nav_inv3"):
            st.session_state.page = "owner_dashboard"
            st.rerun()
        if st.button("➕ Add Product", use_container_width=True, key="nav_add3"):
            st.session_state.page = "owner_add"
            st.rerun()
        if st.button("✏️ Edit / Delete", use_container_width=True, key="nav_edit3"):
            st.session_state.page = "owner_edit"
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="owner_logout3"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    st.title("✏️ Edit / Delete Product")
    st.markdown("---")

    if not inventory_data:
        st.info("No products in inventory yet.")
    else:
        product_labels = [f"{i['name']} (ID: {i['id']})" for i in inventory_data]
        selected_label = st.selectbox("Select a Product", product_labels, key="edit_select")
        selected_index = product_labels.index(selected_label)
        selected_item = inventory_data[selected_index]

        st.markdown("#### ✏️ Edit Details")
        edit_name = st.text_input("Name", value=selected_item["name"], key="edit_name")
        edit_category = st.text_input("Category", value=selected_item["category"], key="edit_category")
        edit_price = st.number_input("Price ($)", value=selected_item["price"], min_value=0.01, step=0.01, format="%.2f", key="edit_price")
        edit_stock = st.number_input("Stock", value=selected_item["stock"], min_value=0, step=1, key="edit_stock")

        if st.button("💾 Save Changes", type="primary", key="save_edit_btn"):
            if not edit_name or not edit_category:
                st.error("❌ Name and category cannot be empty.")
            else:
                for item in inventory_data:
                    if item["id"] == selected_item["id"]:
                        item["name"] = edit_name.strip()
                        item["category"] = edit_category.strip()
                        item["price"] = round(edit_price, 2)
                        item["stock"] = int(edit_stock)
                with open(INVENTORY_FILE, "w") as f:
                    json.dump(inventory_data, f, indent=2)
                st.success("✅ Product updated successfully!")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 🗑️ Delete Product")
        st.warning(f"This will permanently remove **{selected_item['name']}** from inventory.")
        if st.button("🗑️ Delete Product", key="delete_btn"):
            inventory_data[:] = [i for i in inventory_data if i["id"] != selected_item["id"]]
            with open(INVENTORY_FILE, "w") as f:
                json.dump(inventory_data, f, indent=2)
            st.success(f"🗑️ **{selected_item['name']}** deleted.")
            st.rerun()

# EMPLOYEE DASHBOARD

elif st.session_state.page == "employee_dashboard":

    if not st.session_state.logged_in or st.session_state.user["role"] != "Employee":
        st.error("Access denied.")
        st.stop()

    with st.sidebar:
        st.title("🏪 StoreHQ")
        st.markdown(f"👤 **{st.session_state.user['username']}**")
        st.markdown(f"🔑 Role: `Employee`")
        st.markdown("---")
        st.markdown("### Navigation")
        if st.button("📋 View Catalog", use_container_width=True, key="emp_nav_catalog"):
            st.session_state.page = "employee_dashboard"
            st.rerun()
        if st.button("💰 Log a Sale", use_container_width=True, key="emp_nav_sales"):
            st.session_state.page = "employee_sales"
            st.rerun()
        if st.button("🤖 AI Assistant", use_container_width=True, key="emp_nav_ai"):
            st.session_state.page = "employee_ai"
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="emp_logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    st.title("👷 Employee Dashboard")
    st.markdown("Browse the current product catalog and check stock alerts.")
    st.markdown("---")

    low_stock = [i for i in inventory_data if 0 < i["stock"] < 5]
    out_of_stock = [i for i in inventory_data if i["stock"] == 0]

    if out_of_stock:
        st.error("🔴 **Out of Stock:** " + ", ".join(i["name"] for i in out_of_stock))
    if low_stock:
        st.warning("🟡 **Low Stock:** " + ", ".join(f"{i['name']} ({i['stock']} left)" for i in low_stock))

    st.markdown("---")
    categories = ["All"] + sorted(set(i["category"] for i in inventory_data))
    emp_cat = st.selectbox("Filter by Category", categories, key="emp_cat_filter")
    filtered = inventory_data if emp_cat == "All" else [i for i in inventory_data if i["category"] == emp_cat]

    for item in filtered:
        stock_icon = "🔴" if item["stock"] == 0 else ("🟡" if item["stock"] < 5 else "🟢")
        st.markdown(
            f"{stock_icon} **{item['name']}** &nbsp;|&nbsp; "
            f"Category: `{item['category']}` &nbsp;|&nbsp; "
            f"Price: `${item['price']:.2f}` &nbsp;|&nbsp; "
            f"Stock: `{item['stock']}`"
        )


# EMPLOYEE SALES PAGE

elif st.session_state.page == "employee_sales":

    if not st.session_state.logged_in or st.session_state.user["role"] != "Employee":
        st.error("Access denied.")
        st.stop()

    with st.sidebar:
        st.title("🏪 StoreHQ")
        st.markdown(f"👤 **{st.session_state.user['username']}**")
        st.markdown(f"🔑 Role: `Employee`")
        st.markdown("---")
        st.markdown("### Navigation")
        if st.button("📋 View Catalog", use_container_width=True, key="emp_nav_catalog2"):
            st.session_state.page = "employee_dashboard"
            st.rerun()
        if st.button("💰 Log a Sale", use_container_width=True, key="emp_nav_sales2"):
            st.session_state.page = "employee_sales"
            st.rerun()
        if st.button("🤖 AI Assistant", use_container_width=True, key="emp_nav_ai2"):
            st.session_state.page = "employee_ai"
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="emp_logout2"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    st.title("💰 Log a Sale")
    st.markdown("Record a sale — stock will be updated automatically.")
    st.markdown("---")

    in_stock_items = [i for i in inventory_data if i["stock"] > 0]

    if not in_stock_items:
        st.warning("⚠️ No items currently in stock.")
    else:
        sale_labels = [f"{i['name']} (Stock: {i['stock']})" for i in in_stock_items]
        sale_selected_label = st.selectbox("Select Product Sold", sale_labels, key="sale_select")
        sale_index = sale_labels.index(sale_selected_label)
        sale_item = in_stock_items[sale_index]

        sale_qty = st.number_input("Quantity Sold", min_value=1, max_value=sale_item["stock"], step=1, key="sale_qty")

        if st.button("✅ Record Sale", type="primary", key="record_sale_btn"):
            for item in inventory_data:
                if item["id"] == sale_item["id"]:
                    item["stock"] -= int(sale_qty)
            with open(INVENTORY_FILE, "w") as f:
                json.dump(inventory_data, f, indent=2)

            sale_record = {
                "product_id": sale_item["id"],
                "product_name": sale_item["name"],
                "qty_sold": int(sale_qty),
                "price_each": sale_item["price"],
                "total": round(sale_item["price"] * sale_qty, 2),
                "logged_by": st.session_state.user["username"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            sales_data.append(sale_record)
            with open(SALES_FILE, "w") as f:
                json.dump(sales_data, f, indent=2)

            st.success(f"✅ Recorded: {sale_qty}x **{sale_item['name']}** for **${sale_item['price'] * sale_qty:.2f}**")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Recent Sales Log")
    if not sales_data:
        st.info("No sales logged yet.")
    else:
        for s in reversed(sales_data[-10:]):
            st.markdown(f"🕒 `{s['timestamp']}` — **{s['product_name']}** x{s['qty_sold']} = `${s['total']:.2f}` (by {s['logged_by']})")

# EMPLOYEE AI ASSISTANT PAGE

elif st.session_state.page == "employee_ai":

    if not st.session_state.logged_in or st.session_state.user["role"] != "Employee":
        st.error("Access denied.")
        st.stop()

    with st.sidebar:
        st.title("🏪 StoreHQ")
        st.markdown(f"👤 **{st.session_state.user['username']}**")
        st.markdown(f"🔑 Role: `Employee`")
        st.markdown("---")
        st.markdown("### Navigation")
        if st.button("📋 View Catalog", use_container_width=True, key="emp_nav_catalog3"):
            st.session_state.page = "employee_dashboard"
            st.rerun()
        if st.button("💰 Log a Sale", use_container_width=True, key="emp_nav_sales3"):
            st.session_state.page = "employee_sales"
            st.rerun()
        if st.button("🤖 AI Assistant", use_container_width=True, key="emp_nav_ai3"):
            st.session_state.page = "employee_ai"
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="emp_logout3"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    st.title("🤖 Inventory Assistant")
    st.markdown("Ask me about stock levels, alerts, or product info!")
    st.markdown("---")

    #Simulated AI: 5 hardcoded response intents
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about inventory...", key="chat_input")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        text = user_input.lower().strip()

        #Intent 1: Low stock
        if "low" in text or "running low" in text:
            items = [i for i in inventory_data if 0 < i["stock"] < 5]
            if not items:
                bot_reply = "✅ No items are currently low on stock!"
            else:
                lines = "\n".join(f"- **{i['name']}**: {i['stock']} units left" for i in items)
                bot_reply = f"🟡 **Items low on stock (under 5 units):**\n{lines}"

        #Intent 2: Out of stock
        elif "out" in text or "unavailable" in text or "zero" in text:
            items = [i for i in inventory_data if i["stock"] == 0]
            if not items:
                bot_reply = "✅ All items are currently in stock!"
            else:
                lines = "\n".join(f"- **{i['name']}**" for i in items)
                bot_reply = f"🔴 **Out of stock items:**\n{lines}"

        #Intent 3: All items / full catalog
        elif "all" in text or "list" in text or "show" in text or "catalog" in text or "items" in text:
            if not inventory_data:
                bot_reply = "The inventory is empty."
            else:
                lines = "\n".join(
                    f"- **{i['name']}** ({i['category']}) — ${i['price']:.2f} | Stock: {i['stock']}"
                    for i in inventory_data
                )
                bot_reply = f"📦 **Full product catalog:**\n{lines}"

        #Intent 4: Categories
        elif "categor" in text or "type" in text or "section" in text:
            cats = sorted(set(i["category"] for i in inventory_data))
            bot_reply = "🗂️ **Product categories:** " + ", ".join(cats)

        #Intent 5: Help
        elif "help" in text or "what can" in text or "command" in text:
            bot_reply = (
                "💡 **Here's what I can help with:**\n"
                "- *What items are low on stock?*\n"
                "- *What items are out of stock?*\n"
                "- *Show me all items / the full catalog*\n"
                "- *What categories do we carry?*\n"
                "- Type **help** anytime to see this list."
            )

        #Default fallback
        else:
            bot_reply = "🤔 I'm not sure about that. Try asking about *low stock*, *out of stock*, *all items*, or *categories*. Type **help** to see what I can do!"

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()
