import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from vnstock import listing_companies, stock_historical_data
from datetime import datetime, timedelta
from tqdm import tqdm # Thanh tiến trình cho đẹp
import time

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
SHEET_NAME = "LINANCE_DB" # Tên file Google Sheet của Sếp
WORKSHEET_NAME = "RS_DATA" # Tên Tab lưu dữ liệu RS
CREDENTIALS_FILE = "credentials.json" # File chìa khóa Google API

def get_google_sheet():
    """Hàm kết nối vào Google Sheets"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    return sheet

def calculate_rs_pipeline():
    print("🚀 Bắt đầu khởi động cỗ máy tính toán RS (Sức mạnh giá)...")
    
    # 1. LẤY DANH SÁCH TOÀN BỘ MÃ CỔ PHIẾU (HOSE, HNX, UPCOM)
    print("📥 Đang lấy danh sách mã cổ phiếu...")
    df_companies = listing_companies(live=False)
    tickers = df_companies['ticker'].tolist()
    
    # Tính mốc thời gian: Hôm nay, 1 tháng trước (khoảng 22 ngày GD), 3 tháng trước (khoảng 66 ngày GD)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d") # Lấy dư ra 4 tháng để chắc chắn đủ nến
    
    results = []
    
    print(f"🕵️ Đang cào dữ liệu lịch sử của {len(tickers)} mã (Sẽ mất vài phút, uống miếng nước đi Sếp)...")
    
    # 2. VÒNG LẶP CÀO DỮ LIỆU & TÍNH TOÁN HIỆU SUẤT
    for ticker in tqdm(tickers):
        try:
            # Lấy data lịch sử bằng vnstock
            df_hist = stock_historical_data(symbol=ticker, start_date=start_date, end_date=end_date, resolution='1D', type='stock')
            
            if df_hist is not None and len(df_hist) >= 66: # Cần ít nhất 66 phiên (~3 tháng)
                current_price = df_hist.iloc[-1]['close']
                price_1m_ago = df_hist.iloc[-22]['close'] # Giá 1 tháng trước
                price_3m_ago = df_hist.iloc[-66]['close'] # Giá 3 tháng trước
                
                # Tính % Tăng trưởng
                perf_1m = (current_price - price_1m_ago) / price_1m_ago
                perf_3m = (current_price - price_3m_ago) / price_3m_ago
                
                # Trích xuất ngành từ bảng overview (Tùy chọn cho đẹp)
                sector = df_companies[df_companies['ticker'] == ticker]['industry'].values[0]
                
                results.append({
                    "Mã CK": ticker,
                    "Ngành": sector,
                    "Perf_1M": perf_1m,
                    "Perf_3M": perf_3m
                })
            
            # Tuyệt chiêu "Câu giờ" lách luật: Cào 1 mã xong nghỉ 0.05 giây cho API khỏi nghẽn
            time.sleep(0.05) 
            
        except Exception as e:
            continue # Lỗi mã nào bỏ qua mã đó, chạy tiếp
            
    # 3. MA THUẬT XẾP HẠNG RS (1 - 99)
    print("🧮 Đang tiến hành xếp hạng Sức mạnh giá (RS)...")
    df_results = pd.DataFrame(results)
    
    # Dùng hàm rank(pct=True) để xếp hạng phần trăm (thành điểm từ 1 đến 99)
    df_results['RS_1M'] = (df_results['Perf_1M'].rank(pct=True) * 99).astype(int) + 1
    df_results['RS_3M'] = (df_results['Perf_3M'].rank(pct=True) * 99).astype(int) + 1
    
    # Lọc bỏ mấy cột trung gian, chỉ giữ lại kết quả tinh túy nhất
    final_df = df_results[['Mã CK', 'Ngành', 'RS_1M', 'RS_3M']]
    
    # Sắp xếp từ mạnh nhất đến yếu nhất
    final_df = final_df.sort_values(by="RS_1M", ascending=False)
    
    # 4. GHI ĐÈ KẾT QUẢ VÀO GOOGLE SHEETS
    print("☁️ Đang đẩy dữ liệu lên két sắt Google Sheets...")
    sheet = get_google_sheet()
    
    # Xóa sạch dữ liệu cũ
    sheet.clear()
    
    # Ghi dữ liệu mới vào
    sheet.update([final_df.columns.values.tolist()] + final_df.values.tolist())
    
    print("✅ HOÀN TẤT! Đã đẩy thành công bảng xếp hạng RS mới nhất lên hệ thống!")

if __name__ == "__main__":
    calculate_rs_pipeline()
