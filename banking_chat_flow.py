import streamlit as st
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Banking Genişlemiş Giriş", page_icon="📊")
st.title("La Petite Auberge - Genişlemiş Banking Formu")

st.markdown("Aşağıdaki alanları doldurarak detaylı banking bilgilerini girebilirsiniz.")

today = datetime.date.today()
date = st.date_input("Tarih", today)

# Satışlar ve ödemeler
cash_total = st.number_input("Kasa Toplamı (£)", min_value=0.0, format="%.2f")
gross_total = st.number_input("Brüt Satış Tutarı (£)", min_value=0.0, format="%.2f")
net_total = st.number_input("Net Satış Tutarı (£)", min_value=0.0, format="%.2f")
service_charge = st.number_input("Servis Ücreti (£)", min_value=0.0, format="%.2f")
discount_total = st.number_input("Toplam İndirim (£)", min_value=0.0, format="%.2f")
complimentary_total = st.number_input("İkramlar (£)", min_value=0.0, format="%.2f")
staff_food = st.number_input("Personel Yemeği (£)", min_value=0.0, format="%.2f")

total_taken_in = st.number_input("Toplam Alınan Tutar (£)", min_value=0.0, format="%.2f")
total_final = st.number_input("Genel Toplam (£)", min_value=0.0, format="%.2f")

# Kredi kartları
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f")

# Amex
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f")

# Diğer öğeler
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f")
tips_cash = st.number_input("Bahşiş (Nakit) (£)", min_value=0.0, format="%.2f")
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f")
deposit = st.number_input("Kapora / Deposit (£)", min_value=0.0, format="%.2f")

# Sipariş platformları
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f")

# Diğer bilgiler
till_balance = st.number_input("Kasadaki Para Miktarı (£)", min_value=0.0, format="%.2f")
cash_envelope = st.number_input("Zarf içindeki Nakit (£)", min_value=0.0, format="%.2f")
float_val = st.number_input("Float (£)", min_value=0.0, format="%.2f")
total_hours = st.number_input("Toplam Çalışma Saati (Mutfak + Servis)", min_value=0.0, format="%.2f")

item_missing_kitchen = st.text_input("Mutfakta Eksik Olanlar")
item_missing_floor = st.text_input("Serviste Eksik Olanlar")
eat_out = st.text_input("Eat Out to Help Out")
comments = st.text_area("Müşteri Yorumları")
manager = st.text_input("Yönetici")
floor_staff = st.text_input("Servis Personeli")
kitchen_staff = st.text_input("Mutfak Personeli")

# Google Sheets bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("google_sheets_credentials.json", scope)
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