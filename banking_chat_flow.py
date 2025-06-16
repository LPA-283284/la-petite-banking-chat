import streamlit as st
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 📅 Sayfa Ayarı
st.set_page_config(page_title="LPA Banking", page_icon="📊")
st.title("LPA - BANKING")
st.markdown("You can enter detailed banking information by filling in the fields below.")

# 🕰️ Tarih Seçimi
today = datetime.date.today()
date = st.date_input("Date", today)

# 📅 Numeric Inputs
fields = {
    "Gross (£)": "gross_total",
    "Net (£)": "net_total",
    "Service Charge (Main) (£)": "service_charge_main",
    "Discount (£)": "discount_total",
    "Complimentary (£)": "complimentary_total",
    "Staff Food (£)": "staff_food",
    "CC 1 (£)": "cc1",
    "CC 2 (£)": "cc2",
    "CC 3 (£)": "cc3",
    "Amex 1 (£)": "amex1",
    "Amex 2 (£)": "amex2",
    "Amex 3 (£)": "amex3",
    "Voucher (£)": "voucher",
    "Deposit ( - ) (£)": "deposit_minus",
    "Deliveroo (£)": "deliveroo",
    "Uber Eats (£)": "ubereats",
    "Petty Cash (£)": "petty_cash",
    "Deposit ( + ) (£)": "deposit_plus",
    "Tips (CC) (£)": "tips_credit_card",
    "Service Charge (Tips) (£)": "tips_sc",
    "Cash in Envelope (£)": "cash_envelope",
    "Float (£)": "float_val"
}

values = {}
for label, key in fields.items():
    default = 75.0 if key == "float_val" else 0.0
    values[key] = st.number_input(label, min_value=0.0, format="%.2f", value=default, key=key)

# 📈 Hesaplamalar
calculated_taken_in = values["gross_total"] - (values["discount_total"] + values["complimentary_total"] + values["staff_food"])
calculated_till_balance = calculated_taken_in - (
    values["cc1"] + values["cc2"] + values["cc3"] + values["amex1"] + values["amex2"] +
    values["amex3"] + values["voucher"] + values["deposit_plus"] + values["deliveroo"] +
    values["ubereats"] + values["petty_cash"]
)

st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")
st.markdown(f"### 🧳️ Till Balance (Calculated): £{calculated_till_balance:.2f}")

# 📃 Metin Alanları
notes = {
    "Deposits Note": "item_missing_kitchen",
    "Petty Cash Note": "item_missing_floor",
    "Eat Out to Help Out": "eat_out",
    "Customer Reviews": "comments",
    "Manager": "manager",
    "Service Personnel": "floor_staff",
    "Kitchen Staff": "kitchen_staff"
}

note_values = {key: st.text_area(label) if "Note" in label or "Reviews" in label else st.text_input(label)
               for label, key in notes.items()}

# 📆 Google Sheets Bağlantısı
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
info = json.loads(json_data)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(credentials)
sheet = client.open("La Petite Banking Extended").sheet1

# ✉️ Veri Gönderme
if st.button("Submit"):
    row = [str(date), values["gross_total"], values["net_total"], values["service_charge_main"],
           values["discount_total"], values["complimentary_total"], values["staff_food"],
           calculated_taken_in, values["cc1"], values["cc2"], values["cc3"],
           values["amex1"], values["amex2"], values["amex3"], values["voucher"],
           values["deposit_plus"], values["deposit_minus"], values["deliveroo"], values["ubereats"],
           values["petty_cash"], values["tips_credit_card"], values["tips_sc"],
           calculated_till_balance, values["cash_envelope"], values["float_val"],
           note_values["item_missing_kitchen"], note_values["item_missing_floor"],
           note_values["eat_out"], note_values["comments"], note_values["manager"],
           note_values["floor_staff"], note_values["kitchen_staff"]]

    try:
        sheet.append_row(row, value_input_option="USER_ENTERED")
        st.success("✅ Data successfully sent!")
        st.session_state.clear()
        st.rerun()
    except Exception as e:
        st.error(f"❌ Failed to send data: {e}")
