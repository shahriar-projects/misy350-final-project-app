import streamlit as st
import data
import services

st.set_page_config(page_title="StoreHQ - Inventory Manager", layout="wide")

data.init_data_files()

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_assistant" not in st.session_state:
    st.session_state.ai_assistant = None
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = None


# PAGE CONTROLLER FUNCTIONS

def navigate_to(page):
    """Navigate to a page by updating session state and rerunning."""
    st.session_state.page = page
    st.rerun()


def logout():
    """Clear session state and redirect to login."""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "login"
    st.rerun()


def require_role(role):
    """Stop page rendering if the logged-in user does not have the required role."""
    if not st.session_state.logged_in or st.session_state.user.role != role:
        st.error("Access denied. You do not have permission to view this page.")
        st.stop()


def handle_login(username, password):
    """Validate login credentials and update session state on success."""
    if not username or not password:
        st.warning("Please enter both username and password.")
        return
    user = services.validate_login(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.page = "owner_dashboard" if user.is_owner() else "employee_dashboard"
        st.rerun()
    else:
        st.error("Invalid username or password.")


def handle_register(username, password, confirm, role):
    """Validate registration inputs and create a new account."""
    if not username or not password or not confirm:
        st.error("All fields are required.")
        return
    if password != confirm:
        st.error("Passwords do not match.")
        return
    success, message = services.register_user(username, password, role)
    if success:
        st.success(f"{message} You can now log in.")
    else:
        st.error(message)


def handle_add_product(name, category, price, stock):
    """Validate inputs and add a new product to inventory."""
    if not name or not category:
        st.error("Product name and category are required.")
        return
    if stock < 0:
        st.error("Stock cannot be negative.")
        return
    if price <= 0:
        st.error("Price must be greater than zero.")
        return
    item = services.add_product(name, category, price, stock)
    st.success(f"{item.name} has been added to the inventory.")


def handle_update_product(product_id, name, category, price, stock):
    """Validate inputs and update an existing product."""
    if not name or not category:
        st.error("Name and category cannot be empty.")
        return
    if stock < 0:
        st.error("Stock cannot be negative.")
        return
    if price <= 0:
        st.error("Price must be greater than zero.")
        return
    services.update_product(product_id, name, category, price, stock)
    st.success("Product updated successfully.")
    st.rerun()


def handle_record_sale(product_id, product_name, price, qty, logged_by):
    """Validate sale quantity against current stock and record the sale."""
    if qty <= 0:
        st.error("Quantity must be at least 1.")
        return
    inventory = data.load_inventory()
    for item in inventory:
        if item["id"] == product_id:
            if qty > item["stock"]:
                st.error(f"Cannot sell {qty} units. Only {item['stock']} currently in stock.")
                return
    record = services.record_sale(product_id, product_name, price, qty, logged_by)
    st.success(f"Recorded: {qty}x {product_name} for ${record['total']:.2f}")
    st.rerun()


def get_ai_demo_response(user_input, inventory):
    """Generate a keyword-based demo response from live inventory data."""
    text = user_input.lower()
    if "low" in text:
        items = [i for i in inventory if 0 < i["stock"] < 5]
        return ("Low stock items (under 5 units): " + ", ".join(f"{i['name']} ({i['stock']} left)" for i in items)) if items else "No items are currently low on stock."
    elif "out" in text:
        items = [i for i in inventory if i["stock"] == 0]
        return ("Out of stock: " + ", ".join(i["name"] for i in items)) if items else "All items are currently in stock."
    elif "categor" in text:
        cats = sorted(set(i["category"] for i in inventory))
        return "Product categories: " + ", ".join(cats)
    elif "all" in text or "list" in text or "catalog" in text:
        lines = ", ".join(f"{i['name']} (${i['price']:.2f}, stock: {i['stock']})" for i in inventory)
        return "Full catalog: " + lines
    return "Demo mode supports: low stock, out of stock, categories, full catalog. Connect with an API key for free-form questions."


# SIDEBAR RENDERERS

def owner_sidebar():
    with st.sidebar:
        st.title("StoreHQ")
        st.markdown(f"Logged in as: **{st.session_state.user.username}**")
        st.markdown(f"Role: `Shop Owner`")
        st.divider()
        st.markdown("**Navigation**")
        if st.button("Inventory", use_container_width=True, key="nav_inv_own"):
            navigate_to("owner_dashboard")
        if st.button("Add Product", use_container_width=True, key="nav_add_own"):
            navigate_to("owner_add")
        if st.button("Edit / Delete", use_container_width=True, key="nav_edit_own"):
            navigate_to("owner_edit")
        st.divider()
        if st.button("Logout", use_container_width=True, key="owner_logout"):
            logout()


def employee_sidebar():
    with st.sidebar:
        st.title("StoreHQ")
        st.markdown(f"Logged in as: **{st.session_state.user.username}**")
        st.markdown(f"Role: `Employee`")
        st.divider()
        st.markdown("**Navigation**")
        if st.button("View Catalog", use_container_width=True, key="nav_cat_emp"):
            navigate_to("employee_dashboard")
        if st.button("Log a Sale", use_container_width=True, key="nav_sale_emp"):
            navigate_to("employee_sales")
        if st.button("AI Assistant", use_container_width=True, key="nav_ai_emp"):
            navigate_to("employee_ai")
        st.divider()
        if st.button("Logout", use_container_width=True, key="emp_logout"):
            logout()


# LOGIN PAGE
if st.session_state.page == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("StoreHQ")
        st.subheader("Inventory Management System")
        st.divider()

        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True, type="primary", key="login_btn"):
            handle_login(login_username, login_password)

        st.divider()
        if st.button("Register a new account", use_container_width=True, key="go_register_btn"):
            navigate_to("register")

        with st.container(border=True):
            st.caption("Test Accounts:")
            st.caption("Shop Owner: owner1 / owner123")
            st.caption("Employee: employee1 / emp123")


