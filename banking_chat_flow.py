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
EXTENDED_SHEET_ID = "1_zeZ1TKUxnOdsLnFADWk7GTOlMlmP-mQ1ovmwJHxLC0"   # Lpa Banking - Office
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

# Yardimci: text_input'tan float'a cevir
def float_input(label, key, placeholder="0.00", default=0.0, value=None):
    val_str = st.text_input(label, placeholder=placeholder, key=key, value=value if value is not None else "")
    try:
        return float(val_str) if val_str else default
    except ValueError:
        return default

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
gross_total = float_input("Gross (£)", key="gross_total")
net_total = float_input("Net (£)", key="net_total")
service_charge = float_input("Service Charge (£)", key="service_charge")
discount_total = float_input("Discount (£)", key="discount_total")
complimentary_total = float_input("Complimentary (£)", key="complimentary_total")
staff_food = float_input("Staff Food (£)", key="staff_food")

# Hesaplama
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Diger odemeler
cc1 = float_input("CC 1 (£)", key="cc1")
cc2 = float_input("CC 2 (£)", key="cc2")
cc3 = float_input("CC 3 (£)", key="cc3")
amex1 = float_input("Amex 1 (£)", key="amex1")
amex2 = float_input("Amex 2 (£)", key="amex2")
amex3 = float_input("Amex 3 (£)", key="amex3")
voucher = float_input("Voucher (£)", key="voucher")
advance_cash_wages = float_input("Advance & Cash Wages (£)", key="advance_cash_wages")
deposit_minus = float_input("Deposit ( - ) (£)", key="deposit_minus")
deliveroo = float_input("Deliveroo (£)", key="deliveroo")
ubereats = float_input("Uber Eats (£)", key="ubereats")
petty_cash = float_input("Petty Cash (£)", key="petty_cash")
deposit_plus = float_input("Deposit ( + ) (£)", key="deposit_plus")

# Service Charge Tips — otomatik service_charge değerini alsın
tips_sc = float_input("Service Charge Tips (£)", key="tips_sc", default=0.0, value=str(service_charge) if service_charge else "0.0")
tips_credit_card = float_input("CC Tips (£)", key="tips_credit_card")

# Ozet (Advance & Cash Wages DAHIL)
deducted_items = (
    cc1 + cc2 + cc3 +
    amex1 + amex2 + amex3 +
    voucher + deposit_minus + advance_cash_wages +
    deliveroo + ubereats + petty_cash
)
added_items = deposit_plus + tips_credit_card + tips_sc
remaining_custom = calculated_taken_in - deducted_items + added_items

float_val = float_input("Float (£)", key="float_val", placeholder="75.00", default=75.00)
cash_tips = float_input("Cash Tips (£)", key="cash_tips")

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")

cash_in_hand = float_input("Cash In Hand (£)", key="cash_in_hand")

# Fark + Zarf toplami
difference = cash_in_hand - remaining_custom
st.markdown(f"**Difference:** £{difference:.2f}")

cash_in_envelope_total = cash_in_hand + cash_tips
st.markdown(f"### 💰 Cash in Envelope Total: £{cash_in_envelope_total:.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{tips_credit_card + tips_sc + cash_tips:.2f}")

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

    # Satir gonder (Extended sheet)
    row = [
        date_str, z_number, gross_total, net_total, service_charge,
        discount_total, complimentary_total, staff_food,
        calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3,
        voucher, petty_cash, advance_cash_wages, petty_cash_note,
        deposit_plus, deposit_minus, deposit_details,
        deliveroo, ubereats, "",
        tips_credit_card, cash_tips, difference, cash_in_hand,
        tips_credit_card + tips_sc + cash_tips, float_val, manager
    ] + images

    append_row_retry(banking_sheet, row)

    # Ikinci sheet
    second_sheet = open_ws_by_key(client, PRIMARY_SHEET_ID, "BANKING")
    summary_row = [date_str, calculated_taken_in, service_charge, tips_credit_card, cash_tips, cash_in_hand]
    append_row_retry(second_sheet, summary_row)

    st.session_state["form_submitted"] = True

# Basari mesaji
if st.session_state.get("form_submitted"):
    st.markdown(
        """
        <div style="background-color:#d4edda;padding:20px;border-radius:10px;border:1px solid #c3e6cb;">
            <h4 style="color:#155724;">✅ All information and images sent successfully!</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.session_state.pop("form_submitted", None)
