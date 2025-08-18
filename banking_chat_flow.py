import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
import json
import io
import time
from gspread.exceptions import APIError

# === SHEET ID'LERI ===
# /d/<ID>/ kismindaki degerler
EXTENDED_SHEET_ID = "1_zeZ1TKUxnOdsLnFADWk7GTOlMlmP-mQ1ovmwJHxLC0"   # Lpa Banking Extende
PRIMARY_SHEET_ID  = "1FX_qVFBtuX6eWgHxbMpGQcHYhj5s-NFnVV0I3XbjwhQ"   # Lpa Banking

# === Basit retry yardimcilari ===
def open_ws_by_key(client, key, worksheet_name=None, tries=4, base_delay=0.6):
    for i in range(tries):
        try:
            sh = client.open_by_key(key)
            return sh.worksheet(worksheet_name) if worksheet_name else sh
        except APIError:
            if i == tries - 1:
                raise
            time.sleep(base_delay * (2 ** i))

def append_row_retry(worksheet, row, tries=4, base_delay=0.6):
    for i in range(tries):
        try:
            worksheet.append_row(row, value_input_option="USER_ENTERED")
            return
        except APIError:
            if i == tries - 1:
                raise
            time.sleep(base_delay * (2 ** i))

# Sayfa yapilandirmasi
st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

st.markdown("You can enter detailed banking information by filling in the fields below.")
today = datetime.date.today()
date = st.date_input("Date", today)

# Tarihi gun/ay/yil formatina cevir
date_str = date.strftime("%d/%m/%Y")

# Sayisal girisler
z_number = st.text_input("Z Number")
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="net_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="service_charge")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="staff_food")

# Hesaplama
calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Diger odemeler
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex2")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex3")
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="voucher")
advance_cash_wages = st.number_input("Advance & Cash Wages (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="advance_cash_wages")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deposit_minus")
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deliveroo")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="ubereats")
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="petty_cash")
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deposit_plus")

# Service Charge Tips — ustteki service_charge'a bagli
tips_sc = st.number_input(
    "Service Charge Tips (£)",
    min_value=0.0,
    format="%.2f",
    value=service_charge if service_charge else 0.0,
    placeholder="0.00",
    key="tips_sc"
)
tips_credit_card = st.number_input("CC Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_credit_card")

# Ozet (Advance & Cash Wages DAHIL)
deducted_items = (
    (cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) +
    (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
    (voucher or 0.0) + (deposit_minus or 0.0) + (advance_cash_wages or 0.0) +
    (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)
)
added_items = (deposit_plus or 0.0) + (tips_credit_card or 0.0) + (tips_sc or 0.0)
remaining_custom = (calculated_taken_in or 0.0) - (deducted_items or 0.0) + (added_items or 0.0)

float_val = st.number_input("Float (£)", min_value=75.00, format="%.2f", value=75.00, placeholder="75.00", key="float_val")
cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cash_tips")

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")

# Cash In Hand (ilk dokunusta 0.00 temizleme)
if "cash_in_hand_first_edit" not in st.session_state:
    st.session_state.cash_in_hand_first_edit = True

cash_in_hand = st.number_input(
    "Cash In Hand (£)",
    min_value=0.0,
    format="%.2f",
    value=None if st.session_state.cash_in_hand_first_edit else (st.session_state.get("cash_in_hand") or 0.0),
    placeholder="0.00",
    key="cash_in_hand"
)

if st.session_state.cash_in_hand_first_edit and cash_in_hand != 0.0:
    st.session_state.cash_in_hand_first_edit = False

# Fark + Zarf toplami
difference = (cash_in_hand or 0.0) - (remaining_custom or 0.0)
st.markdown(f"**Difference:** £{difference:.2f}")

cash_in_envelope_total = (cash_in_hand or 0.0) + (cash_tips or 0.0)
st.markdown(f"### 💰 Cash in Envelope Total: £{cash_in_envelope_total:.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{(tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0):.2f}")

# Gorsel yukleme
uploaded_files = st.file_uploader("📷 Upload Receipts or Photos", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

# FORM
with st.form("banking_form"):
    deposit_details = st.text_area("Deposit Details Name Date In/Out")
    petty_cash_note = st.text_area("Petty Cash / Advance Details")
    manager = st.text_input("Manager")
    submitted = st.form_submit_button("Submit")

if submitted:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)

    # Extended sheet (ID ile) + worksheet retry
    banking_sheet = open_ws_by_key(client, EXTENDED_SHEET_ID, "BANKING")

    # Drive upload
    photo_links = []
    if uploaded_files:
        creds_drive = Credentials.from_service_account_info(
            json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build('drive', 'v3', credentials=creds_drive)

        for file in uploaded_files:
            # Streamlit UploadedFile → BytesIO; mimetype yedegi
            file_bytes = io.BytesIO(file.getbuffer())
            media = MediaIoBaseUpload(file_bytes, mimetype=(file.type or "application/octet-stream"))

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

    images = (photo_links + [""] * 6)[:6]

    # Satir gonder (Extended sheet) — ISTEDIGIN SIRA
    row = [
        date_str,                             # Date
        z_number,                             # Z #NO
        (gross_total or 0.0),                 # Gross
        (net_total or 0.0),                   # Net
        (service_charge or 0.0),              # Service Charge
        (discount_total or 0.0),              # Discount
        (complimentary_total or 0.0),         # Complimentary
        (staff_food or 0.0),                  # Staff Food
        (calculated_taken_in or 0.0),         # Take-In
        (cc1 or 0.0),                         # Card #1
        (cc2 or 0.0),                         # Card #2
        (cc3 or 0.0),                         # Card #3
        (amex1 or 0.0),                       # Amex #1
        (ame
