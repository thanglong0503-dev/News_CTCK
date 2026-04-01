import math
import base64
import requests
import pandas as pd
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

# --- IMPORT CÁC HÀM TỪ BACKEND ---
from backend.database import fetch_broker_services, fetch_reports_db, fetch_portfolio_db
from backend.official_news import fetch_mainstream_news
from backend.market_data import fetch_realtime_data
from backend.ai_analysis import (
    analyze_news_sentiment, 
    generate_technical_alerts, 
    get_f319_sentiment, 
    fetch_cafef_reports, 
    generate_ai_report_scoring
)

# ==========================================
# KHỐI 0: ĐỒNG HỒ REAL-TIME (TOP BAR)
# ==========================================
def render_topbar_clock():
    clock_html = """
    <style>
        body { margin: 0; font-family: 'Source Sans Pro', sans-serif; background-color: #E65100; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; font-size: 14px; font-weight: 600; }
    </style>
    <div id="clock">Đang tải thời gian...</div>
    <script>
        function updateTime() {
            var now = new Date();
            var days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
            var dayName = days[now.getDay()];
            var dateString = now.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
            var timeString = now.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute:'2-digit', second:'2-digit' });
            document.getElementById('clock').innerHTML = timeString + " &nbsp;|&nbsp; " + dayName + ", " + dateString;
        }
        setInterval(updateTime, 1000);
        updateTime();
    </script>
    """
    components.html(clock_html, height=32)

# ==========================================
# ==========================================
# KHỐI 1: HEADER & BĂNG CHUYỀN VĨ MÔ (TONE CAM TRẮNG)
# ==========================================
import yfinance as yf
import base64
import streamlit as st

def get_base64_of_image(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return ""

@st.cache_data(ttl=60, show_spinner=False)
def get_macro_data():
    tickers = {
        "VNINDEX": "^VNINDEX.VN",
        "BITCOIN": "BTC-USD",
        "VÀNG (Gold)": "GC=F",
        "USD/VND": "VND=X",
        "DẦU BRENT": "BZ=F",
        "NASDAQ": "^IXIC"
    }
    results = []
    
    for name, symbol in tickers.items():
        try:
            data = yf.Ticker(symbol).history(period="5d")
            if len(data) >= 2:
                prev_close = data['Close'].iloc[-2]
                current_price = data['Close'].iloc[-1]
                pct_change = ((current_price - prev_close) / prev_close) * 100
                
                if name in ["VNINDEX", "USD/VND"]:
                    price_str = f"{current_price:,.2f}"
                else:
                    price_str = f"${current_price:,.2f}"
                    
                sign = "+" if pct_change > 0 else ""
                color = "#0ECB81" if pct_change > 0 else "#F6465D" if pct_change < 0 else "#848E9C"
                
                # --- TONE CAM TRẮNG CHO TỪNG ITEM ---
                # Nhãn tên (VNINDEX, VÀNG...) -> Màu Cam (#E65100)
                # Giá tiền -> Màu Đen đậm (#1E2329) để nổi trên nền trắng
                item_html = f"""<span style="color: #E65100; font-weight: 700; margin-right: 6px; text-transform: uppercase;">{name}</span> 
                                <span style="font-weight: 800; color: #1E2329; margin-right: 6px;">{price_str}</span> 
                                <span style="color: {color}; font-weight: 700;">{sign}{pct_change:.2f}%</span>"""
                results.append(item_html)
        except:
            continue
            
    return results

def render_header():
    logo_base64 = get_base64_of_image("assets/logo.png")
    
    if logo_base64:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 16px; margin-top: 10px;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 100px; object-fit: contain;">
            <div>
                <h1 style='font-size: 36px; color: #1E2329; font-weight: 800; margin: 0; padding: 0; letter-spacing: 1px;'>LINANCE</h1>
                <p style='color: #474D57; font-size: 16px; margin-top: 4px; margin-bottom: 0;'>Vietnam Securities Research - Phân tích cấp tổ chức</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px; margin-top: 10px;'>LINANCE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 16px;'>Vietnam Securities Research - Phân tích cấp tổ chức</p>", unsafe_allow_html=True)

    macro_items = get_macro_data()
    
    if macro_items:
        # Dấu chấm phân cách được đổi sang màu Cam nhạt cho hợp tone
        ticker_content = "<span style='margin: 0 40px; color: #FFB74D;'>•</span>".join(macro_items)
        ticker_content = f"{ticker_content} <span style='margin: 0 40px; color: #FFB74D;'>•</span> {ticker_content}"
        
        # CSS Băng chuyền: Nền trắng (#FFFFFF), viền cam nhạt (#FFE0B2), bóng đổ cam nhẹ
        ticker_html = f"""
        <style>
        .ticker-wrap {{
            width: 100%;
            background-color: #FFFFFF; 
            border: 1px solid #FFE0B2;
            padding: 12px 0;
            border-radius: 6px;
            overflow: hidden;
            white-space: nowrap;
            box-shadow: 0 4px 12px rgba(230, 81, 0, 0.05); 
            margin-bottom: 24px;
        }}
        .ticker {{
            display: inline-block;
            white-space: nowrap;
            animation: marquee 25s linear infinite;
        }}
        .ticker:hover {{
            animation-play-state: paused;
            cursor: pointer;
        }}
        @keyframes marquee {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(-50%); }}
        }}
        </style>
        
        <div class="ticker-wrap">
            <div class="ticker" style="font-size: 15px; font-family: 'SF Mono', Consolas, monospace;">
                {ticker_content}
            </div>
        </div>
        """
        st.markdown(ticker_html, unsafe_allow_html=True)
# ==========================================
# KHỐI 1.5: HÀM KÉO DỮ LIỆU BẢN ĐỒ NHIỆT (VN100 - TAB 2)
# ==========================================
import yfinance as yf
import plotly.express as px
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300, show_spinner=False)
def get_market_heatmap_data():
    # NÂNG CẤP LÊN RỔ VN100 (Bao phủ >85% thanh khoản thị trường)
    sectors = {
        'Ngân hàng': ['VCB', 'BID', 'CTG', 'MBB', 'TCB', 'VPB', 'ACB', 'STB', 'SHB', 'HDB', 'TPB', 'MSB', 'LPB', 'VIB', 'EIB', 'OCB', 'SSB'],
        'Bất động sản & KCN': ['VHM', 'VIC', 'VRE', 'NVL', 'DIG', 'DXG', 'KDH', 'NLG', 'PDR', 'KBC', 'IDC', 'SZC', 'HDG', 'TCH', 'CEO'],
        'Chứng khoán': ['SSI', 'VND', 'VCI', 'HCM', 'SHS', 'MBS', 'FTS', 'VIX', 'BSI', 'CTS', 'AGR'],
        'Tài nguyên & Vật liệu': ['HPG', 'HSG', 'NKG', 'DGC', 'DCM', 'DPM', 'GVR', 'PHR', 'CSV'],
        'Xây dựng & Hạ tầng': ['VCG', 'PC1', 'CTD', 'CII', 'HHV', 'LCG', 'FCN', 'HUT', 'HBC'],
        'Bán lẻ & Tiêu dùng': ['MWG', 'PNJ', 'FRT', 'VNM', 'MSN', 'SAB', 'DGW', 'SBT', 'KDC', 'PET', 'HAH', 'GMD', 'VJC', 'HVN'],
        'Công nghệ & Năng lượng': ['FPT', 'GAS', 'PLX', 'POW', 'BSR', 'REE', 'NT2', 'GEG', 'VGI', 'FOX']
    }
    
    vn_tickers = []
    ticker_to_sector = {}
    ticker_to_raw = {}
    for sector, stocks in sectors.items():
        for stock in stocks:
            yf_ticker = f"{stock}.VN"
            vn_tickers.append(yf_ticker)
            ticker_to_sector[yf_ticker] = sector
            ticker_to_raw[yf_ticker] = stock

    try:
        data = yf.download(vn_tickers, period="2d", progress=False)
        if data.empty:
            return pd.DataFrame()

        if len(data) >= 2:
            current_data = data.iloc[-1]
            prev_data = data.iloc[-2]
        else:
            current_data = data.iloc[-1]
            prev_data = current_data

        heat_data = []
        for yf_ticker in vn_tickers:
            raw_ticker = ticker_to_raw[yf_ticker]
            sector = ticker_to_sector[yf_ticker]

            try:
                current_price = float(current_data['Close'][yf_ticker])
                prev_close = float(prev_data['Close'][yf_ticker])
                volume = float(current_data['Volume'][yf_ticker])

                if pd.isna(current_price) or pd.isna(prev_close):
                    continue

                volume = max(volume, 1) 
                pct_change = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0

                heat_data.append({
                    'Ngành': sector,
                    'Mã CK': raw_ticker,
                    'Biến động (%)': pct_change,
                    'Khối lượng': volume,
                    'Giá (VNĐ)': current_price
                })
            except Exception:
                continue

        return pd.DataFrame(heat_data)
    except Exception as e:
        print(f"Lỗi kết nối Yahoo Finance: {e}")
        return pd.DataFrame()

