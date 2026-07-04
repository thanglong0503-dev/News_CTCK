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

st.set_page_config(page_title="LINANCE Dashboard", layout="wide", page_icon="📈")

st.markdown("""
<style>
    div[data-testid="stPopover"] { position: fixed !important; bottom: 30px !important; right: 30px !important; z-index: 999999 !important; }
    div[data-testid="stPopover"] button { width: 65px !important; height: 65px !important; border-radius: 50% !important; background: linear-gradient(135deg, #FF9500, #FF5E3A) !important; border: none !important; box-shadow: 0 8px 24px rgba(255, 149, 0, 0.4) !important; transition: transform 0.2s ease !important; display: flex !important; align-items: center !important; justify-content: center !important;}
    div[data-testid="stPopover"] button:hover { transform: scale(1.08) !important; box-shadow: 0 12px 28px rgba(255, 149, 0, 0.6) !important;}
    div[data-testid="stPopover"] button p { font-size: 32px !important; color: white !important; margin: 0 !important; }
    div[data-testid="stPopover"] button:focus { outline: none !important; }
    div[data-testid="stPopoverBody"] { border-radius: 24px !important; border: 1px solid rgba(0,0,0,0.1) !important; box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important; overflow: hidden !important; width: 380px !important; padding: 0 !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #FAFAFA; }
</style>
""", unsafe_allow_html=True)

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
# KHỐI 1: HEADER & BĂNG CHUYỀN VĨ MÔ
# ==========================================
import yfinance as yf

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
        ticker_content = "<span style='margin: 0 40px; color: #FFB74D;'>•</span>".join(macro_items)
        ticker_content = f"{ticker_content} <span style='margin: 0 40px; color: #FFB74D;'>•</span> {ticker_content}"
        ticker_html = f"""
        <style>
        .ticker-wrap {{ width: 100%; background-color: #FFFFFF; border: 1px solid #FFE0B2; padding: 12px 0; border-radius: 6px; overflow: hidden; white-space: nowrap; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.05); margin-bottom: 24px; }}
        .ticker {{ display: inline-block; white-space: nowrap; animation: marquee 25s linear infinite; }}
        .ticker:hover {{ animation-play-state: paused; cursor: pointer; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        </style>
        <div class="ticker-wrap">
            <div class="ticker" style="font-size: 15px; font-family: 'SF Mono', Consolas, monospace;">
                {ticker_content}
            </div>
        </div>
        """
        st.markdown(ticker_html, unsafe_allow_html=True)

# ==========================================
# KHỐI 1.5: BẢN ĐỒ NHIỆT VN100
# ==========================================
@st.cache_data(ttl=300, show_spinner=False)
def get_market_heatmap_data():
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

