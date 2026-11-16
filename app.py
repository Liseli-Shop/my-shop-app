import streamlit as st
import pandas as pd
from datetime date import date
import os

st.set_page_config(page_title="Liseli Shop", page_icon="🛒")

# --- PASSWORDS ---
OWNER_PASSWORD = "liseli2016"
SALES_PASSWORD = "sales123"  # Change this to what you want to give worker!

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#1E7A34;'>🛒 Liseli Shop</h1>", unsafe_allow_html=True)
    st.write("Welcome! Please login:")
    pwd = st.text_input("Password", type="password")
    if st.button("Login", type="primary"):
        if pwd == OWNER_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.role = "owner"
            st.rerun()
        elif pwd == SALES_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.role = "sales"
            st.rerun()
        else:
            st.error("Wrong password!")
    st.stop()

# Logout button
col_top1, col_top2 = st.columns([4, 1])
with col_top1:
    if st.session_state.role == "owner":
        st.markdown("👑 **Logged in as: OWNER**")
    else:
        st.markdown("👩‍💼 **Logged in as: SALES PERSON**")
with col_top2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.rerun()

st.markdown("""
<style>
.stApp { background-color: #F0FFF4; }
.stButton>button { background-color: #1E7A34 !important; color: white !important; border-radius: 10px; }
h1, h2, h3 { color: #1E7A34; }
</style>
""", unsafe_allow_html=True)

st.title("🛒 Liseli Shop - Sales & Stock")

def clean_name(name):
    return " ".join(word.capitalize() for word in str(name).strip().split())

SALES_FILE = "sales.csv"
STOCK_FILE = "stock.csv"
BARCODE_FILE = "barcodes.csv"

def load_sales():
    if os.path.exists(SALES_FILE):
        df = pd.read_csv(SALES_FILE)
        if "Product" in df.columns:
            df["Product"] = df["Product"].apply(clean_name)
        return df.to_dict("records")
    return []
def save_sales(data):
    pd.DataFrame(data).to_csv(SALES_FILE, index=False)
def load_stock():
    if os.path.exists(STOCK_FILE):
        df = pd.read_csv(STOCK_FILE)
        stock = {}
        for _, row in df.iterrows():
            name = clean_name(row["Product"])
            stock[name] = stock.get(name, 0) + int(row["Qty"])
        return stock
    return {}
def save_stock(stock_dict):
    pd.DataFrame([{"Product": k, "Qty": v} for k, v in stock_dict.items()]).to_csv(STOCK_FILE, index=False)
def load_barcodes():
    if os.path.exists(BARCODE_FILE):
        df = pd.read_csv(BARCODE_FILE)
        d = {}
        for _, row in df.iterrows():
            code = str(row["Barcode"]).strip()
            d[code] = {"Product": clean_name(row["Product"]), "Price": float(row.get("Price", 0))}
        return d
    return {}
def save_barcodes(bar_dict):
    pd.DataFrame([{"Product": v["Product"], "Barcode": k, "Price": v["Price"]} for k, v in bar_dict.items()]).to_csv(BARCODE_FILE, index=False)

if "sales" not in st.session_state:
    st.session_state.sales = load_sales()
if "stock" not in st.session_state:
    st.session_state.stock = load_stock()
if "barcodes" not in st.session_state:
    st.session_state.barcodes = load_barcodes()

# --- OWNER ONLY: Show Today's Total. Sales person does NOT see money total ---
today_sales = [s for s in st.session_state.sales if str(s.get("Date")) == str(date.today())]
if st.session_state.role == "owner":
    today_total = sum(float(s.get("Total", 0)) for s in today_sales)
    st.markdown(f"### 💰 Today's Sales: K {today_total:.2f}  |  🧾 Items Sold: {len(today_sales)}")
else:
    st.markdown(f"### 🧾 Items Sold Today: {len(today_sales)}  |  Keep selling! 💪")