# ==========================================
# KHU VỰC HIỂN THỊ CỦA TAB 2 (BẢN ĐỒ NHIỆT - MÀU CHUẨN SSI)
# ==========================================
def render_tab2_heatmap():
    st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>🗺️ Bản đồ Nhiệt Dòng tiền (Market Heatmap)</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #474D57; font-size: 14px; margin-bottom: 24px;'>Kích thước ô vuông thể hiện Khối lượng giao dịch. Màu sắc phản ánh mức độ Tăng/Giảm chuẩn thị trường Việt Nam.</div>", unsafe_allow_html=True)

    with st.spinner("Đang quét tín hiệu dòng tiền VN100..."):
        df_heat = get_market_heatmap_data()

        if not df_heat.empty:
            # 1. Định dạng chữ: In đậm mã CK
            df_heat['Nhãn hiển thị'] = "<b>" + df_heat['Mã CK'] + "</b><br>" + df_heat['Biến động (%)'].round(2).astype(str) + "%"

            # 2. VẼ TREEMAP VỚI BẢNG MÀU RỜI RẠC (DISCRETE SOLID COLORS)
            fig = px.treemap(
                df_heat,
                path=[px.Constant("Thị Trường VN"), 'Ngành', 'Nhãn hiển thị'],
                values='Khối lượng',
                color='Biến động (%)',
                
                # Khóa cứng biên độ sàn/trần của HOSE (-7% đến +7%)
                range_color=[-7, 7], 
                
                # --- BẢNG MÀU CHỨNG KHOÁN VIỆT NAM (KHÔNG PHA TRỘN) ---
                # 0.0 -> -7% | 0.5 -> 0% | 1.0 -> +7%
                color_continuous_scale=[
                    [0.0, "#00DFD8"], [0.035, "#00DFD8"],  # Xanh lơ (Giảm sàn từ -7% đến -6.5%)
                    [0.035, "#F6465D"], [0.495, "#F6465D"], # Đỏ (Giảm từ -6.5% đến -0.05%)
                    [0.495, "#FFB300"], [0.505, "#FFB300"], # Vàng (Đứng giá quanh 0%)
                    [0.505, "#0ECB81"], [0.965, "#0ECB81"], # Xanh lá (Tăng từ 0.05% đến 6.5%)
                    [0.965, "#9C27B0"], [1.0, "#9C27B0"]    # Tím (Tăng trần từ 6.5% đến 7%)
                ],
                
                hover_data={'Khối lượng': ':.2s', 'Giá (VNĐ)': ':,.0f'}
            )
            
            # 3. Ép khung Layout cho sát lề và Ẩn thanh thang màu (Color Bar)
            fig.update_layout(
                margin=dict(t=30, l=0, r=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False # Tắt thanh thang màu bên phải cho giống SSI
            )
            
            # 4. CHỈNH SỬA FONT CHỮ VÀ VIỀN TRẮNG
            fig.update_traces(
                textinfo="label",
                textfont=dict(color="#FFFFFF", size=15, family="Inter, 'Segoe UI', Arial, sans-serif"), # Chữ Trắng để nổi trên các nền màu đậm
                marker=dict(line=dict(color='#1E2329', width=1)), # Viền màu tối mảnh chia cắt các ô
                hovertemplate="<b>%{label}</b><br>Khối lượng: %{value}<br>Biến động: %{color:.2f}%<extra></extra>"
            )

            # Tăng chiều cao biểu đồ lên 600px để chứa đủ 100 mã
            st.plotly_chart(fig, use_container_width=True, height=600)
            
            # --- VẼ CHÚ THÍCH MÀU SẮC BÊN DƯỚI (LEGEND) ---
            st.markdown("""
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px; font-size: 13px; font-weight: 600; color: #474D57;">
                <div style="display: flex; align-items: center; gap: 6px;"><span style="width: 14px; height: 14px; background-color: #9C27B0; border-radius: 3px;"></span> Tăng trần</div>
                <div style="display: flex; align-items: center; gap: 6px;"><span style="width: 14px; height: 14px; background-color: #0ECB81; border-radius: 3px;"></span> Tăng</div>
                <div style="display: flex; align-items: center; gap: 6px;"><span style="width: 14px; height: 14px; background-color: #FFB300; border-radius: 3px;"></span> Tham chiếu</div>
                <div style="display: flex; align-items: center; gap: 6px;"><span style="width: 14px; height: 14px; background-color: #F6465D; border-radius: 3px;"></span> Giảm</div>
                <div style="display: flex; align-items: center; gap: 6px;"><span style="width: 14px; height: 14px; background-color: #00DFD8; border-radius: 3px;"></span> Giảm sàn</div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("Yahoo Finance đang cập nhật dữ liệu. Vui lòng thử lại sau!")
# ==========================================
# KHỐI 1.6: BIỂU ĐỒ DIỄN BIẾN VN-INDEX (NÚI CAM BRANDING + STATS)
# ==========================================
@st.cache_data(ttl=60, show_spinner=False)
def get_vnindex_intraday():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^VNINDEX.VN?interval=1m&range=1d"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        closes = result['indicators']['quote'][0]['close']
        prev_close = result['meta']['chartPreviousClose']
        
        df = pd.DataFrame({
            'Datetime': pd.to_datetime(timestamps, unit='s', utc=True).tz_convert('Asia/Ho_Chi_Minh'),
            'Close': closes
        }).dropna() 
        
        # --- BÓC TÁCH THÔNG SỐ (STATS) ---
        stats = {
            'prev_close': prev_close,
            'open': df['Close'].iloc[0] if not df.empty else prev_close,
            'volume': result['meta'].get('regularMarketVolume', 0), 
            'day_low': df['Close'].min() if not df.empty else 0,
            'day_high': df['Close'].max() if not df.empty else 0,
            'year_low': 0,
            'year_high': 0,
            'avg_volume': 0
        }
        
        try:
            tkr = yf.Ticker("^VNINDEX.VN")
            fi = tkr.fast_info
            stats['year_low'] = fi.year_low
            stats['year_high'] = fi.year_high
        except:
            pass
            
        return df, float(prev_close), stats
    except Exception as e:
        print(f"Lỗi Hack API Yahoo: {e}")
        return pd.DataFrame(), 0, {}

def render_vnindex_chart():
    st.markdown("<br><div style='height:10px;'></div>", unsafe_allow_html=True)
    
    with st.spinner("Đang trích xuất luồng dữ liệu và thông số từ Yahoo..."):
        df, prev_close, stats = get_vnindex_intraday()
        
        if not df.empty and prev_close > 0:
            current_price = df['Close'].iloc[-1]
            diff = current_price - prev_close
            pct_change = (diff / prev_close) * 100
            
            is_up = current_price >= prev_close
            
            # --- TÁCH BIỆT MÀU SẮC: TEXT (XANH/ĐỎ) & NÚI (CAM BRANDING) ---
            text_color = "#0ECB81" if is_up else "#F6465D"
            sign = "+" if is_up else ""
            mountain_color = "#FF6B00" 
            mountain_fill = "rgba(255, 107, 0, 0.12)"
            
            st.markdown(f"""
            <div style="margin-bottom: 0px; margin-left: -5px; padding-left: 0px;">
                <h2 style='font-size: 16px; font-weight: 700; color: #1E2329; margin: 0; padding: 0; font-family: "Inter", "Segoe UI", Arial, sans-serif;'>^VNINDEX.VN VN-INDEX</h2>
                <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 4px; padding: 0;">
                    <span style="font-size: 36px; font-weight: 800; color: #1E2329; font-family: 'SF Mono', Consolas, monospace; padding: 0;">{current_price:,.2f}</span>
                    <span style="font-size: 16px; font-weight: 700; color: {text_color}; margin-left: 2px;">{sign}{diff:,.2f} ({sign}{pct_change:.2f}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['Datetime'], y=df['Close'],
                mode='lines', line=dict(color=mountain_color, width=2.5),
                fill='tozeroy', fillcolor=mountain_fill,
                name='VN-INDEX',
                hovertemplate='%{x|%H:%M}<br><b>Điểm: %{y:.2f}</b><extra></extra>'
            ))

            fig.add_trace(go.Scatter(
                x=[df['Datetime'].iloc[0], df['Datetime'].iloc[-1]],
                y=[prev_close, prev_close],
                mode='lines', line=dict(color='#848E9C', width=1.5, dash='dash'),
                name='Tham chiếu', hoverinfo='skip'
            ))

            min_y = min(df['Close'].min(), prev_close) * 0.998
            max_y = max(df['Close'].max(), prev_close) * 1.002

            fig.update_layout(
                margin=dict(t=5, l=0, r=0, b=0),
                height=220, 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                dragmode='pan', 
                xaxis=dict(showgrid=False, tickformat="%H:%M", showticklabels=True, ticks="", visible=True, type='date'),
                yaxis=dict(showgrid=False, range=[min_y, max_y], showticklabels=False, visible=False, fixedrange=False),
                showlegend=False, hovermode='x unified'
            )

            config = {'scrollZoom': True, 'displayModeBar': False}
            st.plotly_chart(fig, use_container_width=True, config=config)

            # --- BẢNG THÔNG SỐ ---
            year_range_str = f"{stats['year_low']:,.2f} - {stats['year_high']:,.2f}" if stats['year_high'] > 0 else "N/A"
            vol_str = f"{stats['volume']:,}" if stats['volume'] > 0 else "N/A"
            
            st.markdown(f"""
            <style>
            .stat-row {{ display: flex; justify-content: space-between; border-bottom: 1px dashed #EAECEF; padding: 12px 0; font-size: 14px; }}
            .stat-label {{ color: #474D57; font-weight: 600; }}
            .stat-val {{ color: #1E2329; font-weight: 700; font-family: 'SF Mono', Consolas, monospace; }}
            .stat-col {{ flex: 1; padding: 0 24px; }}
            .stat-col:first-child {{ padding-left: 0; }}
            .stat-col:last-child {{ padding-right: 0; border-right: none; }}
            </style>
            <div style="display: flex; flex-direction: row; width: 100%; margin-top: 10px; margin-bottom: 10px;">
                <div class="stat-col">
                    <div class="stat-row"><span class="stat-label">Previous Close</span><span class="stat-val">{stats['prev_close']:,.2f}</span></div>
                    <div class="stat-row"><span class="stat-label">Open</span><span class="stat-val">{stats['open']:,.2f}</span></div>
                </div>
                <div class="stat-col">
                    <div class="stat-row"><span class="stat-label">Volume</span><span class="stat-val">{vol_str}</span></div>
                    <div class="stat-row"><span class="stat-label">Day's Range</span><span class="stat-val">{stats['day_low']:,.2f} - {stats['day_high']:,.2f}</span></div>
                </div>
                <div class="stat-col">
                    <div class="stat-row"><span class="stat-label">52 Week Range</span><span class="stat-val">{year_range_str}</span></div>
                    <div class="stat-row"><span class="stat-label">Avg. Volume</span><span class="stat-val">N/A</span></div>
                </div>
            </div>
            <hr style='margin: 15px 0px 25px 0px; border-color: #EAECEF;'>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("⚠️ Yahoo Finance đang bảo trì API nội bộ. Vui lòng thử lại sau!")
# ==========================================
# KHỐI 2: TỔNG QUAN, BIỂU ĐỒ & PHÂN TÍCH AI
# ==========================================
def render_hero_section():
    market_data, groups = fetch_realtime_data()

    st.markdown("""<style>
[data-testid="stTabs"] [data-testid="stMarkdownContainer"] { border-bottom: none !important; }
[data-testid="stTabs"] [data-testid="stTab"] { 
    font-size: 16px; font-weight: 600; color: #848E9C; cursor: pointer; border: none; padding: 0px 24px 12px 0px !important; margin-right: 0px; 
    border-bottom: 2px solid transparent; transition: all 0.2s ease;
}
[data-testid="stTabs"] [data-testid="stTab"]:hover { color: #E65100; border-bottom-color: #E65100;}
[data-testid="stTabs"] [data-testid="stTab"]:active { border: none !important; color: #E65100; font-weight: 700;}
[data-testid="stTabs"] [data-testid="stTab"] button:focus { border: none !important; box-shadow: none !important;}
</style>""", unsafe_allow_html=True)

    # Sửa dòng này thành 5 Tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "TỔNG QUAN THỊ TRƯỜNG", 
        "DỮ LIỆU GIAO DỊCH", 
        "PHÂN TÍCH AI", 
        "BÁO CÁO TỔ CHỨC",
        "SO SÁNH DỊCH VỤ" # Tab mới đây!
    ])

  # --- TAB 1: TỔNG QUAN THỊ TRƯỜNG ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        groups_items = list(groups.items())
        
        # CSS MỚI: ĐỔI TÊN CLASS THÀNH 'm-' ĐỂ CÁCH LY HOÀN TOÀN VỚI TAB 5
        css_market = """<style>
        .m-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; width: 100%; }
        
        .m-card { background: #fff; border: 1px solid #EAECEF; border-radius: 12px; padding: 20px; transition: all 0.2s ease; width: 100%; box-sizing: border-box; box-shadow: 0 2px 8px rgba(0,0,0,0.02);}
        .m-card:hover { border-color: #E65100; box-shadow: 0 8px 24px rgba(230, 81, 0, 0.08); transform: translateY(-4px); }
        .m-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid #F0F2F5; padding-bottom: 12px;}
        .m-title { font-weight: 800; font-size: 14px; color: #1E2329; text-transform: uppercase; }
        .m-more { font-size: 12px; color: #707A8A; text-decoration: none; font-weight: 600;}
        .m-more:hover { color: #E65100; }
        .m-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; padding: 4px 0;}
        .m-row:last-child { margin-bottom: 0; }
        
        .m-name { font-weight: 700; font-size: 14px; color: #1E2329; flex: 2; text-align: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 10px;}
        .m-price { font-size: 14px; color: #1E2329; flex: 1.5; text-align: right; font-family: 'SF Mono', Consolas, monospace; font-weight: 600;}
        .m-change { font-size: 14px; font-weight: 700; flex: 1; text-align: right; }
        
        .c-up { color: #0ECB81; } 
        .c-down { color: #F6465D; } 
        </style>"""
        
        cards_html = ""
        
        for group_name, tickers in groups_items[:6]:
            rows_html = ""
            for t in tickers:
                data = market_data.get(t, {"name": t, "price": "N/A", "change": 0})
                color_class = "c-up" if data['change'] >= 0 else "c-down"
                sign = "+" if data['change'] > 0 else ""
                # Đổi luôn HTML sang dùng class m-
                rows_html += f"""<div class="m-row"><div class="m-name">{data['name']}</div><div class="m-price">{data['price']}</div><div class="m-change {color_class}">{sign}{data['change']:.2f}%</div></div>"""
            # Đổi luôn HTML sang dùng class m-
            cards_html += f"""<div class="m-card"><div class="m-header"><div class="m-title">{group_name}</div><a href="#" class="m-more">Chi tiết ></a></div>{rows_html}</div>"""
            
        st.markdown(f"{css_market}<div class='m-grid'>{cards_html}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


# --- TAB 2: DỮ LIỆU GIAO DỊCH ---
    with tab2:
        # Lưu ý: Các dòng dưới đây phải được thụt lề bằng phím Tab (lùi vào 1 ô so với chữ with)
        render_vnindex_chart() 
        render_tab2_heatmap()

    # --- TAB 3: PHÂN TÍCH AI ---
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        market_sentiment_score, top_bullish_news, top_bearish_news = analyze_news_sentiment()
        technical_alerts = generate_technical_alerts()
        f319_data = get_f319_sentiment()

        # Sentiment Index
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase;'>Chỉ số Tâm lý Thị trường (Sentiment Index)</div>", unsafe_allow_html=True)
        col_gauge, col_top_news = st.columns([1, 2.2])
        with col_gauge:
            gauge_color = "#0ECB81" if market_sentiment_score >= 50 else "#F6465D"
            gauge_text = "HƯNG PHẤN (BULLISH)" if market_sentiment_score >= 50 else "SỢ HÃI (BEARISH)"
            css_gauge = """<style>.gauge-container { display: flex; flex-direction: column; align-items: center; justify-content: center; background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 24px; height: 180px;} .gauge-score { font-size: 48px; font-weight: 700; color: #1E2329; margin-bottom: 12px; font-family: 'SF Mono', Consolas, monospace;} .gauge-label { font-size: 13px; font-weight: 700; color: #fff; border-radius: 4px; padding: 6px 16px; text-transform: uppercase;}</style>"""
            st.markdown(f"{css_gauge}<div class='gauge-container'><div class='gauge-score'>{market_sentiment_score:.0f}</div><div class='gauge-label' style='background-color: {gauge_color}'>{gauge_text}</div></div>", unsafe_allow_html=True)

        with col_top_news:
            if not top_bullish_news and not top_bearish_news:
                st.info("Hệ thống đang tổng hợp dữ liệu tin tức...")
            else:
                css_ai_news = """<style>.ai-news-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; height: 180px; display: flex; flex-direction: column; justify-content: center; gap: 16px;} .ai-tag { font-size: 11px; font-weight: 700; border-radius: 4px; padding: 4px 8px; text-transform: uppercase; margin-right: 8px;} .ai-title { font-size: 14px; font-weight: 600; color: #1E2329; line-height: 1.4; display: inline;} .ai-title:hover { color: #E65100; } .b-up-t { color: #0ECB81; background-color: #E6FFF3; border: 1px solid #0ECB81;} .b-down-t { color: #F6465D; background-color: #FFF1F0; border: 1px solid #F6465D;}</style>"""
                rows_html = ""
                if top_bullish_news: rows_html += f"""<div><a href="{top_bullish_news[0]['link']}" target="_blank" style="text-decoration: none;"><span class="ai-tag b-up-t">TÍN HIỆU TÍCH CỰC</span><span class="ai-title">{top_bullish_news[0]['title']}</span></a></div>"""
                if top_bearish_news: rows_html += f"""<div><a href="{top_bearish_news[0]['link']}" target="_blank" style="text-decoration: none;"><span class="ai-tag b-down-t">TÍN HIỆU TIÊU CỰC</span><span class="ai-title">{top_bearish_news[0]['title']}</span></a></div>"""
                st.markdown(f"{css_ai_news}<div class='ai-news-card'>{rows_html}</div>", unsafe_allow_html=True)

        # Technical Alerts
        st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase;'>Báo động Kỹ thuật (Technical Alerts)</div>", unsafe_allow_html=True)
        if technical_alerts:
            css_ai_alerts = """<style>.a-card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px;} .a-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; text-align: center; transition: all 0.2s ease;} .a-card:hover { border-color: #E65100; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08);} .a-ticker { font-size: 16px; font-weight: 700; color: #1E2329; margin-bottom: 12px;} .a-type { font-size: 11px; font-weight: 700; padding: 6px 8px; border-radius: 4px; color: #fff; text-transform: uppercase; display: inline-block; margin-bottom: 12px; width: 100%; box-sizing: border-box;} .a-details { font-size: 12px; color: #707A8A; line-height: 1.5; font-weight: 500;}</style>"""
            cards_html = "".join([f"""<div class="a-card"><div class="a-ticker">{a['ticker']}</div><div class="a-type" style="background-color: {a['color']};">{a['type']}</div><div class="a-details">{a['details']}</div></div>""" for a in technical_alerts])
            st.markdown(f"{css_ai_alerts}<div class='a-card-grid'>{cards_html}</div>", unsafe_allow_html=True)

        # Social Sentiment
        st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase; border-top: 1px solid #EAECEF; padding-top: 32px;'>Cộng Đồng Nhà Đầu Tư (Social Sentiment)</div>", unsafe_allow_html=True)
        if not f319_data['posts']:
            st.markdown("""
            <div style='background-color: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 60px 20px; text-align: center; margin-bottom: 24px;'>
                <div style='font-size: 32px; color: #848E9C; margin-bottom: 16px;'>📭</div>
                <div style='font-size: 16px; font-weight: 700; color: #474D57;'>Hệ thống hiện chưa ghi nhận dữ liệu thảo luận nào.</div>
                <div style='font-size: 14px; color: #848E9C; margin-top: 8px;'>Có thể do giới hạn kết nối hoặc API đang bảo trì. Vui lòng thử lại sau.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            col_social_stats, col_social_posts = st.columns([1.2, 1])
            css_social = """<style>
.soc-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 24px; min-height: 400px;}
.soc-title { font-size: 20px; font-weight: 700; color: #1E2329; margin-bottom: 24px;}
.soc-metrics { display: flex; justify-content: space-between; margin-bottom: 32px;}
.soc-m-item { display: flex; flex-direction: column; gap: 8px;}
.soc-m-lbl { font-size: 12px; color: #707A8A; font-weight: 600;}
.soc-m-val { font-size: 24px; color: #1E2329; font-weight: 700; font-family: 'SF Mono', Consolas, monospace;}
.p-bar-labels { display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; margin-bottom: 8px;}
.p-bar-container { display: flex; height: 16px; width: 100%; border-radius: 4px; overflow: hidden; margin-bottom: 16px;}
.p-bar-bull { background-color: #0ECB81; transition: width 0.5s;}
.p-bar-bear { background-color: #F6465D; transition: width 0.5s;}
.soc-post { border-bottom: 1px solid #F0F2F5; padding-bottom: 16px; margin-bottom: 16px;}
.soc-post:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0;}
.s-author-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;}
.s-author { font-size: 14px; font-weight: 700; color: #1E2329; display: flex; align-items: center; gap: 8px;}
.s-avatar { width: 24px; height: 24px; background-color: #E65100; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px;}
.s-time { font-size: 12px; color: #848E9C;}
.s-content { font-size: 14px; color: #1E2329; line-height: 1.5; font-weight: 500;}
.s-bull-tag { color: #0ECB81; font-weight: 700; font-size: 12px;}
.s-bear-tag { color: #F6465D; font-weight: 700; font-size: 12px;}
</style>"""
            with col_social_stats:
                stats_html = f"""<div class="soc-card">
<div class="soc-title">Dữ liệu thảo luận (24h)</div>
<div class="soc-metrics">
<div class="soc-m-item"><span class="soc-m-lbl">Tương tác nổi bật</span><span class="soc-m-val">🔥</span></div>
<div class="soc-m-item"><span class="soc-m-lbl">Lượt đề cập</span><span class="soc-m-val">{f319_data['total_mentions']:,}</span></div>
<div class="soc-m-item"><span class="soc-m-lbl">Bài đăng</span><span class="soc-m-val">{f319_data['total_posts']}</span></div>
</div>
<div class="p-bar-labels">
<span style="color: #0ECB81;">Bìm bịp (Tăng giá) {f319_data['bullish_pct']}%</span>
<span style="color: #F6465D;">Chim lợn (Giảm giá) {f319_data['bearish_pct']}%</span>
</div>
<div class="p-bar-container">
<div class="p-bar-bull" style="width: {f319_data['bullish_pct']}%;"></div>
<div class="p-bar-bear" style="width: {f319_data['bearish_pct']}%;"></div>
</div>
<div style="font-size: 13px; color: #707A8A; line-height: 1.5; margin-top: 24px;">
Dữ liệu được rà soát tự động. Mức độ "Hưng phấn" áp đảo thường xuất hiện tại các vùng đỉnh ngắn hạn.
</div>
</div>"""
                st.markdown(f"{css_social}{stats_html}", unsafe_allow_html=True)

            with col_social_posts:
                posts_html = ""
                for p in f319_data['posts']:
                    tag_class = "s-bull-tag" if p['sentiment'] == "Bullish" else "s-bear-tag"
                    tag_text = "↑ Mua/Tăng" if p['sentiment'] == "Bullish" else "↓ Bán/Giảm"
                    posts_html += f"""<div class="soc-post">
<div class="s-author-row">
<div class="s-author"><div class="s-avatar">{p['author'][2].upper() if len(p['author']) > 2 else 'U'}</div>{p['author']}</div>
<div class="s-time">{p['time']}</div>
</div>
<div class="s-content">{p['content']} <br><span class="{tag_class}">{tag_text}</span></div>
</div>"""
                st.markdown(f"""<div class="soc-card" style="height: 400px; overflow-y: auto;">
<div class="soc-title">Bài đăng mới nhất</div>
{posts_html}
</div>""", unsafe_allow_html=True)

    # --- TAB 4: TRUNG TÂM KIỂM ĐỊNH BÁO CÁO (BACKTEST) ---
    with tab4:
        st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>🎯 KIỂM ĐỊNH KHUYẾN NGHỊ & DANH MỤC CHIẾN LƯỢC</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #474D57; font-size: 14px; margin-bottom: 24px;'>Theo dõi giá mục tiêu của các CTCK và các danh mục đầu tư trung/dài hạn.</div>", unsafe_allow_html=True)

        # Tạo 2 Tab con bên trong Tab 4
        sub_tab1, sub_tab2 = st.tabs(["Dòng thời gian Khuyến nghị (Ngắn hạn)", "Danh mục Chiến lược (Trung/Dài hạn)"])
        
        # ---------------------------------------------------------
        # THẾ GIỚI 1: DANH MỤC CHIẾN LƯỢC DÀI HẠN
        # ---------------------------------------------------------
        with sub_tab2:
            st.markdown("<br><div style='font-weight: 700; font-size: 16px; margin-bottom: 16px; color: #1E2329;'>Bảng Theo Dõi Danh Mục Đầu Tư Chiến Lược</div>", unsafe_allow_html=True)
            with st.spinner("Đang tải danh mục dài hạn..."):
                portfolio_data = fetch_portfolio_db()
                if not portfolio_data:
                    st.info("Chưa có dữ liệu.")
                else:
                    import pandas as pd
                    df_port = pd.DataFrame(portfolio_data)
                    
                    st.dataframe(
                        df_port,
                        column_config={
                            "Portfolio_Name": "Tên Danh mục",
                            "Sector": "Ngành",
                            "Ticker": st.column_config.TextColumn("Mã CP", width="small"),
                            "Company": "Tên Doanh nghiệp",
                            "Target_Price": st.column_config.NumberColumn("Giá Mục Tiêu (VND)", format="%d ₫"),
                            "Expected_Return": st.column_config.TextColumn("Kỳ Vọng (%)")
                        },
                        hide_index=True,
                        use_container_width=True,
                        height=400 
                    )
                    st.caption("💡 Mẹo: Nhấn vào tiêu đề cột (ví dụ: Tên Danh mục hoặc Kỳ vọng) để tự động sắp xếp.")

        # ---------------------------------------------------------
        # THẾ GIỚI 2: DÒNG THỜI GIAN KHUYẾN NGHỊ (NGẮN HẠN)
        # ---------------------------------------------------------
        with sub_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.spinner("Đang truy xuất hệ thống lưu trữ báo cáo (LINANCE_DB)..."):
                reports_data = fetch_reports_db()
                
                if not reports_data:
                    st.info("💡 Chưa có dữ liệu báo cáo LINANCE_DB")
                else:
                    import pandas as pd
                    import math
                    from datetime import datetime
                    df_rep = pd.DataFrame(reports_data)
                    
                    # Khởi tạo Session State cho phân trang Tab 4
                    if 'report_page' not in st.session_state: st.session_state.report_page = 1
                    
                    col_list, col_leaderboard = st.columns([1.7, 1])
                    
                    # ==========================================
                    # CỘT TRÁI: DANH SÁCH BÁO CÁO + BỘ LỌC
                    # ==========================================
                    with col_list:
                        # --- GIAO DIỆN BỘ LỌC ---
                        st.markdown("<div style='background-color: #FAFAFA; padding: 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #EAECEF;'>", unsafe_allow_html=True)
                        f_col1, f_col2 = st.columns(2)
                        
                        all_rep_brokers = ["Tất cả"] + df_rep['Broker'].dropna().unique().tolist()
                        with f_col1:
                            rep_broker_filter = st.selectbox("Lọc theo Công ty:", all_rep_brokers, key="rep_brk_flt")
                        with f_col2:
                            rep_time_filter = st.selectbox("Thời gian:", ["Tất cả", "Tháng này", "Hôm nay"], key="rep_time_flt")
                        st.markdown("</div>", unsafe_allow_html=True)

                        # --- XỬ LÝ LỌC DATA ---
                        filtered_rep = df_rep.copy()
                        if rep_broker_filter != "Tất cả":
                            filtered_rep = filtered_rep[filtered_rep['Broker'] == rep_broker_filter]
                        
                        if rep_time_filter == "Hôm nay":
                            today_str = datetime.now().strftime("%d/%m/%Y")
                            filtered_rep = filtered_rep[filtered_rep['Date'].astype(str).str.contains(today_str)]
                        elif rep_time_filter == "Tháng này":
                            month_str = datetime.now().strftime("/%m/%Y")
                            filtered_rep = filtered_rep[filtered_rep['Date'].astype(str).str.contains(month_str)]

                        # --- XỬ LÝ PHÂN TRANG ---
                        ITEMS_PER_PAGE = 5
                        total_items = len(filtered_rep)
                        total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
                        
                        if st.session_state.report_page > total_pages: st.session_state.report_page = total_pages
                        if st.session_state.report_page < 1: st.session_state.report_page = 1
                            
                        start_idx = (st.session_state.report_page - 1) * ITEMS_PER_PAGE
                        end_idx = start_idx + ITEMS_PER_PAGE
                        paged_rep = filtered_rep.iloc[start_idx:end_idx]

                        # --- HIỂN THỊ DANH SÁCH ---
                        st.markdown("<div style='font-weight: 700; font-size: 16px; margin-bottom: 16px; color: #1E2329;'>Dòng thời gian Khuyến nghị</div>", unsafe_allow_html=True)
                        
                        if paged_rep.empty:
                            st.warning("Không tìm thấy báo cáo nào khớp với bộ lọc!")
                        else:
                            css_rep = """
                            <style>
                            .rep-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; margin-bottom: 16px; transition: all 0.2s ease; border-left: 4px solid #1E2329; }
                            .rep-card:hover { border-color: #FF6B00; border-left: 4px solid #FF6B00; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); transform: translateX(4px); }
                            .rep-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
                            .rep-tkr { font-size: 20px; font-weight: 800; color: #1E2329; font-family: 'SF Mono', Consolas, monospace;}
                            .rep-brk { font-size: 12px; color: #707A8A; font-weight: 700; background: #F8FAFC; padding: 4px 8px; border-radius: 4px; border: 1px solid #EAECEF;}
                            .rep-mid { display: flex; gap: 32px; margin-bottom: 12px; }
                            .rep-lbl { font-size: 11px; color: #848E9C; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
                            .rep-val { font-size: 15px; font-weight: 700; color: #1E2329; }
                            .act-mua { color: #0ECB81; background: #E6FFF3; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 800;}
                            .act-ban { color: #F6465D; background: #FFF1F0; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 800;}
                            .act-giu { color: #F39C12; background: #FEF5E7; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 800;}
                            .sts-dat { color: #0ECB81; border: 1px solid #0ECB81; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; }
                            .sts-cat { color: #F6465D; border: 1px solid #F6465D; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; }
                            .sts-cho { color: #848E9C; border: 1px solid #848E9C; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; }
                            </style>
                            """
                            
                            reports_html = ""
                            for _, r in paged_rep.iterrows():
                                action = str(r.get('Action', '')).upper()
                                if 'MUA' in action: act_class = 'act-mua'
                                elif 'BÁN' in action: act_class = 'act-ban'
                                else: act_class = 'act-giu'
                                
                                status_raw = str(r.get('Status', 'Đang theo dõi')).strip()
                                if 'Đạt' in status_raw or 'Target' in status_raw:
                                    sts_class = 'sts-dat'
                                    sts_text = '✔️ ĐẠT TARGET'
                                elif 'Cắt' in status_raw or 'Lỗ' in status_raw:
                                    sts_class = 'sts-cat'
                                    sts_text = '❌ CẮT LỖ'
                                else:
                                    sts_class = 'sts-cho'
                                    sts_text = '⏳ ĐANG THEO DÕI'

                                try:
                                    target_price = f"{float(r.get('Target_Price', 0)):,.0f}"
                                    current_price = f"{float(r.get('Current_Price_At_Date', 0)):,.0f}"
                                except:
                                    target_price = r.get('Target_Price', 'N/A')
                                    current_price = r.get('Current_Price_At_Date', 'N/A')

                                reports_html += f"""<div class="rep-card"><div class="rep-top"><div style="display: flex; align-items: center; gap: 12px;"><span class="rep-tkr">{r.get('Ticker', 'N/A')}</span><span class="{act_class}">{action}</span><span class="{sts_class}">{sts_text}</span></div><span class="rep-brk">🏢 {r.get('Broker', 'N/A')}</span></div><div class="rep-mid"><div><div class="rep-lbl">Giá Mục Tiêu</div><div class="rep-val" style="color: #FF6B00;">{target_price}</div></div><div><div class="rep-lbl">Giá Lên Báo Cáo</div><div class="rep-val">{current_price}</div></div><div><div class="rep-lbl">Ngày Phát Hành</div><div class="rep-val" style="color: #707A8A; font-weight: 600;">{r.get('Date', 'N/A')}</div></div></div><div style="font-size: 12px; text-align: right;"><a href="{r.get('Link', '#')}" target="_blank" style="color: #0052FF; font-weight: 600; text-decoration: none;">Xem chi tiết báo cáo ↗</a></div></div>"""
                            st.markdown(f"{css_rep}<div>{reports_html}</div>", unsafe_allow_html=True)

                        # --- RENDER NÚT BẤM CHUYỂN TRANG ---
                        if total_pages > 1:
                            st.markdown("<br>", unsafe_allow_html=True)
                            pag_cols = st.columns([2, 1, 2, 1, 2]) 
                            with pag_cols[1]:
                                if st.button("◀ Trước", disabled=(st.session_state.report_page <= 1), use_container_width=True, key="rep_prev"):
                                    st.session_state.report_page -= 1
                                    st.rerun() 
                            with pag_cols[2]: 
                                st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57;'>Trang {st.session_state.report_page} / {total_pages}</div>", unsafe_allow_html=True)
                            with pag_cols[3]:
                                if st.button("Sau ▶", disabled=(st.session_state.report_page >= total_pages), use_container_width=True, key="rep_next"):
                                    st.session_state.report_page += 1
                                    st.rerun()

                    # ==========================================
                    # CỘT PHẢI: BẢNG XẾP HẠNG CTCK (AI SCORING)
                    # ==========================================
                    with col_leaderboard:
                        st.markdown("<div style='font-weight: 700; font-size: 16px; margin-bottom: 16px; color: #1E2329;'>🏆 Độ Tin Cậy CTCK (Win Rate)</div>", unsafe_allow_html=True)
                        st.markdown(f"""<div style='background: #FAFAFA; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; position: relative; margin-top: 10px;'>
<div style="font-size: 12px; color: #707A8A; margin-bottom: 20px; line-height: 1.5;">Hệ thống đang thu thập thêm dữ liệu giá lịch sử để đánh giá tỷ lệ dự phóng chính xác của các Tổ chức.</div>
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #EAECEF; padding-bottom: 12px; margin-bottom: 12px;"><div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 20px;">🥇</span><span style="font-weight: 700; color: #1E2329; font-size: 14px;">SSI Research</span></div><span style="font-weight: 800; color: #0ECB81; font-size: 16px;">78.5%</span></div>
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #EAECEF; padding-bottom: 12px; margin-bottom: 12px;"><div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 20px;">🥈</span><span style="font-weight: 700; color: #1E2329; font-size: 14px;">VNDirect</span></div><span style="font-weight: 800; color: #0ECB81; font-size: 16px;">72.1%</span></div>
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #EAECEF; padding-bottom: 12px; margin-bottom: 12px;"><div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 20px;">🥉</span><span style="font-weight: 700; color: #1E2329; font-size: 14px;">HSC</span></div><span style="font-weight: 800; color: #0ECB81; font-size: 16px;">69.4%</span></div>
<div style="display: flex; justify-content: space-between; align-items: center; padding-top: 4px;"><div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 16px; width: 20px; text-align: center; color: #848E9C; font-weight: 700;">4</span><span style="font-weight: 700; color: #474D57; font-size: 14px;">VCBS</span></div><span style="font-weight: 800; color: #F39C12; font-size: 16px;">55.0%</span></div>
<div style="margin-top: 24px; padding: 12px; background: #E6FFF3; border-radius: 6px; border: 1px dashed #0ECB81;"><div style="font-size: 11px; color: #0ECB81; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">🤖 AI Consensus</div><div style="font-size: 13px; color: #1E2329; font-weight: 600;">Phần lớn tổ chức đang đồng thuận MUA ở nhóm ngành: <b style="color: #FF6B00;">Công nghệ (FPT, CMG)</b></div></div>
</div>""", unsafe_allow_html=True)
# --- TAB 5: SO SÁNH DỊCH VỤ VÀ GÓI ƯU ĐÃI ---
    with tab5:
        st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>TÌM KIẾM GÓI MARGIN & PHÍ TỐI ƯU</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #474D57; font-size: 14px; margin-bottom: 24px;'>Hệ thống tự động phân tích và xếp hạng các chương trình ưu đãi từ các CTCK.</div>", unsafe_allow_html=True)

        with st.spinner("Đang trích xuất và phân tích các gói dịch vụ..."):
            broker_data = fetch_broker_services()
            
            if not broker_data:
                st.info(" Chưa có dữ liệu.LINANCE_DB")
            else:
                import pandas as pd
                df = pd.DataFrame(broker_data)
                
                # 1. BÓC TÁCH SỐ LIỆU ĐỂ AI TÍNH TOÁN (Xóa dấu %, biến thành số thực)
                df['Margin_Num'] = pd.to_numeric(df['Margin_Rate'].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(999)
                df['Fee_Num'] = pd.to_numeric(df['Trading_Fee'].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(999)
                
                # 2. TÌM RA "QUÁN QUÂN" CỦA THÁNG (Margin thấp nhất, nếu bằng nhau thì xét Phí thấp nhất)
                best_pkg = df.sort_values(by=['Margin_Num', 'Fee_Num']).iloc[0]
                
                # --- VẼ BẢNG VINH DANH QUÁN QUÂN ---
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #FFF4ECE6, #FFE0B280); border: 2px solid #FF6B00; border-radius: 12px; padding: 24px; margin-bottom: 32px; box-shadow: 0 8px 24px rgba(230, 81, 0, 0.15); position: relative; overflow: hidden;">
                    <div style="position: absolute; top: -10px; right: -10px; font-size: 80px; opacity: 0.1;">🏆</div>
                    <div style="color: #FF6B00; font-weight: 800; font-size: 14px; letter-spacing: 1px; margin-bottom: 8px;">🔥 LỰA CHỌN TỐI ƯU NHẤT THỜI ĐIỂM HIỆN TẠI</div>
                    <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px;">
                        <span style="font-size: 28px; font-weight: 800; color: #1E2329;">{best_pkg.get('Broker_Name', 'N/A')}</span>
                        <span style="background: #FF6B00; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">{best_pkg.get('Package_Name', 'Gói Ưu Đãi')}</span>
                    </div>
                    <div style="display: flex; gap: 40px;">
                        <div><div style="font-size: 12px; color: #707A8A; font-weight: 600;">LÃI SUẤT MARGIN</div><div style="font-size: 20px; font-weight: 800; color: #0ECB81;">{best_pkg.get('Margin_Rate', 'N/A')}</div></div>
                        <div><div style="font-size: 12px; color: #707A8A; font-weight: 600;">PHÍ GIAO DỊCH</div><div style="font-size: 20px; font-weight: 800; color: #1E2329;">{best_pkg.get('Trading_Fee', 'N/A')}</div></div>
                        <div><div style="font-size: 12px; color: #707A8A; font-weight: 600;">NGUỒN MARGIN</div><div style="font-size: 16px; font-weight: 700; color: #1E2329; margin-top: 4px;">{best_pkg.get('Margin_Pool', 'N/A')}</div></div>
                    </div>
                    <div style="margin-top: 16px; font-size: 14px; color: #474D57; font-style: italic;">🎯 Điểm nhấn: {best_pkg.get('Pros', '')}</div>
                </div>
                """, unsafe_allow_html=True)

                # 3. BỘ LỌC TÌM KIẾM (FILTERS)
                st.markdown("<div style='font-size: 16px; font-weight: 700; color: #1E2329; margin-bottom: 12px;'>🔍 Lọc & Tìm kiếm</div>", unsafe_allow_html=True)
                col_filter1, col_filter2, col_filter3 = st.columns([2, 1.5, 1.5])
                
                # Danh sách công ty độc nhất
                all_brokers = df['Broker_Name'].dropna().unique().tolist()
                
                with col_filter1:
                    selected_brokers = st.multiselect("Chọn Công ty Chứng khoán:", options=all_brokers, default=all_brokers)
                with col_filter2:
                    sort_option = st.selectbox("Sắp xếp theo:", ["Margin thấp đến cao", "Phí thấp đến cao"])
                with col_filter3:
                    margin_pool = st.selectbox("Tình trạng Margin:", ["Tất cả", "Dồi dào", "Căng"])

                # 4. ÁP DỤNG BỘ LỌC VÀO DATA
                filtered_df = df[df['Broker_Name'].isin(selected_brokers)]
                if margin_pool != "Tất cả":
                    filtered_df = filtered_df[filtered_df['Margin_Pool'].astype(str).str.contains(margin_pool, case=False, na=False)]
                
                if sort_option == "Margin thấp đến cao":
                    filtered_df = filtered_df.sort_values(by=['Margin_Num', 'Fee_Num'])
                else:
                    filtered_df = filtered_df.sort_values(by=['Fee_Num', 'Margin_Num'])

                # 5. VẼ LƯỚI CARD KẾT QUẢ
                st.markdown("<hr style='border-color: #EAECEF; margin: 24px 0;'>", unsafe_allow_html=True)
                
                if filtered_df.empty:
                    st.warning("Không tìm thấy gói dịch vụ nào khớp với bộ lọc của bạn!")
                else:
                    css_broker = """
                    <style>
                    .b-container { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 10px; }
                    .b-card { background: #fff; border: 1px solid #EAECEF; border-radius: 12px; padding: 20px; width: 320px; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; }
                    .b-card:hover { border-color: #FF6B00; box-shadow: 0 8px 24px rgba(230, 81, 0, 0.1); transform: translateY(-4px); }
                    .b-name { font-size: 18px; font-weight: 800; color: #1E2329; margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between; }
                    .b-pkg { font-size: 12px; font-weight: 600; color: #FF6B00; margin-bottom: 16px; background: #FFF2E5; padding: 4px 8px; border-radius: 4px; display: inline-block;}
                    .b-stat { display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px dashed #F0F2F5; padding-bottom: 8px; font-size: 13px; }
                    .b-lbl { color: #707A8A; font-weight: 600; }
                    .b-val { color: #1E2329; font-weight: 700; }
                    .b-pros { background: #F8FAFC; border-radius: 6px; padding: 12px; margin-top: auto; font-size: 12px; color: #474D57; font-style: italic; border-left: 3px solid #FF6B00; }
                    .b-upd { font-size: 10px; color: #848E9C; margin-top: 12px; text-align: right; }
                    </style>
                    """
                    
                    cards_html = ""
                    for _, b in filtered_df.iterrows():
                        pool_color = "#0ECB81" if "Dồi dào" in str(b.get('Margin_Pool', '')) else "#F6465D" if "Căng" in str(b.get('Margin_Pool', '')) else "#F39C12"
                        
                        cards_html += f"""<div class="b-card"><div class="b-name"><span>{b.get('Broker_Name', 'N/A')}</span></div><div class="b-pkg">{b.get('Package_Name', 'Gói Tiêu Chuẩn')}</div><div class="b-stat"><span class="b-lbl">Phí giao dịch</span><span class="b-val" style="color: #FF6B00;">{b.get('Trading_Fee', 'N/A')}</span></div><div class="b-stat"><span class="b-lbl">Lãi suất Margin</span><span class="b-val">{b.get('Margin_Rate', 'N/A')}</span></div><div class="b-stat"><span class="b-lbl">Nguồn Margin</span><span class="b-val" style="color: {pool_color};">{b.get('Margin_Pool', 'N/A')}</span></div><div class="b-pros">🎯 {b.get('Pros', 'Liên hệ chi tiết')}</div><div class="b-upd">Cập nhật: {b.get('Last_Updated', 'N/A')}</div></div>"""
                    
                    final_html = f"{css_broker}<div class='b-container'>{cards_html}</div>"
                    st.markdown(final_html, unsafe_allow_html=True)
# ==========================================
# KHỐI 3: TIN TỨC & CAROUSEL
# ==========================================
@st.fragment
def render_news_section():
    df_news = fetch_mainstream_news()
    
    # --- PHẦN 1: BĂNG CHUYỀN TIN NÓNG ---
    st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase; border-top: 1px solid #EAECEF; padding-top: 24px;'>🔥 Tiêu điểm Giao dịch (Hot News)</div>", unsafe_allow_html=True)
    if not df_news.empty:
        hot_news_df = df_news[df_news['tag'].str.contains('🔥')].head(6)
        if hot_news_df.empty: hot_news_df = df_news.head(6)
        
        slides_html = ""
        for i, row in hot_news_df.iterrows():
            summary = ' '.join(row['title'].split()[:18]) + "..."
            slides_html += f"""
            <div class="slide">
                <a href="{row['link']}" target="_blank" class="scroll-card">
                    <div class="tag-hot">🔥 TIN CHẤN ĐỘNG</div>
                    <div class="meta">{row['ctck']} • {row['date']}</div>
                    <div class="title">{summary}</div>
                </a>
            </div>
            """

        carousel_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif; overflow: hidden; }}
            .slider-container {{ width: 100%; overflow: hidden; position: relative; padding: 10px 0; }}
            .slider-track {{ display: flex; transition: transform 0.6s cubic-bezier(0.25, 1, 0.5, 1); }}
            .slide {{ min-width: 33.333%; padding: 0 8px; box-sizing: border-box; }}
            .scroll-card {{ background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; height: 160px; text-decoration: none; transition: all 0.2s; box-sizing: border-box; }}
            .scroll-card:hover {{ border-color: #E65100; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); }}
            .tag-hot {{ background: #FFF2E5; color: #E65100; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 800; margin-bottom: 8px; display: inline-block; width: max-content; }}
            .meta {{ color: #848E9C; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }}
            .title {{ color: #1E2329; font-size: 15px; font-weight: 700; line-height: 1.4; }}
        </style>
        </head>
        <body>
            <div class="slider-container">
                <div class="slider-track" id="track">
                    {slides_html}
                </div>
            </div>
            <script>
                const track = document.getElementById('track');
                const totalSlides = {len(hot_news_df)};
                let index = 0;
                setInterval(() => {{
                    let maxIndex = totalSlides > 3 ? totalSlides - 3 : 0;
                    if (index >= maxIndex) {{ index = 0; }} else {{ index++; }}
                    track.style.transform = `translateX(-${{index * 33.333}}%)`;
                }}, 5000);
            </script>
        </body>
        </html>
        """
        components.html(carousel_html, height=200)

    # --- PHẦN 2: TÌM KIẾM & LƯỚI TIN TỨC ---
    if 'current_page' not in st.session_state: st.session_state.current_page = 1
    if 'search_query' not in st.session_state: st.session_state.search_query = ""

    st.markdown("<br><div class='section-title' style='margin-top: 0px;'>Thông tin thị trường trong nước và nước ngoài</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background-color: #FFF8F3; padding: 20px; border-radius: 8px; margin-bottom: 24px; border: 1px solid #FFE0B2;'>", unsafe_allow_html=True)
        col_input, col_btn = st.columns([5, 1])
        with col_input: 
            search_val = st.text_input("Tìm kiếm", value=st.session_state.search_query, placeholder="Gõ mã CK hoặc Tên công ty...", label_visibility="collapsed")
        with col_btn:
            if st.button("🔍 Tìm kiếm", use_container_width=True):
                st.session_state.search_query = search_val
                st.session_state.current_page = 1
                
        col_radio, col_region, col_time = st.columns([3, 2, 2])
        with col_radio: 
            filter_type = st.radio("Phân loại:", ["Tất cả", "Công ty", "Tin tức", "Lãnh đạo"], horizontal=True, label_visibility="collapsed")
        with col_region:
            region_filter = st.radio("Khu vực:", ["Tất cả", "🇻🇳 Trong nước", "🌎 Quốc tế"], horizontal=True, label_visibility="collapsed")
        with col_time: 
            time_filter = st.selectbox("Thời gian:", ["Mọi lúc", "Hôm nay", "Tuần này"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    if df_news.empty: 
        st.info("Hệ thống đang cập nhật tin tức...")
        return

    filtered_df = df_news.copy()
    
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        filtered_df = filtered_df[filtered_df['title'].astype(str).str.lower().str.contains(query) | filtered_df['tag'].astype(str).str.lower().str.contains(query)]
        
    if filter_type == "Tin tức": 
        filtered_df = filtered_df[filtered_df['tag'] == "Tin vĩ mô"]
    elif filter_type == "Cổ phiếu quan tâm": 
        filtered_df = filtered_df[filtered_df['tag'].astype(str).str.contains("🔥 Cổ phiếu quan tâm")]

    if region_filter == "🇻🇳 Trong nước":
        filtered_df = filtered_df[filtered_df['region'] == 'VN']
    elif region_filter == "🌎 Quốc tế":
        filtered_df = filtered_df[filtered_df['region'] == 'GLOBAL']

    if time_filter == "Hôm nay":
        today_str = datetime.now().strftime("%d/%m/%Y")
        filtered_df = filtered_df[filtered_df['date'].astype(str).str.contains(today_str)]

    ITEMS_PER_PAGE = 8
    total_items = len(filtered_df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
    
    if st.session_state.current_page > total_pages: 
        st.session_state.current_page = total_pages
        
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paged_df = filtered_df.iloc[start_idx:end_idx]

    if paged_df.empty:
        st.warning("Không tìm thấy kết quả nào phù hợp với từ khóa/bộ lọc của bạn.")
    else:
        css_grid = """<style>
        .n-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; margin-bottom: 16px; transition: all 0.2s ease; height: 100%; display: flex; flex-direction: column; justify-content: space-between;}
        .n-card:hover { border-color: #FF6B00; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); }
        </style>"""
        st.markdown(css_grid, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        for i, row in paged_df.reset_index().iterrows():
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                flag = "🌎" if row.get('region') == 'GLOBAL' else "🇻🇳"
                card_html = f"""<a href="{row['link']}" target="_blank" style="text-decoration: none; color: inherit; display: block; height: 100%;">
<div class='n-card'>
<div>
<div style='color: #FF6B00; font-size: 11px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase;'>{flag} {row['ctck']} • {row['tag']}</div>
<div style='color: #1E2329; font-size: 15px; font-weight: 700; margin-bottom: 12px; line-height: 1.4;'>{row['title']}</div>
</div>
<div style='color: #848E9C; font-size: 12px; font-weight: 600;'>🕒 {row['date']}</div>
</div></a>"""
                st.markdown(card_html, unsafe_allow_html=True)

    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        pag_cols = st.columns([3, 1, 2, 1, 3]) 
        
        with pag_cols[1]:
            if st.button("◀ Trước", disabled=(st.session_state.current_page <= 1), use_container_width=True, key="prev_btn"):
                st.session_state.current_page -= 1
                st.rerun(scope="fragment") 
                
        with pag_cols[2]: 
            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
            
        with pag_cols[3]:
            if st.button("Sau ▶", disabled=(st.session_state.current_page >= total_pages), use_container_width=True, key="next_btn"):
                st.session_state.current_page += 1
                st.rerun(scope="fragment")

# ==========================================
# ==========================================
# KHỐI 4: FOOTER BẢN QUYỀN
# ==========================================
def render_footer():
    st.markdown("""
        <hr style="margin-top: 60px; border-color: #EAECEF;">
        <div style="color: #707A8A; font-size: 12px; padding: 20px 0 40px 0; line-height: 1.6;">
            <p style="font-weight: 600; margin-bottom: 8px; color: #474D57;">Từ chối trách nhiệm:</p>
            <ul style="padding-left: 20px; margin-bottom: 16px;">
                <li>Nội dung trên trang web này được soạn riêng cho mục đích cung cấp thông tin và không phải là cơ sở để đưa ra quyết định đầu tư, hay được hiểu là đề xuất tham gia vào các giao dịch chứng khoán hoặc sử dụng làm chiến lược đầu tư đối với bất kỳ mã cổ phiếu nào.</li>
                <li>Trang web này do <b>Vietnam Securities Research</b> phát hành và không liên quan đến các dịch vụ tư vấn đầu tư, thuế, pháp lý, tài chính, kế toán. Đây không phải là khuyến nghị mua, bán hoặc nắm giữ bất kỳ tài sản nào.</li>
                <li>Thông tin trên trang web này dựa trên các nguồn được xem là đáng tin cậy (Dữ liệu giao dịch từ Yahoo Finance, tin tức từ các báo chính thống), nhưng chúng tôi không đảm bảo tính chính xác hoặc đầy đủ tuyệt đối.</li>
                <li>Bất kỳ quan điểm hoặc ước tính nào được trình bày tại đây phản ánh sự đánh giá của hệ thống vào thời điểm này và có thể thay đổi mà không cần thông báo trước.</li>
            </ul>
            <div style="text-align: center; margin-top: 24px; font-size: 13px;">
                © 2017 - 2026 Vietnam Securities Research. Bảo lưu mọi quyền.<br>
                <span style="font-size: 14px;">Nhà phát triển: <b style="color: #E65100;">ThangLong</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)
