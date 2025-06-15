import streamlit as st
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")
st.markdown("You can enter detailed banking information by filling in the fields below.")

today = datetime.date.today()
date = st.date_input("Date", today)

# Girişler
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="net_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="service_charge")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="staff_food")
calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex2")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex3")
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="voucher")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deposit_minus")
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deliveroo")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="ubereats")
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="petty_cash")
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deposit_plus")
tips_credit_card = st.number_input("Tips (CC) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_credit_card")
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_sc")
cash_envelope = st.number_input("Cash in Envelope (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cash_envelope")

# Hesaplamalar (None korumalı)

calculated_till_balance = (calculated_taken_in or 0.0) - (
    (cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) +
    (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
    (voucher or 0.0) + (deposit_plus or 0.0) +
    (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)
)

st.markdown(f"### 🧾 Till Balance (Calculated): £{calculated_till_balance:.2f}")
float_val = st.number_input("Float (£)", min_value=75.00, format="%.2f", value=None, placeholder="75.00", key="float_val")
# Diğer metin alanları
item_missing_kitchen = st.text_area("Deposits")
item_missing_floor = st.text_area("Petty Cash")
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

if st.button("Submit"):
    row = [str(date), gross_total, net_total, service_charge, discount_total, complimentary_total, staff_food,
           calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher, deposit_plus, deposit_minus,
           deliveroo, ubereats, petty_cash, tips_credit_card, tips_sc, calculated_till_balance,
           cash_envelope, float_val, item_missing_kitchen, item_missing_floor, eat_out,
           comments, manager, floor_staff, kitchen_staff]

    sheet.append_row(row)
    st.success("Data successfully sent it!")
    if st.button("Verileri Gönder"):
    row = [str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
           staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
           deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
           tips_sc, calculated_till_balance, cash_envelope, float_val,
           item_missing_kitchen, item_missing_floor, eat_out,
           comments, manager, floor_staff, kitchen_staff]

    sheet.append_row(row)
    st.success("Veriler Google Sheets'e başarıyla gönderildi!")
    
