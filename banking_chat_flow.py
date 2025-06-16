import streamlit as st
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

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

calculated_taken_in = (gross_total or 0.0) - ((discount_total or 0.0) + (complimentary_total or 0.0) + (staff_
