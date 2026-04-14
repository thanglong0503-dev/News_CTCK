import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from vnstock import listing_companies, stock_historical_data
from datetime import datetime, timedelta
from tqdm import tqdm
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
SHEET_NAME = "LINANCE_DB"
CREDENTIALS_FILE = "credentials.json"
MAX_WORKERS = 10  # Số luồng cào song song (Tăng tốc độ)

def get_google_sheet(worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).worksheet(worksheet_name)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def process_ticker(ticker, industry, start_date, end_date):
    """Hàm xử lý cho từng mã cổ phiếu"""
    try:
        df = stock_historical_data(symbol=ticker, start_date=start_date, end_date=end_date, resolution='1D', type='stock')
        if df is None or len(df) < 50: return None
        
        # Lấy giá trị đóng cửa
        close = df['close']
        current_price = close.iloc[-1]
        
        # 1. Tính RS (Sức mạnh giá)
        perf_1m = (current_price - close.iloc[-22]) / close.iloc[-22]
        perf_3m = (current_price - close.iloc[-66]) / close.iloc[-66] if len(close) >= 66 else perf_1m
        
        # 2. Tính Điểm Kỹ Thuật (Thang điểm 5)
        ma20 = close.tail(20).mean()
        ma50 = close.tail(50).mean()
        rsi = calculate_rsi(close).iloc[-1]
        
        score = 0
        if current_price > ma20: score += 1      # Giá trên MA20
        if current_price > ma50: score += 1      # Giá trên MA50
        if ma20 > ma50: score += 1               # Xu hướng trung hạn lên
        if rsi > 50: score += 1                  # Momentum mạnh
        if rsi > 70: score += 1                  # Rất mạnh (hoặc quá mua tùy view)
        
        # 3. Tính Thanh khoản (Tỷ đồng)
        liquidity = (df['close'] * df['volume']).tail(20).mean() / 1e9

        return {
            "Mã CK": ticker,
            "Ngành": industry,
            "Giá": current_price,
            "RS_1M_Raw": perf_1m,
            "RS_3M_Raw": perf_3m,
            "Điểm_KT": score,
            "Thanh_Khoản_Tỷ": round(liquidity, 2)
        }
    except:
        return None

def main():
    print("🚀 Khởi động Super Bot v2.0 - Chế độ Đa luồng...")
    
    # Lấy danh sách mã
    df_companies = listing_companies(live=False)
    tickers_list = df_companies[['ticker', 'industry']].values.tolist()
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    
    raw_results = []
    
    # --- CHẠY ĐA LUỒNG ---
    print(f"📥 Đang cào dữ liệu {len(tickers_list)} mã với {MAX_WORKERS} luồng...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_ticker, t[0], t[1], start_date, end_date) for t in tickers_list]
        for future in tqdm(as_completed(futures), total=len(tickers_list)):
            res = future.result()
            if res: raw_results.append(res)

    df_final = pd.DataFrame(raw_results)

    # --- XẾP HẠNG RS (1-99) ---
    df_final['RS_1M'] = (df_final['RS_1M_Raw'].rank(pct=True) * 99).astype(int) + 1
    df_final['RS_3M'] = (df_final['RS_3M_Raw'].rank(pct=True) * 99).astype(int) + 1
    
    # --- PHÂN TÍCH NGÀNH (INDUSTRY ROTATION) ---
    print("📊 Đang phân tích sức mạnh nhóm ngành...")
    df_ind = df_final.groupby('Ngành').agg({
        'RS_1M': 'mean',
        'Điểm_KT': 'mean',
        'Mã CK': 'count'
    }).reset_index()
    
    df_ind.columns = ['Ngành', 'RS_TB', 'Điểm_KT_TB', 'Số_Mã']
    
    # Phân loại xu hướng ngành
    def get_trend(s):
        if s >= 3.5: return "TÍCH CỰC"
        if s >= 2.0: return "TRUNG TÍNH"
        return "YẾU"
    
    df_ind['Xu_Hướng'] = df_ind['Điểm_KT_TB'].apply(get_trend)
    df_ind['Top_Ngành'] = df_ind['RS_TB'].apply(lambda x: "TOP" if x >= df_ind['RS_TB'].quantile(0.8) else "")
    df_ind = df_ind.round(1).sort_values(by='RS_TB', ascending=False)

    # --- ĐẨY DỮ LIỆU LÊN GOOGLE SHEETS ---
    print("☁️ Đang đẩy dữ liệu lên 2 Tab...")
    
    # Tab 1: Chi tiết cổ phiếu
    ws_rs = get_google_sheet("RS_DATA")
    df_rs_upload = df_final[['Mã CK', 'Ngành', 'RS_1M', 'RS_3M', 'Điểm_KT', 'Thanh_Khoản_Tỷ', 'Giá']]
    ws_rs.clear()
    ws_rs.update([df_rs_upload.columns.values.tolist()] + df_rs_upload.values.tolist())
    
    # Tab 2: Tổng hợp ngành
    ws_ind = get_google_sheet("INDUSTRY_DATA")
    ws_ind.clear()
    ws_ind.update([df_ind.columns.values.tolist()] + df_ind.values.tolist())

    print("✅ HOÀN TẤT! Hệ thống đã được cập nhật toàn diện.")

if __name__ == "__main__":
    main()
