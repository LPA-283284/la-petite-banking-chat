
import streamlit as st
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Form başarıyla gönderildiyse, state temizlenip sayfa sıfırlanır
if st.session_state.get("form_submitted", False):
    st.session_state.clear()
    st.rerun()

st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")
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

calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Kart ve ödeme girişleri
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", key="amex2")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", key="amex3")
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", key="voucher")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", key="deposit_minus")
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", key="deposit_plus")
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", key="deliveroo")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", key="ubereats")
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", key="petty_cash")
tips_credit_card = st.number_input("Tips (CC) (£)", min_value=0.0, format="%.2f", key="tips_credit_card")
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", key="tips_sc")
cash_envelope = st.number_input("Cash in Envelope (£)", min_value=0.0, format="%.2f", key="cash_envelope")
float_val = st.number_input("Float (£)", min_value=75.00, format="%.2f", key="float_val")

# Hesaplama
calculated_till_balance = calculated_taken_in - (
    cc1 + cc2 + cc3 + amex1 + amex2 + amex3 + voucher +
    deposit_plus + deliveroo + ubereats + petty_cash
)
st.markdown(f"### 🧾 Till Balance (Calculated): £{calculated_till_balance:.2f}")

# Diğer metinler
item_missing_kitchen = st.text_area("Missing Items in Kitchen")
item_missing_floor = st.text_area("Missing Items on Floor")
eat_out = st.text_input("Eat Out to Help Out")
comments = st.text_area("Customer Reviews")
manager = st.text_input("Manager")
floor_staff = st.text_input("Service Personnel")
kitchen_staff = st.text_input("Kitchen Staff")

# Google Sheets bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
info = json.loads(json_data)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(credentials)
sheet = client.open("La Petite Banking Extended").sheet1

# Butona basılınca veriyi gönder ve formu sıfırla
if st.button("Submit"):
    row = [
        str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
        deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
        tips_sc, calculated_till_balance, cash_envelope, float_val,
        item_missing_kitchen, item_missing_floor, eat_out,
        comments, manager, floor_staff, kitchen_staff
    ]

    sheet.append_row(row)
    st.success("Data successfully sent!")
    st.session_state["form_submitted"] = True
    st.rerun()


