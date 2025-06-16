import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

# Form reset
if "form_submitted" in st.session_state and st.session_state.form_submitted:
    st.session_state.clear()
    st.rerun()

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


# Taken In
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Ödeme Yöntemleri
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
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_credit_card")
tips_credit_card = st.number_input("Tips (CC) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_sc")


# Calculated Fields
calculated_till_balance = calculated_taken_in - (
    cc1 + cc2 + cc3 + amex1 + amex2 + amex3 +
    voucher + deposit_plus + deliveroo + ubereats + petty_cash
)

adjusted_net_cash_flow = (
    calculated_taken_in
    - cc1 - cc2 - cc3 - amex1 - amex2 - amex3
    - voucher - deposit_minus - deliveroo - ubereats - petty_cash
    + deposit_plus + tips_credit_card + tips_sc
)

st.markdown(f"### 🧾 Till Balance (Calculated): £{calculated_till_balance:.2f}")
st.markdown(f"### 💼 Adjusted Net Cash Flow: £{adjusted_net_cash_flow:.2f}")

# Diğer Alanlar
item_missing_kitchen = st.text_area("Deposits Note")
item_missing_floor = st.text_area("Petty Cash Note")
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

# Gönderme
if st.button("Verileri Gönder"):
    row = [
        str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
        deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
        tips_sc, calculated_till_balance, adjusted_net_cash_flow, cash_envelope, float_val,
        item_missing_kitchen, item_missing_floor, eat_out,
        comments, manager, floor_staff, kitchen_staff
    ]

    sheet.append_row(row, value_input_option="USER_ENTERED")
    st.success("✅ Veriler Google Sheets'e başarıyla gönderildi!")
    st.session_state["form_submitted"] = True
    st.rerun()