# REGISTRATION PAGE
elif st.session_state.page == "register":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("StoreHQ")
        st.subheader("Create a New Account")
        st.divider()

        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2")
        reg_role = st.selectbox("Role", ["Employee", "Shop Owner"], key="reg_role")

        if st.button("Create Account", use_container_width=True, type="primary", key="register_btn"):
            handle_register(reg_username, reg_password, reg_password2, reg_role)

        st.divider()
        if st.button("Back to Login", use_container_width=True, key="back_login_btn"):
            navigate_to("login")


# OWNER DASHBOARD - tabs reduce scrolling and group related actions
elif st.session_state.page == "owner_dashboard":
    require_role("Shop Owner")
    owner_sidebar()

    st.title("Owner Dashboard")
    st.divider()

    inventory = data.load_inventory()
    low_stock = services.get_low_stock_items()
    out_of_stock = services.get_out_of_stock_items()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", len(inventory))
    c2.metric("Low Stock (under 5)", len(low_stock))
    c3.metric("Out of Stock", len(out_of_stock))
    st.divider()

    tab_view, tab_add, tab_edit = st.tabs(["View Inventory", "Add Product", "Edit / Delete"])

    with tab_view:
        categories = ["All"] + sorted(set(i["category"] for i in inventory))
        selected_cat = st.selectbox("Filter by Category", categories, key="owner_cat_filter")
        filtered = inventory if selected_cat == "All" else [i for i in inventory if i["category"] == selected_cat]

        for item in filtered:
            stock_label = "OUT OF STOCK" if item["stock"] == 0 else ("LOW STOCK" if item["stock"] < 5 else "In Stock")
            with st.expander(f"{item['name']} | {item['category']} | ${item['price']:.2f} | Stock: {item['stock']} | {stock_label}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**ID:** {item['id']}")
                col_a.write(f"**Category:** {item['category']}")
                col_b.write(f"**Price:** ${item['price']:.2f}")
                col_b.write(f"**Stock:** {item['stock']} units")
                if item["stock"] == 0:
                    st.error("This item is out of stock.")
                elif item["stock"] < 5:
                    st.warning("This item is low on stock. Consider restocking.")

    with tab_add:
        with st.container(border=True):
            add_name = st.text_input("Product Name", key="add_name")
            add_category = st.text_input("Category (e.g. Electronics, Stationery, Furniture)", key="add_category")
            col1, col2 = st.columns(2)
            with col1:
                add_price = st.number_input("Price ($)", min_value=0.01, step=0.01, format="%.2f", key="add_price")
            with col2:
                add_stock = st.number_input("Initial Stock", min_value=0, step=1, key="add_stock")

            if st.button("Add Product", type="primary", key="add_product_btn"):
                handle_add_product(add_name, add_category, add_price, add_stock)

    with tab_edit:
        if not inventory:
            st.info("No products in inventory yet.")
        else:
            product_labels = [f"{i['name']} (ID: {i['id']})" for i in inventory]
            selected_label = st.selectbox("Select a Product", product_labels, key="edit_select")
            selected_index = product_labels.index(selected_label)
            selected_item = inventory[selected_index]

            st.markdown("#### Edit Details")
            with st.container(border=True):
                edit_name = st.text_input("Name", value=selected_item["name"], key=f"edit_name_{selected_item['id']}")
                edit_category = st.text_input("Category", value=selected_item["category"], key=f"edit_cat_{selected_item['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    edit_price = st.number_input("Price ($)", value=selected_item["price"], min_value=0.01, step=0.01, format="%.2f", key=f"edit_price_{selected_item['id']}")
                with col2:
                    edit_stock = st.number_input("Stock", value=selected_item["stock"], min_value=0, step=1, key=f"edit_stock_{selected_item['id']}")

                if st.button("Save Changes", type="primary", key="save_edit_btn"):
                    handle_update_product(selected_item["id"], edit_name, edit_category, edit_price, edit_stock)

            st.divider()
            st.markdown("#### Delete Product")
            with st.container(border=True):
                st.warning(f"This will permanently remove {selected_item['name']} from inventory.")
                if st.button("Delete Product", key="delete_btn"):
                    services.delete_product(selected_item["id"])
                    st.success(f"{selected_item['name']} has been deleted.")
                    st.rerun()


# EMPLOYEE DASHBOARD
elif st.session_state.page == "employee_dashboard":
    require_role("Employee")
    employee_sidebar()

    st.title("Employee Dashboard")
    st.markdown("Browse the product catalog and monitor stock levels.")
    st.divider()

    inventory = data.load_inventory()
    low_stock = services.get_low_stock_items()
    out_of_stock = services.get_out_of_stock_items()

    if out_of_stock:
        st.error("Out of Stock: " + ", ".join(i["name"] for i in out_of_stock))
    if low_stock:
        st.warning("Low Stock: " + ", ".join(f"{i['name']} ({i['stock']} left)" for i in low_stock))

    st.divider()
    categories = ["All"] + sorted(set(i["category"] for i in inventory))
    emp_cat = st.selectbox("Filter by Category", categories, key="emp_cat_filter")
    filtered = inventory if emp_cat == "All" else [i for i in inventory if i["category"] == emp_cat]

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        col1.markdown("**Product**")
        col2.markdown("**Category**")
        col3.markdown("**Price**")
        col4.markdown("**Stock**")
        st.divider()
        for item in filtered:
            stock_label = "OUT" if item["stock"] == 0 else ("LOW" if item["stock"] < 5 else str(item["stock"]))
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            col1.write(item["name"])
            col2.write(item["category"])
            col3.write(f"${item['price']:.2f}")
            col4.write(stock_label)


# EMPLOYEE SALES PAGE
elif st.session_state.page == "employee_sales":
    require_role("Employee")
    employee_sidebar()

    st.title("Log a Sale")
    st.markdown("Record a sale and stock will be updated automatically.")
    st.divider()

    inventory = data.load_inventory()
    in_stock_items = [i for i in inventory if i["stock"] > 0]

    if not in_stock_items:
        st.warning("No items are currently in stock.")
    else:
        with st.container(border=True):
            sale_labels = [f"{i['name']} (Stock: {i['stock']})" for i in in_stock_items]
            sale_selected_label = st.selectbox("Select Product Sold", sale_labels, key="sale_select")
            sale_index = sale_labels.index(sale_selected_label)
            sale_item = in_stock_items[sale_index]
            sale_qty = st.number_input("Quantity Sold", min_value=1, max_value=sale_item["stock"], step=1, key="sale_qty")

            if st.button("Record Sale", type="primary", key="record_sale_btn"):
                handle_record_sale(
                    sale_item["id"], sale_item["name"],
                    sale_item["price"], sale_qty,
                    st.session_state.user.username
                )

    st.divider()
    st.subheader("Recent Sales Log")
    sales = data.load_sales()
    if not sales:
        st.info("No sales have been logged yet.")
    else:
        with st.container(border=True):
            for s in reversed(sales[-10:]):
                st.markdown(f"`{s['timestamp']}` — **{s['product_name']}** x{s['qty_sold']} = ${s['total']:.2f} (logged by {s['logged_by']})")


# EMPLOYEE AI ASSISTANT PAGE
elif st.session_state.page == "employee_ai":
    require_role("Employee")
    employee_sidebar()

    st.title("AI Inventory Assistant")
    st.markdown("Ask questions about the store inventory and get real-time answers.")
    st.divider()

    if st.session_state.ai_assistant is None:
        with st.container(border=True):
            st.markdown("### Connect AI Assistant")
            st.markdown("To use the live AI assistant, enter your OpenAI API key below. Your key is used only during this session and is never stored in any file.")

            col1, col2 = st.columns([3, 1])
            with col1:
                api_key_input = st.text_input("OpenAI API Key", type="password", key="api_key_input", placeholder="sk-...")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                connect_btn = st.button("Connect", type="primary", key="connect_ai_btn", use_container_width=True)

            if connect_btn:
                if api_key_input and api_key_input.startswith("sk-"):
                    st.session_state.ai_assistant = services.AIAssistant(api_key_input)
                    st.session_state.ai_mode = "live"
                    st.success("AI Assistant connected. You can now ask questions about the inventory.")
                    st.rerun()
                elif api_key_input:
                    st.error("That does not look like a valid OpenAI API key. Keys must start with 'sk-'.")
                else:
                    st.error("Please enter your OpenAI API key to continue.")

        st.divider()
        with st.container(border=True):
            st.markdown("### Demo Mode (No API Key Required)")
            st.markdown("Use demo mode to test the assistant interface without an OpenAI API key. Responses are generated from live inventory data.")
            if st.button("Use Demo Mode", key="demo_mode_btn", use_container_width=True):
                st.session_state.ai_assistant = "demo"
                st.session_state.ai_mode = "demo"
                st.rerun()

    else:
        inventory = data.load_inventory()

        if st.session_state.get("ai_mode") == "demo":
            st.info("Demo Mode is active. Responses are pre-written based on live inventory. Connect with an OpenAI API key for free-form AI answers.")
        else:
            st.success("Live AI connected. Powered by OpenAI GPT-3.5.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask about the inventory...", key="chat_input")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            if st.session_state.get("ai_mode") == "demo":
                reply = get_ai_demo_response(user_input, inventory)
            else:
                with st.spinner("Thinking..."):
                    reply = st.session_state.ai_assistant.get_response(user_input, inventory)

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat History", key="clear_chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            if st.button("Disconnect AI", key="disconnect_ai", use_container_width=True):
                st.session_state.ai_assistant = None
                st.session_state.ai_mode = None
                st.session_state.chat_history = []
                st.success("AI disconnected. Your API key has been cleared from this session.")
                st.rerun()
