import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="LPA Banking", page_icon="📈")
st.title("LPA - BANKING")

if st.session_state.get("form_submitted"):
    st.session_state.clear()
    st.experimental_rerun()

st.markdown("You can enter detailed banking information by filling in the fields below.")

today = datetime.date.today()
date = st.date_input("Date", today)

# Sample Input Fields
gross_total = st.number_input("Gross (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00")
net_total = st.number_input("Net (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00")
service_charge = st.number_input("Service Charge (£)", min_value=0.0, format="%.2f", value=None, placeholder="0.00")

calculated_taken_in = (gross_total or 0.0) - (service_charge or 0.0)
st.markdown(f"### 💸 Taken In (Calculated): £{calculated_taken_in:.2f}")

# File uploader for Drive
uploaded_file = st.file_uploader("📷 Upload Receipt or Photo", type=["jpg", "jpeg", "png"])
photo_link = ""
if uploaded_file:
    creds_info = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=creds)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        media = MediaFileUpload(tmp.name, resumable=True)

    file_metadata = {'name': uploaded_file.name}
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    photo_link = f"https://drive.google.com/uc?id={file_id}"
    st.success("📸 Image uploaded to Google Drive!")
    st.image(photo_link, caption="Uploaded Image", use_column_width=True)

# Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
info = json.loads(json_data)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(credentials)
sheet = client.open("La Petite Banking Extended").sheet1

if st.button("Send it"):
    row = [
        str(date),
        gross_total,
        net_total,
        service_charge,
        calculated_taken_in,
        photo_link
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")
    st.success("Data successfully sent!")
    st.session_state["form_submitted"] = True
    st.experimental_rerun()
