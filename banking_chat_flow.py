import streamlit as st
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Sayfa ayarı
st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

# Form gönderildiyse sıfırlama
if "form_submitted" in st.session_state and st.session_state.form_submitted:
    st.session_state.clear()
    st.rerun()

st.markdown("You can enter detailed banking information by filling in the fields below.")

# Tarih
today = datetime.date.today()
date = st.date_input("Date", today)

# Girişler
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=0.0, key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=0.0, key="net_total")
service_charge_main = st.number_input("Service Charge (Main) (£)", min_value=0.0, format="%.2f", value=0.0, key="service_charge_main")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=0.0, key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=0.0, key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=0.0, key="staff_food")

# Hesaplama: Taken In
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Ödeme yöntemleri
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=0.0, key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=0.0, key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=0.0, key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=0.0, key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=0.0, key="amex2")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=0.0, key="amex3")
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=0.0, key="voucher")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=0.0, key="deposit_minus")
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=0.0, key="deliveroo")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=0.0, key="ubereats")
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=0.0, key="petty_cash")
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", value=0.0, key="deposit_plus")
tips_credit_card = st.number_input("Tips (CC) (£)", min_value=0.0, format="%.2f", value=0.0, key="tips_credit_card")
tips_sc = st.number_input("Service Charge (Tips) (£)", min_value=0.0, format="%.2f", value=0.0, key="tips_sc")
cash_envelope = st.number_input("Cash in Envelope (£)", min_value=0.0, format="%.2f", value=0.0, key="cash_envelope")
float_val = st.number_input("Float (£)", min_value=75.0, format="%.2f", value=75.0, key="float_val")

# Hesaplama: Till Balance
calculated_till_balance = calculated_taken_in - (
    cc1 + cc2 + cc3 + amex1 + amex2 + amex3 +
    voucher + deposit_plus + deliveroo + ubereats + petty_cash
)
st.markdown(f"### 🧾 Till Balance (Calculated): £{calculated_till_balance:.2f}")

# Metin alanları
item_missing_kitchen = st.text_area("Deposits Note", key="text_deposits")
item_missing_floor = st.text_area("Petty Cash Note", key="text_petty")
eat_out = st.text_input("Eat Out to Help Out", key="text_eatout")
comments = st.text_area("Customer Reviews", key="text_comments")
manager = st.text_input("Manager", key="text_manager")
floor_staff = st.text_input("Service Personnel", key="text_floor")
kitchen_staff = st.text_input("Kitchen Staff", key="text_kitchen")

# Google Sheets bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
info = json.loads(json_data)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(credentials)
sheet = client.open("La Petite Banking Extended").sheet1

# Form gönderme
if st.button("Submit"):
    row = [str(date), gross_total, net_total, service_charge_main, discount_total, complimentary_total,
           staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
           deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
           tips_sc, calculated_till_balance, cash_envelope, float_val,
           item_missing_kitchen, item_missing_floor, eat_out,
           comments, manager, floor_staff, kitchen_staff]

    sheet.append_row(row, value_input_option="USER_ENTERED")
    st.success("✅ Data successfully sent!")

    # Sayfayı sıfırla
    st.session_state["form_submitted"] = True
    st.rerun()

