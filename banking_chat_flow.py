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

# Otomatik sıfırlama için
if "form_submitted" in st.session_state and st.session_state.form_submitted:
    st.session_state.clear()
    st.rerun()

today = datetime.date.today()

with st.form("banking_form"):
    st.markdown("You can enter detailed banking information by filling in the fields below.")
    
    date = st.date_input("Date", today)

    gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
    net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="net_total")
    service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="service_charge")
    discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="discount_total")
    complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="complimentary_total")
    staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="staff_food")

    calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
    st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

    cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=None, key="cc1")
    cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=None, key="cc2")
    cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=None, key="cc3")
    amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=None, key="amex1")
    amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=None, key="amex2")
    amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=None, key="amex3")
    voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=None, key="voucher")
    deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=None, key="deposit_minus")
    deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=None, key="deliveroo")
    ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=None, key="ubereats")
    petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=None, key="petty_cash")
    deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", value=None, key="deposit_plus")
    tips_credit_card = st.number_input("CC Tips (£)", min_value=0.0, format="%.2f", value=None, key="tips_credit_card")
    tips_sc = st.number_input("Service Charge Tips (£)", min_value=0.0, format="%.2f", value=None, key="tips_sc")
    float_val = st.number_input("Float (£)", min_value=0.0, format="%.2f", value=None, key="float_val")
    cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=None, key="cash_tips")

    deducted_items = sum(filter(None, [cc1, cc2, cc3, amex1, amex2, amex3, voucher, deposit_minus, deliveroo, ubereats, petty_cash]))
    added_items = sum(filter(None, [deposit_plus, tips_credit_card, tips_sc]))
    remaining_custom = calculated_taken_in - deducted_items + added_items

    st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
    st.markdown(f"### 💰 Cash in Envelope Total: £{(remaining_custom or 0.0) + (cash_tips or 0.0):.2f}")
    st.markdown(f"##### ➕ Cash Tips Breakdown (CC + SC + Cash): £{(tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0):.2f}")

    deposits = st.text_area("Deposits")
    petty_cash_note = st.text_area("Petty Cash Notes")
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

    # Google Drive bağlantısı
    creds_drive = Credentials.from_service_account_info(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build('drive', 'v3', credentials=creds_drive)

    # Görsel yükleme
    photo_links = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
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

    # Verileri gönder
    banking_row = [
        str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
        deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
        tips_sc, remaining_custom, float_val, deposits, petty_cash_note, eat_out,
        comments, manager, floor_staff, kitchen_staff
    ] + photo_links  # görseller ayrı hücrelerde aynı satırda

    banking_sheet.append_row(banking_row, value_input_option="USER_ENTERED")
    st.success("✅ All information and image links have been sent to the BANKING sheet!")

    st.session_state["form_submitted"] = True
    st.rerun()
