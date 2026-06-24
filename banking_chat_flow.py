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

def date_exists_in_sheet(worksheet, date_str, tries=3, base_delay=0.6):
    """Verilen tarih (A sutunu) bu sayfada zaten var mi? Cift kayit engeli icin."""
    for i in range(tries):
        try:
            col = worksheet.col_values(1)  # A sutunu = tarihler
            return date_str in col
        except APIError:
            if i == tries - 1:
                # Kontrol edilemezse engelleme; False don (akisi durdurmamak icin)
                return False
            time.sleep(base_delay * (2 ** i))
    return False

# Sayfa yapilandirmasi
st.set_page_config(page_title="LPA Banking", page_icon="📊")

# === KREM ARKAPLAN + BORDO YAZI TEMASI ===
st.markdown(
    """
    <style>
    :root { --krem:#F5EBDC; --bordo:#7B1E2B; }
    .stApp { background-color: var(--krem); }
    /* Tum yazilar bordo */
    .stApp, .stApp p, .stApp label, .stApp span, .stApp div,
    h1, h2, h3, h4, h5, h6, .stMarkdown { color: var(--bordo) !important; }
    /* Baslik */
    h1 { font-weight: 800; letter-spacing: 1px; }
    /* Input alanlari */
    .stTextInput input, .stTextArea textarea, .stDateInput input {
        background-color: #FFFDF8 !important;
        color: var(--bordo) !important;
        border: 1px solid var(--bordo) !important;
        border-radius: 8px !important;
    }
    /* Salt-okunur (disabled) alan da bordo gozuksun, sadece hafif soluk arkaplan */
    .stTextInput input:disabled {
        background-color: #EFE6D6 !important;
        color: var(--bordo) !important;
        -webkit-text-fill-color: var(--bordo) !important;
        opacity: 1 !important;
    }
    /* number_input alanlari */
    .stNumberInput input {
        background-color: #FFFDF8 !important;
        color: var(--bordo) !important;
        border: 1px solid var(--bordo) !important;
        border-radius: 8px !important;
    }
    /* number_input +/- butonlari */
    .stNumberInput button {
        background-color: #FFFDF8 !important;
        color: var(--bordo) !important;
        border: 1px solid var(--bordo) !important;
    }
    /* Submit butonu */
    .stButton button, .stFormSubmitButton button {
        background-color: var(--bordo) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    .stButton button *, .stFormSubmitButton button * {
        color: #FFFFFF !important;
    }
    .stButton button:hover, .stFormSubmitButton button:hover {
        background-color: #5e1620 !important;
    }
    /* File uploader */
    .stFileUploader { border: 1px dashed var(--bordo); border-radius: 8px; padding: 6px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("LPA - BANKING")

# === KULLANICI GIRISI + TAKIP (LOGIN & AUDIT) ===
# Kullanicilar kodun icinde DEGIL, st.secrets icinde saklanir.
# Streamlit Cloud -> Settings -> Secrets kismina su sekilde ekle:
#
#   [users]
#   ahmet = "ahmet-sifresi"
#   mehmet = "mehmet-sifresi"
#
# Log icin EXTENDED_SHEET_ID'deki spreadsheet'te "LOG" adli bir worksheet olustur.
# Sutunlar onerisi: Timestamp | User | Action | Detail

LOG_WORKSHEET_NAME = "LOG"

def _get_creds():
    return ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )

def write_log(user, action, detail=""):
    """Giris ve veri gonderimlerini LOG sayfasina yazar. Hata olsa bile uygulamayi durdurmaz."""
    try:
        client = gspread.authorize(_get_creds())
        log_ws = open_ws_by_key(client, EXTENDED_SHEET_ID, LOG_WORKSHEET_NAME)
        ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        append_row_retry(log_ws, [ts, user or "", action or "", detail or ""])
    except Exception:
        # Log yazilamazsa kullaniciyi engelleme; sessizce gec.
        pass

def check_login():
    """Dogru kullanici adi + sifre girilene kadar uygulamayi kilitli tutar."""
    if st.session_state.get("auth_ok"):
        return True

    st.markdown("#### 🔒 This area is protected. Please log in.")
    username = st.text_input("Username", key="login_user")
    pwd = st.text_input("Password", type="password", key="login_pwd")

    if st.button("Enter"):
        users = st.secrets.get("users", None)
        if users is None:
            st.error("⚠️ Kullanici listesi (users) Secrets'a eklenmemis.")
        elif username in users and pwd == users[username]:
            st.session_state["auth_ok"] = True
            st.session_state["current_user"] = username
            st.session_state.pop("login_pwd", None)
            write_log(username, "LOGIN", "Basarili giris")
            st.rerun()
        else:
            st.error("❌ Incorrect username or password.")
            write_log(username or "?", "LOGIN_FAIL", "Hatali giris denemesi")
    return False

if not check_login():
    st.stop()

# Giris yapan kullanici (log ve gosterim icin)
current_user = st.session_state.get("current_user", "?")
st.caption(f"👤 Logged in as: {current_user}")



st.markdown("You can enter detailed banking information by filling in the fields below.")
today = datetime.date.today()
date = st.date_input("Date", today)

# Tarihi gun/ay/yil formatina cevir
date_str = date.strftime("%d/%m/%Y")

# === Yardımcı fonksiyon: sayisal giris ===
# Alanlar BOS baslar (sifir gosterilmez). Bos birakilan alan hesaplamada 0 sayilir.
# Tiklayinca alan zaten bos oldugu icin direkt rakam yazilir. Virgul de nokta kabul edilir.
def float_input(label, key, default=""):
    val = st.text_input(label, value=default, key=key)
    if not val:
        return 0.0
    try:
        return float(val.replace(",", ".").strip())
    except ValueError:
        st.warning(f"⚠️ '{label}' alanina gecersiz sayi girildi, 0.0 kullanildi.")
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
calculated_taken_in = gross_total - (discount_total + complimentary_total + staff_food)
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

# Service Charge Tips — SADECE GOSTERIM. Deger tamamen ustteki Service Charge'dan gelir.
# Salt-okunur (disabled): kullanici buradan degistiremez, tek kaynak ust alan.
tips_sc = service_charge
st.text_input(
    "Service Charge Tips (£)",
    value=f"{service_charge:.2f}",
    key="tips_sc_display",
    disabled=True
)

# CC Tips — ETKISIZ. Salt-okunur, hep 0.00. Hesaplamalara 0 olarak girer.
tips_credit_card = 0.0
st.text_input(
    "CC Tips (£)",
    value="0.00",
    key="tips_credit_card_display",
    disabled=True
)

# Ozet (Advance & Cash Wages DAHIL)
deducted_items = (
    cc1 + cc2 + cc3 + amex1 + amex2 + amex3 +
    voucher + deposit_minus + advance_cash_wages +
    deliveroo + ubereats + petty_cash
)
added_items = deposit_plus + tips_credit_card + tips_sc
remaining_custom = calculated_taken_in - deducted_items + added_items

# Float otomatik 75.00 gelir, gerekirse duzenlenebilir
float_val = float_input("Float (£)", "float_val", default="75.00")
cash_tips = float_input("Cash Tips (£)", "cash_tips")

st.markdown(f"### 🧮 Till Balance: £{remaining_custom:.2f}")

# Cash In Hand
cash_in_hand = float_input("Cash In Hand (£)", "cash_in_hand")

# Fark + Zarf toplami  (abs kaldirildi - dogru isaretli fark)
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
    # Basit zorunlu alan kontrolu
    if not z_number.strip() or not manager.strip():
        st.error("❌ Lutfen 'Z Number' ve 'Manager' alanlarini doldurun.")
        st.stop()

    # === CIFT GONDERIM KORUMASI ===
    # Bu kaydin benzersiz bir imzasini cikar. Ayni imza daha once gonderildiyse tekrar yazma.
    submission_signature = f"{date_str}|{z_number}|{calculated_taken_in:.2f}|{cash_in_hand:.2f}"
    if st.session_state.get("last_submission") == submission_signature:
        st.warning("⚠️ Bu kayit zaten gonderilmis gorunuyor. Tekrar gondermek istiyorsan alanlari degistir.")
        st.stop()

    try:
        with st.spinner("Sending... please wait..."):
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
                scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            )
            client = gspread.authorize(creds)

            # Once iki worksheet'i de ac (biri acilamiyorsa hic yazma, yarim kayit olmasin)
            banking_sheet = open_ws_by_key(client, EXTENDED_SHEET_ID, "BANKING")
            second_sheet = open_ws_by_key(client, PRIMARY_SHEET_ID, "BANKING")

            # Ayni tarih icin tekrar kayit engeli (gunde 1 kayit yeterli).
            # Bu, sayfa yenilense bile calisir cunku dogrudan sheet'e bakar.
            if date_exists_in_sheet(banking_sheet, date_str):
                st.error(f"⚠️ {date_str} tarihi icin zaten bir kayit var. Cift kayit engellendi.")
                st.stop()

            # Drive upload (hata yonetimli)
            photo_links = []
            if uploaded_files:
                creds_drive = Credentials.from_service_account_info(
                    json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
                    scopes=["https://www.googleapis.com/auth/drive"]
                )
                drive_service = build('drive', 'v3', credentials=creds_drive)

                for file in uploaded_files:
                    try:
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

                        photo_links.append(f"https://drive.google.com/file/d/{uploaded['id']}/view")
                    except Exception as e:
                        st.warning(f"⚠️ '{file.name}' yuklenemedi: {e}")

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
                cc1, cc2, cc3,
                amex1, amex2, amex3,
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
                0.0,
                difference,
                cash_in_hand,
                tips_credit_card + tips_sc + cash_tips,
                float_val,
                manager or ""
            ] + images
            append_row_retry(banking_sheet, row)

            # Ikinci sheet (ozet)
            summary_row = [
                date_str or "",
                calculated_taken_in,
                service_charge,
                tips_credit_card,
                cash_tips,
                cash_in_hand
            ]
            try:
                append_row_retry(second_sheet, summary_row)
            except Exception as e:
                # Ana satir yazildi ama ozet yazilamadi -> yarim kayit uyarisi
                st.warning(
                    "⚠️ Ana kayit yazildi ancak ozet sayfaya yazilamadi. "
                    f"Lutfen ozet sayfayi elle kontrol edin. Detay: {e}"
                )
                write_log(current_user, "SUMMARY_FAIL", f"Date={date_str}, Z={z_number}")

            # Basarili: imzayi kaydet ki ayni kayit tekrar gonderilmesin
            st.session_state["last_submission"] = submission_signature

            # Veri gonderimini logla (kim, ne zaman, hangi gun + Z number)
            write_log(
                current_user,
                "SUBMIT",
                f"Date={date_str}, Z={z_number}, TakenIn={calculated_taken_in:.2f}"
            )

        st.session_state["form_submitted"] = True

    except Exception as e:
        st.error(f"❌ Gonderim sirasinda hata olustu, kayit tamamlanmadi: {e}")
        write_log(current_user, "SUBMIT_FAIL", f"Date={date_str}, Z={z_number}, Hata={e}")

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
