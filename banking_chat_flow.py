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

# Bug varsa state temizle
if "form_submitted" in st.session_state and st.session_state.form_submitted:
    st.session_state.clear()
    st.rerun()

st.markdown("You can enter detailed banking information by filling in the fields below.")
today = datetime.date.today()
date = st.date_input("Date", today)

# Sayısal girişler
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=0.0)
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=0.0)
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=0.0)
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=0.0)
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=0.0)
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=0.0)

# Hesaplama
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Diğer ödemeler
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=0.0)
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=0.0)
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=0.0)
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=0.0)
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=0.0)
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=0.0)
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=0.0)
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=0.0)
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=0.0)
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=0.0)
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=0.0)
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", value=0.0)
tips_credit_card = st.number_input("CC Tips (£)", min_value=0.0, format="%.2f", value=0.0)
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", value=0.0)

# Özet
deducted_items = cc1 + cc2 + cc3 + amex1 + amex2 + amex3 + voucher + deposit_minus + deliveroo + ubereats + petty_cash
added_items = deposit_plus + tips_credit_card + tips_sc
remaining_custom = calculated_taken_in - deducted_items + added_items

float_val = st.number_input("Float (£)", min_value=75.0, format="%.2f", value=75.0)
cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=0.0)

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
st.markdown(f"### 💰 Cash in Envelope Total: £{remaining_custom + cash_tips:.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{tips_credit_card + tips_sc + cash_tips:.2f}")

# Görsel yükleme (form dışında, görünür değil)
uploaded_files = st.file_uploader("📷 Upload Receipts or Photos", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

# FORM
with st.form("banking_form"):
    deposits = st.text_area("Deposits")
    petty_cash_note = st.text_area("Petty Cash Note")
    eat_out = st.text_input("Eat Out to Help Out")
    comments = st.text_area("Customer Reviews")
    manager = st.text_input("Manager")
    floor_staff = st.text_input("Service Personnel")
    kitchen_staff = st.text_input("Kitchen Staff")

    submitted = st.form_submit_button("Submit")

# FORM GÖNDERİLDİ
if submitted:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("La Petite Banking Extended")
    banking_sheet = sheet.worksheet("BANKING")

    # Drive upload (klasöre)
    photo_links = []
    if uploaded_files:
        creds_drive = Credentials.from_service_account_info(
            json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build('drive', 'v3', credentials=creds_drive)

        for file in uploaded_files:
            media = MediaIoBaseUpload(file, mimetype=file.type)
            uploaded = drive_service.files().create(
                body={"name": file.name, "parents": ["18HTYODsW_iDd9EBj3-bquyyGaWxflUNx"]},
                media_body=media,
                fields="id"
            ).execute()
            drive_service.permissions().create(
                fileId=uploaded["id"],
                body={"type": "anyone", "role": "reader"}
            ).execute()
            photo_links.append(f"https://drive.google.com/uc?id={uploaded['id']}")

    # Satır gönder
    row = [
    str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
    staff_food, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
    deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash,
    tips_credit_card, tips_sc,

    calculated_taken_in,        # 💸 Taken In
    remaining_custom,           # 🧮 Till Balance
    remaining_custom + cash_tips,  # 💰 Cash in Envelope
    tips_credit_card + tips_sc + cash_tips,  # ➕ Tips Breakdown

    float_val, cash_tips,
    deposits, petty_cash_note, eat_out,
    comments, manager, floor_staff, kitchen_staff
] + photo_links  # Her link ayrı hücreye

    banking_sheet.append_row(row, value_input_option="USER_ENTERED")

    st.success("✅ All information and images sent successfully!")
    st.session_state.form_submitted = True
    st.rerun()
