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


# Diğer ödemeler
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
tips_sc = st.number_input(
    "Servis Charge (£)",
    min_value=0.0,
    format="%.2f",
    value=service_charge or 0.0,  # Üstteki Service Charge değerini alır
    key="tips_credit_card"
)
tips_credit_card = st.number_input("CC Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_sc")


# Özet
deducted_items = (
    (cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) +
    (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
    (voucher or 0.0) + (deposit_minus or 0.0) +
    (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)
)
added_items = (deposit_plus or 0.0) + (tips_credit_card or 0.0) + (tips_sc or 0.0)
remaining_custom = calculated_taken_in - deducted_items + added_items


float_val = st.number_input("Float (£)", min_value=0.0, format="%.2f", value=75.0, placeholder="0.00", key="float_val")
cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="cash_tips")


st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
# 💵 Elimde Olan Para girişi (Till Balance'ın hemen altında)
actual_cash = st.number_input(
    "💵Money I have (£)",
    min_value=0.0,
    format="%.2f",
    value=0.0,
    key="actual_cash"
)


st.markdown(f"### 💰 Cash in Envelope Total: £{(actual_cash or 0.0) + (cash_tips or 0.0):.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{(tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0):.2f}")


# Görsel yükleme (form dışında, görünür değil)
uploaded_files = st.file_uploader("📷 Upload Receipts or Photos", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

# FORM
with st.form("banking_form"):
    deposits = st.text_area("Deposits")
    petty_cash_note = st.text_area("Petty Cash Note")
    comments = st.text_area("Customer Reviews")
    manager = st.text_input("Manager")
    
    submitted = st.form_submit_button("Submit")

# FORM GÖNDERİLDİ
if submitted:
    # --- Primary creds (BAŞKA HESAP) ---
    primary_info = json.loads(st.secrets["PRIMARY_GOOGLE_SHEETS_CREDENTIALS"])
    primary_creds = ServiceAccountCredentials.from_json_keyfile_dict(
        primary_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    primary_client = gspread.authorize(primary_creds)

    # --- Secondary creds (MEVCUT HESAP) ---
    secondary_info = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
    secondary_creds = ServiceAccountCredentials.from_json_keyfile_dict(
        secondary_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    secondary_client = gspread.authorize(secondary_creds)

    # --- Drive upload (klasöre) ---
    photo_links = []
    if uploaded_files:
        drive_creds = Credentials.from_service_account_info(
            secondary_info,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build('drive', 'v3', credentials=drive_creds)
        folder_id = "18HTYODsW_iDd9EBj3-bquyyGaWxflUNx"

        for file in uploaded_files:
            media = MediaIoBaseUpload(file, mimetype=file.type)
            uploaded = drive_service.files().create(
                body={"name": file.name, "parents": [folder_id]},
                media_body=media,
                fields="id"
            ).execute()
            drive_service.permissions().create(
                fileId=uploaded["id"],
                body={"type": "anyone", "role": "reader"}
            ).execute()
            photo_links.append(f"https://drive.google.com/uc?id={uploaded['id']}")

    # En fazla 6 görsel sütunu
    max_images = 6
    photo_links = (photo_links + [""] * max_images)[:max_images]

    # --- PRIMARY SHEET: La Petite Banking Extended / BANKING ---
    primary_ss = primary_client.open("La Petite Banking Extended")
    banking_sheet = primary_ss.worksheet("BANKING")

    # Satır (senin istediğin sırada)
    row = [
        date.strftime("%d/%m/%Y"),  # DATE
        z_number,                   # Z - NUMBER
        gross_total, net_total, service_charge, discount_total, complimentary_total,
        staff_food,
        (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0)),  # TAKE-IN
        cc1, cc2, cc3, amex1, amex2, amex3,
        voucher,
        deposit_minus, deliveroo, ubereats, petty_cash,
        deposit_plus,
        tips_credit_card, tips_sc,
        # TILL BALANCE
        ((gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0))) -
        ((cc1 or 0.0) + (cc2 or 0.0) + (cc3 or 0.0) + (amex1 or 0.0) + (amex2 or 0.0) + (amex3 or 0.0) +
         (voucher or 0.0) + (deposit_minus or 0.0) + (deliveroo or 0.0) + (ubereats or 0.0) + (petty_cash or 0.0)) +
        ((deposit_plus or 0.0) + (tips_credit_card or 0.0) + (tips_sc or 0.0)),
        # CASH IN ENVELOPE = Money I Have + Cash Tips
        (st.session_state.get("money_i_have", 0.0) or 0.0) + (cash_tips or 0.0),
        st.session_state.get("money_i_have", 0.0) or 0.0,             # MONEY I HAVE
        (tips_credit_card or 0.0) + (tips_sc or 0.0) + (cash_tips or 0.0),  # CC+SC+CASH
        st.session_state.get("float_val", 75.0) if "float_val" in st.session_state else 75.0,  # FLOAT
        cash_tips,                 # CASH TIPS
        st.session_state.get("deposits", ""),            # DEPOSITS - NOTES
        st.session_state.get("petty_cash_note", ""),     # PETTY CASH - NOTES
        st.session_state.get("comments", ""),            # COSTUMERS REVIEWS
        st.session_state.get("manager", ""),             # MANAGER
    ] + photo_links

    banking_sheet.append_row(row, value_input_option="USER_ENTERED")

    # --- SECONDARY SHEET: LPA Banking / BANKING ---
    secondary_ss = secondary_client.open("LPA Banking")
    second_sheet = secondary_ss.worksheet("BANKING")
    second_sheet.append_row(
        [
            date.strftime("%d/%m/%Y"),
            (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_food or 0.0)),
            service_charge,
            tips_credit_card,
            cash_tips,
        ],
        value_input_option="USER_ENTERED"
    )

    st.session_state["form_submitted"] = True
