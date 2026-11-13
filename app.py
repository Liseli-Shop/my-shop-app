import streamlit as st
import os
from datetime import date
import pandas as pd
from io import BytesIO

# --- MAKE IT BEAUTIFUL ---
st.set_page_config(page_title="My Shop", page_icon="🛒")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .big-total {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #28a745;
    }
    .big-total h2 { color: #155724; margin: 0; }
    .big-total h1 { color: #155724; margin: 0; font-size: 45px; }
    div[data-testid="stFormSubmitButton"] button {
        background-color: #28a745;
        color: white;
        font-size: 18px;
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
        padding: 10px;
    }
    .download-box {
        background-color: #eef2ff;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #a5b4fc;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛒 My Shop Sales App</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: grey;'>Today: {date.today()} | Lusaka, Zambia</p>", unsafe_allow_html=True)
st.write("---")

# --- ADD SALE FORM ---
with st.form("sale_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("🛍️ Product name")
        price = st.number_input("💰 Price per item (K)", min_value=0.0)
    with col2:
        quantity = st.number_input("📦 How many sold", min_value=0, step=1)
        st.write("")
        st.write("")
    submitted = st.form_submit_button("➕ Add Sale")
    if submitted:
        if product == "":
            st.error("Please enter a product name")
        else:
            product = product.strip().title()
            total = price * quantity
            today = date.today()
            with open("sales.txt", "a") as file:
                file.write(f"{product},{price},{quantity},{total},{today}\n")
            st.success(f"✅ Saved! {product} = K {total:.2f}")

# --- SHOW TOTALS ---
st.write("---")

if os.path.exists("sales.txt"):
    # Read all sales once
    all_lines = []
    all_dates = []
    with open("sales.txt", "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 5:
                all_lines.append(parts)
                if parts[4] not in all_dates:
                    all_dates.append(parts[4])
    all_dates.sort(reverse=True)  # Newest first

    today_str = str(date.today())

    # ===== 1. DASHBOARD - ALWAYS TODAY =====
    grouped_today = {}
    grand_total_today = 0
    total_items_today = 0
    for parts in all_lines:
        name, p, q, t, d = parts[0], float(parts[1]), int(parts[2]), float(parts[3]), parts[4]
        if d != today_str:
            continue
        key = (name, p)
        if key not in grouped_today:
            grouped_today[key] = {"Product": name, "Price": p, "Qty": 0, "Total": 0.0, "Date": d}
        grouped_today[key]["Qty"] += q
        grouped_today[key]["Total"] += t
        grouped_today[key]["Date"] = d
        grand_total_today += t
        total_items_today += q

    if grouped_today:
        st.markdown(f"""
        <div class="big-total">
            <h2>💰 Today's Total Sales - {today_str}</h2>
            <h1>K {grand_total_today:.2f}</h1>
            <p>{total_items_today} items sold | {len(grouped_today)} different products</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.subheader(f"📋 Today's Sales - {today_str}")
        sales_table_today = []
        for item in grouped_today.values():
            sales_table_today.append({
                "Product": item["Product"],
                "Price": f"K {item['Price']:.2f}",
                "Qty": item["Qty"],
                "Total": f"K {item['Total']:.2f}",
                "Last Date": item["Date"]
            })
        st.table(sales_table_today)
    else:
        st.info(f"No sales yet for today ({today_str}) - Add your first sale above!")

    st.write("---")

    # ===== 2. DOWNLOAD SECTION - OWNER CHOOSES DATE =====
    st.subheader("📥 Download Sales Report")
    st.markdown('<div class="download-box">', unsafe_allow_html=True)
    st.write("Choose what you want to download:")

    # Default = Today, options = Today + All Dates + all other dates
    download_options = [today_str, "All Dates"] + [d for d in all_dates if d != today_str]
    download_date = st.selectbox("Download for:", download_options, key="download_date")

    # Build table for download based on chosen date
    grouped_download = {}
    grand_total_dl = 0
    total_items_dl = 0
    for parts in all_lines:
        name, p, q, t, d = parts[0], float(parts[1]), int(parts[2]), float(parts[3]), parts[4]
        if download_date != "All Dates" and d != download_date:
            continue
        key = (name, p)
        if key not in grouped_download:
            grouped_download[key] = {"Product": name, "Price": p, "Qty": 0, "Total": 0.0, "Date": d}
        grouped_download[key]["Qty"] += q
        grouped_download[key]["Total"] += t
        grouped_download[key]["Date"] = d
        grand_total_dl += t
        total_items_dl += q

    if grouped_download:
        st.write(f"**Preview for {download_date}:** {total_items_dl} items, Total: K {grand_total_dl:.2f}")
        sales_table_dl = []
        for item in grouped_download.values():
            sales_table_dl.append({
                "Product": item["Product"],
                "Price": f"K {item['Price']:.2f}",
                "Qty": item["Qty"],
                "Total": f"K {item['Total']:.2f}",
                "Last Date": item["Date"]
            })
        # Small preview
        st.dataframe(sales_table_dl, use_container_width=True, hide_index=True)

        df = pd.DataFrame(sales_table_dl)
        df.loc[len(df)] = ["GRAND TOTAL", "", total_items_dl, f"K {grand_total_dl:.2f}", ""]
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sales')
        excel_data = output.getvalue()

        file_name = f"sales_{download_date}.xlsx" if download_date != "All Dates" else f"sales_All_Dates_{date.today()}.xlsx"
        st.download_button(
            label=f"📥 Download Excel for {download_date}",
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info(f"No sales for {download_date}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    if st.button("🗑️ Clear All Sales"):
        os.remove("sales.txt")
        st.rerun()
else:
    st.info("No sales yet - Add your first sale above!")