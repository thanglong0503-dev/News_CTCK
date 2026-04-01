import json
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

def get_db_connection():
    try:
        # Kiểm tra xem Key có tồn tại trong Secrets không
        if "GOOGLE_CREDENTIALS" not in st.secrets:
            st.error("❌ Thiếu 'GOOGLE_CREDENTIALS' trong Streamlit Secrets!")
            return None
            
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Thử mở file
        try:
            db = client.open("LINANCE_DB")
            return db
        except gspread.exceptions.SpreadsheetNotFound:
            st.error("❌ Không tìm thấy file 'LINANCE_DB'. Hãy chắc chắn ngươi đã Share file cho Email của con bot!")
            return None
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google API: {e}")
        return None

def fetch_broker_services():
    db = get_db_connection()
    if db:
        try:
            sheet = db.worksheet("BROKER_SERVICES")
            data = sheet.get_all_records()
            return data
        except gspread.exceptions.WorksheetNotFound:
            st.error("❌ Không tìm thấy tab 'BROKER_SERVICES'. Hãy kiểm tra tên Tab dưới đáy file Sheet!")
            return []
        except Exception as e:
            st.error(f"❌ Lỗi đọc dữ liệu: {e}")
            return []
    return []
# --- HÀM LẤY DỮ LIỆU TỪ SHEET 1 (REPORTS_DB) ---
def fetch_reports_db():
    db = get_db_connection()
    if db:
        try:
            sheet = db.worksheet("REPORTS_DB")
            data = sheet.get_all_records()
            return data
        except Exception as e:
            # Đừng dùng st.error ở đây kẻo rác giao diện, cứ print ra Terminal là được
            print(f"Lỗi đọc Sheet REPORTS_DB: {e}") 
            return []
    return []    
