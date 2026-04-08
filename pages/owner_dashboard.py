import streamlit as st
import json
import os

st.set_page_config(page_title="Owner Dashboard - StoreHQ", page_icon="🏪", layout="wide")

# ---------- auth guard ----------
if not st.session_state.get("logged_in") or st.session_state.user["role"] != "Shop Owner":
    st.warning("Access denied. Please log in as a Shop Owner.")
    st.stop()

# ---------- helpers ----------
DATA_FILE = "data/inventory.json"

def load_inventory():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_inventory(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def next_id(inventory):
    if not inventory:
        return 1
    return max(item["id"] for item in inventory) + 1

# ---------- sidebar ----------
with st.sidebar:
    st.title("🏪 StoreHQ")
    st.markdown(f"👤 **{st.session_state.user['username']}**")
    st.markdown(f"🔑 Role: `{st.session_state.user['role']}`")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.switch_page("app.py")

# ---------- main ----------
st.title("🛠️ Owner Dashboard")
st.markdown("Manage your store inventory — add, edit, restock, and remove products.")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📦 View Inventory", "➕ Add Product", "✏️ Edit / Delete"])

# ── TAB 1: View ──
with tab1:
    inventory = load_inventory()
    if not inventory:
        st.info("No products yet. Add some in the **Add Product** tab.")
    else:
        # summary metrics
        total_items = len(inventory)
        low_stock = [i for i in inventory if i["stock"] < 5]
        out_of_stock = [i for i in inventory if i["stock"] == 0]

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Products", total_items)
        c2.metric("Low Stock (< 5)", len(low_stock))
        c3.metric("Out of Stock", len(out_of_stock))
        st.markdown("---")

        # filter
        categories = ["All"] + sorted(set(i["category"] for i in inventory))
        selected_cat = st.selectbox("Filter by Category", categories)

        filtered = inventory if selected_cat == "All" else [i for i in inventory if i["category"] == selected_cat]

        for item in filtered:
            stock_color = "🔴" if item["stock"] == 0 else ("🟡" if item["stock"] < 5 else "🟢")
            with st.expander(f"{stock_color} **{item['name']}** — {item['category']} | ${item['price']:.2f} | Stock: {item['stock']}"):
                st.write(f"**Product ID:** {item['id']}")
                st.write(f"**Category:** {item['category']}")
                st.write(f"**Price:** ${item['price']:.2f}")
                st.write(f"**Stock:** {item['stock']} units")
                if item["stock"] == 0:
                    st.error("⚠️ Out of stock!")
                elif item["stock"] < 5:
                    st.warning("⚠️ Low stock — consider restocking.")

# ── TAB 2: Add Product ──
with tab2:
    st.subheader("Add a New Product")
    with st.form("add_product_form"):
        name = st.text_input("Product Name")
        category = st.text_input("Category (e.g. Electronics, Stationery)")
        price = st.number_input("Price ($)", min_value=0.01, step=0.01, format="%.2f")
        stock = st.number_input("Initial Stock", min_value=0, step=1)
        submitted = st.form_submit_button("Add Product", type="primary")

    if submitted:
        if not name or not category:
            st.error("Product name and category are required.")
        else:
            inventory = load_inventory()
            new_item = {
                "id": next_id(inventory),
                "name": name.strip(),
                "category": category.strip(),
                "price": round(price, 2),
                "stock": int(stock)
            }
            inventory.append(new_item)
            save_inventory(inventory)
            st.success(f"✅ **{name}** added successfully!")

# ── TAB 3: Edit / Delete ──
with tab3:
    inventory = load_inventory()
    if not inventory:
        st.info("No products to edit yet.")
    else:
        product_names = {f"{i['name']} (ID: {i['id']})": i for i in inventory}
        selected_label = st.selectbox("Select a Product to Edit or Delete", list(product_names.keys()))
        selected_item = product_names[selected_label]

        st.markdown("#### ✏️ Edit Product")
        with st.form("edit_form"):
            new_name = st.text_input("Name", value=selected_item["name"])
            new_category = st.text_input("Category", value=selected_item["category"])
            new_price = st.number_input("Price ($)", value=selected_item["price"], min_value=0.01, step=0.01, format="%.2f")
            new_stock = st.number_input("Stock", value=selected_item["stock"], min_value=0, step=1)
            update_btn = st.form_submit_button("💾 Save Changes", type="primary")

        if update_btn:
            for item in inventory:
                if item["id"] == selected_item["id"]:
                    item["name"] = new_name.strip()
                    item["category"] = new_category.strip()
                    item["price"] = round(new_price, 2)
                    item["stock"] = int(new_stock)
            save_inventory(inventory)
            st.success("✅ Product updated!")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🗑️ Delete Product")
        st.warning(f"This will permanently delete **{selected_item['name']}**.")
        if st.button("🗑️ Delete Product", type="secondary"):
            inventory = [i for i in inventory if i["id"] != selected_item["id"]]
            save_inventory(inventory)
            st.success(f"🗑️ **{selected_item['name']}** deleted.")
            st.rerun()
