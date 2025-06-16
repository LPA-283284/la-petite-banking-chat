import streamlit as st
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="LPA Banking", page_icon="📋")
st.title("LPA - BANKING")

if "form_submitted" in st.session_state and st.session_state.form_submitted:
    st.session_state.clear()
    st.rerun()

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
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Ödeme yöntemleri
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", key="amex2")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", key="amex3")
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", key="voucher")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", key="deposit_minus")
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", key="deliveroo")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", key="ubereats")
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", key="petty_cash")
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", key="deposit_plus")
tips_credit_card = st.number_input("Tips (CC) (£)", min_value=0.0, format="%.2f", key="tips_credit_card")
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", key="tips_sc")
cash_envelope = st.number_input("Cash in Envelope (£)", min_value=0.0, format="%.2f", key="cash_envelope")
float_val = st.number_input("Float (£)", min_value=75.00, format="%.2f", value=75.00, key="float_val")

# Yeni hesaplama: Diğer düşüler ve eklenenler
outflows = sum((cc1, cc2, cc3, amex1, amex2, amex3, voucher, deposit_minus, deliveroo, ubereats, petty_cash))
inflows = sum((deposit_plus, tips_credit_card, tips_sc))

total_adjusted_balance = calculated_taken_in - outflows + inflows
st.markdown(f"### 📊 Adjusted Net Cash Flow: £{total_adjusted_balance:.2f}")

# Google Sheets bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
info = json.loads(json_data)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(credentials)
sheet = client.open("La Petite Banking Extended").sheet1

# Form gönderme
if st.button("Verileri Gönder"):
    row = [str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
           staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
           deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
           tips_sc, total_adjusted_balance, cash_envelope, float_val]

    sheet.append_row(row, value_input_option="USER_ENTERED")
    st.success("Veriler Google Sheets'e başarıyla gönderildi!")
    st.session_state["form_submitted"] = True
    st.rerun()
