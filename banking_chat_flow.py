import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
import json

st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

if "form_submitted" in st.session_state and st.session_state.form_submitted:
    st.session_state.clear()
    st.rerun()

st.markdown("You can enter detailed banking information by filling in the fields below.")

today = datetime.date.today()
date = st.date_input("Date", today)

gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="net_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="service_charge")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="staff_food")

calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Ödemeler
cc1 = st.number_input("CC 1 (£)", 0.0, format="%.2f")
cc2 = st.number_input("CC 2 (£)", 0.0, format="%.2f")
cc3 = st.number_input("CC 3 (£)", 0.0, format="%.2f")
amex1 = st.number_input("Amex 1 (£)", 0.0, format="%.2f")
amex2 = st.number_input("Amex 2 (£)", 0.0, format="%.2f")
amex3 = st.number_input("Amex 3 (£)", 0.0, format="%.2f")
voucher = st.number_input("Voucher (£)", 0.0, format="%.2f")
deposit_minus = st.number_input("Deposit ( - ) (£)", 0.0, format="%.2f")
deliveroo = st.number_input("Deliveroo (£)", 0.0, format="%.2f")
ubereats = st.number_input("Uber Eats (£)", 0.0, format="%.2f")
petty_cash = st.number_input("Petty Cash (£)", 0.0, format="%.2f")
deposit_plus = st.number_input("Deposit ( + ) (£)", 0.0, format="%.2f")
tips_sc = st.number_input("Servis Charge (£)", 0.0, format="%.2f")
tips_credit_card = st.number_input("CC Tips (£)", 0.0, format="%.2f")
cash_tips = st.number_input("Cash Tips (£)", 0.0, format="%.2f")
float_val = st.number_input("Float (£)", min_value=75.0, format="%.2f", value=75.0)

deducted_items = cc1 + cc2 + cc3 + amex1 + amex2 + amex3 + voucher + deposit_minus + deliveroo + ubereats + petty_cash
added_items = deposit_plus + tips_credit_card + tips_sc
remaining_custom = calculated_taken_in - deducted_items + added_items

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
st.markdown(f"### 💰 Cash in Envelope Total: £{remaining_custom + cash_tips:.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{tips_credit_card + tips_sc + cash_tips:.2f}")

# Görsel yükleme
uploaded_file = st.file_uploader("📷 Upload Receipt or Photo", type=["jpg", "jpeg", "png", "pdf"])
photo_link = ""
if uploaded_file:
    creds_drive = Credentials.from_service_account_info(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build('drive', 'v3', credentials=creds_drive)
    media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
    uploaded = drive_service.files().create(
        body={'name': uploaded_file.name}, media_body=media, fields='id'
    ).execute()
    drive_service.permissions().create(
        fileId=uploaded['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    photo_link = f"https://drive.google.com/uc?id={uploaded['id']}"
    st.success("📸 Image uploaded to Google Drive!")
    st.image(photo_link)

# Ek alanlar
deposits = st.text_area("Deposits")
petty_cash_note = st.text_area("Petty Cash")
eat_out = st.text_input("Eat Out to Help Out")
comments = st.text_area("Customer Reviews")
manager = st.text_input("Manager")
floor_staff = st.text_input("Service Personnel")
kitchen_staff = st.text_input("Kitchen Staff")

# Sheets bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
info = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(creds)
sheet = client.open("La Petite Banking Extended").sheet1

if st.button("Send it"):
    row = [
        str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
        deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
        tips_sc, remaining_custom, float_val,
        deposits, petty_cash_note, eat_out,
        comments, manager, floor_staff, kitchen_staff, photo_link
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")
    st.success("✅ Data successfully sent!")
    st.session_state["form_submitted"] = True
    st.rerun()
