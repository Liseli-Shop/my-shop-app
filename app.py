import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="My Shop", page_icon="🛒")
st.title("🛒 My Shop Sales App")
st.write(f"Today: {date.today()} | Lusaka, Zambia")

if "sales" not in st.session_state:
    st.session_state.sales = []

# --- ADD SALE ---
st.subheader("Add New Sale")
product = st.text_input("Product name")
qty = st.number_input("How many sold", min_value=0, step=1, value=1)
price = st.number_input("Price per item (K)", min_value=0.0, step=1.0)

if st.button("➕ Add Sale", type="primary"):
    if not product.strip():
        st.error("Please type a product name!")
    elif qty <= 0:
        st.error("Quantity must be more than 0! You can't sell 0 items.")
    elif price <= 0:
        st.error("Price must be more than 0!")
    else:
        total = qty * price
        st.session_state.sales.append({
            "Product": product.strip(),
            "Price": price,
            "Qty": qty,
            "Total": total,
            "Last Date": str(date.today())
        })
        st.success(f"Saved! {product} = K {total:.2f}")

# --- TOTALS ---
today_sales = st.session_state.sales
total_sales = sum(s["Total"] for s in today_sales)
total_items = sum(s["Qty"] for s in today_sales)

st.markdown(f"""
<div style="background-color:#d4edda; padding:20px; border-radius:10px; text-align:center;">
<h2>💰 Today's Total Sales - {date.today()}</h2>
<h1>K {total_sales:.2f}</h1>
<p>{total_items} items sold | {len(today_sales)} different products</p>
</div>
""", unsafe_allow_html=True)

# --- LIST WITH DELETE ---
st.subheader(f"📋 Today's Sales - {date.today()}")

if len(today_sales) == 0:
    st.info("No sales yet today. Add your first sale above!")
else:
    for i, s in enumerate(today_sales):
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        col1.write(f"**{s['Product']}**")
        col2.write(f"K {s['Price']:.2f}")
        col3.write(f"Qty: {s['Qty']}")
        col4.write(f"K {s['Total']:.2f}")
        if col5.button("🗑️ Delete", key=f"del_{i}"):
            st.session_state.sales.pop(i)
            st.rerun()

# --- DOWNLOAD ---
st.subheader("📥 Download Sales Report")
if len(today_sales) > 0:
    df = pd.DataFrame(today_sales)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download as Excel / CSV", csv, "sales.csv", "text/csv")
