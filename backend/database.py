import json
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

@st.cache_resource # Lưu kết nối này lại để không bị Google khóa vì gọi quá nhiều lần
def get_db_connection():
    try:
        # 1. Lấy chìa khóa JSON từ két sắt Streamlit
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        
        # 2. Định nghĩa quyền hạn (Đọc/Ghi Sheets và Drive)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # 3. Ký giấy xác nhận với Google
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # 4. Mở khóa đúng file LINANCE_DB
        db = client.open("LINANCE_DB")
        return db
    except Exception as e:
        print(f"Lỗi kết nối Database: {e}")
        return None

# --- HÀM TEST ĐỌC DỮ LIỆU TỪ SHEET 3 (BROKER_SERVICES) ---
def fetch_broker_services():
    db = get_db_connection()
    if db:
        try:
            # Chọn đúng cái Tab (Sheet) thứ 3 mà ngươi đã tạo
            sheet = db.worksheet("BROKER_SERVICES")
            
            # Lấy toàn bộ dữ liệu dưới dạng danh sách Dictionary
            data = sheet.get_all_records()
            return data
        except Exception as e:
            print(f"Lỗi đọc Sheet BROKER_SERVICES: {e}")
            return []
    return []
