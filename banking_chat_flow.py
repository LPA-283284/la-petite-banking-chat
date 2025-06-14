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

# Satışlar ve ödemeler
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")

# Otomatik hesaplama
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Kredi kartları
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")

# Amex
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")

# Diğer öğeler
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deposit_minus")

# Sipariş platformları
Deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
Ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
Petty_Cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")

# Otomatik Till Balance
calculated_till_balance = calculated_taken_in - (cc1 + cc2 + cc3 + amex1 +amex2+ amex3 + voucher + deposit + deliveroo + ubereats + Petty_Cash)
st.markdown(f"### 🧾 Till Balance (Calculated): £{calculated_till_balance:.2f}")

# Diğer bilgiler
deposit = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", key="deposit1", value=None, placeholder="0.00", key="gross_total")
tips_credit_card = st.number_input("Tips (CC) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
till_balance = st.number_input("Till Balance (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
cash_envelope = st.number_input("Cash in Envelope (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
float_val = st.number_input("Float (£)", min_value=75.00, format="%.2f", value=None, placeholder="0.00", key="gross_total")


item_missing_kitchen = st.text_input("Mutfakta Eksik Olanlar")
item_missing_floor = st.text_input("Serviste Eksik Olanlar")
eat_out = st.text_input("Eat Out to Help Out")
comments = st.text_area("Müşteri Yorumları")
manager = st.text_input("Yönetici")
floor_staff = st.text_input("Servis Personeli")
kitchen_staff = st.text_input("Mutfak Personeli")

# Google Sheets bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
info = json.loads(json_data)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)

client = gspread.authorize(credentials)
sheet = client.open("La Petite Banking Extended").sheet1

if st.button("Verileri Gönder"):
    row = [str(date), cash_total, gross_total, net_total, service_charge, discount_total, complimentary_total,
           staff_food, total_taken_in, total_final, cc1, cc2, cc3, amex1, amex2, amex3, voucher, tips_cash,
           tips_sc, deposit, deliveroo, ubereats, till_balance, cash_envelope, float_val, total_hours,
           item_missing_kitchen, item_missing_floor, eat_out, comments, manager, floor_staff, kitchen_staff]

    sheet.append_row(row)
    st.success("Veriler Google Sheets'e başarıyla gönderildi!")

    columns = ["Tarih", "Kasa", "Brüt", "Net", "Servis", "İndirim", "İkram", "Personel Yemeği", "Toplam Alınan", "Genel Toplam",
               "CC1", "CC2", "CC3", "Amex1", "Amex2", "Amex3", "Voucher", "Bahşiş Nakit", "Servis Charge", "Kapora",
               "Deliveroo", "Uber Eats", "Kasa Bakiyesi", "Zarf Nakit", "Float", "Toplam Saat",
               "Eksik Mutfak", "Eksik Servis", "Eat Out", "Yorumlar", "Yönetici", "Servis Personeli", "Mutfak Personeli"]

    df = pd.DataFrame([row], columns=columns)
    st.dataframe(df)
