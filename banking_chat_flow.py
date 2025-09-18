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

# Sayfa yapilandirmasi
st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

st.markdown("You can enter detailed banking information by filling in the fields below.")
today = datetime.date.today()
date = st.date_input("Date", today)

# Tarihi gun/ay/yil formatina cevir
date_str = date.strftime("%d/%m/%Y")

# === Yardımcı fonksiyon (text → float) ===
def float_input(label, key):
    val = st.text_input(label, value="", key=key)
    try:
        return float(val) if val else 0.0
    except ValueError:
        return 0.0

# Sayisal girisler
z_number = st.text_input("Z Number")
gross_total = float_input("Gross (£)", "gross_total")
net_total = float_input("Net (£)", "net_total")
service_charge = float_input("Service Charge (£)", "service_charge")
discount_total = float_input("Discount (£)", "discount_total")
complimentary_total = float_input("Complimentary (£)", "complimentary_total")
staff_food = float_input("Staff Food (£)", "staff_food")

# Hesaplama
calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Diger odemeler
cc1 = float_input("CC 1 (£)", "cc1")
cc2 = float_input("CC 2 (£)", "cc2")
cc3 = float_input("CC 3 (£)", "cc3")
amex1 = float_input("Amex 1 (£)", "amex1")
amex2 = float_input("Amex 2 (£)", "amex2")
amex3 = float_input("Amex 3 (£)", "amex3")
voucher = float_input("Voucher (£)", "voucher")
advance_cash_wages = float_input("Advance & Cash Wages (£)", "advance_cash_wages")
deposit_minus = float_input("Deposit ( - ) (£)", "deposit_minus")
deliveroo = float_input("Deliveroo (£)", "deliveroo")
ubereats = float_input("Uber Eats (£)", "ubereats")
petty_cash = float_input("Petty Cash (£)", "petty_cash")
deposit_plus = float_input("Deposit ( + ) (£)", "deposit_plus")

# Service Charge Tips — ustteki service_charge'a bagli
tips_sc = float_input("Service Charge Tips (£)", "tips_sc")
if tips_sc == 0.0 and service_charge:
    tips_sc = service_charge

tips_credit_card = float_input("CC Tips (£)", "tips_credit_card")

# Ozet (Advance & Cash Wages DAHIL)
deducted_items = (
    (cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) +
    (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
    (voucher or 0.0) + (deposit_minus or 0.0) + (advance_cash_wages or 0.0) +
    (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)
)
added_items = (deposit_plus or 0.0) + (tips_credit_card or 0.0) + (tips_sc or 0.0)
remaining_custom = (calculated_taken_in or 0.0) - (deducted_items or 0.0) + (added_items or 0.0)

float_val = float_input("Float (£)", "float_val")
if float_val == 0.0:
    float_val = 75.0
cash_tips = float_input("Cash Tips (£)", "cash_tips")

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")

# Cash In Hand
cash_in_hand = float_input("Cash In Hand (£)", "cash_in_hand")

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
        date_str or "",
        z_number or "",
        gross_total,
        net_total,
        service_charge,
        discount_total,
        complimentary_total,
        staff_food,
        calculated_taken_in,
        cc1,
        cc2,
        cc3,
        amex1,
        amex2,
        amex3,
        voucher,
        petty_cash,
        advance_cash_wages,
        petty_cash_note or "",
        deposit_plus,
        deposit_minus,
        deposit_details or "",
        deliveroo,
        ubereats,
        "",
        tips_credit_card,
        cash_tips,
        difference,
        cash_in_hand,
        (tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0),
        float_val,
        manager or ""
    ] + images
    append_row_retry(banking_sheet, row)

    # Ikinci sheet: ID ile ve retry'li
    second_sheet = open_ws_by_key(client, PRIMARY_SHEET_ID, "BANKING")
    summary_row = [
        date_str or "",
        calculated_taken_in,
        service_charge,
        tips_credit_card,
        cash_tips,
        cash_in_hand
    ]
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
