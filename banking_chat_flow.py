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


calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Ödemeler
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex2")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="amex3")
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="voucher")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deposit_minus")
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deliveroo")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="ubereats")
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="petty_cash")
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="deposit_plus")
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_credit_card")
tips_credit_card = st.number_input("CC Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_sc")


deducted_items = (
    (cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) +
    (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
    (voucher or 0.0) + (deposit_minus or 0.0) +
    (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)
)
added_items = (deposit_plus or 0.0) + (tips_credit_card or 0.0) + (tips_sc or 0.0)
remaining_custom = calculated_taken_in - deducted_items + added_items

float_val = st.number_input("Float (£)", min_value=0.0, format="%.2f", value=None, placeholder="75.00", key="float_val")
cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cash_tips")

# Göster
st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
st.markdown(f"### 💰 Cash in Envelope Total: £{(remaining_custom or 0.0) + (cash_tips or 0.0):.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{(tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0):.2f}")


# Görsel yükleme
uploaded_files = st.file_uploader("📷 Upload Receipts or Photos", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)
photo_links = []

if uploaded_files:
    creds_drive = Credentials.from_service_account_info(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build('drive', 'v3', credentials=creds_drive)

    for uploaded_file in uploaded_files:
        media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
        uploaded = drive_service.files().create(
            body={'name': uploaded_file.name}, media_body=media, fields='id'
        ).execute()

        # 🔐 HER DOSYA İÇİN PAYLAŞIM İZNİ VER
        drive_service.permissions().create(
            fileId=uploaded['id'],
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        # ✅ BEKLEME ZORUNLU DEĞİL AMA STABILİTE İÇİN FAYDALI
        import time
        time.sleep(0.3)

        photo_link = f"https://drive.google.com/uc?id={uploaded['id']}"
        photo_links.append(photo_link)
        st.success(f"📸 Uploaded: {uploaded_file.name}")
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

if st.button("Submit"):
    row = [
        str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
        deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
        tips_sc, remaining_custom, float_val,
        deposits, petty_cash_note, eat_out,
        comments, manager, floor_staff, kitchen_staff, ", ".join(photo_links)
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")
    st.success("✅ Data successfully sent!")

    # 🔁 Giriş alanlarını sıfırla
    for key in list(st.session_state.keys()):
        if isinstance(st.session_state[key], float):
            st.session_state.pop(key, None)
        elif isinstance(st.session_state[key], str):
            st.session_state[key] = ""
        elif isinstance(st.session_state[key], int):
            st.session_state[key] = 0
        else:
            del st.session_state[key]

    st.rerun()
