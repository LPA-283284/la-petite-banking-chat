import streamlit as st
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile

st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

if "form_submitted" in st.session_state and st.session_state.form_submitted:
    st.session_state.clear()
    st.rerun()

st.markdown("You can enter detailed banking information by filling in the fields below.")

today = datetime.date.today()
date = st.date_input("Date", today)

# Girişler
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="net_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="service_charge")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="staff_food")

calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

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

# Çıkarılacaklar
deducted_items = (
    (cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) +
    (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
    (voucher or 0.0) + (deposit_minus or 0.0) +
    (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)
)

# Eklenecekler
added_items = (
    (deposit_plus or 0.0) + (tips_credit_card or 0.0) + (tips_sc or 0.0)
)

remaining_custom = calculated_taken_in - deducted_items + added_items
float_val = st.number_input("Float (£)", min_value=75.00, format="%.2f", value=None, placeholder="75.00", key="float_val")
cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cash_tips")

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
st.markdown(f"### 💰 Cash in Envelope Total: £{(remaining_custom or 0.0) + (cash_tips or 0.0):.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{(tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0):.2f}")

# Fotoğraf yükleme ve Drive'a gönderme
# Fotoğraf yükleme ve Drive'a gönderme (tek alanda yapılır)
uploaded_file = st.file_uploader("📷 Upload Receipt or Photo", type=["jpg", "jpeg", "png", "pdf"])
photo_link = ""
image_drive_url = ""

if uploaded_file is not None:
    scope = ["https://www.googleapis.com/auth/drive"]
    gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]), scope)
    drive = GoogleDrive(gauth)

    # Dosyayı geçici olarak kaydet
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    # Drive'a yükle
    file_drive = drive.CreateFile({'title': uploaded_file.name})
    file_drive.SetContentFile(temp_file_path)
    file_drive.Upload()
    file_drive.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
    image_drive_url = file_drive['alternateLink']
    photo_link = f"https://drive.google.com/uc?id={file_drive['id']}"

    st.success("📤 Image uploaded to Google Drive!")
    if uploaded_file.type.startswith("image/"):
        st.image(photo_link, caption="Uploaded Image", use_column_width=True)
    else:
        st.markdown(f"[📄 View Uploaded File]({photo_link})")

deposits = st.text_area("Deposits")
petty_cash_note = st.text_area("Petty Cash")
eat_out = st.text_input("Eat Out to Help Out")
comments = st.text_area("Customer Reviews")
manager = st.text_input("Manager")
floor_staff = st.text_input("Service Personnel")
kitchen_staff = st.text_input("Kitchen Staff")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
info = json.loads(json_data)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(credentials)
sheet = client.open("La Petite Banking Extended").sheet1

# Fotoğraf yükleme
uploaded_file = st.file_uploader("📷 Upload Banking Photo", type=["jpg", "jpeg", "png", "pdf"])
image_drive_url = ""

# Fotoğraf Google Drive’a yüklenecekse (gerekli kütüphane: pydrive)
if uploaded_file is not None:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from io import BytesIO

    # Yetkilendirme (mevcut kimlik bilgileri ile)
    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)

    file_drive = drive.CreateFile({'title': uploaded_file.name})
    file_drive.SetContentString(uploaded_file.getvalue().decode("latin1") if uploaded_file.type != "application/pdf" else uploaded_file.getvalue().decode("latin1", errors="ignore"))
    file_drive.Upload()
    image_drive_url = file_drive['alternateLink']
    st.success("📤 Image uploaded to Google Drive!")

if st.button("Send it"):
    row = [
    str(date), gross_total, net_total, service_charge, discount_total, complimentary_total,
    staff_food, calculated_taken_in, cc1, cc2, cc3, amex1, amex2, amex3, voucher,
    deposit_plus, deposit_minus, deliveroo, ubereats, petty_cash, tips_credit_card,
    tips_sc, remaining_custom, float_val, deposits, petty_cash_note, eat_out,
    comments, manager, floor_staff, kitchen_staff, photo_link, image_drive_url

    sheet.append_row(row)
    st.success("Data successfully sent it!")
    st.session_state["form_submitted"] = True
    st.rerun()
