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

# Başarı mesajını kalıcı göstermek için (sayfa yenilese de kalsın)
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# Üstte kalıcı başarı mesajı
if st.session_state.form_submitted:
    st.markdown(
        """
        <div style="background-color:#d4edda;padding:20px;border-radius:10px;border:1px solid #c3e6cb;">
            <h4 style="color:#155724;">✅ All information and images sent successfully!</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("You can enter detailed banking information by filling in the fields below.")

# Tarih (görüntü formatını gün/ay/yıl olarak yazacağız; Sheets'e string olarak gider)
today = datetime.date.today()
date = st.date_input("Date", today)

# Sayısal girişler (varsayılan 0.00; kullanıcı değiştirirse değerler hesaplara yansır)
z_number = st.text_input("Z Number")
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="gross_total")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="net_total")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="service_charge")
discount_total = st.number_input("Discount (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="discount_total")
complimentary_total = st.number_input("Complimentary (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="complimentary_total")
staff_food = st.number_input("Staff Food (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="staff_food")


# Taken-In
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# Kart/ödemeler
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


# Bahşişler
tips_credit_card = st.number_input("CC Tips (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_sc")
tips_sc = st.number_input("Servis Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00", key="tips_sc")

# Özet hesaplamalar
deducted_items = cc1 + cc2 + cc3 + amex1 + amex2 + amex3 + voucher + deposit_minus + deliveroo + ubereats + petty_cash
added_items = deposit_plus + tips_credit_card + tips_sc
remaining_custom = calculated_taken_in - deducted_items + added_items  # Till Balance

# Float ve Cash
float_val = st.number_input("Float (£)", min_value=75.0, format="%.2f", value=75.0)
cash_tips = st.number_input("Cash Tips (£)", min_value=0.0, format="%.2f", value=None)

# Money I Have (yeni alan) ve Cash in Envelope Total = Money I Have + Cash Tips
money_i_have = st.number_input("Money I Have (£)", min_value=0.0, format="%.2f", value=None)

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")
st.markdown(f"### 💰 Cash in Envelope Total: £{(money_i_have + cash_tips):.2f}")
st.markdown(f"##### ➕ Cash Tips Breakdown Total (CC + SC + Cash): £{(tips_credit_card + tips_sc + cash_tips):.2f}")

# Çoklu görsel yükleme (form DIŞINDA, önizleme göstermiyoruz)
uploaded_files = st.file_uploader(
    "📷 Upload Receipts or Photos",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True
)

# Form: not alanları
with st.form("banking_form"):
    deposits = st.text_area("Deposits - Notes")
    petty_cash_note = st.text_area("Petty Cash - Notes")
    comments = st.text_area("Customers Reviews")
    manager = st.text_input("Manager")

    submitted = st.form_submit_button("Submit")

# Gönderim
if submitted:
    # ---- Sheets ve Drive için TEK secret kullan ----
    info = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
    scopes_all = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    # gspread (Sheets)
    credentials_sheets = ServiceAccountCredentials.from_json_keyfile_dict(info, scopes_all)
    client = gspread.authorize(credentials_sheets)

    # Drive (dosya yükleme)
    creds_drive = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    drive_service = build('drive', 'v3', credentials=creds_drive)

    # Görselleri Drive klasörüne yükle ve linkleri topla
    photo_links = []
    if uploaded_files:
        for file in uploaded_files:
            media = MediaIoBaseUpload(file, mimetype=file.type)
            uploaded = drive_service.files().create(
                body={"name": file.name, "parents": ["18HTYODsW_iDd9EBj3-bquyyGaWxflUNx"]},
                media_body=media,
                fields="id"
            ).execute()
            # Public read
            drive_service.permissions().create(
                fileId=uploaded["id"],
                body={"type": "anyone", "role": "reader"}
            ).execute()
            photo_links.append(f"https://drive.google.com/uc?id={uploaded['id']}")

    # PRIMARY: "La Petite Banking Extended" -> "BANKING"
    primary_ss = client.open("La Petite Banking Extended")
    banking_ws = primary_ss.worksheet("BANKING")

    # Tarihi dd/mm/YYYY string olarak yaz
    date_str = date.strftime("%d/%m/%Y")

    # İSTENEN SIRAYA UYGUN SATIR
    # DATE, Z - NUMBER, GROSS, NET, SC, DISCOUNT, COMLIMENTARY, STAFF FOOD, TAKE-IN,
    # CC-1, CC-2, CC-3, AMEX-1, AMEX-2, AMEX-3, VOCUHER, DEPOSIT (-), DELIVEROO, UBER EATS, PETTY CASH,
    # DEPOSIT (+), CC TIPS, SC, TILL BALANCE, CASH IN ENVELOPE, MONEY I HAVE, CC+SC+CASH, FLOAT, CASH TIPS,
    # DEPOSITS - NOTES, PETTY CASH - NOTES, COSTUMERS REVIEWS, MANAGER, IMAGES -1 ... IMAGES -6
    row = [
        date_str,
        z_number,
        gross_total, net_total, service_charge, discount_total, complimentary_total, staff_food,
        calculated_taken_in,
        cc1, cc2, cc3, amex1, amex2, amex3, voucher,
        deposit_minus, deliveroo, ubereats, petty_cash,
        deposit_plus, tips_credit_card, tips_sc,
        remaining_custom,                     # Till Balance
        (money_i_have + cash_tips),           # Cash in Envelope
        money_i_have,                         # Money I Have
        (tips_credit_card + tips_sc + cash_tips),  # CC+SC+CASH
        float_val, cash_tips,
        deposits, petty_cash_note, comments, manager
    ]

    # Görsel linklerini (en fazla 6 tane) ayrı hücrelere ekle
    max_imgs = 6
    row += (photo_links + [""] * max(0, max_imgs - len(photo_links)))[:max_imgs]

    # Satırı yaz
    banking_ws.append_row(row, value_input_option="USER_ENTERED")

    # SECOND: "LPA Banking" -> "BANKING" (özet)
    second_ws = client.open("LPA Banking").worksheet("BANKING")
    summary_row = [
        date_str,
        calculated_taken_in,  # Take-in
        service_charge,
        tips_credit_card,
        cash_tips
    ]
    second_ws.append_row(summary_row, value_input_option="USER_ENTERED")

    # Kalıcı mesaj için flag'i set et (sayfayı rerun etmiyoruz ki mesaj kalsın)
    st.session_state.form_submitted = True
    st.success("✅ All information and images sent successfully!")
