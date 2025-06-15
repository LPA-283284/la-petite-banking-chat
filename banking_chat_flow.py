import streamlit as st
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

# Sayfa yeniden yüklendiyse girişleri temizle
if st.session_state.get("form_submitted"):
    st.session_state.clear()
    st.experimental_rerun()

st.markdown("You can enter detailed banking information by filling in the fields below.")

today = datetime.date.today()
date = st.date_input("Date", today)

# Girişler
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", key="net_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", key="service_charge")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", key="staff_food")

# Hesaplama: Taken In
calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Kartlar ve diğer gelirler
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", key="amex2")
amex3 = st.number_input("Amex_

