import streamlit as st
import datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

today = datetime.date.today()
date = st.date_input("Date", today)

# Sayısal alanlar
def num(label, key):
    return st.number_input(label, min_value=0.0, format="%.2f", value=None, placeholder="0.00", key=key)

gross_total = num("Gross (£)", "gross_total")
net_total = num("Net (£)", "net_total")
service_charge = num("Service Charge (£)", "service_charge")
discount_total = num("Discount (£)", "discount_total")
complimentary_total = num("Complimentary (£)", "complimentary_total")
staff_food = num("Staff Food (£)", "staff_food")

calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

cc1 = num("CC 1 (£)", "cc1")
cc2 = num("CC 2 (£)", "cc2")
cc3 = num("CC 3 (£)", "cc3")
amex1 = num("Amex 1 (£)", "amex1")
amex2 = num("Amex 2 (£)", "amex2")
amex3 = num("Amex 3 (£)", "amex3")
voucher = num("Voucher (£)", "voucher")
deposit_minus = num("Deposit ( - ) (£)", "deposit_minus")
deliveroo = num("Deliveroo (£)", "deliveroo")
ubereats = num("Uber Eats (£)", "ubereats")
petty_cash = num("Petty Cash (£)", "petty_cash")
deposit_plus = num("Deposit ( + ) (£)", "deposit_plus")
tips_sc = num("Servis Charge (£)", "tips_sc")
tips_credit_card = num("CC Tips (£)", "tips_credit_card")

deducted_items = sum(x or 0.0 for x in [cc1, cc2, cc3, amex1, amex2, amex3, voucher, deposit_minus, deliveroo, ubereats, petty_cash])
added_items = sum(x or 0.0 for x in [deposit_plus, tips_sc, tips_credit_card])
remaining_custom = calculated_taken_in - deducted_items + added_items

float_val = num("Float (£)", "float_val")
cash_tips = num("Cash Tips (£)", "cash_tips")

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
st.markdown(f"### 💰 Cash in Envelope Total: £{(remaining_custom or 0.0) + (cash_tips or 0.0):.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{(tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0):.2f}")

# Form alanları
with st.form("banking_form"):
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
    # Google Sheets bağlantısı
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    info = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    client = gspread.authorize(creds)
    sheet = client.open("La Petite Banking Extended")
    banking_sheet = sheet.worksheet("BANKING")

    # Drive bağlantısı
    creds_drive = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    drive_service = build('drive', 'v3', credentials=creds_drive)

    # Görselleri yükle
    photo_links = []
    for uploaded_file in uploaded_files or []:
        media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
        uploaded = drive_service.files().create(
            body={'name': uploaded_file.name}, media_body=media, fields='id'
        ).execute()
        drive_service.permissions().create(
            fileId=uploaded['id'],
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        photo_link = f"https://drive.google.com/uc?id={uploaded['id']}"
        photo_links.append(photo_link)

    # Veriyi gönder
    row = [
        str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
        deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
        tips_sc, remaining_custom, float_val,
        deposits, petty_cash_note, eat_out,
        comments, manager, floor_staff, kitchen_staff
    ] + photo_links  # Görselleri aynı satıra hücre hücre ekle

    banking_sheet.append_row(row, value_input_option="USER_ENTERED")
    st.success("✅ All information and images sent successfully!")

    # Formu sıfırla
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
