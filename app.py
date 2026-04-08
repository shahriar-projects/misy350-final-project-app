import streamlit as st
import json

st.set_page_config(page_title="StoreHQ - Inventory Manager", page_icon="🏪", layout="centered")

# ---------- helpers ----------
def load_users():
    with open("data/users.json", "r") as f:
        return json.load(f)

def login(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None

# ---------- session defaults ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ---------- redirect if already logged in ----------
if st.session_state.logged_in:
    role = st.session_state.user["role"]
    if role == "Shop Owner":
        st.switch_page("pages/owner_dashboard.py")
    else:
        st.switch_page("pages/employee_dashboard.py")

# ---------- login UI ----------
st.title("🏪 StoreHQ")
st.subheader("Inventory Management System")
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True, type="primary"):
        if username and password:
            user = login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter both username and password.")

    st.markdown("---")
    st.caption("**Demo Accounts:**")
    st.caption("Shop Owner → `owner1` / `owner123`")
    st.caption("Employee → `employee1` / `emp123`")
