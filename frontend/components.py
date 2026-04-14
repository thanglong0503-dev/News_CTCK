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
from backend.database import fetch_broker_services, fetch_reports_db, fetch_portfolio_db, fetch_manual_price_db, fetch_vndiamond_db
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
    st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>Bản đồ Nhiệt Dòng tiền (Market Heatmap)</div>", unsafe_allow_html=True)
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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["TỔNG QUAN THỊ TRƯỜNG", "DỮ LIỆU GIAO DỊCH", "PHÂN TÍCH AI", "BÁO CÁO TỔ CHỨC", "SO SÁNH DỊCH VỤ", "PHÂN TÍCH CỔ PHIẾU"])

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


        # =========================================================
        # KHU VỰC ĐỊNH LƯỢNG KÉP (BẢNG TRÁI + TOP-DOWN PHẢI)
        # =========================================================
        st.markdown("<br><h3 style='color: #1E2329; margin-top: 32px; margin-bottom: 24px; border-top: 1px solid #EAECEF; padding-top: 32px;'>Định Lượng Dòng Tiền & Bộ Lọc Sóng Ngành</h3>", unsafe_allow_html=True)

        import pandas as pd
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        import json

        @st.cache_data(ttl=3600, show_spinner="Đang rút data từ Google Sheets...")
        def fetch_db_from_sheet(worksheet_name):
            try:
                creds_str = st.secrets["GOOGLE_CREDENTIALS"]
                creds_dict = json.loads(creds_str)
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)
                sheet = client.open("LINANCE_DB").worksheet(worksheet_name)
                
                # SỬA LỖI Ở ĐÂY: Lấy raw string thay vì để nó tự format sai
                raw_data = sheet.get_all_values()
                if len(raw_data) > 1:
                    headers = raw_data[0]
                    df = pd.DataFrame(raw_data[1:], columns=headers)
                    return df
                return pd.DataFrame()
            except Exception as e:
                st.error(f"Lỗi kết nối Tab {worksheet_name}: {e}")
                return pd.DataFrame()

        with st.spinner("Đang xử lý dữ liệu chuẩn Việt Nam..."):
            df_rs_raw = fetch_db_from_sheet("RS_DATA")
            df_ind_raw = fetch_db_from_sheet("INDUSTRY_DATA")
            
            # Hàm dọn dẹp số liệu: chuyển phẩy thành chấm và ép kiểu an toàn
            def clean_number(series):
                return pd.to_numeric(series.astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

            if not df_ind_raw.empty:
                df_ind = df_ind_raw.copy()
                df_ind['RS_TB'] = clean_number(df_ind['RS_TB'])
                df_ind['Điểm_KT_TB'] = clean_number(df_ind['Điểm_KT_TB'])
            else:
                df_ind = pd.DataFrame()

            if not df_rs_raw.empty:
                df_rs = df_rs_raw.copy()
                df_rs['RS_1M'] = clean_number(df_rs['RS_1M'])
                df_rs['RS_3M'] = clean_number(df_rs['RS_3M'])
                df_rs['Thanh_Khoản_Tỷ'] = clean_number(df_rs['Thanh_Khoản_Tỷ'])
                df_rs['Điểm_KT'] = clean_number(df_rs['Điểm_KT'])
            else:
                df_rs = pd.DataFrame()

        col_left, col_right = st.columns([1, 1.1], gap="large")

        # --- CỘT TRÁI: BẢNG XẾP HẠNG (GIỮ NGUYÊN) ---
        with col_left:
            st.markdown("<div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase;'>🔥 Bảng Xếp Hạng Sức Mạnh Giá (RS)</div>", unsafe_allow_html=True)
            st.markdown("<div style='color: #707A8A; font-size: 13px; margin-bottom: 16px;'>Dữ liệu đã lọc Rác. <span style='color: #9C27B0; font-weight: 800;'>Màu Tím (RS > 90)</span> là các mã dẫn dắt.</div>", unsafe_allow_html=True)

            if df_rs.empty:
                st.warning("⚠️ Đang tải dữ liệu cổ phiếu...")
            else:
                df_rs_filtered = df_rs[df_rs['RS_1M'] >= 80]
                df_rs_sorted = df_rs_filtered.sort_values(by="RS_1M", ascending=False).head(20).reset_index(drop=True)

                css_rs_table = "<style>.rs-table-container { width: 100%; background: #fff; border: 1px solid #EAECEF; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }.rs-table { width: 100%; border-collapse: collapse; text-align: center; font-family: 'Segoe UI', sans-serif; }.rs-table th { background-color: #F8FAFC; color: #474D57; font-size: 11px; font-weight: 800; text-transform: uppercase; padding: 12px 16px; border-bottom: 2px solid #EAECEF; }.rs-table td { padding: 10px 16px; border-bottom: 1px solid #F0F2F5; font-size: 14px; font-weight: 700; color: #1E2329; }.rs-ticker { font-size: 15px; font-weight: 900; color: #1E2329; }.rs-sector { font-size: 10px; color: #848E9C; font-weight: 600; }.rs-cell { color: #fff; font-weight: 800; font-size: 13px; border-radius: 4px; padding: 4px 8px; display: inline-block; min-width: 32px; }</style>"
                
                def get_rs_style(score):
                    if score >= 90: return "background-color: #9C27B0; color: #FFFFFF;"
                    elif score >= 70: return "background-color: #0ECB81; color: #FFFFFF;"
                    elif score >= 40: return "background-color: #FFB300; color: #1E2329;"
                    else: return "background-color: #F6465D; color: #FFFFFF;"

                rows_html = ""
                for _, row in df_rs_sorted.iterrows():
                    style_1m = get_rs_style(row['RS_1M'])
                    style_3m = get_rs_style(row['RS_3M'])
                    rows_html += f"<tr><td style='text-align: left;'><div class='rs-ticker'>{row['Mã CK']}</div><div class='rs-sector'>{row['Ngành']}</div></td><td><div class='rs-cell' style='{style_1m}'>{int(row['RS_1M'])}</div></td><td><div class='rs-cell' style='{style_3m}'>{int(row['RS_3M'])}</div></td></tr>"
                    
                table_html = f"<div class='rs-table-container'><table class='rs-table'><thead><tr><th style='text-align: left;'>CỔ PHIẾU</th><th>RS 1T</th><th>RS 3T</th></tr></thead><tbody>{rows_html}</tbody></table></div>"
                st.markdown(css_rs_table + table_html, unsafe_allow_html=True)


        # --- CỘT PHẢI: BỘ LỌC TOP-DOWN ---
        with col_right:
            st.markdown("<div style='font-size: 14px; font-weight: 700; color: #303F9F; text-transform: uppercase; margin-bottom: 16px;'>🎯 Screener Tài Chính: Lọc Sóng Ngành</div>", unsafe_allow_html=True)
            st.markdown("<div style='color: #707A8A; font-size: 13px; margin-bottom: 16px;'>Chọn Ngành đang dẫn sóng để tìm ra những Cổ phiếu mạnh nhất.</div>", unsafe_allow_html=True)

            if df_ind.empty or df_rs.empty:
                st.warning("⚠️ Đang tải dữ liệu bộ lọc...")
            else:
                df_ind_sorted = df_ind.sort_values(by="RS_TB", ascending=False).reset_index(drop=True)
                industry_options = [f"{row['Ngành']} (RS: {row['RS_TB']:.1f})" for _, row in df_ind_sorted.iterrows()]

                st.markdown("<span style='font-weight:700; font-size:14px; color:#1E2329;'>BƯỚC 1: CHỌN NGÀNH ĐỂ SOI DÒNG TIỀN</span>", unsafe_allow_html=True)
                selected_option = st.selectbox("Danh sách Ngành (Sắp xếp từ mạnh đến yếu):", industry_options, label_visibility="collapsed")
                
                selected_industry_name = selected_option.split(" (RS:")[0]

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-weight:700; font-size:14px; color:#1E2329;'>BƯỚC 2: TOP CỔ PHIẾU NGÀNH <span style='color:#E65100;'>{selected_industry_name.upper()}</span></span>", unsafe_allow_html=True)
                
                df_filtered = df_rs[(df_rs['Ngành'] == selected_industry_name) & (df_rs['Thanh_Khoản_Tỷ'] > 0)].copy()
                df_filtered = df_filtered.sort_values(by="RS_1M", ascending=False).head(15).reset_index(drop=True)

                if df_filtered.empty:
                    st.info("Chưa có dữ liệu cổ phiếu thanh khoản cao cho ngành này.")
                else:
                    rows_html_right = ""
                    for _, row in df_filtered.iterrows():
                        style_1m = get_rs_style(row['RS_1M'])
                        score = int(row['Điểm_KT'])
                        stars = "⭐" * score + "☆" * (5 - score)

                        rows_html_right += f"<tr><td style='text-align: left;'><div class='rs-ticker'>{row['Mã CK']}</div><div class='rs-sector'>Thanh khoản: {row['Thanh_Khoản_Tỷ']:.1f} Tỷ</div></td><td><div class='rs-cell' style='{style_1m}'>{int(row['RS_1M'])}</div></td><td style='color: #E65100; font-size: 13px; font-weight: 700;'>{stars}</td></tr>"
                        
                    table_html_right = f"<div class='rs-table-container'><table class='rs-table'><thead><tr><th style='text-align: left;'>MÃ CK</th><th>RS 1T</th><th>ĐIỂM KỸ THUẬT</th></tr></thead><tbody>{rows_html_right}</tbody></table></div>"
                    st.markdown(css_rs_table + table_html_right, unsafe_allow_html=True)

        # =========================================================
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
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Dòng thời gian Khuyến nghị (Ngắn hạn)", "Danh mục Chiến lược (Trung/Dài hạn)","VNDiamond Flow"])
        
        # ---------------------------------------------------------
      # ---------------------------------------------------------
        # THẾ GIỚI 1: DANH MỤC CHIẾN LƯỢC DÀI HẠN (BẢN FULL CHUẨN KHÔNG LỖI)
        # ---------------------------------------------------------
        with sub_tab2:
            st.markdown("<br><div style='font-weight: 900; font-size: 18px; margin-bottom: 16px; color: #FF6B00; text-transform: uppercase; border-left: 4px solid #FF6B00; padding-left: 12px;'>Quản trị & Đánh giá Danh mục Đầu tư (Real-time)</div>", unsafe_allow_html=True)
            
            @st.fragment
            def render_long_term_portfolio():
                import pandas as pd
                import yfinance as yf
                import time

                # ==========================================
               # ==========================================
                # 1. KÉT SẮT & ĐỘNG CƠ LẤY SỈ (BẢN GỐC CHỈ DÙNG .VN)
                # ==========================================
                if 'port_cached_df' not in st.session_state or time.time() - st.session_state.get('port_cache_time', 0) > 900:
                    with st.spinner("Đang đồng bộ dữ liệu Danh mục Dài hạn (Bản gốc ổn định)..."):
                        portfolio_data = fetch_portfolio_db()
                        
                       # --- 1. KÉO PHAO CỨU SINH TỪ THỦ CÔNG (BẢN SẠCH CHẠY NGẦM) ---
                        manual_dict = {}
                        try:
                            manual_data = fetch_manual_price_db()
                            if manual_data and len(manual_data) > 1:
                                for row in manual_data[1:]: # Bỏ qua dòng tiêu đề
                                    if len(row) >= 2:
                                        tk = str(row[0]).strip().upper()
                                        if tk:
                                            # Ép kiểu bất chấp mọi định dạng
                                            pr_str = str(row[1]).replace(',', '').replace('.', '').replace(' ', '').strip()
                                            try:
                                                manual_dict[tk] = float(pr_str)
                                            except: pass
                        except Exception as e:
                            pass
                        # -------------------------------------------------------------
                        # ------------------------------------------------
                        # -------------------------------------------
                        
                        if not portfolio_data:
                            st.session_state.port_cached_df = pd.DataFrame()
                        else:
                            df_port = pd.DataFrame(portfolio_data)
                            
                            unique_tickers = df_port['Ticker'].dropna().astype(str).str.strip().unique().tolist()
                            yf_tickers = [t + ".VN" if not t.endswith(".VN") else t for t in unique_tickers if t]
                            
                            batch_data = pd.DataFrame()
                            if yf_tickers:
                                try:
                                    batch_data = yf.download(yf_tickers, period="6mo", group_by='ticker', threads=False, progress=False, ignore_tz=True)
                                except Exception as e: pass

                            current_prices, actual_returns, statuses, highest_prices = [], [], [], []

                            for _, row in df_port.iterrows():
                                tkr = str(row.get('Ticker', '')).strip()
                                rec_p = float(row.get('Rec_Price', 0)) if str(row.get('Rec_Price', 0)).replace('.','',1).isdigit() else 0
                                tgt_p = float(row.get('Target_Price', 0)) if str(row.get('Target_Price', 0)).replace('.','',1).isdigit() else 0
                                rec_date_str = str(row.get('Rec_Date', ''))
                                
                                cp, highest_price, lowest_price = 0, 0, 0
                                yf_t = tkr + ".VN" if not tkr.endswith(".VN") else tkr
                                
                                if not batch_data.empty and yf_tickers:
                                    try:
                                        if len(yf_tickers) == 1: ticker_df = batch_data 
                                        elif isinstance(batch_data.columns, pd.MultiIndex) and yf_t in batch_data.columns.levels[0]: ticker_df = batch_data[yf_t]
                                        else: ticker_df = pd.DataFrame()
                                        
                                        if not ticker_df.empty:
                                            sliced_df = ticker_df.copy()
                                            if sliced_df.index.tz is not None: sliced_df.index = sliced_df.index.tz_localize(None)
                                            try:
                                                start_ts = pd.to_datetime(rec_date_str, format="%d/%m/%Y")
                                                sliced_df = sliced_df[sliced_df.index >= start_ts]
                                            except: pass 
                                                
                                            if not sliced_df.empty:
                                                valid_closes = sliced_df['Close'].dropna()
                                                if not valid_closes.empty:
                                                    cp = valid_closes.iloc[-1]
                                                    highest_price = sliced_df['High'].dropna().max()
                                                    lowest_price = sliced_df['Low'].dropna().min()
                                                    if cp < 1000 and cp > 0: cp *= 1000; highest_price *= 1000; lowest_price *= 1000
                                    except: pass
                                
                                # ==========================================
                                # KÍCH HOẠT PHAO CỨU SINH HYBRID NẾU YAHOO LỖI
                                # ==========================================
                                if cp == 0 or pd.isna(cp):
                                    if tkr in manual_dict:
                                        cp = float(manual_dict[tkr])
                                        if highest_price == 0: highest_price = cp
                                        if lowest_price == 0: lowest_price = cp
                                # ==========================================
                                
                                current_prices.append(cp if cp > 0 else None) 
                                highest_prices.append(highest_price if highest_price > 0 else None)
                                
                                if rec_p > 0 and cp > 0: actual_returns.append(((cp - rec_p) / rec_p) * 100)
                                else: actual_returns.append(None) 
                                    
                                if cp == 0 or lowest_price == 0: 
                                    statuses.append("⏳ Đang bám sát") 
                                elif highest_price >= tgt_p and tgt_p > 0: 
                                    statuses.append("✔️ Đã Đạt Target")
                                elif rec_p > 0 and lowest_price > 0 and lowest_price <= rec_p * 0.88: 
                                    if cp >= rec_p * 0.98: statuses.append("⏳ Đang bám sát")
                                    else: statuses.append("❌ Đã Chạm Cắt Lỗ")
                                else: statuses.append("⏳ Đang bám sát")

                            df_port['Current_Price'] = current_prices
                            df_port['Actual_Return'] = actual_returns
                            df_port['Auto_Status'] = statuses
                            df_port['Highest_Reached'] = highest_prices
                            
                            st.session_state.port_cached_df = df_port
                            st.session_state.port_cache_time = time.time()

                # ==========================================
                # 2. VẼ GIAO DIỆN TỪ RAM SIÊU TỐC
                # ==========================================
                cached_port = st.session_state.port_cached_df
                
                if cached_port.empty:
                    st.info("💡 Chưa có dữ liệu. Ngươi hãy tạo tab 'PORTFOLIO_DB' trên Sheets nhé!")
                    return
                
                st.markdown("""
                <style>
                div[data-baseweb="select"] > div {
                    background-color: #FFF9F5 !important;
                    border: 1px solid #FFE0B2 !important;
                    border-radius: 8px !important;
                    font-weight: 700 !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                df_port = cached_port.copy()
                portfolios = df_port['Portfolio_Name'].dropna().unique().tolist()
                
                st.markdown("<div style='background-color: #FFF; padding: 16px; border-radius: 12px; margin-bottom: 24px; border: 1px solid #FFE0B2; box-shadow: 0 4px 12px rgba(255,107,0,0.05);'>", unsafe_allow_html=True)
                selected_port = st.selectbox("📌 Chọn Danh mục Chiến lược để theo dõi:", portfolios, key="long_term_port_filter")
                st.markdown("</div>", unsafe_allow_html=True)

                filtered_port = df_port[df_port['Portfolio_Name'] == selected_port].copy()

                num_stocks = len(filtered_port)
                try:
                    avg_expected = filtered_port['Expected_Return'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float).mean()
                    avg_exp_str = f"+{avg_expected:.1f}%"
                except: avg_exp_str = "N/A"
                    
                valid_returns = [r for r in filtered_port['Actual_Return'].tolist() if r is not None and not pd.isna(r)]
                if valid_returns:
                    avg_actual = sum(valid_returns) / len(valid_returns)
                    color_act = "#0ECB81" if avg_actual >= 0 else "#F6465D"
                    sign_act = "+" if avg_actual > 0 else ""
                    avg_act_str = f"{sign_act}{avg_actual:.1f}%"
                else:
                    color_act = "#707A8A"
                    avg_act_str = "N/A"
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                card_style = "background: linear-gradient(180deg, #FFFFFF 0%, #FFF9F5 100%); border: 1px solid #FFE0B2; border-bottom: 4px solid #FF6B00; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(255,107,0,0.08); transition: all 0.3s ease;"
                title_style = "color: #FF6B00; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;"
                
                with col_s1: st.markdown(f"<div style='{card_style}'><div style='{title_style}'>📦 Số Lượng Mã</div><div style='font-size: 26px; font-weight: 900; color: #1E2329;'>{num_stocks}</div></div>", unsafe_allow_html=True)
                with col_s2: st.markdown(f"<div style='{card_style}'><div style='{title_style}'>🎯 Kỳ Vọng TB</div><div style='font-size: 26px; font-weight: 900; color: #1E2329;'>{avg_exp_str}</div></div>", unsafe_allow_html=True)
                with col_s3: st.markdown(f"<div style='{card_style}'><div style='{title_style}'>💰 Lãi/Lỗ T.Tế</div><div style='font-size: 26px; font-weight: 900; color: {color_act};'>{avg_act_str}</div></div>", unsafe_allow_html=True)
                with col_s4:
                    dat_target_count = filtered_port['Auto_Status'].tolist().count('✔️ Đã Đạt Target')
                    st.markdown(f"<div style='{card_style}'><div style='{title_style}'>🏆 Đã Chạm Target</div><div style='font-size: 26px; font-weight: 900; color: #0ECB81;'>{dat_target_count}/{num_stocks}</div></div>", unsafe_allow_html=True)

                st.markdown("<div style='background: #FF6B00; color: white; padding: 12px 16px; border-radius: 8px 8px 0 0; font-weight: 800; font-size: 14px; letter-spacing: 1px; margin-top: 32px;'>📊 BẢNG THEO DÕI CHI TIẾT DANH MỤC CỔ PHIẾU</div>", unsafe_allow_html=True)
                
                st.dataframe(
                    filtered_port,
                    column_config={
                        "Portfolio_Name": None, 
                        "Sector": None, 
                        "Rec_Date": st.column_config.TextColumn("🔸 NGÀY KN"),
                        "Ticker": st.column_config.TextColumn("🔸 MÃ CP", width="small"),
                        "Company": st.column_config.TextColumn("🔸 DOANH NGHIỆP", width="medium"),
                        "Rec_Price": st.column_config.NumberColumn("🔸 GIÁ KN", format="%d ₫"),
                        "Current_Price": st.column_config.NumberColumn("🔸 GIÁ HIỆN TẠI", format="%d ₫"),
                        "Highest_Reached": st.column_config.NumberColumn("🔸 ĐỈNH ĐÃ CHẠM", format="%d ₫"),
                        "Target_Price": st.column_config.NumberColumn("🔸 GIÁ MỤC TIÊU", format="%d ₫"),
                        "Expected_Return": st.column_config.TextColumn("🔸 KỲ VỌNG"),
                        "Actual_Return": st.column_config.NumberColumn("🔸 LÃI/LỖ", format="%.1f %%"),
                        "Auto_Status": st.column_config.TextColumn("🔸 ĐÁNH GIÁ (AI)"),
                        "Link": st.column_config.LinkColumn("🔸 NGUỒN", display_text="Xem ↗")
                    },
                    hide_index=True,
                    width="stretch",
                    height=450 
                )
            
            # KÍCH HOẠT TIỂU VŨ TRỤ
            render_long_term_portfolio()
# ---------------------------------------------------------
        # ---------------------------------------------------------
        # ---------------------------------------------------------
        # THẾ GIỚI 3: THEO DÕI DÒNG TIỀN VNDIAMOND (HYBRID REAL-TIME)
        # ---------------------------------------------------------
        with sub_tab3:
            st.markdown("<br><div style='font-weight: 900; font-size: 18px; margin-bottom: 16px; color: #FF6B00; text-transform: uppercase; border-left: 5px solid #FF6B00; padding-left: 12px;'>Phân tích Dòng tiền Cơ cấu Rổ VNDiamond</div>", unsafe_allow_html=True)
            
            @st.fragment
            def render_vndiamond_flow():
                import pandas as pd
                import yfinance as yf
                import time

                if 'diamond_cached_df' not in st.session_state or time.time() - st.session_state.get('diamond_cache_time', 0) > 900:
                    with st.spinner("Đang soi dòng tiền Kim cương..."):
                        diamond_data = fetch_vndiamond_db()
                        manual_data = fetch_manual_price_db()
                        
                        manual_dict = {}
                        if manual_data and len(manual_data) > 1:
                            for row in manual_data[1:]:
                                if len(row) >= 2:
                                    tk = str(row[0]).strip().upper()
                                    if tk:
                                        pr_str = str(row[1]).replace(',', '').replace('.', '').replace(' ', '').strip()
                                        try: manual_dict[tk] = float(pr_str)
                                        except: pass

                        if not diamond_data:
                            st.session_state.diamond_cached_df = pd.DataFrame()
                        else:
                            df_dm = pd.DataFrame(diamond_data)
                            unique_tickers = df_dm['Ticker'].dropna().astype(str).str.strip().unique().tolist()
                            yf_tickers = [t + ".VN" if not t.endswith(".VN") else t for t in unique_tickers if t]
                            
                            batch_prices = {}
                            if yf_tickers:
                                try:
                                    yf_data = yf.download(yf_tickers, period="1d", interval="1m", threads=False, progress=False, ignore_tz=True)
                                    if not yf_data.empty:
                                        for tkr in unique_tickers:
                                            yf_t = tkr + ".VN" if not tkr.endswith(".VN") else tkr
                                            cp = 0
                                            try:
                                                if len(yf_tickers) == 1: cp = yf_data['Close'].dropna().iloc[-1]
                                                elif 'Close' in yf_data.columns and yf_t in yf_data['Close'].columns:
                                                    cp = yf_data['Close'][yf_t].dropna().iloc[-1]
                                            except: pass
                                            if cp > 0:
                                                if cp < 1000: cp *= 1000
                                                batch_prices[tkr] = cp
                                except: pass

                            final_prices, cash_flows, clean_vols = [], [], []
                            for _, row in df_dm.iterrows():
                                tkr = str(row.get('Ticker', '')).strip().upper()
                                vol_val = row.get('Est_Volume', row.get('Est_Trade_Vol', row.get('Ước tính giao dịch', row.get('Volume', row.get('Khối lượng', 0)))))
                                try: est_trade = float(str(vol_val).replace(',', '').replace(' ', ''))
                                except: est_trade = 0
                                
                                cp = batch_prices.get(tkr, 0)
                                if (cp == 0 or pd.isna(cp)) and tkr in manual_dict:
                                    cp = manual_dict[tkr]
                                
                                final_prices.append(cp if cp > 0 else None)
                                clean_vols.append(est_trade) 
                                cash_flows.append(cp * est_trade if cp > 0 else 0)

                            df_dm['Current_Price'] = final_prices
                            df_dm['Clean_Volume'] = clean_vols 
                            df_dm['Est_Cash_Flow'] = cash_flows
                            st.session_state.diamond_cached_df = df_dm
                        st.session_state.diamond_cache_time = time.time()

                df_final = st.session_state.diamond_cached_df
                if df_final.empty:
                    st.info("Chưa có dữ liệu")
                else:
                    total_buy = df_final[df_final['Clean_Volume'] > 0]['Est_Cash_Flow'].sum()
                    total_sell = abs(df_final[df_final['Clean_Volume'] < 0]['Est_Cash_Flow'].sum())
                    net_flow = total_buy - total_sell

                    # TONE CAM - TRẮNG CHO WIDGET (HTML TÙY CHỈNH NÂNG CAO)
                    net_color = "#0ECB81" if net_flow >= 0 else "#F6465D"
                    net_sign = "+" if net_flow > 0 else ""
                    net_icon = "📈" if net_flow >= 0 else "📉"
                    
                    metrics_html = f"""
                    <div style="display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px; background: #FFFFFF; border: 1px solid #EAECEF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                            <div style="font-size: 12px; color: #707A8A; font-weight: 800; text-transform: uppercase; margin-bottom: 8px;">Lực Mua Dự Kiến</div>
                            <div style="font-size: 26px; font-weight: 900; color: #1E2329;">{total_buy/1e9:,.1f} <span style="font-size: 16px; color: #707A8A;">Tỷ ₫</span></div>
                        </div>
                        <div style="flex: 1; min-width: 200px; background: #FFFFFF; border: 1px solid #EAECEF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                            <div style="font-size: 12px; color: #707A8A; font-weight: 800; text-transform: uppercase; margin-bottom: 8px;">Lực Xả Dự Kiến</div>
                            <div style="font-size: 26px; font-weight: 900; color: #1E2329;">{total_sell/1e9:,.1f} <span style="font-size: 16px; color: #707A8A;">Tỷ ₫</span></div>
                        </div>
                        <div style="flex: 1; min-width: 200px; background: linear-gradient(180deg, #FFFFFF 0%, #FFF9F5 100%); border: 1px solid #FFE0B2; border-bottom: 4px solid #FF6B00; border-radius: 12px; padding: 20px; box-shadow: 0 4px 16px rgba(255,107,0,0.08);">
                            <div style="font-size: 12px; color: #FF6B00; font-weight: 900; text-transform: uppercase; margin-bottom: 8px;">{net_icon} Trạng Thái Ròng</div>
                            <div style="font-size: 26px; font-weight: 900; color: {net_color};">{net_sign}{net_flow/1e9:,.1f} <span style="font-size: 16px;">Tỷ ₫</span></div>
                        </div>
                    </div>
                    """
                    st.markdown(metrics_html, unsafe_allow_html=True)

                    # TONE CAM - TRẮNG CHO BẢNG DỮ LIỆU
                    st.markdown("<div style='background: linear-gradient(90deg, #FF6B00 0%, #FFA033 100%); color: white; padding: 12px 16px; border-radius: 8px 8px 0 0; font-weight: 800; font-size: 14px; letter-spacing: 1px;'>💎 BẢNG DÒNG TIỀN CHI TIẾT (ĐÃ CHUẨN HÓA VNĐ)</div>", unsafe_allow_html=True)

                    # Chuẩn hóa dữ liệu sang dạng chuỗi có dấu phẩy để UI hiển thị đẹp tuyệt đối
                    df_display = df_final.copy()
                    df_display['Khối Lượng'] = df_display['Clean_Volume'].apply(lambda x: f"{x:,.0f}")
                    df_display['Giá Hiện Tại'] = df_display['Current_Price'].apply(lambda x: f"{x:,.0f} ₫" if pd.notnull(x) else "N/A")
                    df_display['Thành Tiền (VNĐ)'] = df_display['Est_Cash_Flow'].apply(lambda x: f"{x:,.0f} ₫")
                    
                    st.dataframe(
                        df_display,
                        column_config={
                            "Ticker": st.column_config.TextColumn("MÃ CP", width="small"),
                            "Industry": st.column_config.TextColumn("NGÀNH", width="medium"),
                            "New_Weight": st.column_config.TextColumn("TỶ TRỌNG", width="small"),
                            "Khối Lượng": st.column_config.TextColumn("KHỐI LƯỢNG GD", width="medium"),
                            "Giá Hiện Tại": st.column_config.TextColumn("GIÁ HT", width="medium"),
                            "Thành Tiền (VNĐ)": st.column_config.TextColumn("GIÁ TRỊ DÒNG TIỀN", width="large"),
                            "Old_Weight": None, "Est_Volume": None, "Est_Trade_Vol": None, "Ước tính giao dịch": None, "Volume": None, "Khối lượng": None, "Clean_Volume": None, "Current_Price": None, "Est_Cash_Flow": None
                        },
                        hide_index=True, use_container_width=True, height=500
                    )
                    st.caption("Dữ liệu dòng tiền = Giá hiện tại x Khối lượng ước tính. Dấu âm (-) thể hiện áp lực bán ròng.")
# =========================================================
                    # BỘ NÃO PHÂN TÍCH VÀ TỔNG KẾT TỰ ĐỘNG (ĐÃ ÉP PHẲNG CHỐNG LỖI)
                    # =========================================================
                    try:
                        # Lọc Top 3 Hút tiền và Top 3 Xả hàng
                        top_buy_df = df_final[df_final['Clean_Volume'] > 0].sort_values(by='Clean_Volume', ascending=False).head(3)
                        top_sell_df = df_final[df_final['Clean_Volume'] < 0].sort_values(by='Clean_Volume', ascending=True).head(3)
                        
                        top_buy_html = "".join([f"<li style='margin-bottom: 4px;'><b>{row['Ticker']}</b>: Tăng mạnh <span style='color: #0ECB81; font-weight: 700;'>+{row['Clean_Volume']:,.0f}</span> cp</li>" for _, row in top_buy_df.iterrows()])
                        top_sell_html = "".join([f"<li style='margin-bottom: 4px;'><b>{row['Ticker']}</b>: Bán ra <span style='color: #F6465D; font-weight: 700;'>{row['Clean_Volume']:,.0f}</span> cp</li>" for _, row in top_sell_df.iterrows()])
                        
                        # Quét Radar đặc biệt cho các mã bị bán ròng mạnh nhất (Chờ loại)
                        warning_note = ""
                        if not top_sell_df.empty:
                            worst_ticker = top_sell_df.iloc[0]['Ticker']
                            warning_note = f"<div style='margin-top: 12px; padding-top: 10px; border-top: 1px dashed #FCA5A5; color: #DC2626; font-size: 12px; font-weight: 700;'>🚨 CẢNH BÁO: {worst_ticker} vào danh sách nguy cơ chờ loại khỏi rổ!</div>"

                        # Ép toàn bộ code HTML thành 1 dòng sát lề để Streamlit không nhận nhầm là Code Block
                        summary_html = f"<div style='background: #FFFFFF; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; margin-top: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);'><div style='font-size: 14px; font-weight: 800; color: #1E2329; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;'><span style='font-size: 18px;'>🤖</span> TỔNG KẾT & PHÂN TÍCH NHANH TỪ HỆ THỐNG</div><div style='display: flex; gap: 16px; flex-wrap: wrap;'><div style='flex: 1; min-width: 250px; background: #F0FDFA; border-left: 4px solid #0ECB81; padding: 12px 16px; border-radius: 4px;'><div style='font-size: 12px; font-weight: 900; color: #0ECB81; margin-bottom: 8px;'>🔥 TÂM ĐIỂM HÚT TIỀN (GIA TĂNG TỶ TRỌNG)</div><ul style='margin: 0; padding-left: 20px; font-size: 13px; color: #1E2329;'>{top_buy_html if top_buy_html else '<li>Chưa có dữ liệu mua</li>'}</ul></div><div style='flex: 1; min-width: 250px; background: #FEF2F2; border-left: 4px solid #F6465D; padding: 12px 16px; border-radius: 4px;'><div style='font-size: 12px; font-weight: 900; color: #F6465D; margin-bottom: 8px;'>⚠️ ÁP LỰC BÁN RÒNG (GIẢM TỶ TRỌNG)</div><ul style='margin: 0; padding-left: 20px; font-size: 13px; color: #1E2329;'>{top_sell_html if top_sell_html else '<li>Chưa có dữ liệu bán</li>'}</ul>{warning_note}</div></div><div style='margin-top: 16px; padding-top: 12px; border-top: 1px solid #EAECEF; font-size: 11px; color: #848E9C; font-style: italic; text-align: right;'>📚 Nguồn tham khảo: <b>THAY ĐỔI THÀNH PHẦN CHỈ SỐ Q2/2026 - Dữ liệu chốt ngày 31/03/2026</b></div></div>"
                        
                        st.markdown(summary_html, unsafe_allow_html=True)
                    except Exception as e: pass
                    # =========================================================
            render_vndiamond_flow()
        # ---------------------------------------------------------
      # ---------------------------------------------------------
        # THẾ GIỚI 2: DÒNG THỜI GIAN KHUYẾN NGHỊ (BẢN FULL HOÀN CHỈNH TỐI THƯỢNG)
        # ---------------------------------------------------------
        with sub_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            
            if 'report_page' not in st.session_state: st.session_state.report_page = 1

            @st.fragment
            def render_short_term_timeline():
                import pandas as pd
                import math
                import yfinance as yf
                import time
                from datetime import datetime

                # ==========================================
                # ==========================================
                # 1. KÉT SẮT & ĐỘNG CƠ LẤY SỈ (BẢN GỐC CHỈ DÙNG .VN)
                # ==========================================
                if 'rep_cached_df' not in st.session_state or time.time() - st.session_state.get('rep_cache_time', 0) > 900:
                    with st.spinner("Đang tải báo cáo và đồng bộ giá (Bản gốc ổn định)..."):
                        reports_data = fetch_reports_db()
                        
                        # --- 1. KÉO DỮ LIỆU TỪ SHEET THỦ CÔNG (ĐỘNG CƠ CỤC SÚC BẤT TỬ) ---
                        manual_dict = {}
                        try:
                            manual_data = fetch_manual_price_db()
                            # Nếu cào được data và có nhiều hơn 1 dòng (dòng 1 là tiêu đề)
                            if manual_data and len(manual_data) > 1:
                                for row in manual_data[1:]: # Bỏ qua dòng Ticker, Price đầu tiên
                                    if len(row) >= 2:
                                        tk = str(row[0]).strip().upper()
                                        if tk:
                                            # San bằng mọi loại dấu phẩy, chấm, khoảng trắng
                                            pr_str = str(row[1]).replace(',', '').replace('.', '').replace(' ', '').strip()
                                            try:
                                                manual_dict[tk] = float(pr_str)
                                            except: pass
                        except Exception as e:
                            pass
                        # -------------------------------------------
                        
                        if not reports_data:
                            st.session_state.rep_cached_df = pd.DataFrame()
                        else:
                            df_temp = pd.DataFrame(reports_data)
                            df_temp['Parsed_Date'] = pd.to_datetime(df_temp['Date'], format="%d/%m/%Y", errors='coerce')
                            df_temp = df_temp.sort_values(by='Parsed_Date', ascending=False).reset_index(drop=True)
                            
                            unique_tickers = df_temp['Ticker'].dropna().astype(str).str.strip().unique().tolist()
                            # TRỞ VỀ CÁCH CŨ: CHỈ DÙNG ĐUÔI .VN ĐỂ KHÔNG BỊ LỖI
                            yf_tickers = [t + ".VN" if not t.endswith(".VN") else t for t in unique_tickers if t]
                            
                            batch_data = pd.DataFrame()
                            if yf_tickers:
                                try:
                                    batch_data = yf.download(yf_tickers, period="6mo", group_by='ticker', threads=False, progress=False, ignore_tz=True)
                                except Exception as e: pass
                            
                            current_prices, auto_statuses = [], []
                            
                            for _, r in df_temp.iterrows():
                                tkr = str(r.get('Ticker', '')).strip()
                                rec_p = float(r.get('Current_Price_At_Date', 0)) if str(r.get('Current_Price_At_Date', 0)).replace('.','',1).isdigit() else 0
                                tgt_p = float(r.get('Target_Price', 0)) if str(r.get('Target_Price', 0)).replace('.','',1).isdigit() else 0
                                rec_date_str, manual_status = str(r.get('Date', '')), str(r.get('Status', '')).strip().upper() 
                                
                                cp, highest_price, lowest_price = 0, 0, 0
                                yf_t = tkr + ".VN" if not tkr.endswith(".VN") else tkr
                                
                                if not batch_data.empty and yf_tickers:
                                    try:
                                        if len(yf_tickers) == 1: ticker_df = batch_data 
                                        elif isinstance(batch_data.columns, pd.MultiIndex) and yf_t in batch_data.columns.levels[0]: ticker_df = batch_data[yf_t]
                                        else: ticker_df = pd.DataFrame()
                                        
                                        if not ticker_df.empty:
                                            sliced_df = ticker_df.copy()
                                            if sliced_df.index.tz is not None: sliced_df.index = sliced_df.index.tz_localize(None)
                                            try:
                                                start_ts = pd.to_datetime(rec_date_str, format="%d/%m/%Y")
                                                sliced_df = sliced_df[sliced_df.index >= start_ts]
                                            except: pass 
                                                
                                            if not sliced_df.empty:
                                                valid_closes = sliced_df['Close'].dropna()
                                                if not valid_closes.empty:
                                                    cp = valid_closes.iloc[-1]
                                                    highest_price = sliced_df['High'].dropna().max()
                                                    lowest_price = sliced_df['Low'].dropna().min()
                                                    if cp < 1000 and cp > 0: cp *= 1000; highest_price *= 1000; lowest_price *= 1000
                                    except: pass
                                
                                # ==========================================
                                # KÍCH HOẠT PHAO CỨU SINH HYBRID NẾU YAHOO LỖI
                                # ==========================================
                                if cp == 0 or pd.isna(cp):
                                    if tkr in manual_dict:
                                        cp = float(manual_dict[tkr])
                                        if highest_price == 0: highest_price = cp
                                        if lowest_price == 0: lowest_price = cp
                                # ==========================================
                                        
                                current_prices.append(cp)
                                
                                # CƠ CHẾ ĐÁNH GIÁ (NỚI 12% + LUẬT ÂN XÁ PHỤC HỒI 98%)
                                if 'ĐẠT' in manual_status or 'TARGET' in manual_status: auto_statuses.append("✔️ ĐẠT TARGET")
                                elif 'CẮT' in manual_status or 'LỖ' in manual_status: auto_statuses.append("❌ CẮT LỖ")      
                                else:
                                    if cp == 0 or lowest_price == 0: 
                                        auto_statuses.append("⏳ ĐANG THEO DÕI")
                                    elif highest_price >= tgt_p and tgt_p > 0: 
                                        auto_statuses.append("✔️ ĐẠT TARGET")
                                    elif rec_p > 0 and lowest_price <= rec_p * 0.88:
                                        if cp >= rec_p * 0.98: 
                                            auto_statuses.append("⏳ ĐANG THEO DÕI") 
                                        else:
                                            auto_statuses.append("❌ CẮT LỖ")
                                    else: 
                                        auto_statuses.append("⏳ ĐANG THEO DÕI")
                                    
                            df_temp['Realtime_Price'] = current_prices
                            df_temp['Auto_Status'] = auto_statuses
                            st.session_state.rep_cached_df = df_temp
                        st.session_state.rep_cache_time = time.time()

                # ==========================================
                # 2. VẼ GIAO DIỆN
                # ==========================================
                cached_df = st.session_state.rep_cached_df
                if cached_df.empty:
                    st.info("Chưa có dữ liệu báo cáo LINANCE_DB")
                    return
                
                df_rep = cached_df.copy()
                col_list, col_leaderboard = st.columns([1.7, 1])
                
                with col_list:
                    st.markdown("<div style='background-color: #FAFAFA; padding: 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #EAECEF;'>", unsafe_allow_html=True)
                    f_col1, f_col2 = st.columns(2)
                    all_rep_brokers = ["Tất cả"] + df_rep['Broker'].dropna().unique().tolist()
                    with f_col1: rep_broker_filter = st.selectbox("Lọc theo Công ty:", all_rep_brokers, key="rep_brk_flt")
                    with f_col2: rep_time_filter = st.selectbox("Thời gian:", ["Tất cả", "Tháng này", "Hôm nay"], key="rep_time_flt")
                    st.markdown("</div>", unsafe_allow_html=True)

                    filtered_rep = df_rep.copy()
                    if rep_broker_filter != "Tất cả": filtered_rep = filtered_rep[filtered_rep['Broker'] == rep_broker_filter]
                    if rep_time_filter == "Hôm nay":
                        today_str = datetime.now().strftime("%d/%m/%Y")
                        filtered_rep = filtered_rep[filtered_rep['Date'].astype(str).str.contains(today_str)]
                    elif rep_time_filter == "Tháng này":
                        month_str = datetime.now().strftime("/%m/%Y")
                        filtered_rep = filtered_rep[filtered_rep['Date'].astype(str).str.contains(month_str)]

                    ITEMS_PER_PAGE = 5
                    total_items = len(filtered_rep)
                    total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
                    
                    if st.session_state.report_page > total_pages: st.session_state.report_page = total_pages
                    if st.session_state.report_page < 1: st.session_state.report_page = 1
                        
                    start_idx = (st.session_state.report_page - 1) * ITEMS_PER_PAGE
                    end_idx = start_idx + ITEMS_PER_PAGE
                    paged_rep = filtered_rep.iloc[start_idx:end_idx]

                    st.markdown("<div style='font-weight: 700; font-size: 16px; margin-bottom: 16px; color: #1E2329;'>Dòng thời gian Khuyến nghị</div>", unsafe_allow_html=True)
                    
                    if paged_rep.empty: st.warning("Không tìm thấy báo cáo nào khớp với bộ lọc!")
                    else:
                        css_rep = "<style>.rep-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; margin-bottom: 16px; transition: all 0.2s ease; border-left: 4px solid #1E2329; } .rep-card:hover { border-color: #FF6B00; border-left: 4px solid #FF6B00; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); transform: translateX(4px); } .rep-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; } .rep-tkr { font-size: 20px; font-weight: 800; color: #1E2329; font-family: 'SF Mono', Consolas, monospace;} .rep-brk { font-size: 12px; color: #707A8A; font-weight: 700; background: #F8FAFC; padding: 4px 8px; border-radius: 4px; border: 1px solid #EAECEF;} .rep-mid { display: flex; gap: 24px; margin-bottom: 12px; flex-wrap: wrap;} .rep-lbl { font-size: 11px; color: #848E9C; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; } .rep-val { font-size: 15px; font-weight: 700; color: #1E2329; } .act-badge { background: #F0F2F5; color: #474D57; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 800;} .act-mua { color: #0ECB81; background: #E6FFF3; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 800;} .act-ban { color: #F6465D; background: #FFF1F0; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 800;} .act-giu { color: #F39C12; background: #FEF5E7; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 800;} .sts-dat { color: #0ECB81; border: 1px solid #0ECB81; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; } .sts-cat { color: #F6465D; border: 1px solid #F6465D; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; } .sts-cho { color: #848E9C; border: 1px solid #848E9C; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; }</style>"
                        reports_html = ""
                        for _, r in paged_rep.iterrows():
                            action = str(r.get('Action', '')).upper()
                            if 'MUA' in action or 'TĂNG' in action or 'KHẢ QUAN' in action: act_class = 'act-mua'
                            elif 'BÁN' in action or 'GIẢM' in action or 'KÉM' in action: act_class = 'act-ban'
                            elif 'GIỮ' in action or 'TRUNG LẬP' in action: act_class = 'act-giu'
                            else: act_class = 'act-badge'
                            
                            auto_sts = r['Auto_Status']
                            if 'ĐẠT' in auto_sts: sts_class = 'sts-dat'
                            elif 'CẮT' in auto_sts: sts_class = 'sts-cat'
                            else: sts_class = 'sts-cho'

                            try:
                                target_price = f"{float(r.get('Target_Price', 0)):,.0f}"
                                rec_price = f"{float(r.get('Current_Price_At_Date', 0)):,.0f}"
                                realtime_price = f"{float(r.get('Realtime_Price', 0)):,.0f}" if r.get('Realtime_Price', 0) > 0 else "N/A"
                            except: target_price, rec_price, realtime_price = 'N/A', 'N/A', 'N/A'

                            reports_html += f"""<div class="rep-card"><div class="rep-top"><div style="display: flex; align-items: center; gap: 12px;"><span class="rep-tkr">{r.get('Ticker', 'N/A')}</span><span class="{act_class}">{action}</span><span class="{sts_class}">{auto_sts}</span></div><span class="rep-brk">🏢 {r.get('Broker', 'N/A')}</span></div><div class="rep-mid"><div><div class="rep-lbl">Giá Khuyến Nghị</div><div class="rep-val">{rec_price}</div></div><div><div class="rep-lbl">Giá Hiện Tại</div><div class="rep-val" style="color: #0052FF;">{realtime_price}</div></div><div><div class="rep-lbl">Giá Mục Tiêu</div><div class="rep-val" style="color: #FF6B00;">{target_price}</div></div><div><div class="rep-lbl">Ngày Phát Hành</div><div class="rep-val" style="color: #707A8A; font-weight: 600;">{r.get('Date', 'N/A')}</div></div></div><div style="font-size: 12px; text-align: right;"><a href="{r.get('Link', '#')}" target="_blank" style="color: #0052FF; font-weight: 600; text-decoration: none;">Xem chi tiết báo cáo ↗</a></div></div>"""
                        st.markdown(f"{css_rep}<div>{reports_html}</div>", unsafe_allow_html=True)

                    if total_pages > 1:
                        st.markdown("<br>", unsafe_allow_html=True)
                        pag_cols = st.columns([2, 1, 2, 1, 2]) 
                        with pag_cols[1]:
                            if st.button("◀ Trước", disabled=(st.session_state.report_page <= 1), use_container_width=True, key="rep_prev"):
                                st.session_state.report_page -= 1
                        with pag_cols[2]: 
                            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57;'>Trang {st.session_state.report_page} / {total_pages}</div>", unsafe_allow_html=True)
                        with pag_cols[3]:
                            if st.button("Sau ▶", disabled=(st.session_state.report_page >= total_pages), use_container_width=True, key="rep_next"):
                                st.session_state.report_page += 1

                with col_leaderboard:
                    st.markdown("<div style='font-weight: 700; font-size: 16px; margin-bottom: 16px; color: #1E2329;'>BẢNG XẾP HẠNG</div>", unsafe_allow_html=True)
                    
                    def get_win_loss_auto(status):
                        s = str(status).strip().lower()
                        if 'đạt target' in s: return 'Win'
                        if 'cắt lỗ' in s: return 'Loss'
                        return 'Pending'
                    filtered_rep['Result'] = filtered_rep['Auto_Status'].apply(get_win_loss_auto)
                    closed_df = filtered_rep[filtered_rep['Result'].isin(['Win', 'Loss'])]
                    
                    leaderboard_html = ""
                    if closed_df.empty: leaderboard_html = "<div style='font-size: 13px; color: #707A8A; text-align: center; padding: 20px; border-bottom: 1px dashed #EAECEF; margin-bottom: 12px;'>Chưa có mã chạm Target hoặc Cắt lỗ.</div>"
                    else:
                        win_stats = closed_df.groupby('Broker')['Result'].apply(lambda x: (x == 'Win').sum() / len(x) * 100).reset_index(name='Win_Rate')
                        win_stats['Total'] = closed_df.groupby('Broker')['Result'].count().values
                        win_stats = win_stats.sort_values(by=['Win_Rate', 'Total'], ascending=[False, False]).reset_index(drop=True)
                        medals = ["🥇", "🥈", "🥉"]
                        for idx, row in win_stats.iterrows():
                            rank_icon = f"<span style='font-size: 20px;'>{medals[idx]}</span>" if idx < 3 else f"<span style='font-size: 16px; width: 20px; text-align: center; color: #848E9C; font-weight: 700;'>{idx+1}</span>"
                            rate_color = "#0ECB81" if row['Win_Rate'] >= 60 else "#F39C12" if row['Win_Rate'] >= 40 else "#F6465D"
                            leaderboard_html += f"<div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #EAECEF; padding-bottom: 12px; margin-bottom: 12px;'><div style='display: flex; align-items: center; gap: 10px;'>{rank_icon}<span style='font-weight: 700; color: #1E2329; font-size: 14px;'>{row['Broker']}</span></div><span style='font-weight: 800; color: {rate_color}; font-size: 16px;'>{row['Win_Rate']:.1f}%</span></div>"
                            
                    buy_mask = filtered_rep['Action'].fillna('').astype(str).str.upper().str.contains('MUA|TĂNG|KHẢ QUAN')
                    buy_df = filtered_rep[buy_mask]
                    consensus_html = "Hệ thống đang thu thập thêm dữ liệu để đánh giá."
                    if not buy_df.empty:
                        top_tickers_str = ", ".join(buy_df['Ticker'].value_counts().head(3).index.tolist())
                        consensus_html = f"Phần lớn Tổ chức đang đồng thuận <b style='color: #0ECB81;'>MUA</b> ở các mã: <b style='color: #FF6B00;'>{top_tickers_str}</b>"

                    radar_html = ""
                    if not filtered_rep.empty:
                        total_recs = len(filtered_rep)
                        sell_mask = filtered_rep['Action'].fillna('').astype(str).str.upper().str.contains('BÁN|GIẢM|KÉM')
                        buy_count = buy_mask.sum()
                        sell_count = sell_mask.sum()
                        hold_count = total_recs - buy_count - sell_count
                        
                        buy_pct = (buy_count / total_recs) * 100 if total_recs > 0 else 0
                        sell_pct = (sell_count / total_recs) * 100 if total_recs > 0 else 0
                        hold_pct = (hold_count / total_recs) * 100 if total_recs > 0 else 0

                        upside_df = filtered_rep[(filtered_rep['Auto_Status'].astype(str).str.contains('ĐANG THEO DÕI')) & buy_mask].copy()
                        upside_df['Realtime_Price'] = pd.to_numeric(upside_df['Realtime_Price'], errors='coerce')
                        upside_df['Target_Price'] = pd.to_numeric(upside_df['Target_Price'], errors='coerce')
                        
                        valid_upside = upside_df[(upside_df['Realtime_Price'] > 0) & (upside_df['Target_Price'] > upside_df['Realtime_Price'])].copy()
                        
                        top_upside_html = "<div style='font-size: 12px; color: #848E9C; font-style: italic;'>Hiện chưa có mã nào thỏa mãn tiêu chí bứt phá.</div>"
                        if not valid_upside.empty:
                            valid_upside['Upside_Pct'] = ((valid_upside['Target_Price'] - valid_upside['Realtime_Price']) / valid_upside['Realtime_Price']) * 100
                            top_stock = valid_upside.sort_values(by='Upside_Pct', ascending=False).iloc[0]
                            
                            t_tkr = top_stock.get('Ticker', 'N/A')
                            t_brk = top_stock.get('Broker', 'N/A')
                            t_up = top_stock.get('Upside_Pct', 0)
                            t_cp = f"{top_stock.get('Realtime_Price', 0):,.0f}"
                            t_tp = f"{top_stock.get('Target_Price', 0):,.0f}"
                            
                            top_upside_html = f"<div style='background: #FFFFFF; border-radius: 8px; padding: 12px; border: 1px solid #EAECEF; border-left: 4px solid #0ECB81; box-shadow: 0 2px 8px rgba(0,0,0,0.04);'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'><span style='font-size: 18px; font-weight: 900; color: #1E2329; font-family: \"SF Mono\", Consolas, monospace;'>{t_tkr}</span><span style='background: #E6FFF3; color: #0ECB81; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 800;'>+{t_up:.1f}% Upside</span></div><div style='display: flex; justify-content: space-between; font-size: 12px; color: #707A8A; margin-bottom: 4px;'><span>Giá HT: <b style='color: #1E2329;'>{t_cp}</b></span><span>Target: <b style='color: #FF6B00;'>{t_tp}</b></span></div><div style='font-size: 10px; color: #848E9C; text-align: right; font-weight: 600;'>Đề xuất bởi: {t_brk}</div></div>"

                        radar_html = f"<div style='margin-top: 16px; padding: 16px; background: linear-gradient(180deg, #FFFFFF 0%, #FFF9F5 100%); border-radius: 12px; border: 1px solid #FFE0B2; border-bottom: 4px solid #FF6B00; color: #1E2329; box-shadow: 0 4px 12px rgba(255,107,0,0.08);'><div style='font-size: 14px; font-weight: 900; color: #FF6B00; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;'><span style='font-size: 18px;'>🔥</span> RADAR CƠ HỘI (AI SCAN)</div><div style='margin-bottom: 20px;'><div style='font-size: 11px; color: #FF6B00; text-transform: uppercase; font-weight: 800; margin-bottom: 8px;'>🚀 Cổ phiếu có dư địa tăng cao nhất</div>{top_upside_html}</div><div><div style='font-size: 11px; color: #FF6B00; text-transform: uppercase; font-weight: 800; margin-bottom: 8px;'>🌡️ Nhiệt kế Khuyến nghị</div><div style='display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 6px; background: #EAECEF;'><div style='width: {buy_pct}%; background: #0ECB81;'></div><div style='width: {hold_pct}%; background: #F39C12;'></div><div style='width: {sell_pct}%; background: #F6465D;'></div></div><div style='display: flex; justify-content: space-between; font-size: 10px; color: #474D57; font-weight: 800;'><span style='color: #0ECB81;'>MUA {buy_pct:.0f}%</span><span style='color: #F39C12;'>GIỮ {hold_pct:.0f}%</span><span style='color: #F6465D;'>BÁN {sell_pct:.0f}%</span></div></div></div>"

                    final_html = f"<div style='background: #FAFAFA; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; position: relative; margin-top: 10px;'><div style='font-size: 12px; color: #707A8A; margin-bottom: 20px; line-height: 1.5;'>Tỷ lệ Win Rate được AI tự động tính toán.</div>{leaderboard_html}<div style='margin-top: 24px; padding: 12px; background: #E6FFF3; border-radius: 6px; border: 1px dashed #0ECB81;'><div style='font-size: 11px; color: #0ECB81; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;'>🤖 AI Consensus</div><div style='font-size: 13px; color: #1E2329; font-weight: 600;'>{consensus_html}</div></div></div>{radar_html}"
                    st.markdown(final_html, unsafe_allow_html=True)

            render_short_term_timeline()
# --- TAB 5: SO SÁNH DỊCH VỤ VÀ GÓI ƯU ĐÃI ---
    with tab5:
        st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>TÌM KIẾM GÓI MARGIN & PHÍ TỐI ƯU</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #474D57; font-size: 14px; margin-bottom: 24px;'>Hệ thống tự động phân tích và xếp hạng các chương trình ưu đãi từ các CTCK.</div>", unsafe_allow_html=True)

        # BÙA CHÚ BỌC GIAO DIỆN LẠI THÀNH TIỂU VŨ TRỤ CHỐNG LAG
        @st.fragment
        def render_broker_comparison():
            import pandas as pd
            import time
            
            # ==========================================
            # 1. KÉT SẮT RAM: CHỈ TẢI DATA TỪ SHEETS 1 LẦN DUY NHẤT
            # ==========================================
            if 'svc_cached_df' not in st.session_state or time.time() - st.session_state.get('svc_cache_time', 0) > 900:
                with st.spinner("Đang trích xuất và phân tích các gói dịch vụ..."):
                    broker_data = fetch_broker_services()
                    if not broker_data:
                        st.session_state.svc_cached_df = pd.DataFrame()
                    else:
                        st.session_state.svc_cached_df = pd.DataFrame(broker_data)
                    st.session_state.svc_cache_time = time.time()

            df = st.session_state.svc_cached_df.copy()
            
            if df.empty:
                st.info("💡 Chưa có dữ liệu gói dịch vụ. Vui lòng kiểm tra lại hệ thống LINANCE_DB.")
                return

            # ==========================================
            # 2. XỬ LÝ SỐ LIỆU TỪ RAM SIÊU TỐC
            # ==========================================
            # BÓC TÁCH SỐ LIỆU ĐỂ AI TÍNH TOÁN (Xóa dấu %, biến thành số thực)
            df['Margin_Num'] = pd.to_numeric(df['Margin_Rate'].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(999)
            df['Fee_Num'] = pd.to_numeric(df['Trading_Fee'].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(999)
            
            # TÌM RA "QUÁN QUÂN" CỦA THÁNG (Margin thấp nhất, nếu bằng nhau thì xét Phí thấp nhất)
            best_pkg = df.sort_values(by=['Margin_Num', 'Fee_Num']).iloc[0]
            
            # --- VẼ BẢNG VINH DANH QUÁN QUÂN ---
            st.markdown(f"""<div style="background: linear-gradient(135deg, #FFF4ECE6, #FFE0B280); border: 2px solid #FF6B00; border-radius: 12px; padding: 24px; margin-bottom: 32px; box-shadow: 0 8px 24px rgba(230, 81, 0, 0.15); position: relative; overflow: hidden;"><div style="position: absolute; top: -10px; right: -10px; font-size: 80px; opacity: 0.1;">🏆</div><div style="color: #FF6B00; font-weight: 800; font-size: 14px; letter-spacing: 1px; margin-bottom: 8px;">🔥 LỰA CHỌN TỐI ƯU NHẤT THỜI ĐIỂM HIỆN TẠI</div><div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px;"><span style="font-size: 28px; font-weight: 800; color: #1E2329;">{best_pkg.get('Broker_Name', 'N/A')}</span><span style="background: #FF6B00; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">{best_pkg.get('Package_Name', 'Gói Ưu Đãi')}</span></div><div style="display: flex; gap: 40px;"><div><div style="font-size: 12px; color: #707A8A; font-weight: 600;">LÃI SUẤT MARGIN</div><div style="font-size: 20px; font-weight: 800; color: #0ECB81;">{best_pkg.get('Margin_Rate', 'N/A')}</div></div><div><div style="font-size: 12px; color: #707A8A; font-weight: 600;">PHÍ GIAO DỊCH</div><div style="font-size: 20px; font-weight: 800; color: #1E2329;">{best_pkg.get('Trading_Fee', 'N/A')}</div></div><div><div style="font-size: 12px; color: #707A8A; font-weight: 600;">NGUỒN MARGIN</div><div style="font-size: 16px; font-weight: 700; color: #1E2329; margin-top: 4px;">{best_pkg.get('Margin_Pool', 'N/A')}</div></div></div><div style="margin-top: 16px; font-size: 14px; color: #474D57; font-style: italic;">🎯 Điểm nhấn: {best_pkg.get('Pros', '')}</div></div>""", unsafe_allow_html=True)

            # --- BỘ LỌC TÌM KIẾM (FILTERS) ---
            st.markdown("<div style='font-size: 16px; font-weight: 700; color: #1E2329; margin-bottom: 12px;'>🔍 Lọc & Tìm kiếm</div>", unsafe_allow_html=True)
            col_filter1, col_filter2, col_filter3 = st.columns([2, 1.5, 1.5])
            
            all_brokers = df['Broker_Name'].dropna().unique().tolist()
            
            with col_filter1:
                selected_brokers = st.multiselect("Chọn Công ty Chứng khoán:", options=all_brokers, default=all_brokers, key="tab5_brokers")
            with col_filter2:
                sort_option = st.selectbox("Sắp xếp theo:", ["Margin thấp đến cao", "Phí thấp đến cao"], key="tab5_sort")
            with col_filter3:
                margin_pool = st.selectbox("Tình trạng Margin:", ["Tất cả", "Dồi dào", "Căng"], key="tab5_pool")

            # --- ÁP DỤNG BỘ LỌC VÀO DATA ---
            filtered_df = df[df['Broker_Name'].isin(selected_brokers)]
            if margin_pool != "Tất cả":
                filtered_df = filtered_df[filtered_df['Margin_Pool'].astype(str).str.contains(margin_pool, case=False, na=False)]
            
            if sort_option == "Margin thấp đến cao":
                filtered_df = filtered_df.sort_values(by=['Margin_Num', 'Fee_Num'])
            else:
                filtered_df = filtered_df.sort_values(by=['Fee_Num', 'Margin_Num'])

            # --- VẼ LƯỚI CARD KẾT QUẢ ---
            st.markdown("<hr style='border-color: #EAECEF; margin: 24px 0;'>", unsafe_allow_html=True)
            
            if filtered_df.empty:
                st.warning("Không tìm thấy gói dịch vụ nào khớp với bộ lọc của bạn!")
            else:
                css_broker = "<style>.b-container { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 10px; } .b-card { background: #fff; border: 1px solid #EAECEF; border-radius: 12px; padding: 20px; width: 320px; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; } .b-card:hover { border-color: #FF6B00; box-shadow: 0 8px 24px rgba(230, 81, 0, 0.1); transform: translateY(-4px); } .b-name { font-size: 18px; font-weight: 800; color: #1E2329; margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between; } .b-pkg { font-size: 12px; font-weight: 600; color: #FF6B00; margin-bottom: 16px; background: #FFF2E5; padding: 4px 8px; border-radius: 4px; display: inline-block;} .b-stat { display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px dashed #F0F2F5; padding-bottom: 8px; font-size: 13px; } .b-lbl { color: #707A8A; font-weight: 600; } .b-val { color: #1E2329; font-weight: 700; } .b-pros { background: #F8FAFC; border-radius: 6px; padding: 12px; margin-top: auto; font-size: 12px; color: #474D57; font-style: italic; border-left: 3px solid #FF6B00; } .b-upd { font-size: 10px; color: #848E9C; margin-top: 12px; text-align: right; }</style>"
                cards_html = ""
                for _, b in filtered_df.iterrows():
                    pool_color = "#0ECB81" if "Dồi dào" in str(b.get('Margin_Pool', '')) else "#F6465D" if "Căng" in str(b.get('Margin_Pool', '')) else "#F39C12"
                    cards_html += f"""<div class="b-card"><div class="b-name"><span>{b.get('Broker_Name', 'N/A')}</span></div><div class="b-pkg">{b.get('Package_Name', 'Gói Tiêu Chuẩn')}</div><div class="b-stat"><span class="b-lbl">Phí giao dịch</span><span class="b-val" style="color: #FF6B00;">{b.get('Trading_Fee', 'N/A')}</span></div><div class="b-stat"><span class="b-lbl">Lãi suất Margin</span><span class="b-val">{b.get('Margin_Rate', 'N/A')}</span></div><div class="b-stat"><span class="b-lbl">Nguồn Margin</span><span class="b-val" style="color: {pool_color};">{b.get('Margin_Pool', 'N/A')}</span></div><div class="b-pros">🎯 {b.get('Pros', 'Liên hệ chi tiết')}</div><div class="b-upd">Cập nhật: {b.get('Last_Updated', 'N/A')}</div></div>"""
                
                st.markdown(f"{css_broker}<div class='b-container'>{cards_html}</div>", unsafe_allow_html=True)

        # ==========================================
        # 3. KÍCH HOẠT VŨ TRỤ CHỐNG LAG LÊN MÀN HÌNH
        # ==========================================
        render_broker_comparison()
# =========================================================
    # =========================================================
    # TAB 6: TRUNG TÂM PHÂN TÍCH & ĐỊNH GIÁ CỔ PHIẾU
    # =========================================================
    with tab6:
        st.markdown("<br><div style='font-weight: 900; font-size: 20px; margin-bottom: 24px; color: #FF6B00; text-transform: uppercase; border-left: 5px solid #FF6B00; padding-left: 12px;'>Trung Tâm Phân Tích & Định Giá Chuyên Sâu</div>", unsafe_allow_html=True)
        
        # --- 1. LÁ CHẮN BỘ NHỚ ĐỆM (CACHE 1 TIẾNG CHỐNG SPAM YAHOO) ---
        @st.cache_data(ttl=3600, show_spinner=False)
        def fetch_stock_data_pro(ticker):
            import yfinance as yf
            import pandas as pd
            try:
                stock = yf.Ticker(ticker + ".VN")
                hist = stock.history(period="1y")
                if hist.empty: return None, None
                
                # Hàm .info của Yahoo là chúa hay báo lỗi 429, phải bọc Try/Except riêng
                info_data = {}
                try: info_data = stock.info
                except: pass
                
                return hist, info_data
            except Exception as e:
                return None, str(e)

        @st.fragment
        def render_stock_analysis_standalone():
            import plotly.graph_objects as go
            import pandas as pd
            
            # --- 2. ĐÓNG GÓI Ô TÌM KIẾM VÀO FORM (Bấm nút mới chạy) ---
            with st.form(key="search_stock_form"):
                col_search, col_btn, col_empty = st.columns([2, 1, 3])
                with col_search:
                    search_ticker = st.text_input("🔍 Nhập mã CP (VD: FPT, MBB):", value="FPT", max_chars=10, label_visibility="collapsed").upper().strip()
                with col_btn:
                    submit_search = st.form_submit_button("Phân Tích")

            if search_ticker:
                with st.spinner(f"Đang cào dữ liệu mật của {search_ticker}..."):
                    hist, info = fetch_stock_data_pro(search_ticker)
                    
                    if hist is None:
                        st.error(f"Đang lấy dữ liệu quay lại sau ít phút ")
                        return
                    
                    if not hist.empty:
                        if info is None: info = {}
                        # Bố cục 2 cột cho màn hình chính
                        col_left, col_right = st.columns([1, 2.5])
                        
                        with col_left:
                            # 1. KHỐI HIỂN THỊ GIÁ REAL-TIME
                            current_price = info.get('currentPrice', hist['Close'].iloc[-1])
                            prev_close = info.get('previousClose', hist['Close'].iloc[-2])
                            change = current_price - prev_close
                            change_pct = (change / prev_close) * 100 if prev_close else 0
                            
                            color = "#0ECB81" if change >= 0 else "#F6465D"
                            sign = "+" if change >= 0 else ""
                            
                            st.markdown(f"""
                            <div style='background: #FFFFFF; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); margin-bottom: 24px;'>
                                <h2 style='margin:0; color:#1E2329; font-size: 38px; font-weight: 900;'>{search_ticker}</h2>
                                <div style='color: #848E9C; font-size: 13px; margin-bottom: 12px; text-transform: uppercase;'>{info.get('industry', 'Bảng điện tử HOSE/HNX')}</div>
                                <h1 style='margin:0; color:{color}; font-size: 34px;'>{current_price:,.0f} ₫</h1>
                                <div style='color:{color}; font-size: 15px; font-weight: 800;'>{sign}{change:,.0f} ({sign}{change_pct:.2f}%)</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 2. BẢNG CHỈ SỐ TÀI CHÍNH
                            st.markdown("<div style='font-weight: 800; font-size: 16px; margin-bottom: 12px; color: #1E2329;'>Chỉ số tài chính</div>", unsafe_allow_html=True)
                            
                            metrics = {
                                "Vốn hóa": f"{info.get('marketCap', 0)/1e9:,.0f} Tỷ" if info.get('marketCap') else "N/A",
                                "Khối lượng TB": f"{info.get('averageVolume', 0):,.0f}" if info.get('averageVolume') else "N/A",
                                "EPS (TTM)": f"{info.get('trailingEps', 0):,.0f} ₫" if info.get('trailingEps') else "N/A",
                                "P/E": f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A",
                                "P/B": f"{info.get('priceToBook', 0):.2f}" if info.get('priceToBook') else "N/A",
                                "Beta": f"{info.get('beta', 0):.2f}" if info.get('beta') else "N/A"
                            }
                            
                            for k, v in metrics.items():
                                st.markdown(f"<div style='display: flex; justify-content: space-between; border-bottom: 1px dashed #EAECEF; padding: 10px 0; font-size: 14px;'><span style='color:#707A8A;'>{k}</span><span style='font-weight:800; color:#1E2329;'>{v}</span></div>", unsafe_allow_html=True)

                        with col_right:
                            # 3. BIỂU ĐỒ NẾN KỸ THUẬT
                            st.markdown("<div style='font-weight: 800; font-size: 16px; margin-bottom: 12px; color: #1E2329;'>Phân tích Kỹ thuật (1 Năm)</div>", unsafe_allow_html=True)
                            fig_tech = go.Figure(data=[go.Candlestick(
                                x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                                increasing_line_color='#0ECB81', decreasing_line_color='#F6465D'
                            )])
                            fig_tech.update_layout(
                                margin=dict(l=0, r=0, t=10, b=0), height=350,
                                xaxis_rangeslider_visible=False, 
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                yaxis=dict(gridcolor='#F0F0F0', fixedrange=False), # Mở khóa trục Y
                                xaxis=dict(fixedrange=False), # Mở khóa trục X
                                dragmode='pan' # Chuyển chuột sang chế độ Bàn tay để kéo thả
                            )
                            
                            # CẤY CẤU HÌNH VÀO CHART: Cho phép cuộn chuột để Zoom In/Out
                            tech_config = {
                                'scrollZoom': True, 
                                'displayModeBar': True, # Hiện thanh công cụ góc trên bên phải
                                'displaylogo': False
                            }
                            st.plotly_chart(fig_tech, use_container_width=True, config=tech_config)

                            # 4. BIỂU ĐỒ ĐỊNH GIÁ P/E
                            st.markdown("<div style='font-weight: 800; font-size: 16px; margin-top: 24px; margin-bottom: 12px; color: #1E2329;'>Định giá cổ phiếu theo P/E</div>", unsafe_allow_html=True)
                            eps = info.get('trailingEps', 0)
                            if eps and eps > 0:
                                hist['PE_History'] = hist['Close'] / eps
                                mean_pe = hist['PE_History'].mean()

                                fig_pe = go.Figure()
                                fig_pe.add_trace(go.Scatter(
                                    x=hist.index, y=hist['PE_History'], mode='lines', name='Mức P/E',
                                    line=dict(color='#FF6B00', width=2), fill='tozeroy', fillcolor='rgba(255, 107, 0, 0.1)'
                                ))
                                fig_pe.add_trace(go.Scatter(
                                    x=hist.index, y=[mean_pe]*len(hist), mode='lines', name='P/E Trung bình',
                                    line=dict(color='#848E9C', width=1.5, dash='dash')
                                ))
                                fig_pe.update_layout(
                                    margin=dict(l=0, r=0, t=10, b=0), height=300,
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                    yaxis=dict(gridcolor='#F0F0F0', fixedrange=False),
                                    xaxis=dict(fixedrange=False),
                                    dragmode='pan',
                                    showlegend=False
                                )
                                pe_config = {'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False}
                                st.plotly_chart(fig_pe, use_container_width=True, config=pe_config)
                            else:
                                st.info("💡 Không đủ dữ liệu Lợi nhuận (EPS) để vẽ biểu đồ định giá P/E.")

        # Chạy hàm
        render_stock_analysis_standalone()    
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
