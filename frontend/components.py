import math
import base64
import requests
import pandas as pd
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px

# --- IMPORT CÁC HÀM TỪ BACKEND ---
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
# KHỐI 1: HEADER
# ==========================================
def get_base64_of_image(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return ""

def render_header():
    logo_base64 = get_base64_of_image("assets/logo.png")
    if logo_base64:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 24px; margin-top: 10px;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 100px; object-fit: contain;">
            <div>
                <h1 style='font-size: 36px; color: #1E2329; font-weight: 800; margin: 0; padding: 0; letter-spacing: 1px;'>LINANCE</h1>
                <p style='color: #474D57; font-size: 16px; margin-top: 4px; margin-bottom: 0;'>Vietnam Securities Research - Phân tích cấp tổ chức</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px; margin-top: 10px;'>LINANCE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 32px;'>Vietnam Securities Research - Phân tích cấp tổ chức</p>", unsafe_allow_html=True)

# ==========================================
# ==========================================
# KHỐI 1.5: HÀM KÉO DỮ LIỆU BẢN ĐỒ NHIỆT (TAB 2)
# ==========================================
import yfinance as yf
import plotly.express as px
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300, show_spinner=False)
def get_market_heatmap_data():
    sectors = {
        'Ngân hàng': ['VCB', 'BID', 'CTG', 'MBB', 'TCB', 'VPB', 'ACB', 'STB', 'SHB', 'HDB', 'TPB', 'MSB', 'LPB'],
        'Bất động sản': ['VHM', 'VIC', 'VRE', 'NVL', 'DIG', 'DXG', 'KDH', 'NLG', 'PDR', 'CEO'],
        'Chứng khoán': ['SSI', 'VND', 'VCI', 'HCM', 'SHS', 'MBS', 'FTS'],
        'Thép & Xây dựng': ['HPG', 'HSG', 'NKG', 'VCG', 'PC1', 'CTD'],
        'Bán lẻ & Tiêu dùng': ['MWG', 'PNJ', 'FRT', 'VNM', 'MSN', 'SAB', 'DGW'],
        'Công nghệ & Năng lượng': ['FPT', 'GAS', 'PLX', 'POW', 'BSR', 'DGC']
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

# ĐÃ ĐƯỢC BỌC VÀO HÀM ĐỂ KHÔNG BỊ LỖI IMPORT
def render_tab2_heatmap():
    st.markdown("<br><div style='font-size: 20px; font-weight: 800; color: #1E2329; margin-bottom: 8px; text-transform: uppercase;'>🗺️ Bản đồ Nhiệt Dòng tiền (Market Heatmap)</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #474D57; font-size: 14px; margin-bottom: 24px;'>Kích thước ô vuông thể hiện Khối lượng giao dịch. Màu sắc thể hiện mức độ Tăng (Xanh) / Giảm (Đỏ).</div>", unsafe_allow_html=True)

    with st.spinner("Đang quét tín hiệu dòng tiền từ Yahoo Finance..."):
        df_heat = get_market_heatmap_data()

        if not df_heat.empty:
            df_heat['Nhãn hiển thị'] = df_heat['Mã CK'] + "<br><span style='font-size:16px; font-weight:800;'>" + df_heat['Biến động (%)'].round(2).astype(str) + "%</span>"

            fig = px.treemap(
                df_heat,
                path=[px.Constant("Thị Trường VN"), 'Ngành', 'Nhãn hiển thị'],
                values='Khối lượng',
                color='Biến động (%)',
                color_continuous_scale=['#F6465D', '#F9F9FA', '#0ECB81'], 
                color_continuous_midpoint=0,
                hover_data={'Khối lượng': ':.2s', 'Giá (VNĐ)': ':,.0f'}
            )
            
            fig.update_layout(
                margin=dict(t=20, l=0, r=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Segoe UI", size=15, color="#1E2329")
            )
            
            fig.update_traces(
                textinfo="label",
                textfont_color="black",
                hovertemplate="<b>%{label}</b><br>Khối lượng: %{value}<br>Biến động: %{color:.2f}%<extra></extra>"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Yahoo Finance đang cập nhật dữ liệu. Vui lòng thử lại sau!")

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

    tab1, tab2, tab3, tab4 = st.tabs(["TỔNG QUAN THỊ TRƯỜNG", "DỮ LIỆU GIAO DỊCH", "PHÂN TÍCH AI", "BÁO CÁO TỔ CHỨC"])

    # --- TAB 1: TỔNG QUAN THỊ TRƯỜNG ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        groups_items = list(groups.items())
        css_binance = """<style>
.b-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px 16px; min-height: 240px; transition: all 0.2s ease; }
.b-card:hover { border-color: #E65100; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); }
.b-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #F0F2F5; padding-bottom: 12px;}
.b-title { font-weight: 700; font-size: 14px; color: #1E2329; text-transform: uppercase; }
.b-more { font-size: 12px; color: #707A8A; text-decoration: none; font-weight: 600; transition: color 0.2s;}
.b-more:hover { color: #E65100; }
.b-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.b-row:last-child { margin-bottom: 0; }
.b-name { font-weight: 600; font-size: 14px; color: #1E2329; width: 35%; }
.b-price { font-size: 14px; color: #1E2329; text-align: right; width: 35%; font-family: 'SF Mono', Consolas, monospace; font-weight: 600;}
.b-change { font-size: 14px; font-weight: 600; text-align: right; width: 30%; }
.c-up { color: #0ECB81; } 
.c-down { color: #F6465D; } 
</style>"""
        
        # Hàng 1
        cols1 = st.columns(3)
        for col, (group_name, tickers) in zip(cols1, groups_items[:3]):
            with col:
                rows_html = ""
                for t in tickers:
                    data = market_data.get(t, {"name": t, "price": "N/A", "change": 0})
                    color_class = "c-up" if data['change'] >= 0 else "c-down"
                    sign = "+" if data['change'] > 0 else ""
                    rows_html += f"""<div class="b-row"><div class="b-name">{data['name']}</div><div class="b-price">{data['price']}</div><div class="b-change {color_class}">{sign}{data['change']:.2f}%</div></div>"""
                card_html = f"""<div class="b-card"><div class="b-header"><div class="b-title">{group_name}</div><a href="#" class="b-more">Chi tiết ></a></div>{rows_html}</div>"""
                st.markdown(f"{css_binance}{card_html}", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

        # Hàng 2
        cols2 = st.columns(3)
        for col, (group_name, tickers) in zip(cols2, groups_items[3:]):
            with col:
                rows_html = ""
                for t in tickers:
                    data = market_data.get(t, {"name": t, "price": "N/A", "change": 0})
                    color_class = "c-up" if data['change'] >= 0 else "c-down"
                    sign = "+" if data['change'] > 0 else ""
                    rows_html += f"""<div class="b-row"><div class="b-name">{data['name']}</div><div class="b-price">{data['price']}</div><div class="b-change {color_class}">{sign}{data['change']:.2f}%</div></div>"""
                card_html = f"""<div class="b-card"><div class="b-header"><div class="b-title">{group_name}</div><a href="#" class="b-more">Chi tiết ></a></div>{rows_html}</div>"""
                st.markdown(f"{css_binance}{card_html}", unsafe_allow_html=True)

    # --- TAB 2: DỮ LIỆU GIAO DỊCH ---
    with tab2:
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

    # --- TAB 4: BÁO CÁO TỔ CHỨC ---
    with tab4:
        st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase;'>Trung tâm Lưu trữ & Phân tích Báo cáo</div>", unsafe_allow_html=True)
        with st.spinner("Đang truy xuất hệ thống báo cáo từ các Công ty Chứng khoán..."):
            reports_data = fetch_cafef_reports()
            
        if not reports_data:
            st.info("Hệ thống hiện chưa lấy được báo cáo mới. Vui lòng thử lại sau.")
        else:
            col_list, col_ai = st.columns([1.5, 1])
            with col_list:
                st.markdown("<div style='font-weight: 700; font-size: 18px; margin-bottom: 16px; color: #1E2329;'>Báo cáo Phát hành Gần đây</div>", unsafe_allow_html=True)
                for r in reports_data:
                    ticker_badge = f"<span style='background-color: #FFF2E5; color: #E65100; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; margin-right: 8px;'>{r['ticker']}</span>"
                    st.markdown(f"""
                    <div style='background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; margin-bottom: 12px; transition: all 0.2s ease;'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;'>
                            <div style='font-size: 15px; font-weight: 600; color: #1E2329; line-height: 1.4;'>{ticker_badge} {r['title']}</div>
                        </div>
                        <div style='display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #848E9C;'>
                            <span>🏢 Nguồn: {r['source']} | 🕒 {r['date']}</span>
                            <a href='{r['link']}' target='_blank' style='color: #0052FF; font-weight: 600; text-decoration: none;'>Đọc báo cáo ↗</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_ai:
                ai_data = generate_ai_report_scoring(reports_data)
                st.markdown("<div style='font-weight: 700; font-size: 18px; margin-bottom: 16px; color: #1E2329;'>AI Consensus Scoring</div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 16px;'>
                    <div style='font-size: 14px; color: #707A8A; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;'>Chỉ số đồng thuận Tổ chức</div>
                    <div style='font-size: 48px; font-weight: 800; color: {ai_data['color']}; line-height: 1; margin-bottom: 8px; font-family: "SF Mono", Consolas, monospace;'>{ai_data['score']}</div>
                    <div style='display: inline-block; background-color: {ai_data['color']}20; color: {ai_data['color']}; padding: 6px 12px; border-radius: 4px; font-size: 13px; font-weight: 700;'>{ai_data['consensus']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                buy_badges = "".join([f"<span style='background: #0ECB8120; color: #0ECB81; padding: 4px 8px; border-radius: 4px; margin-right: 6px; font-weight: 700; font-size: 12px;'>{t}</span>" for t in ai_data['top_buy']]) if ai_data['top_buy'] else "<span style='color:#848E9C; font-size:13px;'>Không có</span>"
                sell_badges = "".join([f"<span style='background: #F6465D20; color: #F6465D; padding: 4px 8px; border-radius: 4px; margin-right: 6px; font-weight: 700; font-size: 12px;'>{t}</span>" for t in ai_data['top_sell']]) if ai_data['top_sell'] else "<span style='color:#848E9C; font-size:13px;'>Không có</span>"

                st.markdown(f"""
                <div style='background: #FAFAFA; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #EAECEF; padding-bottom: 12px; margin-bottom: 12px;'>
                        <span style='color: #474D57; font-size: 14px; font-weight: 600;'>🎯 Độ tin cậy AI (Backtest)</span>
                        <span style='color: #1E2329; font-size: 16px; font-weight: 700;'>{ai_data['confidence']}%</span>
                    </div>
                    <div style='margin-bottom: 16px;'>
                        <div style='font-size: 12px; color: #848E9C; margin-bottom: 8px; text-transform: uppercase; font-weight: 600;'>🔥 Top Tổ chức Gom Hàng</div>
                        <div>{buy_badges}</div>
                    </div>
                    <div>
                        <div style='font-size: 12px; color: #848E9C; margin-bottom: 8px; text-transform: uppercase; font-weight: 600;'>❄️ Top Tổ chức Xả Hàng</div>
                        <div>{sell_badges}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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
