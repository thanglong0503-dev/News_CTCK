import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300) # Cứ 5 phút tự động xếp hạng lại một lần
def fetch_realtime_data():
    # 1. CỘT 1: TỔNG QUAN VĨ MÔ (Cố định 5 chỉ số)
    macro_tickers = ["BTC-USD", "GC=F", "VND=X", "BZ=F", "^IXIC"]

    # 2. RỔ VN100 (100 Cổ phiếu vốn hóa & thanh khoản hàng đầu thị trường)
    vn100_tickers = [
        # VN30 (Nhóm trụ cột)
        "ACB.VN", "BCM.VN", "BID.VN", "BVH.VN", "CTG.VN", "FPT.VN", "GAS.VN", "GVR.VN", "HDB.VN", "HPG.VN",
        "MBB.VN", "MSN.VN", "MWG.VN", "PLX.VN", "POW.VN", "SAB.VN", "SHB.VN", "SSB.VN", "SSI.VN", "STB.VN",
        "TCB.VN", "TPB.VN", "VCB.VN", "VHM.VN", "VIB.VN", "VIC.VN", "VJC.VN", "VNM.VN", "VPB.VN", "VRE.VN",
        # Midcap & Thanh khoản cao (70 mã)
        "DGC.VN", "VND.VN", "VIX.VN", "DIG.VN", "PDR.VN", "KBC.VN", "HSG.VN", "NKG.VN", "VCI.VN", "HCM.VN",
        "DXG.VN", "NLG.VN", "KDH.VN", "PC1.VN", "GEG.VN", "GEX.VN", "VGC.VN", "IDC.VN", "SZC.VN", "HDG.VN",
        "ASM.VN", "BCG.VN", "CII.VN", "CTD.VN", "DBC.VN", "DCM.VN", "DPM.VN", "EIB.VN", "FCN.VN", "FRT.VN",
        "HAH.VN", "HHV.VN", "HT1.VN", "IJC.VN", "LCG.VN", "LPB.VN", "MSB.VN", "NT2.VN", "OCB.VN", "PAN.VN",
        "PHR.VN", "PNJ.VN", "PTB.VN", "PVD.VN", "PVS.VN", "REE.VN", "SBT.VN", "SCS.VN", "SJS.VN", "TCH.VN",
        "TCM.VN", "TDC.VN", "TNG.VN", "VCF.VN", "VCS.VN", "VHC.VN", "VPI.VN", "VSH.VN", "AAA.VN", "ANV.VN",
        "BWE.VN", "CTR.VN", "DGW.VN", "HAX.VN", "MCH.VN", "PET.VN", "QNS.VN", "SKG.VN", "TLG.VN", "VTP.VN"
    ]

    all_tickers = macro_tickers + vn100_tickers
    market_data = {}
    stats = []

    try:
        # Tải dữ liệu sỉ (Bulk Download) 105 mã cùng lúc, dùng Threads để tăng tốc
        df = yf.download(all_tickers, period="5d", group_by='ticker', threads=True)
    except Exception as e:
        print(f"Lỗi tải Yahoo Finance: {e}")
        return {}, {}

    # 3. LỌC VÀ TÍNH TOÁN DỮ LIỆU TỪNG MÃ
    for t in all_tickers:
        try:
            # Xử lý cấu trúc dữ liệu của Yahoo Finance khi tải nhiều mã
            if len(all_tickers) > 1:
                hist = df[t].dropna()
            else:
                hist = df.dropna()

            if hist.empty or len(hist) < 2: continue

            close_today = float(hist['Close'].iloc[-1])
            close_yest = float(hist['Close'].iloc[-2])
            vol_today = float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0

            # Tính toán % Thay đổi (Momentum)
            change_pct = ((close_today - close_yest) / close_yest) * 100

            # Tên hiển thị chuẩn UI
            if t == "BTC-USD": name = "BITCOIN (BTC)"
            elif t == "GC=F": name = "VÀNG (Gold)"
            elif t == "VND=X": name = "USD/VND"
            elif t == "BZ=F": name = "DẦU BRENT"
            elif t == "^IXIC": name = "NASDAQ"
            else: name = t.replace(".VN", "")

            # Format giá tiền hiển thị ($ hoặc VNĐ)
            if t in ["BTC-USD", "GC=F", "BZ=F", "^IXIC"]:
                price_str = f"${close_today:,.1f}"
            else:
                price_str = f"{close_today:,.0f}"

            # Lưu vào từ điển hiển thị UI
            market_data[t] = {
                "name": name,
                "price": price_str,
                "change": change_pct,
                "volume": vol_today,
                "close": close_today
            }

            # Lưu vào danh sách thống kê để AI bốc ra xếp hạng (Chỉ tính cổ phiếu VN)
            if t in vn100_tickers:
                stats.append({
                    "ticker": t,
                    "change": change_pct,
                    "volume": vol_today,
                    "trade_value": close_today * vol_today # Giá trị giao dịch (Quy mô dòng tiền)
                })
        except:
            continue

    # --- 4. THUẬT TOÁN XẾP HẠNG ĐỘNG (DYNAMIC SORTING TRÊN RỔ VN100) ---
    df_stats = pd.DataFrame(stats)

    if not df_stats.empty:
        # Lọc ra 5 mã có Khối lượng (Volume) khủng nhất phiên hôm nay
        top_vol = df_stats.sort_values(by="volume", ascending=False).head(5)["ticker"].tolist()
        
        # Lọc ra 5 mã Tăng mạnh nhất phiên hôm nay (Top Momentum)
        top_smg = df_stats.sort_values(by="change", ascending=False).head(5)["ticker"].tolist()
        
        # Lọc ra 5 mã Dẫn dắt thị trường (Hút Tiền nhiều nhất - Top Trade Value)
        top_cap = df_stats.sort_values(by="trade_value", ascending=False).head(5)["ticker"].tolist()
    else:
        top_vol, top_smg, top_cap = [], [], []

    # 5. LẮP RÁP VÀO CÁC CỘT TRÊN GIAO DIỆN
    groups = {
        "TỔNG QUAN THỊ TRƯỜNG": macro_tickers,     # Cố định
        "HÚT TIỀN MẠNH NHẤT": top_cap,             # AI tự chọn từ VN100
        "TOP SMG (MẠNH NHẤT)": top_smg,            # AI tự chọn từ VN100
        "VOLUME KHỦNG NHẤT": top_vol               # AI tự chọn từ VN100
    }

    return market_data, groups