def delete_sale(index_to_delete):
    sale = st.session_state.sales[index_to_delete]
    prod = clean_name(sale["Product"])
    qty_back = int(sale["Qty"])
    st.session_state.stock[prod] = st.session_state.stock.get(prod, 0) + qty_back
    save_stock(st.session_state.stock)
    st.session_state.sales.pop(index_to_delete)
    save_sales(st.session_state.sales)
    st.session_state.msg = f"Deleted {prod} - Stock returned! {prod} now has {st.session_state.stock[prod]}"

# --- TABS BY ROLE ---
if st.session_state.role == "owner":
    tab1, tab2, tab3 = st.tabs(["➕ Sell", "📦 Stock", "📊 Report 👑 Owner Only"])
else:
    tab1, tab2 = st.tabs(["➕ Sell", "📦 Stock"])
    tab3 = None

with tab1:
    st.markdown("### ➕ Add New Sale")
    st.markdown("**📷 Have a scanner? Click the Barcode box and SCAN!**")
    def lookup_barcode():
        code = str(st.session_state.get("scan_code", "")).strip()
        if not code:
            st.session_state.msg = "Scan or type a barcode first!"
            return
        if code in st.session_state.barcodes:
            info = st.session_state.barcodes[code]
            st.session_state.prod_name = info["Product"]
            st.session_state.prod_price = float(info["Price"])
            st.session_state.msg = f"Found! {info['Product']} - K {info['Price']:.2f}"
        else:
            st.session_state.msg = f"Barcode {code} not found! Add it in Stock tab first."
        st.session_state.scan_code = ""
    st.text_input("🔍 Scan Barcode Here (or type barcode)", key="scan_code", placeholder="Click here then scan...")
    st.button("🔍 Find Product", on_click=lookup_barcode)
    def add_sale():
        product = clean_name(st.session_state.get("prod_name", ""))
        qty = st.session_state.get("prod_qty", 1)
        price = st.session_state.get("prod_price", 0.0)
        if not product:
            st.session_state.msg = "Please type a product name or scan barcode!"
            return
        if qty <= 0:
            st.session_state.msg = "Quantity must be more than 0!"
            return
        if price <= 0:
            st.session_state.msg = "Price must be more than 0!"
            return
        current_stock = st.session_state.stock.get(product, 0)
        if current_stock < qty:
            st.session_state.msg = f"Not enough stock! You only have {current_stock} of {product} left."
            return
        total = qty * price
        st.session_state.sales.append({"Product": product, "Price": price, "Qty": qty, "Total": total, "Date": str(date.today())})
        save_sales(st.session_state.sales)
        st.session_state.stock[product] = current_stock - qty
        save_stock(st.session_state.stock)
        st.session_state.msg = f"Saved! {product} = K {total:.2f} | Stock left: {st.session_state.stock[product]}"
        st.session_state.prod_name = ""
        st.session_state.prod_qty = 1
        st.session_state.prod_price = 0.0
    product_raw = st.text_input("Product name", key="prod_name")
    product = clean_name(product_raw)
    if product and product in st.session_state.stock:
        st.info(f"📦 In Stock: {st.session_state.stock[product]}")
    elif product:
        st.warning("⚠️ This product has 0 stock - Add stock first in Stock tab!")
    col_a, col_b = st.columns(2)
    with col_a:
        qty = st.number_input("How many sold", min_value=0, step=1, value=1, key="prod_qty")
    with col_b:
        price = st.number_input("Price per item (K)", min_value=0.0, step=1.0, key="prod_price")
    st.button("➕ Add Sale", type="primary", on_click=add_sale)
    if "msg" in st.session_state and st.session_state.msg:
        if "Saved!" in st.session_state.msg or "Deleted" in st.session_state.msg or "Found!" in st.session_state.msg:
            st.success(st.session_state.msg)
        else:
            st.error(st.session_state.msg)
        st.session_state.msg = ""
    st.markdown("---")
    st.markdown("### Today's Sales - Delete if wrong")
    if today_sales:
        for i, s in enumerate(st.session_state.sales):
            if str(s.get("Date")) == str(date.today()):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                with c1:
                    st.write(f"{clean_name(s['Product'])}")
                with c2:
                    st.write(f"x{s['Qty']}")
                with c3:
                    # Sales person does NOT see money, Owner sees it
                    if st.session_state.role == "owner":
                        st.write(f"K {float(s['Total']):.2f}")
                    else:
                        st.write("---")
                with c4:
                    if st.button("🗑️ Delete", key=f"del_today_{i}"):
                        delete_sale(i)
                        st.rerun()
    else:
        st.write("No sales yet today.")

