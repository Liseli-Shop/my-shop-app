import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Liseli Shop", page_icon="🛒")

# --- PASSWORD ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#1E7A34;'>🛒 Liseli Shop</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Welcome! Please enter password</p>", unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password")
    if st.button("Login", type="primary"):
        if pwd == "liseli2016":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong password!")
    st.stop()

# --- GREEN STYLE ---
st.markdown("""
<style>
.stApp { background-color: #F0FFF4; }
.stButton>button { background-color: #1E7A34 !important; color: white !important; border-radius: 10px; }
h1, h2, h3 { color: #1E7A34; }
</style>
""", unsafe_allow_html=True)

st.title("🛒 Liseli Shop - Sales & Stock")

# --- LOAD DATA ---
SALES_FILE = "sales.csv"
STOCK_FILE = "stock.csv"

def load_sales():
    if os.path.exists(SALES_FILE):
        return pd.read_csv(SALES_FILE).to_dict("records")
    return []

def save_sales(data):
    pd.DataFrame(data).to_csv(SALES_FILE, index=False)

def load_stock():
    if os.path.exists(STOCK_FILE):
        df = pd.read_csv(STOCK_FILE)
        return dict(zip(df["Product"], df["Qty"]))
    return {}

def save_stock(stock_dict):
    pd.DataFrame([{"Product": k, "Qty": v} for k, v in stock_dict.items()]).to_csv(STOCK_FILE, index=False)

if "sales" not in st.session_state:
    st.session_state.sales = load_sales()
if "stock" not in st.session_state:
    st.session_state.stock = load_stock()

# --- TODAY'S TOTAL ---
today_sales = [s for s in st.session_state.sales if str(s.get("Date")) == str(date.today())]
today_total = sum(float(s.get("Total", 0)) for s in today_sales)
st.markdown(f"### 💰 Today's Sales: K {today_total:.2f}  |  🧾 Items Sold: {len(today_sales)}")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Sell", "📦 Stock", "📊 Report"])

with tab1:
    st.markdown("### ➕ Add New Sale")
    
    def add_sale():
        product = st.session_state.get("prod_name", "").strip()
        qty = st.session_state.get("prod_qty", 1)
        price = st.session_state.get("prod_price", 0.0)
        if not product:
            st.session_state.msg = "Please type a product name!"
            return
        if qty <= 0:
            st.session_state.msg = "Quantity must be more than 0!"
            return
        if price <= 0:
            st.session_state.msg = "Price must be more than 0!"
            return
        # Check stock
        current_stock = st.session_state.stock.get(product, 0)
        if current_stock < qty:
            st.session_state.msg = f"Not enough stock! You only have {current_stock} of {product} left."
            return
        
        total = qty * price
        st.session_state.sales.append({"Product": product, "Price": price, "Qty": qty, "Total": total, "Date": str(date.today())})
        save_sales(st.session_state.sales)
        # Reduce stock
        st.session_state.stock[product] = current_stock - qty
        save_stock(st.session_state.stock)
        st.session_state.msg = f"Saved! {product} = K {total:.2f} | Stock left: {st.session_state.stock[product]}"
        st.session_state.prod_name = ""
        st.session_state.prod_qty = 1
        st.session_state.prod_price = 0.0

    product = st.text_input("Product name", key="prod_name")
    # Show stock for this product
    if product.strip() and product.strip() in st.session_state.stock:
        st.info(f"📦 In Stock: {st.session_state.stock[product.strip()]}")
    elif product.strip():
        st.warning("⚠️ This product has 0 stock - Add stock first in Stock tab!")
    
    col_a, col_b = st.columns(2)
    with col_a:
        qty = st.number_input("How many sold", min_value=0, step=1, value=1, key="prod_qty")
    with col_b:
        price = st.number_input("Price per item (K)", min_value=0.0, step=1.0, key="prod_price")
    
    st.button("➕ Add Sale", type="primary", on_click=add_sale)
    if "msg" in st.session_state and st.session_state.msg:
        if "Saved!" in st.session_state.msg:
            st.success(st.session_state.msg)
        else:
            st.error(st.session_state.msg)
        st.session_state.msg = ""

    st.markdown("---")
    st.markdown("### Today's Sales")
    if today_sales:
        st.dataframe(pd.DataFrame(today_sales), use_container_width=True)
    else:
        st.write("No sales yet today.")

with tab2:
    st.markdown("### 📦 Add Stock")
    st.write("Add stock when you buy new items from the market.")
    
    def add_stock():
        p = st.session_state.get("stock_name", "").strip()
        q = st.session_state.get("stock_qty", 1)
        if not p:
            st.session_state.stock_msg = "Type product name!"
            return
        if q <= 0:
            st.session_state.stock_msg = "Quantity must be more than 0!"
            return
        st.session_state.stock[p] = st.session_state.stock.get(p, 0) + q
        save_stock(st.session_state.stock)
        st.session_state.stock_msg = f"Added! {p} now has {st.session_state.stock[p]} in stock."
        st.session_state.stock_name = ""
        st.session_state.stock_qty = 1

    st.text_input("Product name", key="stock_name")
    st.number_input("How many are you adding?", min_value=0, step=1, value=1, key="stock_qty")
    st.button("📦 Add Stock", type="primary", on_click=add_stock)
    if "stock_msg" in st.session_state and st.session_state.stock_msg:
        st.success(st.session_state.stock_msg)
        st.session_state.stock_msg = ""
    
    st.markdown("---")
    st.markdown("### 📦 Current Stock")
    if st.session_state.stock:
        stock_df = pd.DataFrame([{"Product": k, "Qty Left": v, "Status": "⚠️ LOW - Buy More!" if v <= 5 else "✅ OK"} for k, v in st.session_state.stock.items()])
        st.dataframe(stock_df, use_container_width=True)
    else:
        st.write("No stock yet. Add some above!")

with tab3:
    st.markdown("### 📊 All Sales Report")
    if st.session_state.sales:
        df = pd.DataFrame(st.session_state.sales)
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total All Time: K {df['Total'].sum():.2f}**")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Report (CSV)", csv, "sales_report.csv", "text/csv")
    else:
        st.write("No sales yet.")
