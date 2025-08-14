import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
import json

# Sayfa yapılandırması
st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")

st.markdown("You can enter detailed banking information by filling in the fields below.")
today = datetime.date.today()
date = st.date_input("Date", today)

# Tarihi gün/ay/yıl formatına çevir
date_str = date.strftime("%d/%m/%Y")

# Sayısal girişler
z_number = st.text_input("Z Number")
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="net_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="service_charge")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="staff_food")

# Hesaplama
calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Diğer ödemeler
cc1 = st.number_input("CC 1 (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="cc1")
cc2 = st.number_input("CC 2 (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="cc2")
cc3 = st.number_input("CC 3 (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="cc3")
amex1 = st.number_input("Amex 1 (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="amex1")
amex2 = st.number_input("Amex 2 (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="amex2")
amex3 = st.number_input("Amex 3 (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="amex3")
voucher = st.number_input("Voucher (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="voucher")
deposit_minus = st.number_input("Deposit ( - ) (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="deposit_minus")
deliveroo = st.number_input("Deliveroo (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="deliveroo")
ubereats = st.number_input("Uber Eats (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="ubereats")
petty_cash = st.number_input("Petty Cash (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="petty_cash")
deposit_plus = st.number_input("Deposit ( + ) (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="deposit_plus")

# Doğru key eşleşmesi
tips_sc = st.number_input("Service Charge Tips (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="tips_sc")
tips_credit_card = st.number_input("CC Tips (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="tips_credit_card")

# Özet
deducted_items = (
    (cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) +
    (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
    (voucher or 0.0) + (deposit_minus or 0.0) +
    (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)
)
added_items = (deposit_plus or 0.0) + (tips_credit_card or 0.0) + (tips_sc or 0.0)
remaining_custom = (calculated_taken_in or 0.0) - (deducted_items or 0.0) + (added_items or 0.0)

float_val = st.number_input("Float (£)", min_value=75.00, format="%.2f", value=75.00, placeholder="75.00", key="float_val")
cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=0.0, placeholder="0.00", key="cash_tips")

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")

# Money I Have (ilk dokunuşta 0.00 temizleme)
if "money_i_have_first_edit" not in st.session_state:
    st.session_state.money_i_have_first_edit = True

money_i_have = st.number_input(
    "Money I Have (£)",
    min_value=0.0,
    format="%.2f",
    value=0.0 if st.session_state.money_i_have_first_edit else (st.session_state.get("money_i_have") or 0.0),
    placeholder="0.00",
    key="money_i_have"
)

if st.session_state.money_i_have_first_edit and money_i_have != 0.0:
    st.session_state.money_i_have_first_edit = False

# Fark hesaplama
difference = (money_i_have or 0.0) - (remaining_custom or 0.0)
st.markdown(f"**Difference:** £{difference:.2f}")

st.markdown(f"### 💰 Cash in Envelope Total: £{(remaining_custom or 0.0) + (cash_tips or 0.0):.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{(tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0):.2f}")

# Görsel yükleme
uploaded_files = st.file_uploader("📷 Upload Receipts or Photos", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

# FORM
with st.form("banking_form"):
    deposits = st.text_area("Deposits")
    petty_cash_note = st.text_area("Petty Cash Note")
    comments = st.text_area("Customer Reviews")
    manager = st.text_input("Manager")
    submitted = st.form_submit_button("Submit")

if submitted:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("La Petite Banking Extended")
    banking_sheet = sheet.worksheet("BANKING")

    # Drive upload
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

    # Satır gönder (Extended sheet) — Z Number dahil
    row = [
        date_str,
        (gross_total or 0.0), (net_total or 0.0), (service_charge or 0.0), (discount_total or 0.0), (complimentary_total or 0.0),
        (staff_food or 0.0),
        (calculated_taken_in or 0.0),
        (cc1 or 0.0), (cc2 or 0.0), (cc3 or 0.0), (amex1 or 0.0), (amex2 or 0.0), (amex3 or 0.0),
        (voucher or 0.0),
        (deposit_minus or 0.0), (deliveroo or 0.0), (ubereats or 0.0), (petty_cash or 0.0),
        (deposit_plus or 0.0),
        (tips_credit_card or 0.0), (tips_sc or 0.0),
        (remaining_custom or 0.0),
        (money_i_have or 0.0),
        (difference or 0.0),
        (remaining_custom or 0.0) + (cash_tips or 0.0),
        (tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0),
        (float_val or 0.0), (cash_tips or 0.0),
        deposits, petty_cash_note,
        comments, manager,
        z_number  # ✅ Z Number artık Extended sheet'e gidiyor
    ] + photo_links

    banking_sheet.append_row(row, value_input_option="USER_ENTERED")

    # İkinci sheet'e özet veri (Summary)
    second_sheet = client.open("LPA Banking").worksheet("BANKING")
    summary_row = [
        date_str,
        (calculated_taken_in or 0.0),
        (service_charge or 0.0),
        (tips_credit_card or 0.0),
        (cash_tips or 0.0),
        (money_i_have or 0.0),
        (difference or 0.0)
    ]
    second_sheet.append_row(summary_row, value_input_option="USER_ENTERED")

    st.session_state["form_submitted"] = True

# Başarı mesajı
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