with tab2:
    st.markdown("### 📦 Add Stock + Barcode")
    def add_stock():
        p = clean_name(st.session_state.get("stock_name", ""))
        q = st.session_state.get("stock_qty", 1)
        code = str(st.session_state.get("stock_barcode", "")).strip()
        price = st.session_state.get("stock_price", 0.0)
        if not p:
            st.session_state.stock_msg = "Type product name!"
            return
        if q <= 0:
            st.session_state.stock_msg = "Quantity must be more than 0!"
            return
        st.session_state.stock[p] = st.session_state.stock.get(p, 0) + q
        save_stock(st.session_state.stock)
        if code:
            st.session_state.barcodes[code] = {"Product": p, "Price": float(price)}
            save_barcodes(st.session_state.barcodes)
        st.session_state.stock_msg = f"Added! {p} now has {st.session_state.stock[p]} in stock. Barcode saved!"
        st.session_state.stock_name = ""
        st.session_state.stock_qty = 1
        st.session_state.stock_barcode = ""
        st.session_state.stock_price = 0.0
    st.text_input("Product name", key="stock_name")
    st.text_input("Barcode (click here and scan product)", key="stock_barcode", placeholder="e.g. 600123456789 or leave empty")
    st.number_input("Price per item (K) - for barcode auto-fill", min_value=0.0, step=1.0, key="stock_price")
    st.number_input("How many are you adding?", min_value=0, step=1, value=1, key="stock_qty")
    st.button("📦 Add Stock", type="primary", on_click=add_stock)
    if "stock_msg" in st.session_state and st.session_state.stock_msg:
        st.success(st.session_state.stock_msg)
        st.session_state.stock_msg = ""
    st.markdown("---")
    st.markdown("### 📦 Current Stock")
    if st.session_state.stock:
        rows = []
        for k, v in st.session_state.stock.items():
            bcode = ""
            price_show = ""
            for code, info in st.session_state.barcodes.items():
                if info["Product"] == k:
                    bcode = code
                    # Sales person should not see price in stock? We hide for safety
                    if st.session_state.role == "owner":
                        price_show = f"K {info['Price']:.2f}"
                    else:
                        price_show = "---"
                    break
            rows.append({"Product": k, "Qty Left": v, "Barcode": bcode, "Price": price_show, "Status": "⚠️ LOW" if v <= 5 else "✅ OK"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.write("No stock yet.")

# --- OWNER ONLY TAB ---
if st.session_state.role == "owner" and tab3 is not None:
    with tab3:
        st.markdown("### 📊 All Sales Report - Owner Only 👑")
        st.write("Only you can see this! Your sales person cannot see this tab.")
        if st.session_state.sales:
            for i, s in enumerate(st.session_state.sales):
                c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
                with c1:
                    st.write(f"{clean_name(s['Product'])} ({s['Date']})")
                with c2:
                    st.write(f"x{s['Qty']}")
                with c3:
                    st.write(f"K {float(s['Total']):.2f}")
                with c4:
                    st.write(f"K {float(s['Price']):.2f} each")
                with c5:
                    if st.button("🗑️", key=f"del_all_{i}"):
                        delete_sale(i)
                        st.rerun()
            df = pd.DataFrame(st.session_state.sales)
            st.markdown(f"**Total All Time: K {df['Total'].sum():.2f}**")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Report (CSV)", csv, "sales_report.csv", "text/csv")
        else:
            st.write("No sales yet.")
