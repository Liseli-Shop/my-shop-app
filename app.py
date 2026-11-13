import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="My Shop", page_icon="🛒", layout="centered")

# --- GREEN BEAUTIFUL STYLE ---
st.markdown("""
<style>
    .main { background-color: #f0f9f0; }
    h1 { color: #1a7a1a !important; text-align: center; }
    .big-card {
        background: linear-gradient(135deg, #1a7a1a, #2ecc71);
        padding: 25px; border-radius: 20px; text-align: center; color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .big-card h1 { color: white !important; font-size: 48px; margin: 0; }
    .big-card h2 { color: white !important; }
    .stButton > button {
        background-color: #1a7a1a !important; color: white !important;
        border-radius: 12px !important; font-weight: bold !important;
        padding: 10px 20px !important; border: none !important;
    }
    .stButton > button:hover { background-color: #145a14 !important; }
</style>
""", unsafe_allow_html=True)

# --- PASSWORD LOCK ---
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    st.title("🛒 My Shop")
    st.markdown("### 🔒 This shop is private")
    st.write("Enter password to see your sales:")
    pwd = st.text_input("Password", type="password")
    if st.button("🔓 Unlock My Shop", type="primary"):
        if pwd == "liseli2016":
            st.session_state.unlocked = True
            st.success("Welcome back, Liseli! 💚")
            st.rerun()
        else:
            st.error("Wrong password! Try again.")
    st.stop()

# --- MAIN APP (only if unlocked) ---
st.title("🛒 My Shop Sales App")
st.markdown("<p style='text-align:center; color:#555;'>💚 Liseli's Shop | Lusaka, Zambia</p>", unsafe_allow_html=True)
st.write(f"📅 Today: {date.today()}")

FILE = "sales.csv"

def load_sales():
    if os.path.exists(FILE):
        try:
            return pd.read_csv(FILE).to_dict("records")
        except:
            return []
    return []

def save_sales(sales):
    pd.DataFrame(sales).to_csv(FILE, index=False)

if "sales" not in st.session_state:
    st.session_state.sales = load_sales()

# --- ADD SALE ---
st.markdown("### ➕ Add New Sale")
product = st.text_input("Product name")
col_a, col_b = st.columns(2)
with col_a:
    qty = st.number_input("How many sold", min_value=0, step=1, value=1)
with col_b:
    price = st.number_input("Price per item (K)", min_value=0.0, step=1.0)

if st.button("➕ Add Sale", type="primary"):
    if not product.strip():
        st.error("Please type a product name!")
    elif qty <= 0:
        st.error("Quantity must be more than 0!")
    elif price <= 0:
        st.error("Price must be more than 0!")
    else:
        total = qty * price
        st.session_state.sales.append({
            "Product": product.strip(),
            "Price": price,
            "Qty": qty,
            "Total": total,
            "Date": str(date.today())
        })
        save_sales(st.session_state.sales)
        st.success(f"Saved! {product} = K {total:.2f}")
        st.rerun()

# --- TOTALS ---
today_str = str(date.today())
today_sales = [s for s in st.session_state.sales if str(s.get("Date", today_str)) == today_str]
total_sales = sum(float(s["Total"]) for s in today_sales)
total_items = sum(int(s["Qty"]) for s in today_sales)

st.markdown(f"""
<div class="big-card">
<h2>💰 Today's Total Sales</h2>
<h1>K {total_sales:.2f}</h1>
<p>✨ {total_items} items sold | {len(today_sales)} products | {today_str}</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- LIST ---
st.markdown(f"### 📋 Today's Sales - {today_str}")
if len(today_sales) == 0:
    st.info("No sales yet today. Add your first sale above!")
else:
    for s in today_sales:
        idx = st.session_state.sales.index(s)
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
        c1.write(f"**{s['Product']}**")
        c2.write(f"K {float(s['Price']):.2f}")
        c3.write(f"Qty: {int(s['Qty'])}")
        c4.write(f"**K {float(s['Total']):.2f}**")
        if c5.button("🗑️", key=f"del_{idx}"):
            st.session_state.sales.pop(idx)
            save_sales(st.session_state.sales)
            st.rerun()

# --- DOWNLOAD + LOCK ---
st.markdown("### 📥 Download Report")
if len(st.session_state.sales) > 0:
    df = pd.DataFrame(st.session_state.sales)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download as Excel / CSV", csv, "sales.csv", "text/csv")

if st.button("🔒 Lock Shop"):
    st.session_state.unlocked = False
    st.rerun()
