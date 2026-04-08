import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Employee Dashboard - StoreHQ", page_icon="🏪", layout="wide")

# ---------- auth guard ----------
if not st.session_state.get("logged_in") or st.session_state.user["role"] != "Employee":
    st.warning("Access denied. Please log in as an Employee.")
    st.stop()

# ---------- helpers ----------
INVENTORY_FILE = "data/inventory.json"
SALES_FILE = "data/sales.json"

def load_inventory():
    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)

def save_inventory(data):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_sales():
    with open(SALES_FILE, "r") as f:
        return json.load(f)

def save_sales(data):
    with open(SALES_FILE, "w") as f:
        json.dump(data, f, indent=2)

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
st.title("👷 Employee Dashboard")
st.markdown("Browse inventory, log daily sales, and check for low-stock alerts.")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 View Catalog", "💰 Log a Sale", "🤖 AI Assistant"])

# ── TAB 1: View Catalog ──
with tab1:
    inventory = load_inventory()
    if not inventory:
        st.info("No products available.")
    else:
        categories = ["All"] + sorted(set(i["category"] for i in inventory))
        selected_cat = st.selectbox("Filter by Category", categories)
        filtered = inventory if selected_cat == "All" else [i for i in inventory if i["category"] == selected_cat]

        for item in filtered:
            stock_color = "🔴" if item["stock"] == 0 else ("🟡" if item["stock"] < 5 else "🟢")
            st.markdown(
                f"{stock_color} **{item['name']}** &nbsp;|&nbsp; "
                f"Category: `{item['category']}` &nbsp;|&nbsp; "
                f"Price: `${item['price']:.2f}` &nbsp;|&nbsp; "
                f"Stock: `{item['stock']}`"
            )
        st.markdown("---")
        low_stock_items = [i for i in inventory if 0 < i["stock"] < 5]
        out_of_stock = [i for i in inventory if i["stock"] == 0]
        if out_of_stock:
            st.error("🔴 **Out of Stock:** " + ", ".join(i["name"] for i in out_of_stock))
        if low_stock_items:
            st.warning("🟡 **Low Stock:** " + ", ".join(f"{i['name']} ({i['stock']} left)" for i in low_stock_items))

# ── TAB 2: Log a Sale ──
with tab2:
    inventory = load_inventory()
    in_stock = [i for i in inventory if i["stock"] > 0]

    if not in_stock:
        st.warning("No items in stock to sell.")
    else:
        st.subheader("Log a Daily Sale")
        product_map = {f"{i['name']} (Stock: {i['stock']})": i for i in in_stock}
        selected_label = st.selectbox("Select Product Sold", list(product_map.keys()))
        selected_item = product_map[selected_label]

        qty = st.number_input("Quantity Sold", min_value=1, max_value=selected_item["stock"], step=1)

        if st.button("✅ Record Sale", type="primary"):
            # deduct stock
            for item in inventory:
                if item["id"] == selected_item["id"]:
                    item["stock"] -= int(qty)
            save_inventory(inventory)

            # log sale
            sales = load_sales()
            sales.append({
                "product_id": selected_item["id"],
                "product_name": selected_item["name"],
                "qty_sold": int(qty),
                "price_each": selected_item["price"],
                "total": round(selected_item["price"] * qty, 2),
                "logged_by": st.session_state.user["username"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_sales(sales)
            st.success(f"✅ Logged sale: {qty}x **{selected_item['name']}** for ${selected_item['price'] * qty:.2f}")
            st.rerun()

        st.markdown("---")
        st.subheader("Recent Sales Log")
        sales = load_sales()
        if not sales:
            st.info("No sales logged yet.")
        else:
            for s in reversed(sales[-10:]):
                st.markdown(f"🕒 `{s['timestamp']}` — **{s['product_name']}** x{s['qty_sold']} = `${s['total']:.2f}` (by {s['logged_by']})")

# ── TAB 3: AI Assistant (Simulated) ──
with tab3:
    st.subheader("🤖 Inventory Assistant")
    st.markdown("Ask me about the inventory! I can help with stock levels and alerts.")

    HARDCODED_RESPONSES = {
        "low": "low_stock",
        "low stock": "low_stock",
        "running low": "low_stock",
        "out": "out_of_stock",
        "out of stock": "out_of_stock",
        "unavailable": "out_of_stock",
        "what items": "all_items",
        "show items": "all_items",
        "list items": "all_items",
        "all products": "all_items",
        "categories": "categories",
        "category": "categories",
        "what categories": "categories",
        "help": "help",
        "what can you do": "help",
        "commands": "help",
    }

    def get_response(user_input):
        text = user_input.lower().strip()
        inventory = load_inventory()

        for keyword, intent in HARDCODED_RESPONSES.items():
            if keyword in text:
                if intent == "low_stock":
                    items = [i for i in inventory if 0 < i["stock"] < 5]
                    if not items:
                        return "✅ Great news — no items are low on stock right now!"
                    lines = "\n".join(f"- **{i['name']}**: {i['stock']} left" for i in items)
                    return f"🟡 **Low stock items (less than 5 units):**\n{lines}"

                elif intent == "out_of_stock":
                    items = [i for i in inventory if i["stock"] == 0]
                    if not items:
                        return "✅ No items are currently out of stock!"
                    lines = "\n".join(f"- **{i['name']}**" for i in items)
                    return f"🔴 **Out of stock items:**\n{lines}"

                elif intent == "all_items":
                    if not inventory:
                        return "The inventory is empty."
                    lines = "\n".join(f"- **{i['name']}** ({i['category']}) — ${i['price']:.2f} | Stock: {i['stock']}" for i in inventory)
                    return f"📦 **All products:**\n{lines}"

                elif intent == "categories":
                    cats = sorted(set(i["category"] for i in inventory))
                    return "🗂️ **Available categories:** " + ", ".join(cats)

                elif intent == "help":
                    return (
                        "💡 **I can answer questions like:**\n"
                        "- *What items are low on stock?*\n"
                        "- *What items are out of stock?*\n"
                        "- *Show me all items*\n"
                        "- *What categories do we have?*"
                    )

        return "🤔 I didn't understand that. Try asking about *low stock*, *out of stock*, *all items*, or *categories*. Type **help** to see what I can do!"

    # chat UI
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about inventory...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = get_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