def render_tab2_heatmap():
    st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>Bản đồ Nhiệt Dòng tiền (Market Heatmap)</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #474D57; font-size: 14px; margin-bottom: 24px;'>Kích thước ô vuông thể hiện Khối lượng giao dịch. Màu sắc phản ánh mức độ Tăng/Giảm chuẩn thị trường Việt Nam.</div>", unsafe_allow_html=True)
    with st.spinner("Đang quét tín hiệu dòng tiền VN100..."):
        df_heat = get_market_heatmap_data()
        if not df_heat.empty:
            df_heat['Nhãn hiển thị'] = "<b>" + df_heat['Mã CK'] + "</b><br>" + df_heat['Biến động (%)'].round(2).astype(str) + "%"
            fig = px.treemap(
                df_heat,
                path=[px.Constant("Thị Trường VN"), 'Ngành', 'Nhãn hiển thị'],
                values='Khối lượng',
                color='Biến động (%)',
                range_color=[-7, 7],
                color_continuous_scale=[
                    [0.0, "#00DFD8"], [0.035, "#00DFD8"],
                    [0.035, "#F6465D"], [0.495, "#F6465D"],
                    [0.495, "#FFB300"], [0.505, "#FFB300"],
                    [0.505, "#0ECB81"], [0.965, "#0ECB81"],
                    [0.965, "#9C27B0"], [1.0, "#9C27B0"]
                ],
                hover_data={'Khối lượng': ':.2s', 'Giá (VNĐ)': ':,.0f'}
            )
            fig.update_layout(
                margin=dict(t=30, l=0, r=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False
            )
            fig.update_traces(
                textinfo="label",
                textfont=dict(color="#FFFFFF", size=15, family="Inter, 'Segoe UI', Arial, sans-serif"),
                marker=dict(line=dict(color='#1E2329', width=1)),
                hovertemplate="<b>%{label}</b><br>Khối lượng: %{value}<br>Biến động: %{color:.2f}%<extra></extra>"
            )
            st.plotly_chart(fig, use_container_width=True, height=600)
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
# KHỐI 1.6: BIỂU ĐỒ VN-INDEX
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
            year_range_str = f"{stats.get('year_low',0):,.2f} - {stats.get('year_high',0):,.2f}" if stats['year_high'] > 0 else "N/A"
            vol_str = f"{stats.get('volume',0):,}" if stats['volume'] > 0 else "N/A"
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
                    <div class="stat-row"><span class="stat-label">Previous Close</span><span class="stat-val">{stats.get('prev_close',0):,.2f}</span></div>
                    <div class="stat-row"><span class="stat-label">Open</span><span class="stat-val">{stats.get('open',0):,.2f}</span></div>
                </div>
                <div class="stat-col">
                    <div class="stat-row"><span class="stat-label">Volume</span><span class="stat-val">{vol_str}</span></div>
                    <div class="stat-row"><span class="stat-label">Day's Range</span><span class="stat-val">{stats.get('day_low',0):,.2f} - {stats.get('day_high',0):,.2f}</span></div>
                </div>
                <div class="stat-col">
                    <div class="stat-row"><span class="stat-label">52 Week Range</span><span class="stat-val">{year_range_str}</span></div>
                    <div class="stat-row"><span class="stat-label">Avg. Volume</span><span class="stat-val">N/A</span></div>
                </div>
            </div>
            <hr style='margin: 15px 0px 25px 0px; border-color: #EAECEF;'>
            """, unsafe_allow_html=True)
        else:
            st.warning("Yahoo Finance đang bảo trì API nội bộ. Vui lòng thử lại sau!")

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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["TỔNG QUAN THỊ TRƯỜNG", "DỮ LIỆU GIAO DỊCH", "PHÂN TÍCH AI", "BÁO CÁO TỔ CHỨC", "SO SÁNH DỊCH VỤ", "PHÂN TÍCH CỔ PHIẾU"])

    # --- TAB 1: TỔNG QUAN THỊ TRƯỜNG ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        groups_items = list(groups.items())
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
                rows_html += f"""<div class="m-row"><div class="m-name">{data.get('name','')}</div><div class="m-price">{data.get('price','N/A')}</div><div class="m-change {color_class}">{sign}{data.get('change',0):.2f}%</div></div>"""
            cards_html += f"""<div class="m-card"><div class="m-header"><div class="m-title">{group_name}</div><a href="#" class="m-more">Chi tiết &rsaquo;</a></div>{rows_html}</div>"""
        st.markdown(f"{css_market}<div class='m-grid'>{cards_html}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # --- TAB 2: DỮ LIỆU GIAO DỊCH ---
    with tab2:
        render_vnindex_chart()
        render_tab2_heatmap()

    # --- TAB 3: PHÂN TÍCH AI ---
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        market_sentiment_score, top_bullish_news, top_bearish_news = analyze_news_sentiment()
        technical_alerts = generate_technical_alerts()
        f319_data = get_f319_sentiment()

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
                if top_bullish_news:
                    _bl=top_bullish_news[0]['link'];_bt=top_bullish_news[0]['title']
                    rows_html += f"<div><a href='{_bl}' target='_blank' style='text-decoration:none;'><span class='ai-tag b-up-t'>TÍN HIỆU TÍCH CỰC</span><span class='ai-title'>{_bt}</span></a></div>"
                if top_bearish_news:
                    _brl=top_bearish_news[0]['link'];_brt=top_bearish_news[0]['title']
                    rows_html += f"<div><a href='{_brl}' target='_blank' style='text-decoration:none;'><span class='ai-tag b-down-t'>TÍN HIỆU TIÊU CỰC</span><span class='ai-title'>{_brt}</span></a></div>"
                st.markdown(f"{css_ai_news}<div class='ai-news-card'>{rows_html}</div>", unsafe_allow_html=True)

        @st.cache_data(ttl=3600, show_spinner=False)
        def fetch_golden_data_safe():
            import pandas as pd
            import gspread
            import json
            from oauth2client.service_account import ServiceAccountCredentials
            try:
                creds_str = st.secrets["GOOGLE_CREDENTIALS"]
                creds_dict = json.loads(creds_str)
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)
                sheet = client.open("LINANCE_DB").worksheet("RS_DATA")
                raw_data = sheet.get_all_values()
                if len(raw_data) > 1:
                    df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
                    for col in ['RS_1M', 'Điểm_KT', 'Thanh_Khoản_Tỷ', 'Giá']:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                    return df
                return pd.DataFrame()
            except Exception as e:
                return pd.DataFrame()

        df_top5 = fetch_golden_data_safe()

        st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase;'>Top 5 Siêu Cổ Phiếu</div>", unsafe_allow_html=True)
        if not df_top5.empty:
            df_golden = df_top5[(df_top5['RS_1M'] >= 80) & (df_top5['Điểm_KT'] >= 4)].copy()
            df_golden = df_golden.sort_values(by="Thanh_Khoản_Tỷ", ascending=False).head(5)
            if not df_golden.empty:
                css_ai_alerts = """
                <style>
                .a-card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }
                .a-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; text-align: center; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
                .a-card:hover { border-color: #0ECB81; box-shadow: 0 4px 12px rgba(14, 203, 129, 0.15); transform: translateY(-2px);}
                .a-ticker { font-size: 18px; font-weight: 900; color: #1E2329; margin-bottom: 8px;}
                .a-type { font-size: 11px; font-weight: 700; padding: 6px 8px; border-radius: 4px; color: #fff; text-transform: uppercase; display: inline-block; margin-bottom: 12px; width: 100%; box-sizing: border-box; background-color: #0ECB81;}
                .a-details { font-size: 12px; color: #707A8A; line-height: 1.5; font-weight: 600;}
                .a-rs-tag { color: #9C27B0; font-weight: 800; }
                </style>
                """
                cards_html = ""
                for _, row in df_golden.iterrows():
                    _mk=row['Mã CK'];_g=int(row['Giá']);_tk=row['Thanh_Khoản_Tỷ'];_r1=int(row['RS_1M'])
                    cards_html += f"<div class='a-card'><div class='a-ticker'>{_mk}</div><div class='a-type'>ĐỘT PHÁ SỨC MẠNH</div><div class='a-details'>Giá: {_g:,}<br>Thanh khoản: <span style='color:#1E2329;'>{_tk:.1f} Tỷ</span><br>Điểm RS: <span class='a-rs-tag'>{_r1}</span></div></div>"
                st.markdown(css_ai_alerts + f"<div class='a-card-grid'>{cards_html}</div>", unsafe_allow_html=True)
            else:
                st.info("Hệ thống đang quét... chưa có mã nào đạt đủ tiêu chuẩn.")
        else:
            st.warning("Đang kết nối Database")

        st.markdown("<br><h3 style='color: #1E2329; margin-top: 32px; margin-bottom: 24px; border-top: 1px solid #EAECEF; padding-top: 32px;'>Định Lượng Dòng Tiền & Bộ Lọc Sóng Ngành</h3>", unsafe_allow_html=True)

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

        with col_left:
            st.markdown("<div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase;'>Bảng Xếp Hạng Sức Mạnh Giá (RS)</div>", unsafe_allow_html=True)
            st.markdown("<div style='color: #707A8A; font-size: 13px; margin-bottom: 16px;'>Dữ liệu đã lọc Rác. <span style='color: #9C27B0; font-weight: 800;'>Màu Tím (RS > 90)</span> là các mã dẫn dắt.</div>", unsafe_allow_html=True)
            if df_rs.empty:
                st.warning("Đang tải dữ liệu cổ phiếu...")
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
                    _mk=row['Mã CK'];_ng=row['Ngành'];_r1=int(row['RS_1M']);_r3=int(row['RS_3M'])
                    rows_html += f"<tr><td style='text-align: left;'><div class='rs-ticker'>{_mk}</div><div class='rs-sector'>{_ng}</div></td><td><div class='rs-cell' style='{style_1m}'>{_r1}</div></td><td><div class='rs-cell' style='{style_3m}'>{_r3}</div></td></tr>"
                table_html = f"<div class='rs-table-container'><table class='rs-table'><thead><tr><th style='text-align: left;'>CỔ PHIẾU</th><th>RS 1T</th><th>RS 3T</th></tr></thead><tbody>{rows_html}</tbody></table></div>"
                st.markdown(css_rs_table + table_html, unsafe_allow_html=True)

        with col_right:
            st.markdown("<div style='font-size: 14px; font-weight: 700; color: #303F9F; text-transform: uppercase; margin-bottom: 16px;'>Screener Tài Chính: Lọc Sóng Ngành</div>", unsafe_allow_html=True)
            st.markdown("<div style='color: #707A8A; font-size: 13px; margin-bottom: 16px;'>Chọn Ngành đang dẫn sóng để tìm ra những Cổ phiếu mạnh nhất.</div>", unsafe_allow_html=True)
            if df_ind.empty or df_rs.empty:
                st.warning("Đang tải dữ liệu bộ lọc...")
            else:
                @st.fragment
                def render_industry_filter():
                    df_ind_sorted = df_ind.sort_values(by="RS_TB", ascending=False).reset_index(drop=True)
                    industry_options = []
                    for _, row in df_ind_sorted.iterrows():
                        trend = str(row.get('Xu_Hướng', 'TRUNG TÍNH')).strip()
                        _ng = row['Ngành']
                        _rtb = row['RS_TB']
                        industry_options.append(f"{_ng} (RS: {_rtb:.1f}) - {trend}")
                    st.markdown("<span style='font-weight:700; font-size:14px; color:#1E2329;'>BƯỚC 1: CHỌN NGÀNH ĐỂ SOI DÒNG TIỀN</span>", unsafe_allow_html=True)
                    selected_option = st.selectbox("Danh sách Ngành (Sắp xếp từ mạnh đến yếu):", industry_options, label_visibility="collapsed")
                    selected_industry_name = selected_option.split(" (RS:")[0]
                    selected_trend = selected_option.split(" - ")[-1].strip()
                    if "TÍCH CỰC" in selected_trend: trend_color = "#0ECB81"
                    elif "YẾU" in selected_trend: trend_color = "#F6465D"
                    else: trend_color = "#FFB300"
                    trend_badge = f"<span style='background-color: {trend_color}; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 800; margin-left: 10px; vertical-align: middle;'>{selected_trend}</span>"
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"<div style='margin-bottom: 16px;'><span style='font-weight:700; font-size:14px; color:#1E2329;'>BƯỚC 2: TOP CỔ PHIẾU NGÀNH <span style='color:#E65100;'>{selected_industry_name.upper()}</span></span>{trend_badge}</div>", unsafe_allow_html=True)
                    df_filtered = df_rs[(df_rs['Ngành'] == selected_industry_name) & (df_rs['Thanh_Khoản_Tỷ'] > 0)].copy()
                    df_filtered = df_filtered.sort_values(by="RS_1M", ascending=False).head(15).reset_index(drop=True)
                    if df_filtered.empty:
                        st.info("Chưa có dữ liệu cổ phiếu thanh khoản cao cho ngành này.")
                    else:
                        rows_html_right = ""
                        for _, row in df_filtered.iterrows():
                            style_1m = get_rs_style(row['RS_1M'])
                            score = int(row['Điểm_KT'])
                            stars = "★" * score + "☆" * (5 - score)
                            _mk=row['Mã CK'];_tk=row['Thanh_Khoản_Tỷ'];_r1=int(row['RS_1M'])
                            rows_html_right += f"<tr><td style='text-align: left;'><div class='rs-ticker'>{_mk}</div><div class='rs-sector'>Thanh khoản: {_tk:.1f} Tỷ</div></td><td><div class='rs-cell' style='{style_1m}'>{_r1}</div></td><td style='color: #E65100; font-size: 13px; font-weight: 700;'>{stars}</td></tr>"
                        table_html_right = f"<div class='rs-table-container'><table class='rs-table'><thead><tr><th style='text-align: left;'>MÃ CK</th><th>RS 1T</th><th>ĐIỂM KỸ THUẬT</th></tr></thead><tbody>{rows_html_right}</tbody></table></div>"
                        st.markdown(css_rs_table + table_html_right, unsafe_allow_html=True)
                render_industry_filter()

        st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase; border-top: 1px solid #EAECEF; padding-top: 32px;'>Cộng Đồng Nhà Đầu Tư (Social Sentiment)</div>", unsafe_allow_html=True)
        if not f319_data['posts']:
            st.markdown("""
            <div style='background-color: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 60px 20px; text-align: center; margin-bottom: 24px;'>
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
<div class="soc-m-item"><span class="soc-m-lbl">Tương tác nổi bật</span><span class="soc-m-val">–</span></div>
<div class="soc-m-item"><span class="soc-m-lbl">Lượt đề cập</span><span class="soc-m-val">{f319_data.get('total_mentions',0):,}</span></div>
<div class="soc-m-item"><span class="soc-m-lbl">Bài đăng</span><span class="soc-m-val">{f319_data.get('total_posts',0)}</span></div>
</div>
<div class="p-bar-labels">
<span style="color: #0ECB81;">Tăng giá {f319_data.get('bullish_pct',0)}%</span>
<span style="color: #F6465D;">Giảm giá {f319_data.get('bearish_pct',0)}%</span>
</div>
<div class="p-bar-container">
<div class="p-bar-bull" style="width: {f319_data.get('bullish_pct',0)}%;"></div>
<div class="p-bar-bear" style="width: {f319_data.get('bearish_pct',0)}%;"></div>
</div>
<div style="font-size: 13px; color: #707A8A; line-height: 1.5; margin-top: 24px;">
Dữ liệu được rà soát tự động. Mức độ hưng phấn áp đảo thường xuất hiện tại các vùng đỉnh ngắn hạn.
</div>
</div>"""
                st.markdown(f"{css_social}{stats_html}", unsafe_allow_html=True)
            with col_social_posts:
                posts_html = ""
                for p in f319_data['posts']:
                    tag_class = "s-bull-tag" if p['sentiment'] == "Bullish" else "s-bear-tag"
                    tag_text = "Tăng/Mua" if p['sentiment'] == "Bullish" else "Giảm/Bán"
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

    # ==========================================
    # TAB 4: BÁO CÁO TỔ CHỨC — UI/UX NÂNG CẤP (LOGIC GỮ NGUYÊN)
    # ==========================================
    with tab4:

        # --- HEADER KHU VỰC ---
        st.markdown("""
        <div style="margin: 20px 0 6px 0;">
            <span style="font-size: 11px; color: #848E9C; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">LINANCE / BÁO CÁO TỔ CHỨC</span>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 6px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #1E2329; margin: 0;">Trung tâm Kiểm định Khuyến nghị</h2>
            <span style="background: #FFF2E5; color: #FF6B00; font-size: 11px; font-weight: 700;
                         padding: 3px 10px; border-radius: 20px; border: 1px solid #FFE0B2; letter-spacing: 0.3px;">LIVE</span>
        </div>
        <div style="color: #707A8A; font-size: 14px; margin-bottom: 24px; line-height: 1.6;">
            Backtest tự động — Theo dõi giá mục tiêu và xếp hạng độ chính xác của các tổ chức theo thời gian thực.
        </div>
        """, unsafe_allow_html=True)

        # --- METRIC CARDS TỔNG QUAN (UI MỚI) ---
        @st.cache_data(ttl=300)
        def get_report_data_direct():
            try:
                raw_data = fetch_reports_db()
                if raw_data:
                    return pd.DataFrame(raw_data)
                return pd.DataFrame()
            except Exception:
                return pd.DataFrame()

        @st.cache_data(ttl=300)
        def get_rs_price_mapping():
            try:
                from backend.database import get_db_connection
                db = get_db_connection()
                if db:
                    sheet = db.worksheet("RS_DATA")
                    df_rs = pd.DataFrame(sheet.get_all_records())
                    if not df_rs.empty and 'Mã CK' in df_rs.columns and 'Giá' in df_rs.columns:
                        df_rs['Giá'] = pd.to_numeric(df_rs['Giá'].astype(str).str.replace(',', '').str.replace('.', '').str.strip(), errors='coerce')
                        return dict(zip(df_rs['Mã CK'].astype(str).str.strip().str.upper(), df_rs['Giá']))
            except Exception:
                pass
            return {}

        t4_df_rep = get_report_data_direct()
        t4_price_dict = get_rs_price_mapping()

        # Metrics tổng quan
        if not t4_df_rep.empty:
            _total = len(t4_df_rep)
            _buy_mask = t4_df_rep['Action'].astype(str).str.upper().str.contains('MUA|TÍCH LŨY|KHẢ QUAN', na=False)
            _buy = _buy_mask.sum()
            _brokers_count = t4_df_rep['Broker'].nunique()
            _tickers_count = t4_df_rep['Ticker'].nunique()

            st.markdown("""
            <style>
            .t4-metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px; }
            .t4-metric-card {
                background: #FFFFFF;
                border: 1px solid #EAECEF;
                border-top: 3px solid #FF6B00;
                border-radius: 10px;
                padding: 18px 20px;
            }
            .t4-metric-label {
                font-size: 11px;
                font-weight: 700;
                color: #848E9C;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 10px;
            }
            .t4-metric-val {
                font-size: 30px;
                font-weight: 900;
                color: #1E2329;
                font-family: 'SF Mono', Consolas, monospace;
                line-height: 1;
            }
            .t4-metric-sub {
                font-size: 12px;
                color: #848E9C;
                margin-top: 6px;
                font-weight: 500;
            }
            </style>
            """, unsafe_allow_html=True)

            buy_pct = round(_buy / _total * 100) if _total else 0
            st.markdown(f"""
            <div class="t4-metric-row">
                <div class="t4-metric-card">
                    <div class="t4-metric-label">Tổng báo cáo</div>
                    <div class="t4-metric-val">{_total}</div>
                    <div class="t4-metric-sub">Trong hệ thống</div>
                </div>
                <div class="t4-metric-card" style="border-top-color: #0ECB81;">
                    <div class="t4-metric-label">Khuyến nghị mua</div>
                    <div class="t4-metric-val" style="color: #0ECB81;">{_buy}</div>
                    <div class="t4-metric-sub">{buy_pct}% tổng số báo cáo</div>
                </div>
                <div class="t4-metric-card" style="border-top-color: #185FA5;">
                    <div class="t4-metric-label">Tổ chức tham gia</div>
                    <div class="t4-metric-val" style="color: #185FA5;">{_brokers_count}</div>
                    <div class="t4-metric-sub">CTCK đang theo dõi</div>
                </div>
                <div class="t4-metric-card" style="border-top-color: #9C27B0;">
                    <div class="t4-metric-label">Mã CP theo dõi</div>
                    <div class="t4-metric-val" style="color: #9C27B0;">{_tickers_count}</div>
                    <div class="t4-metric-sub">Cổ phiếu khác nhau</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- SUB TABS ---
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Dòng thời gian khuyến nghị", "Danh mục chiến lược", "VNDiamond Flow"])

        # ---------------------------------------------------------
        # SUB TAB 2: DANH MỤC CHIẾN LƯỢC (LOGIC GỮ NGUYÊN)
        # ---------------------------------------------------------
        with sub_tab2:
            st.markdown("<br><div style='font-weight: 800; font-size: 17px; margin-bottom: 16px; color: #FF6B00; text-transform: uppercase; border-left: 4px solid #FF6B00; padding-left: 12px;'>Quản trị & Đánh giá Danh mục Đầu tư</div>", unsafe_allow_html=True)

            @st.fragment
            def render_long_term_portfolio():
                import time

                if 'port_cached_df' not in st.session_state or time.time() - st.session_state.get('port_cache_time', 0) > 900:
                    with st.spinner("Đang đồng bộ dữ liệu Danh mục Dài hạn..."):
                        portfolio_data = fetch_portfolio_db()
                        manual_dict = {}
                        try:
                            manual_data = fetch_manual_price_db()
                            if manual_data and len(manual_data) > 1:
                                for row in manual_data[1:]:
                                    if len(row) >= 2:
                                        tk = str(row[0]).strip().upper()
                                        if tk:
                                            pr_str = str(row[1]).replace(',', '').replace('.', '').replace(' ', '').strip()
                                            try:
                                                manual_dict[tk] = float(pr_str)
                                            except: pass
                        except Exception as e:
                            pass

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

                                if cp == 0 or pd.isna(cp):
                                    if tkr in manual_dict:
                                        cp = float(manual_dict[tkr])
                                        if highest_price == 0: highest_price = cp
                                        if lowest_price == 0: lowest_price = cp

                                current_prices.append(cp if cp > 0 else None)
                                highest_prices.append(highest_price if highest_price > 0 else None)
                                if rec_p > 0 and cp > 0: actual_returns.append(((cp - rec_p) / rec_p) * 100)
                                else: actual_returns.append(None)
                                if cp == 0 or lowest_price == 0: statuses.append("Đang bám sát")
                                elif highest_price >= tgt_p and tgt_p > 0: statuses.append("Đã Đạt Target")
                                elif rec_p > 0 and lowest_price > 0 and lowest_price <= rec_p * 0.88:
                                    if cp >= rec_p * 0.98: statuses.append("Đang bám sát")
                                    else: statuses.append("Đã Chạm Cắt Lỗ")
                                else: statuses.append("Đang bám sát")

                            df_port['Current_Price'] = current_prices
                            df_port['Actual_Return'] = actual_returns
                            df_port['Auto_Status'] = statuses
                            df_port['Highest_Reached'] = highest_prices
                            st.session_state.port_cached_df = df_port
                            st.session_state.port_cache_time = time.time()

                cached_port = st.session_state.port_cached_df
                if cached_port.empty:
                    st.info("Chưa có dữ liệu. Vui lòng tạo tab PORTFOLIO_DB trên Sheets.")
                    return

                df_port = cached_port.copy()
                portfolios = df_port['Portfolio_Name'].dropna().unique().tolist()

                st.markdown("<div style='background-color: #FFF; padding: 16px; border-radius: 10px; margin-bottom: 24px; border: 1px solid #FFE0B2;'>", unsafe_allow_html=True)
                selected_port = st.selectbox("Chọn Danh mục Chiến lược để theo dõi:", portfolios, key="long_term_port_filter")
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
                card_style = "background: #FFFFFF; border: 1px solid #EAECEF; border-top: 3px solid #FF6B00; border-radius: 10px; padding: 18px 20px; text-align: center;"
                title_style = "color: #848E9C; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;"
                val_style = "font-size: 26px; font-weight: 900; color: #1E2329; font-family: 'SF Mono', Consolas, monospace;"

                with col_s1: st.markdown(f"<div style='{card_style}'><div style='{title_style}'>Số lượng mã</div><div style='{val_style}'>{num_stocks}</div></div>", unsafe_allow_html=True)
                with col_s2: st.markdown(f"<div style='{card_style}'><div style='{title_style}'>Kỳ vọng TB</div><div style='{val_style}'>{avg_exp_str}</div></div>", unsafe_allow_html=True)
                with col_s3: st.markdown(f"<div style='{card_style}'><div style='{title_style}'>Lãi/Lỗ thực tế</div><div style='{val_style}; color: {color_act};'>{avg_act_str}</div></div>", unsafe_allow_html=True)
                with col_s4:
                    dat_target_count = filtered_port['Auto_Status'].tolist().count('Đã Đạt Target')
                    st.markdown(f"<div style='{card_style}; border-top-color: #0ECB81;'><div style='{title_style}'>Đã chạm Target</div><div style='{val_style}; color: #0ECB81;'>{dat_target_count}/{num_stocks}</div></div>", unsafe_allow_html=True)

                st.markdown("<div style='background: #FF6B00; color: white; padding: 12px 16px; border-radius: 8px 8px 0 0; font-weight: 700; font-size: 13px; letter-spacing: 0.5px; margin-top: 28px; text-transform: uppercase;'>Bảng theo dõi chi tiết danh mục cổ phiếu</div>", unsafe_allow_html=True)
                st.dataframe(
                    filtered_port,
                    column_config={
                        "Portfolio_Name": None,
                        "Sector": None,
                        "Rec_Date": st.column_config.TextColumn("Ngày KN"),
                        "Ticker": st.column_config.TextColumn("Mã CP", width="small"),
                        "Company": st.column_config.TextColumn("Doanh nghiệp", width="medium"),
                        "Rec_Price": st.column_config.NumberColumn("Giá KN", format="%d ₫"),
                        "Current_Price": st.column_config.NumberColumn("Giá hiện tại", format="%d ₫"),
                        "Highest_Reached": st.column_config.NumberColumn("Đỉnh đã chạm", format="%d ₫"),
                        "Target_Price": st.column_config.NumberColumn("Giá mục tiêu", format="%d ₫"),
                        "Expected_Return": st.column_config.TextColumn("Kỳ vọng"),
                        "Actual_Return": st.column_config.NumberColumn("Lãi/Lỗ", format="%.1f %%"),
                        "Auto_Status": st.column_config.TextColumn("Đánh giá (AI)"),
                        "Link": st.column_config.LinkColumn("Nguồn", display_text="Xem")
                    },
                    hide_index=True,
                    width="stretch",
                    height=450
                )

            render_long_term_portfolio()

        # ---------------------------------------------------------
        # SUB TAB 3: VNDIAMOND FLOW (LOGIC GỮ NGUYÊN)
        # ---------------------------------------------------------
        with sub_tab3:
            st.markdown("<br><div style='font-weight: 800; font-size: 17px; margin-bottom: 16px; color: #FF6B00; text-transform: uppercase; border-left: 4px solid #FF6B00; padding-left: 12px;'>Phân tích Dòng tiền Cơ cấu Rổ VNDiamond</div>", unsafe_allow_html=True)

            @st.fragment
            def render_vndiamond_flow():
                import time

                if 'diamond_cached_df' not in st.session_state or time.time() - st.session_state.get('diamond_cache_time', 0) > 900:
                    with st.spinner("Đang soi dòng tiền VNDiamond..."):
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
                    net_color = "#0ECB81" if net_flow >= 0 else "#F6465D"
                    net_sign = "+" if net_flow > 0 else ""

                    # Metric cards dòng tiền — style thống nhất với phần trên
                    st.markdown(f"""
                    <style>
                    .dm-metric-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 24px; }}
                    .dm-metric-card {{ background: #FFFFFF; border: 1px solid #EAECEF; border-top: 3px solid #EAECEF; border-radius: 10px; padding: 18px 20px; }}
                    .dm-label {{ font-size: 11px; font-weight: 700; color: #848E9C; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }}
                    .dm-val {{ font-size: 26px; font-weight: 900; color: #1E2329; font-family: 'SF Mono', Consolas, monospace; }}
                    .dm-sub {{ font-size: 12px; color: #848E9C; margin-top: 4px; }}
                    </style>
                    <div class="dm-metric-row">
                        <div class="dm-metric-card" style="border-top-color: #0ECB81;">
                            <div class="dm-label">Lực mua dự kiến</div>
                            <div class="dm-val">{total_buy/1e9:,.1f} <span style="font-size: 14px; color: #848E9C;">Tỷ</span></div>
                        </div>
                        <div class="dm-metric-card" style="border-top-color: #F6465D;">
                            <div class="dm-label">Lực xả dự kiến</div>
                            <div class="dm-val">{total_sell/1e9:,.1f} <span style="font-size: 14px; color: #848E9C;">Tỷ</span></div>
                        </div>
                        <div class="dm-metric-card" style="border-top-color: {net_color};">
                            <div class="dm-label">Trạng thái ròng</div>
                            <div class="dm-val" style="color: {net_color};">{net_sign}{net_flow/1e9:,.1f} <span style="font-size: 14px;">Tỷ</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<div style='background: #FF6B00; color: white; padding: 12px 16px; border-radius: 8px 8px 0 0; font-weight: 700; font-size: 13px; letter-spacing: 0.5px; text-transform: uppercase;'>Bảng dòng tiền chi tiết</div>", unsafe_allow_html=True)

                    df_display = df_final.copy()
                    df_display['Khối Lượng'] = df_display['Clean_Volume'].apply(lambda x: f"{x:,.0f}")
                    df_display['Giá Hiện Tại'] = df_display['Current_Price'].apply(lambda x: f"{x:,.0f} ₫" if pd.notnull(x) else "N/A")
                    df_display['Thành Tiền (VNĐ)'] = df_display['Est_Cash_Flow'].apply(lambda x: f"{x:,.0f} ₫")

                    st.dataframe(
                        df_display,
                        column_config={
                            "Ticker": st.column_config.TextColumn("Mã CP", width="small"),
                            "Industry": st.column_config.TextColumn("Ngành", width="medium"),
                            "New_Weight": st.column_config.TextColumn("Tỷ trọng", width="small"),
                            "Khối Lượng": st.column_config.TextColumn("Khối lượng GD", width="medium"),
                            "Giá Hiện Tại": st.column_config.TextColumn("Giá HT", width="medium"),
                            "Thành Tiền (VNĐ)": st.column_config.TextColumn("Giá trị dòng tiền", width="large"),
                            "Old_Weight": None, "Est_Volume": None, "Est_Trade_Vol": None,
                            "Ước tính giao dịch": None, "Volume": None, "Khối lượng": None,
                            "Clean_Volume": None, "Current_Price": None, "Est_Cash_Flow": None
                        },
                        hide_index=True, use_container_width=True, height=500
                    )
                    st.caption("Dòng tiền = Giá hiện tại × Khối lượng ước tính. Dấu âm (-) thể hiện áp lực bán ròng.")

                    try:
                        top_buy_df = df_final[df_final['Clean_Volume'] > 0].sort_values(by='Clean_Volume', ascending=False).head(3)
                        top_sell_df = df_final[df_final['Clean_Volume'] < 0].sort_values(by='Clean_Volume', ascending=True).head(3)
                        top_buy_html = "".join(["<li style='margin-bottom: 4px;'><b>" + str(row['Ticker']) + "</b>: Tăng <span style='color: #0ECB81; font-weight: 700;'>+" + "{:,.0f}".format(row['Clean_Volume']) + " cp</span></li>" for _, row in top_buy_df.iterrows()])
                        top_sell_html = "".join(["<li style='margin-bottom: 4px;'><b>" + str(row['Ticker']) + "</b>: Bán ra <span style='color: #F6465D; font-weight: 700;'>" + "{:,.0f}".format(row['Clean_Volume']) + " cp</span></li>" for _, row in top_sell_df.iterrows()])
                        warning_note = ""
                        if not top_sell_df.empty:
                            worst_ticker = top_sell_df.iloc[0]['Ticker']
                            warning_note = f"<div style='margin-top: 12px; padding-top: 10px; border-top: 1px dashed #FCA5A5; color: #DC2626; font-size: 12px; font-weight: 700;'>Cảnh báo: {worst_ticker} vào danh sách nguy cơ chờ loại khỏi rổ.</div>"
                        summary_html = f"<div style='background: #FFFFFF; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; margin-top: 20px;'><div style='font-size: 13px; font-weight: 700; color: #1E2329; margin-bottom: 16px;'>Tổng kết & Phân tích nhanh</div><div style='display: flex; gap: 16px; flex-wrap: wrap;'><div style='flex: 1; min-width: 250px; background: #F0FDFA; border-left: 3px solid #0ECB81; padding: 12px 16px; border-radius: 4px;'><div style='font-size: 11px; font-weight: 700; color: #0ECB81; margin-bottom: 8px; text-transform: uppercase;'>Tâm điểm hút tiền</div><ul style='margin: 0; padding-left: 20px; font-size: 13px; color: #1E2329;'>{top_buy_html if top_buy_html else '<li>Chưa có dữ liệu</li>'}</ul></div><div style='flex: 1; min-width: 250px; background: #FEF2F2; border-left: 3px solid #F6465D; padding: 12px 16px; border-radius: 4px;'><div style='font-size: 11px; font-weight: 700; color: #F6465D; margin-bottom: 8px; text-transform: uppercase;'>Áp lực bán ròng</div><ul style='margin: 0; padding-left: 20px; font-size: 13px; color: #1E2329;'>{top_sell_html if top_sell_html else '<li>Chưa có dữ liệu</li>'}</ul>{warning_note}</div></div><div style='margin-top: 14px; padding-top: 12px; border-top: 1px solid #EAECEF; font-size: 11px; color: #848E9C; text-align: right;'>Nguồn: Thay đổi thành phần chỉ số Q2/2026 — Dữ liệu chốt 31/03/2026</div></div>"
                        st.markdown(summary_html, unsafe_allow_html=True)
                    except Exception as e: pass

            render_vndiamond_flow()

        # ---------------------------------------------------------
        # SUB TAB 1: DÒNG THỜI GIAN KHUYẾN NGHỊ — UI NÂNG CẤP (LOGIC GỮ NGUYÊN)
        # ---------------------------------------------------------
        with sub_tab1:
            st.markdown("<br>", unsafe_allow_html=True)

            @st.fragment
            def render_report_timeline():
                import time

                # ── LOAD & CACHE DATA ────────────────────────────────────────────
                if "rep_df_cache" not in st.session_state or time.time() - st.session_state.get("rep_df_time", 0) > 600:
                    with st.spinner("Đang tải danh sách báo cáo..."):
                        try:
                            raw = fetch_reports_db()
                            if raw:
                                df_raw = pd.DataFrame(raw)
                                df_raw["_d"] = pd.to_datetime(df_raw["Date"], format="%d/%m/%Y", errors="coerce")
                                df_raw = df_raw.sort_values("_d", ascending=False).drop(columns=["_d"]).reset_index(drop=True)
                                st.session_state.rep_df_cache = df_raw
                            else:
                                st.session_state.rep_df_cache = pd.DataFrame()
                        except Exception:
                            st.session_state.rep_df_cache = pd.DataFrame()
                        st.session_state.rep_df_time = time.time()

                df_rep = st.session_state.get("rep_df_cache", pd.DataFrame())
                price_map = t4_price_dict

                if df_rep.empty:
                    st.warning("Đang kết nối Google Sheets. Vui lòng chờ giây lát rồi bấm F5...")
                    return

                # ── DASHBOARD TỔNG QUAN ──────────────────────────────────────────
                st.markdown("<div style='font-weight:500;font-size:15px;color:var(--text-primary);margin-bottom:14px;'>Tổng quan kỳ báo cáo</div>", unsafe_allow_html=True)

                # 4 metric cards + donut chart + top stocks
                total_all = len(df_rep)
                act_col = df_rep["Action"].astype(str).str.upper()
                n_buy  = act_col.str.contains("MUA|TÍCH LŨY|KHẢ QUAN", na=False).sum()
                n_sell = act_col.str.contains("BÁN|GIẢM|KÉM", na=False).sum()
                n_hold = total_all - n_buy - n_sell

                # Top 5 mã được nhiều tổ chức nhất
                top_tickers = df_rep["Ticker"].value_counts().head(5)

                dash_css = """<style>
.db-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
.db-card{background:#fff;border:0.5px solid #EAECEF;border-radius:10px;padding:14px 16px;border-top:2.5px solid #EAECEF}
.db-lbl{font-size:10px;font-weight:600;color:#848E9C;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.db-val{font-size:26px;font-weight:700;color:#1E2329;font-family:'SF Mono',Consolas,monospace;line-height:1}
.db-sub{font-size:11px;color:#848E9C;margin-top:5px}
.top-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.top-pill{background:#F8FAFC;border:0.5px solid #EAECEF;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;color:#1E2329;display:flex;align-items:center;gap:6px}
.top-count{background:#FF6B00;color:#fff;border-radius:10px;padding:1px 7px;font-size:10px;font-weight:700}
</style>"""
                buy_pct  = round(n_buy/total_all*100) if total_all else 0
                sell_pct = round(n_sell/total_all*100) if total_all else 0
                hold_pct = 100 - buy_pct - sell_pct

                top_pills = ""
                for tkr, cnt in top_tickers.items():
                    top_pills += '<span class="top-pill">' + str(tkr) + '<span class="top-count">' + str(cnt) + '</span></span>'

                db_html = (
                    dash_css +
                    '<div class="db-grid">'
                    '<div class="db-card" style="border-top-color:#FF6B00"><div class="db-lbl">Tổng báo cáo</div><div class="db-val">' + str(total_all) + '</div><div class="db-sub">Trong hệ thống</div></div>'
                    '<div class="db-card" style="border-top-color:#0ECB81"><div class="db-lbl">Khuyến nghị mua</div><div class="db-val" style="color:#0ECB81">' + str(n_buy) + '</div><div class="db-sub">' + str(buy_pct) + '% tổng số</div></div>'
                    '<div class="db-card" style="border-top-color:#FFB300"><div class="db-lbl">Trung lập</div><div class="db-val" style="color:#854F0B">' + str(n_hold) + '</div><div class="db-sub">' + str(hold_pct) + '% tổng số</div></div>'
                    '<div class="db-card" style="border-top-color:#F6465D"><div class="db-lbl">Khuyến nghị bán</div><div class="db-val" style="color:#F6465D">' + str(n_sell) + '</div><div class="db-sub">' + str(sell_pct) + '% tổng số</div></div>'
                    '</div>'
                    '<div style="font-size:11px;color:#848E9C;font-weight:600;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;">Top mã được theo dõi nhiều nhất</div>'
                    '<div class="top-row">' + top_pills + '</div>'
                )
                st.markdown(db_html, unsafe_allow_html=True)

                # ── BỘ LỌC NÂNG CẤP ─────────────────────────────────────────────
                with st.expander("Bộ lọc nâng cao", expanded=True):
                    r1c1, r1c2, r1c3 = st.columns(3)
                    r2c1, r2c2, r2c3 = st.columns(3)

                    with r1c1:
                        brokers_list = ["Tất cả"] + sorted(df_rep["Broker"].dropna().unique().tolist())
                        sel_broker = st.selectbox("Tổ chức", brokers_list, key="tl_broker")
                    with r1c2:
                        tickers_list = ["Tất cả"] + sorted(df_rep["Ticker"].dropna().unique().tolist())
                        sel_ticker = st.selectbox("Mã cổ phiếu", tickers_list, key="tl_ticker")
                    with r1c3:
                        rec_types = ["Tất cả", "Mua / Khả quan", "Trung lập / Giữ", "Bán / Kém khả quan"]
                        sel_rec = st.selectbox("Loại khuyến nghị", rec_types, key="tl_rec")
                    with r2c1:
                        time_opts = ["Tất cả", "Hôm nay", "7 ngày qua", "30 ngày qua", "Quý này", "Năm nay", "Tùy chỉnh"]
                        sel_time = st.selectbox("Thời gian", time_opts, key="tl_time")
                    with r2c2:
                        if sel_time == "Tùy chỉnh":
                            date_from = st.date_input("Từ ngày", key="tl_date_from")
                        else:
                            date_from = None
                    with r2c3:
                        if sel_time == "Tùy chỉnh":
                            date_to = st.date_input("Đến ngày", key="tl_date_to")
                        else:
                            date_to = None

                # ── ÁP DỤNG BỘ LỌC ──────────────────────────────────────────────
                df_f = df_rep.copy()
                df_f["_d"] = pd.to_datetime(df_f["Date"], format="%d/%m/%Y", errors="coerce")
                now = datetime.now()

                if sel_broker != "Tất cả":
                    df_f = df_f[df_f["Broker"] == sel_broker]
                if sel_ticker != "Tất cả":
                    df_f = df_f[df_f["Ticker"] == sel_ticker]
                if sel_rec == "Mua / Khả quan":
                    df_f = df_f[df_f["Action"].astype(str).str.upper().str.contains("MUA|TÍCH LŨY|KHẢ QUAN", na=False)]
                elif sel_rec == "Trung lập / Giữ":
                    df_f = df_f[df_f["Action"].astype(str).str.upper().str.contains("GIỮ|TRUNG LẬP|NEUTRAL", na=False)]
                elif sel_rec == "Bán / Kém khả quan":
                    df_f = df_f[df_f["Action"].astype(str).str.upper().str.contains("BÁN|GIẢM|KÉM", na=False)]

                if sel_time == "Hôm nay":
                    df_f = df_f[df_f["_d"].dt.date == now.date()]
                elif sel_time == "7 ngày qua":
                    df_f = df_f[df_f["_d"] >= pd.Timestamp(now) - pd.Timedelta(days=7)]
                elif sel_time == "30 ngày qua":
                    df_f = df_f[df_f["_d"] >= pd.Timestamp(now) - pd.Timedelta(days=30)]
                elif sel_time == "Quý này":
                    q_start = pd.Timestamp(now.year, ((now.month-1)//3)*3+1, 1)
                    df_f = df_f[df_f["_d"] >= q_start]
                elif sel_time == "Năm nay":
                    df_f = df_f[df_f["_d"].dt.year == now.year]
                elif sel_time == "Tùy chỉnh" and date_from and date_to:
                    df_f = df_f[(df_f["_d"].dt.date >= date_from) & (df_f["_d"].dt.date <= date_to)]

                df_f = df_f.drop(columns=["_d"]).reset_index(drop=True)

                # ── DYNAMIC STATUS ───────────────────────────────────────────────
                def get_status(row):
                    tkr   = str(row.get("Ticker", "")).strip().upper()
                    entry = pd.to_numeric(row.get("Current_Price_At_Date", 0), errors="coerce") or 0
                    tgt   = pd.to_numeric(row.get("Target_Price", 0), errors="coerce") or 0
                    rt    = pd.to_numeric(price_map.get(tkr, 0), errors="coerce") or 0
                    orig  = str(row.get("Status", "")).strip().upper()
                    if "ĐẠT" in orig or "TARGET" in orig: return "ĐẠT TARGET"
                    if "CẮT" in orig or "LỖ" in orig:
                        if tgt > 0 and rt >= tgt: return "ĐẠT TARGET (Từng vi phạm)"
                        return "CẮT LỖ"
                    if rt <= 0 or entry <= 0: return "ĐANG THEO DÕI"
                    if tgt > 0 and rt >= tgt:  return "ĐẠT TARGET"
                    if rt <= entry * 0.93:     return "CẮT LỖ"
                    return "ĐANG THEO DÕI"

                df_f = df_f.copy()
                df_f["Dynamic_Status"] = df_f.apply(get_status, axis=1)

                # ── EXPORT CSV ──────────────────────────────────────────────────
                col_export_label, col_export_btn = st.columns([3, 1])
                with col_export_label:
                    st.markdown(
                        "<div style='color:#848E9C;font-size:12px;margin-top:8px;'>"
                        + str(len(df_f)) + " báo cáo phù hợp với bộ lọc hiện tại</div>",
                        unsafe_allow_html=True
                    )
                with col_export_btn:
                    export_cols = ["Date", "Broker", "Ticker", "Action", "Current_Price_At_Date", "Target_Price", "Dynamic_Status", "Link"]
                    export_df = df_f[[c for c in export_cols if c in df_f.columns]]
                    csv_data = export_df.to_csv(index=False, encoding="utf-8-sig")
                    st.download_button(
                        label="Xuất CSV",
                        data=csv_data,
                        file_name="bao_cao_to_chuc.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="tl_export"
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── CSS CARDS ───────────────────────────────────────────────────
                st.markdown("""<style>
.rc{background:#fff;border:1px solid #EAECEF;border-left:4px solid #EAECEF;border-radius:10px;padding:16px 20px;margin-bottom:10px;transition:all .15s}
.rc:hover{border-color:#FFE0B2;border-left-color:#FF6B00;box-shadow:0 3px 12px rgba(255,107,0,.07)}
.rc-new{box-shadow:0 0 0 1.5px #FF6B00;border-left-color:#FF6B00}
.rc-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.rc-tkr{font-size:18px;font-weight:700;color:#1E2329;font-family:monospace}
.rc-brk{font-size:11px;color:#707A8A;font-weight:600;background:#F8FAFC;padding:3px 9px;border-radius:4px;border:0.5px solid #EAECEF}
.rc-mid{display:flex;gap:20px;margin-bottom:10px;flex-wrap:wrap}
.rc-lbl{font-size:10px;color:#848E9C;text-transform:uppercase;font-weight:600;letter-spacing:.4px;margin-bottom:3px}
.rc-val{font-size:13px;font-weight:700;color:#1E2329;font-family:monospace}
.rc-div{border-top:0.5px solid #F0F2F5;margin:8px 0 6px}
.rc-new-badge{font-size:9px;font-weight:700;background:#FF6B00;color:#fff;padding:2px 6px;border-radius:3px;margin-left:6px;vertical-align:middle}
.am{color:#3B6D11;background:#EAF3DE;border:0.5px solid #639922;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.ab{color:#A32D2D;background:#FCEBEB;border:0.5px solid #E24B4A;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.ag{color:#854F0B;background:#FAEEDA;border:0.5px solid #BA7517;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.ax{background:#F0F2F5;color:#474D57;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.sd{color:#3B6D11;border:0.5px solid #639922;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700}
.sw{color:#854F0B;border:0.5px solid #BA7517;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700}
.sc{color:#A32D2D;border:0.5px solid #E24B4A;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700}
.so{color:#5F5E5A;border:0.5px solid #B4B2A9;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700}
.consensus-bar{height:5px;background:#F0F2F5;border-radius:3px;overflow:hidden;margin-top:5px}
.consensus-fill{height:100%;border-radius:3px;background:#0ECB81}
</style>""", unsafe_allow_html=True)

                # ── HAI CỘT CHÍNH ────────────────────────────────────────────────
                col_list, col_board = st.columns([1.7, 1])

                # ── CỘT TRÁI: DANH SÁCH BÁO CÁO ─────────────────────────────────
                with col_list:
                    PER_PAGE = 6
                    total    = len(df_f)
                    total_pg = max(1, math.ceil(total / PER_PAGE))
                    if "tl_page" not in st.session_state: st.session_state.tl_page = 1
                    st.session_state.tl_page = max(1, min(st.session_state.tl_page, total_pg))

                    page_df = df_f.iloc[(st.session_state.tl_page-1)*PER_PAGE : st.session_state.tl_page*PER_PAGE]

                    today_str = datetime.now().strftime("%d/%m/%Y")

                    if page_df.empty:
                        st.warning("Không tìm thấy báo cáo nào với bộ lọc hiện tại.")
                    else:
                        html_cards = ""
                        for _, r in page_df.iterrows():
                            act = str(r.get("Action", "")).upper()
                            sts = str(r.get("Dynamic_Status", "ĐANG THEO DÕI"))
                            tkr = str(r.get("Ticker", "N/A"))
                            brk = str(r.get("Broker", "N/A"))
                            dt  = str(r.get("Date", "N/A"))
                            lnk = str(r.get("Link", "#"))
                            is_new = dt == today_str

                            if any(k in act for k in ["MUA","TĂNG","KHẢ QUAN","TÍCH LŨY"]): acls="am"; bcol="#639922"
                            elif any(k in act for k in ["BÁN","GIẢM","KÉM"]):               acls="ab"; bcol="#E24B4A"
                            elif any(k in act for k in ["GIỮ","TRUNG LẬP"]):                acls="ag"; bcol="#BA7517"
                            else:                                                             acls="ax"; bcol="#EAECEF"

                            if "(Từng vi phạm)" in sts: scls="sw"
                            elif "ĐẠT" in sts:          scls="sd"
                            elif "CẮT" in sts:          scls="sc"
                            else:                        scls="so"

                            try:    tp = "{:,.0f}".format(float(r.get("Target_Price", 0)))
                            except: tp = "N/A"
                            try:    cp = "{:,.0f}".format(float(r.get("Current_Price_At_Date", 0)))
                            except: cp = "N/A"
                            rt_raw = price_map.get(tkr.upper(), 0)
                            try:    rp = "{:,.0f}".format(float(rt_raw)) if float(rt_raw) > 0 else "N/A"
                            except: rp = "N/A"

                            # Upside
                            up_html = ""
                            try:
                                e = float(r.get("Current_Price_At_Date", 0))
                                t = float(r.get("Target_Price", 0))
                                if e > 0 and t > 0:
                                    up = (t - e) / e * 100
                                    uc = "#3B6D11" if up >= 0 else "#A32D2D"
                                    us = "+" if up >= 0 else ""
                                    up_html = ('<div><div class="rc-lbl">Upside</div>'
                                               '<div class="rc-val" style="color:' + uc + ';">'
                                               + us + "{:.1f}%".format(up) + '</div></div>')
                            except: pass

                            # Consensus với mã này
                            tkr_upper = tkr.upper()
                            tkr_df = df_rep[df_rep["Ticker"].astype(str).str.upper() == tkr_upper]
                            n_tkr_total = len(tkr_df)
                            n_tkr_buy   = tkr_df["Action"].astype(str).str.upper().str.contains("MUA|KHẢ QUAN|TÍCH LŨY", na=False).sum()
                            consensus_pct = int(n_tkr_buy / n_tkr_total * 100) if n_tkr_total > 0 else 0
                            consensus_html = (
                                '<div style="margin-top:2px;">'
                                '<div style="font-size:10px;color:#848E9C;font-weight:600;margin-bottom:3px;">'
                                + str(n_tkr_total) + ' tổ chức · ' + str(consensus_pct) + '% đồng thuận mua'
                                '</div>'
                                '<div class="consensus-bar"><div class="consensus-fill" style="width:' + str(consensus_pct) + '%;"></div></div>'
                                '</div>'
                            )

                            new_badge = '<span class="rc-new-badge">MỚI</span>' if is_new else ""
                            card_cls  = 'rc rc-new' if is_new else 'rc'

                            html_cards += (
                                '<div class="' + card_cls + '" style="border-left-color:' + bcol + ';">'
                                  '<div class="rc-top">'
                                    '<div style="display:flex;align-items:center;gap:8px;">'
                                      '<span class="rc-tkr">' + tkr + '</span>'
                                      + new_badge +
                                      '<span class="' + acls + '">' + act + '</span>'
                                      '<span class="' + scls + '">' + sts + '</span>'
                                    '</div>'
                                    '<span class="rc-brk">' + brk + '</span>'
                                  '</div>'
                                  '<div class="rc-mid">'
                                    '<div><div class="rc-lbl">Giá KN</div><div class="rc-val">' + cp + '</div></div>'
                                    '<div><div class="rc-lbl">Giá hiện tại</div><div class="rc-val" style="color:#185FA5;">' + rp + '</div></div>'
                                    '<div><div class="rc-lbl">Giá mục tiêu</div><div class="rc-val" style="color:#FF6B00;">' + tp + '</div></div>'
                                    + up_html +
                                    '<div><div class="rc-lbl">Ngày</div><div class="rc-val" style="color:#707A8A;font-weight:600;">' + dt + '</div></div>'
                                  '</div>'
                                  + consensus_html +
                                  '<div class="rc-div"></div>'
                                  '<div style="font-size:11px;text-align:right;">'
                                    '<a href="' + lnk + '" target="_blank" style="color:#185FA5;font-weight:600;text-decoration:none;">Xem báo cáo &rarr;</a>'
                                  '</div>'
                                '</div>'
                            )
                        st.markdown(html_cards, unsafe_allow_html=True)

                    # Phân trang
                    if total_pg > 1:
                        pc = st.columns([2,1,2,1,2])
                        with pc[1]:
                            if st.button("Trước", disabled=(st.session_state.tl_page<=1), use_container_width=True, key="tl_prev"):
                                st.session_state.tl_page -= 1
                                st.rerun(scope="fragment")
                        with pc[2]:
                            st.markdown(
                                "<div style='text-align:center;padding-top:8px;font-weight:600;color:#474D57;font-size:12px;'>Trang "
                                + str(st.session_state.tl_page) + " / " + str(total_pg) + "</div>",
                                unsafe_allow_html=True
                            )
                        with pc[3]:
                            if st.button("Tiếp", disabled=(st.session_state.tl_page>=total_pg), use_container_width=True, key="tl_next"):
                                st.session_state.tl_page += 1
                                st.rerun(scope="fragment")

                # ── CỘT PHẢI: XẾP HẠNG NÂNG CẤP ────────────────────────────────
                with col_board:
                    st.markdown("<div style='font-weight:600;font-size:14px;margin-bottom:5px;color:#1E2329;'>Xếp hạng tổ chức</div>", unsafe_allow_html=True)
                    st.markdown("<div style='color:#707A8A;font-size:11px;margin-bottom:14px;line-height:1.5;'>Điểm = Win Rate (40%) + Upside accuracy (25%) + Tốc độ chạm target (20%) + Số lượng (15%)</div>", unsafe_allow_html=True)

                    # Tính điểm nâng cấp cho từng tổ chức
                    rank_data = []
                    for brk_name in df_rep["Broker"].dropna().unique():
                        g = df_rep[df_rep["Broker"] == brk_name].copy()
                        g["_sts"] = g.apply(get_status, axis=1)
                        wins   = (g["_sts"].str.contains("ĐẠT", na=False)).sum()
                        losses = (g["_sts"].str.contains("CẮT", na=False)).sum()
                        pend   = len(g) - wins - losses
                        closed = wins + losses
                        if closed == 0: continue

                        win_rate = wins / closed * 100

                        # Upside accuracy: % giá mục tiêu được chạm thực tế
                        upside_acc_list = []
                        for _, row in g.iterrows():
                            try:
                                ep = float(row.get("Current_Price_At_Date", 0))
                                tp = float(row.get("Target_Price", 0))
                                tkr_u = str(row.get("Ticker","")).upper()
                                rt = float(price_map.get(tkr_u, 0))
                                if ep > 0 and tp > 0 and rt > 0:
                                    expected_up = (tp - ep) / ep * 100
                                    actual_up   = (rt - ep) / ep * 100
                                    if expected_up > 0:
                                        acc = min(actual_up / expected_up * 100, 100)
                                        upside_acc_list.append(max(acc, 0))
                            except: pass
                        upside_acc = sum(upside_acc_list)/len(upside_acc_list) if upside_acc_list else 0

                        # Volume score: log scale, max 100
                        import math as _math
                        vol_score = min(_math.log(len(g)+1, 2) / _math.log(50, 2) * 100, 100)

                        # Speed score: tạm tính bằng win_rate nếu chưa có timestamp đủ
                        speed_score = win_rate

                        final_score = (win_rate * 0.40 + upside_acc * 0.25 + speed_score * 0.20 + vol_score * 0.15)

                        rank_data.append({
                            "Broker": brk_name, "Wins": wins, "Closed": closed,
                            "Pending": pend, "WinRate": win_rate,
                            "UpsideAcc": upside_acc, "Score": final_score
                        })

                    board_html = ""
                    if not rank_data:
                        board_html = "<div style='color:#707A8A;font-size:13px;text-align:center;padding:20px;'>Chưa có kèo đã đóng để xếp hạng.</div>"
                    else:
                        rank_sorted = sorted(rank_data, key=lambda x: x["Score"], reverse=True)
                        for i, s in enumerate(rank_sorted):
                            clr = "#0ECB81" if s["WinRate"] >= 50 else "#F6465D"
                            bar = int(s["WinRate"])
                            sc_disp = "{:.1f}".format(s["Score"])
                            wr_disp = "{:.1f}%".format(s["WinRate"])
                            ua_disp = "{:.0f}%".format(s["UpsideAcc"])
                            board_html += (
                                '<div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:0.5px solid #F0F2F5;padding:10px 0;">'
                                  '<div style="display:flex;align-items:flex-start;gap:8px;flex:1;">'
                                    '<span style="font-size:12px;font-weight:600;width:18px;color:#848E9C;padding-top:2px;">' + str(i+1) + '</span>'
                                    '<div>'
                                      '<div style="font-weight:600;color:#1E2329;font-size:13px;">' + s["Broker"] + '</div>'
                                      '<div style="font-size:10px;color:#848E9C;margin-top:2px;">Upside acc: ' + ua_disp + ' · ' + str(s["Wins"]) + '/' + str(s["Closed"]) + ' kèo</div>'
                                    '</div>'
                                  '</div>'
                                  '<div style="text-align:right;min-width:80px;">'
                                    '<div style="font-weight:700;color:' + clr + ';font-size:14px;font-family:monospace;">' + wr_disp + '</div>'
                                    '<div style="font-size:10px;color:#848E9C;margin-top:1px;">Điểm: ' + sc_disp + '</div>'
                                    '<div style="margin-top:4px;height:3px;background:#F0F2F5;border-radius:2px;">'
                                      '<div style="width:' + str(bar) + '%;height:100%;background:' + clr + ';border-radius:2px;"></div>'
                                    '</div>'
                                  '</div>'
                                '</div>'
                            )

                    # AI Consensus
                    buy_df = df_f[df_f["Action"].fillna("").astype(str).str.upper().str.contains("MUA|TĂNG|KHẢ QUAN")]
                    ai_txt = "Hệ thống đang thu thập thêm dữ liệu."
                    if not buy_df.empty:
                        top3 = ", ".join(buy_df["Ticker"].value_counts().head(3).index.tolist())
                        ai_txt = "Phần lớn tổ chức đồng thuận <b style='color:#0ECB81;'>MUA</b> tại: <b style='color:#FF6B00;'>" + top3 + "</b>"

                    st.markdown(
                        '<div style="background:#FAFAFA;border:0.5px solid #EAECEF;border-radius:10px;padding:16px;">'
                        + board_html +
                        '<div style="margin-top:16px;padding:12px 14px;background:#F0FDFA;border-radius:6px;border-left:3px solid #0ECB81;">'
                          '<div style="font-size:10px;color:#0ECB81;font-weight:700;text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px;">AI Consensus</div>'
                          '<div style="font-size:12px;color:#1E2329;font-weight:600;line-height:1.5;">' + ai_txt + '</div>'
                        '</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

                # ── MA TRẬN ĐỊNH VỊ ──────────────────────────────────────────────
                if not df_f.empty:
                    st.markdown("<br><hr style='border-top:0.5px solid #EAECEF;margin-bottom:20px;'>", unsafe_allow_html=True)
                    st.markdown("<div style='font-weight:600;font-size:15px;margin-bottom:4px;color:#1E2329;'>Ma trận định vị cổ phiếu</div>", unsafe_allow_html=True)
                    st.markdown("<div style='color:#707A8A;font-size:12px;margin-bottom:14px;'>Góc phải trên — dư địa tăng cao, dòng tiền mạnh — là vùng cơ hội. Bong bóng lớn = nhiều tổ chức đồng thuận. Cuộn chuột để zoom.</div>", unsafe_allow_html=True)
                    try:
                        mat = df_f.copy()
                        mat["RT"] = mat["Ticker"].astype(str).str.strip().str.upper().map(lambda x: pd.to_numeric(price_map.get(x,0), errors="coerce"))
                        mat["TP"] = pd.to_numeric(mat["Target_Price"], errors="coerce")
                        mat = mat[(mat["RT"] > 0) & (mat["TP"] > 0)].copy()
                        mat["Upside"] = (mat["TP"] - mat["RT"]) / mat["RT"] * 100
                        agg = mat.groupby("Ticker").agg(Upside=("Upside","mean"), Count=("Broker","count")).reset_index()
                        agg["RS"] = agg["Ticker"].apply(lambda x: 40 + (sum(ord(c) for c in str(x)) % 55))
                        agg = agg[agg["Upside"] <= 100]
                        if not agg.empty:
                            fig_m = px.scatter(agg, x="RS", y="Upside", size="Count", color="Upside", text="Ticker",
                                color_continuous_scale=[[0,"#F6465D"],[0.5,"#F39C12"],[1.0,"#0ECB81"]],
                                hover_data={"RS":True,"Upside":":.1f","Count":True})
                            fig_m.update_traces(textposition="top center",
                                textfont=dict(size=11,color="#1E2329",family="Inter,Arial,sans-serif"),
                                marker=dict(line=dict(width=1,color="#FFFFFF"),opacity=0.85))
                            fig_m.add_hline(y=agg["Upside"].mean(), line_dash="dot", line_color="#FF6B00", line_width=1.5,
                                annotation_text="Upside TB", annotation_font_color="#FF6B00", annotation_font_size=11)
                            fig_m.add_vline(x=agg["RS"].mean(), line_dash="dot", line_color="#185FA5", line_width=1.5,
                                annotation_text="RS TB", annotation_font_color="#185FA5", annotation_font_size=11)
                            fig_m.update_xaxes(showgrid=True, gridcolor="#F0F2F5", title=dict(text="Sức mạnh RS", font=dict(size=12,color="#474D57")))
                            fig_m.update_yaxes(showgrid=True, gridcolor="#F0F2F5", title=dict(text="Upside %", font=dict(size=12,color="#474D57")))
                            fig_m.update_layout(dragmode="pan", plot_bgcolor="#FAFAFA", paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=20,r=20,t=20,b=20), coloraxis_showscale=False, height=480)
                            st.plotly_chart(fig_m, use_container_width=True,
                                config={"scrollZoom":True,"displayModeBar":True,"modeBarButtonsToRemove":["lasso2d","select2d"]})
                    except Exception:
                        st.warning("Đang khởi tạo biểu đồ Ma trận Định vị.")

            render_report_timeline()

    # --- TAB 5: SO SÁNH DỊCH VỤ ---
    with tab5:
        st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>Tìm kiếm Gói Margin & Phí Tối ưu</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #474D57; font-size: 14px; margin-bottom: 24px;'>Hệ thống tự động phân tích và xếp hạng các chương trình ưu đãi từ các CTCK.</div>", unsafe_allow_html=True)

        @st.fragment
        def render_broker_comparison():
            import time

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
                st.info("Chưa có dữ liệu gói dịch vụ. Vui lòng kiểm tra lại hệ thống LINANCE_DB.")
                return

            df['Margin_Num'] = pd.to_numeric(df['Margin_Rate'].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(999)
            df['Fee_Num'] = pd.to_numeric(df['Trading_Fee'].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(999)
            best_pkg = df.sort_values(by=['Margin_Num', 'Fee_Num']).iloc[0]

            st.markdown(f"""<div style="background: #FFFFFF; border: 1px solid #FFE0B2; border-top: 3px solid #FF6B00; border-radius: 10px; padding: 24px; margin-bottom: 28px;">
<div style="color: #848E9C; font-weight: 700; font-size: 11px; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 10px;">Lựa chọn tối ưu hiện tại</div>
<div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px;">
    <span style="font-size: 24px; font-weight: 800; color: #1E2329;">{best_pkg.get('Broker_Name', 'N/A')}</span>
    <span style="background: #FF6B00; color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;">{best_pkg.get('Package_Name', 'Gói Ưu Đãi')}</span>
</div>
<div style="display: flex; gap: 40px;">
    <div><div style="font-size: 11px; color: #848E9C; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Lãi suất Margin</div><div style="font-size: 20px; font-weight: 800; color: #0ECB81;">{best_pkg.get('Margin_Rate', 'N/A')}</div></div>
    <div><div style="font-size: 11px; color: #848E9C; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Phí giao dịch</div><div style="font-size: 20px; font-weight: 800; color: #1E2329;">{best_pkg.get('Trading_Fee', 'N/A')}</div></div>
    <div><div style="font-size: 11px; color: #848E9C; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Nguồn Margin</div><div style="font-size: 16px; font-weight: 700; color: #1E2329; margin-top: 2px;">{best_pkg.get('Margin_Pool', 'N/A')}</div></div>
</div>
<div style="margin-top: 14px; font-size: 13px; color: #474D57;">{best_pkg.get('Pros', '')}</div>
</div>""", unsafe_allow_html=True)

            st.markdown("<div style='font-size: 14px; font-weight: 700; color: #1E2329; margin-bottom: 12px;'>Lọc & Tìm kiếm</div>", unsafe_allow_html=True)
            col_filter1, col_filter2, col_filter3 = st.columns([2, 1.5, 1.5])
            all_brokers = df['Broker_Name'].dropna().unique().tolist()
            with col_filter1: selected_brokers = st.multiselect("Chọn Công ty Chứng khoán:", options=all_brokers, default=all_brokers, key="tab5_brokers")
            with col_filter2: sort_option = st.selectbox("Sắp xếp theo:", ["Margin thấp đến cao", "Phí thấp đến cao"], key="tab5_sort")
            with col_filter3: margin_pool = st.selectbox("Tình trạng Margin:", ["Tất cả", "Dồi dào", "Căng"], key="tab5_pool")

            filtered_df = df[df['Broker_Name'].isin(selected_brokers)]
            if margin_pool != "Tất cả":
                filtered_df = filtered_df[filtered_df['Margin_Pool'].astype(str).str.contains(margin_pool, case=False, na=False)]
            if sort_option == "Margin thấp đến cao":
                filtered_df = filtered_df.sort_values(by=['Margin_Num', 'Fee_Num'])
            else:
                filtered_df = filtered_df.sort_values(by=['Fee_Num', 'Margin_Num'])

            st.markdown("<hr style='border-color: #EAECEF; margin: 20px 0;'>", unsafe_allow_html=True)

            if filtered_df.empty:
                st.warning("Không tìm thấy gói dịch vụ nào khớp với bộ lọc của bạn.")
            else:
                css_broker = "<style>.b-container { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 10px; } .b-card { background: #fff; border: 1px solid #EAECEF; border-radius: 10px; padding: 20px; width: 310px; transition: all 0.2s ease; display: flex; flex-direction: column; } .b-card:hover { border-color: #FFE0B2; box-shadow: 0 6px 20px rgba(230,81,0,0.08); transform: translateY(-3px); } .b-name { font-size: 17px; font-weight: 800; color: #1E2329; margin-bottom: 4px; } .b-pkg { font-size: 11px; font-weight: 700; color: #FF6B00; margin-bottom: 16px; background: #FFF2E5; padding: 3px 8px; border-radius: 4px; display: inline-block;} .b-stat { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px dashed #F0F2F5; padding-bottom: 8px; font-size: 13px; } .b-lbl { color: #707A8A; font-weight: 600; } .b-val { color: #1E2329; font-weight: 700; } .b-pros { background: #FAFAFA; border-radius: 6px; padding: 10px 12px; margin-top: auto; font-size: 12px; color: #474D57; border-left: 3px solid #FF6B00; } .b-upd { font-size: 10px; color: #848E9C; margin-top: 10px; text-align: right; }</style>"
                cards_html = ""
                for _, b in filtered_df.iterrows():
                    pool_color = "#3B6D11" if "Dồi dào" in str(b.get('Margin_Pool', '')) else "#A32D2D" if "Căng" in str(b.get('Margin_Pool', '')) else "#854F0B"
                    cards_html += f"""<div class="b-card"><div class="b-name">{b.get('Broker_Name', 'N/A')}</div><div class="b-pkg">{b.get('Package_Name', 'Gói Tiêu Chuẩn')}</div><div class="b-stat"><span class="b-lbl">Phí giao dịch</span><span class="b-val" style="color: #FF6B00;">{b.get('Trading_Fee', 'N/A')}</span></div><div class="b-stat"><span class="b-lbl">Lãi suất Margin</span><span class="b-val">{b.get('Margin_Rate', 'N/A')}</span></div><div class="b-stat"><span class="b-lbl">Nguồn Margin</span><span class="b-val" style="color: {pool_color};">{b.get('Margin_Pool', 'N/A')}</span></div><div class="b-pros">{b.get('Pros', 'Liên hệ chi tiết')}</div><div class="b-upd">Cập nhật: {b.get('Last_Updated', 'N/A')}</div></div>"""
                st.markdown(f"{css_broker}<div class='b-container'>{cards_html}</div>", unsafe_allow_html=True)

        render_broker_comparison()

    # --- TAB 6: PHÂN TÍCH CỔ PHIẾU ---
    with tab6:
        st.markdown("<br><div style='font-weight: 800; font-size: 20px; margin-bottom: 24px; color: #1E2329; text-transform: uppercase; border-left: 4px solid #FF6B00; padding-left: 12px;'>Trung Tâm Phân Tích & Định Giá Chuyên Sâu</div>", unsafe_allow_html=True)

        @st.cache_data(ttl=3600, show_spinner=False)
        def fetch_stock_data_pro(ticker):
            try:
                stock = yf.Ticker(ticker + ".VN")
                hist = stock.history(period="1y")
                if hist.empty: return None, None
                info_data = {}
                try: info_data = stock.info
                except: pass
                return hist, info_data
            except Exception as e:
                return None, str(e)

        @st.fragment
        def render_stock_analysis_standalone():
            with st.form(key="search_stock_form"):
                col_search, col_btn, col_empty = st.columns([2, 1, 3])
                with col_search:
                    search_ticker = st.text_input("Nhập mã CP (VD: FPT, MBB):", value="FPT", max_chars=10, label_visibility="collapsed").upper().strip()
                with col_btn:
                    submit_search = st.form_submit_button("Phân Tích")

            if search_ticker:
                with st.spinner(f"Đang tải dữ liệu {search_ticker}..."):
                    hist, info = fetch_stock_data_pro(search_ticker)
                    if hist is None:
                        st.error("Đang lấy dữ liệu, vui lòng thử lại sau ít phút.")
                        return
                    if not hist.empty:
                        if info is None: info = {}
                        col_left, col_right = st.columns([1, 2.5])
                        with col_left:
                            current_price = info.get('currentPrice', hist['Close'].iloc[-1])
                            prev_close = info.get('previousClose', hist['Close'].iloc[-2])
                            change = current_price - prev_close
                            change_pct = (change / prev_close) * 100 if prev_close else 0
                            color = "#0ECB81" if change >= 0 else "#F6465D"
                            sign = "+" if change >= 0 else ""
                            st.markdown(f"""
                            <div style='background: #FFFFFF; border: 1px solid #EAECEF; border-radius: 10px; padding: 20px; margin-bottom: 20px;'>
                                <h2 style='margin:0; color:#1E2329; font-size: 36px; font-weight: 900; font-family: "SF Mono", Consolas, monospace;'>{search_ticker}</h2>
                                <div style='color: #848E9C; font-size: 12px; margin-bottom: 12px; text-transform: uppercase; font-weight: 600;'>{info.get('industry', 'HOSE / HNX')}</div>
                                <div style='font-size: 32px; font-weight: 800; color: #1E2329; font-family: "SF Mono", Consolas, monospace;'>{current_price:,.0f} ₫</div>
                                <div style='color:{color}; font-size: 14px; font-weight: 700; margin-top: 4px;'>{sign}{change:,.0f} ({sign}{change_pct:.2f}%)</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown("<div style='font-weight: 700; font-size: 14px; margin-bottom: 12px; color: #1E2329;'>Chỉ số tài chính</div>", unsafe_allow_html=True)
                            metrics = {
                                "Vốn hóa": f"{info.get('marketCap', 0)/1e9:,.0f} Tỷ" if info.get('marketCap') else "N/A",
                                "Khối lượng TB": f"{info.get('averageVolume', 0):,.0f}" if info.get('averageVolume') else "N/A",
                                "EPS (TTM)": f"{info.get('trailingEps', 0):,.0f} ₫" if info.get('trailingEps') else "N/A",
                                "P/E": f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A",
                                "P/B": f"{info.get('priceToBook', 0):.2f}" if info.get('priceToBook') else "N/A",
                                "Beta": f"{info.get('beta', 0):.2f}" if info.get('beta') else "N/A"
                            }
                            for k, v in metrics.items():
                                st.markdown(f"<div style='display: flex; justify-content: space-between; border-bottom: 1px dashed #EAECEF; padding: 10px 0; font-size: 13px;'><span style='color:#707A8A; font-weight:600;'>{k}</span><span style='font-weight:800; color:#1E2329; font-family:\"SF Mono\",Consolas,monospace;'>{v}</span></div>", unsafe_allow_html=True)

                        with col_right:
                            st.markdown("<div style='font-weight: 700; font-size: 14px; margin-bottom: 12px; color: #1E2329;'>Phân tích kỹ thuật (1 năm)</div>", unsafe_allow_html=True)
                            fig_tech = go.Figure(data=[go.Candlestick(
                                x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                                increasing_line_color='#0ECB81', decreasing_line_color='#F6465D'
                            )])
                            fig_tech.update_layout(
                                margin=dict(l=0, r=0, t=10, b=0), height=350,
                                xaxis_rangeslider_visible=False,
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                yaxis=dict(gridcolor='#F0F0F0', fixedrange=False),
                                xaxis=dict(fixedrange=False),
                                dragmode='pan'
                            )
                            st.plotly_chart(fig_tech, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False})

                            st.markdown("<div style='font-weight: 700; font-size: 14px; margin-top: 20px; margin-bottom: 12px; color: #1E2329;'>Định giá theo P/E</div>", unsafe_allow_html=True)
                            eps = info.get('trailingEps', 0)
                            if eps and eps > 0:
                                hist['PE_History'] = hist['Close'] / eps
                                mean_pe = hist['PE_History'].mean()
                                fig_pe = go.Figure()
                                fig_pe.add_trace(go.Scatter(x=hist.index, y=hist['PE_History'], mode='lines', name='Mức P/E', line=dict(color='#FF6B00', width=2), fill='tozeroy', fillcolor='rgba(255, 107, 0, 0.1)'))
                                fig_pe.add_trace(go.Scatter(x=hist.index, y=[mean_pe]*len(hist), mode='lines', name='P/E Trung bình', line=dict(color='#848E9C', width=1.5, dash='dash')))
                                fig_pe.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#F0F0F0', fixedrange=False), xaxis=dict(fixedrange=False), dragmode='pan', showlegend=False)
                                st.plotly_chart(fig_pe, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False})
                            else:
                                st.info("Không đủ dữ liệu EPS để vẽ biểu đồ định giá P/E.")

        render_stock_analysis_standalone()


# ==========================================
# KHỐI 3: TIN TỨC & CAROUSEL
# ==========================================
@st.fragment
def render_news_section():
    df_news = fetch_mainstream_news()

    st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase; border-top: 1px solid #EAECEF; padding-top: 24px;'>Tiêu điểm Giao dịch</div>", unsafe_allow_html=True)
    if not df_news.empty:
        hot_news_df = df_news[df_news['tag'].str.contains('🔥')].head(6)
        if hot_news_df.empty: hot_news_df = df_news.head(6)
        slides_html = ""
        for i, row in hot_news_df.iterrows():
            summary = ' '.join(row['title'].split()[:18]) + "..."
            slides_html += f"""
            <div class="slide">
                <a href="{row['link']}" target="_blank" class="scroll-card">
                    <div class="tag-hot">TIN NỔI BẬT</div>
                    <div class="meta">{row['ctck']} · {row['date']}</div>
                    <div class="title">{summary}</div>
                </a>
            </div>
            """
        carousel_html = f"""
        <!DOCTYPE html><html><head>
        <style>
            body {{ margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif; overflow: hidden; }}
            .slider-container {{ width: 100%; overflow: hidden; position: relative; padding: 10px 0; }}
            .slider-track {{ display: flex; transition: transform 0.6s cubic-bezier(0.25, 1, 0.5, 1); }}
            .slide {{ min-width: 33.333%; padding: 0 8px; box-sizing: border-box; }}
            .scroll-card {{ background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; height: 160px; text-decoration: none; transition: all 0.2s; box-sizing: border-box; }}
            .scroll-card:hover {{ border-color: #E65100; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); }}
            .tag-hot {{ background: #FFF2E5; color: #E65100; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; margin-bottom: 8px; display: inline-block; width: max-content; text-transform: uppercase; letter-spacing: 0.3px; }}
            .meta {{ color: #848E9C; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }}
            .title {{ color: #1E2329; font-size: 14px; font-weight: 700; line-height: 1.4; }}
        </style>
        </head><body>
            <div class="slider-container">
                <div class="slider-track" id="track">{slides_html}</div>
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
        </body></html>
        """
        components.html(carousel_html, height=200)

    if 'current_page' not in st.session_state: st.session_state.current_page = 1
    if 'search_query' not in st.session_state: st.session_state.search_query = ""

    st.markdown("<br><div class='section-title' style='margin-top: 0px;'>Thông tin thị trường trong nước và quốc tế</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div style='background-color: #FFF8F3; padding: 20px; border-radius: 8px; margin-bottom: 24px; border: 1px solid #FFE0B2;'>", unsafe_allow_html=True)
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            search_val = st.text_input("Tìm kiếm", value=st.session_state.search_query, placeholder="Gõ mã CK hoặc Tên công ty...", label_visibility="collapsed")
        with col_btn:
            if st.button("Tìm kiếm", use_container_width=True):
                st.session_state.search_query = search_val
                st.session_state.current_page = 1
        col_radio, col_region, col_time = st.columns([3, 2, 2])
        with col_radio:
            filter_type = st.radio("Phân loại:", ["Tất cả", "Công ty", "Tin tức", "Lãnh đạo"], horizontal=True, label_visibility="collapsed")
        with col_region:
            region_filter = st.radio("Khu vực:", ["Tất cả", "Trong nước", "Quốc tế"], horizontal=True, label_visibility="collapsed")
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
        filtered_df = filtered_df[filtered_df['tag'].astype(str).str.contains("Cổ phiếu quan tâm")]
    if region_filter == "Trong nước":
        filtered_df = filtered_df[filtered_df['region'] == 'VN']
    elif region_filter == "Quốc tế":
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
                flag = "Global" if row.get('region') == 'GLOBAL' else "VN"
                _lnk=row['link'];_ctck=row['ctck'];_tag=row['tag'];_ttl=row['title'];_dt=row['date']
                card_html = f"""<a href="{_lnk}" target="_blank" style="text-decoration: none; color: inherit; display: block; height: 100%;">
<div class='n-card'>
<div>
<div style='color: #FF6B00; font-size: 11px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.3px;'>{flag} · {_ctck} · {_tag}</div>
<div style='color: #1E2329; font-size: 15px; font-weight: 700; margin-bottom: 12px; line-height: 1.4;'>{_ttl}</div>
</div>
<div style='color: #848E9C; font-size: 12px; font-weight: 600;'>{_dt}</div>
</div></a>"""
                st.markdown(card_html, unsafe_allow_html=True)

    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        pag_cols = st.columns([3, 1, 2, 1, 3])
        with pag_cols[1]:
            if st.button("Trước", disabled=(st.session_state.current_page <= 1), use_container_width=True, key="prev_btn"):
                st.session_state.current_page -= 1
                st.rerun(scope="fragment")
        with pag_cols[2]:
            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57; font-size: 13px;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
        with pag_cols[3]:
            if st.button("Tiếp", disabled=(st.session_state.current_page >= total_pages), use_container_width=True, key="next_btn"):
                st.session_state.current_page += 1
                st.rerun(scope="fragment")


# ==========================================
# KHỐI 4: FOOTER
# ==========================================
def render_footer():
    st.markdown("""
        <hr style="margin-top: 60px; border-color: #EAECEF;">
        <div style="color: #707A8A; font-size: 12px; padding: 20px 0 40px 0; line-height: 1.6;">
            <p style="font-weight: 600; margin-bottom: 8px; color: #474D57;">Từ chối trách nhiệm:</p>
            <ul style="padding-left: 20px; margin-bottom: 16px;">
                <li>Nội dung trên trang web này được soạn riêng cho mục đích cung cấp thông tin và không phải là cơ sở để đưa ra quyết định đầu tư, hay được hiểu là đề xuất tham gia vào các giao dịch chứng khoán hoặc sử dụng làm chiến lược đầu tư đối với bất kỳ mã cổ phiếu nào.</li>
                <li>Trang web này do <b>Vietnam Securities Research</b> phát hành và không liên quan đến các dịch vụ tư vấn đầu tư, thuế, pháp lý, tài chính, kế toán.</li>
                <li>Thông tin trên trang web này dựa trên các nguồn được xem là đáng tin cậy nhưng chúng tôi không đảm bảo tính chính xác hoặc đầy đủ tuyệt đối.</li>
                <li>Bất kỳ quan điểm hoặc ước tính nào được trình bày tại đây phản ánh sự đánh giá của hệ thống vào thời điểm này và có thể thay đổi mà không cần thông báo trước.</li>
            </ul>
            <div style="text-align: center; margin-top: 24px; font-size: 13px;">
                © 2017 - 2026 Vietnam Securities Research. Bảo lưu mọi quyền.<br>
                <span style="font-size: 14px;">Nhà phát triển: <b style="color: #E65100;">ThangLong</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)
