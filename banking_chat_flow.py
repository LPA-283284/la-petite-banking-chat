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

# Google Sheets bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
info = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(creds)

# Form alanı
with st.form("banking_form"):
    st.markdown("You can enter detailed banking information below.")
    date = st.date_input("Date", datetime.date.today())
    
    gross_total = st.text_input("Gross (£)")
    net_total = st.text_input("Net (£)")
    service_charge = st.text_input("Service Charge (£)")
    discount_total = st.text_input("Discount (£)")
    complimentary_total = st.text_input("Complimentary (£)")
    staff_food = st.text_input("Staff Food (£)")

    cc1 = st.text_input("CC 1 (£)")
    cc2 = st.text_input("CC 2 (£)")
    cc3 = st.text_input("CC 3 (£)")
    amex1 = st.text_input("Amex 1 (£)")
    amex2 = st.text_input("Amex 2 (£)")
    amex3 = st.text_input("Amex 3 (£)")
    voucher = st.text_input("Voucher (£)")
    deposit_minus = st.text_input("Deposit ( - ) (£)")
    deliveroo = st.text_input("Deliveroo (£)")
    ubereats = st.text_input("Uber Eats (£)")
    petty_cash = st.text_input("Petty Cash (£)")
    deposit_plus = st.text_input("Deposit ( + ) (£)")
    tips_credit_card = st.text_input("CC Tips (£)")
    tips_sc = st.text_input("Servis Charge (£)")
    float_val = st.text_input("Float (£)")
    cash_tips = st.text_input("Cash Tips (£)")

    deposits = st.text_area("Deposits")
    petty_cash_note = st.text_area("Petty Cash")
    eat_out = st.text_input("Eat Out to Help Out")
    comments = st.text_area("Customer Reviews")
    manager = st.text_input("Manager")
    floor_staff = st.text_input("Service Personnel")
    kitchen_staff = st.text_input("Kitchen Staff")

    uploaded_files = st.file_uploader("📷 Upload Receipts or Photos", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

    submitted = st.form_submit_button("Submit")

if submitted:
    # Drive bağlantısı
    creds_drive = Credentials.from_service_account_info(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build('drive', 'v3', credentials=creds_drive)

    # Fotoğrafları yükle
    photo_links = []
    for uploaded_file in uploaded_files:
        media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
        uploaded = drive_service.files().create(
            body={'name': uploaded_file.name}, media_body=media, fields='id'
        ).execute()
        drive_service.permissions().create(
            fileId=uploaded['id'], body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        photo_links.append(f"https://drive.google.com/uc?id={uploaded['id']}")

    # Verileri gönder
    sheet = client.open("La Petite Banking Extended")
    banking_sheet = sheet.worksheet("BANKING")
    banking_row = [
        str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food, cc1, cc2, cc3, amex1, amex2, amex3, voucher, deposit_plus,
        deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
        tips_sc, float_val, cash_tips, deposits, petty_cash_note, eat_out,
        comments, manager, floor_staff, kitchen_staff
    ]
    banking_sheet.append_row(banking_row, value_input_option="USER_ENTERED")

    # Fotoğraf linklerini IMAGES sayfasına ekle
    try:
        images_sheet = sheet.worksheet("IMAGES")
    except:
        images_sheet = sheet.add_worksheet(title="IMAGES", rows="100", cols="20")
    images_sheet.append_row(photo_links, value_input_option="USER_ENTERED")

    st.success("All information and images sent successfully!")

    st.experimental_rerun()
