import math
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from backend.official_news import fetch_mainstream_news
from backend.market_data import fetch_realtime_data
from datetime import datetime
from backend.ai_analysis import analyze_news_sentiment, generate_technical_alerts

# --- KHỐI 0: ĐỒNG HỒ REAL-TIME (TOP BAR) ---
def render_topbar_clock():
    # Nhúng JS để đồng hồ tự chạy từng giây mà không cần F5 tải lại trang
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
    # Chiều cao 32px vừa vặn làm một dải ruy băng mỏng ở trên cùng
    components.html(clock_html, height=32)

# --- KHỐI 1: HEADER ---
def render_header():
    st.markdown("<h1 style='font-size: 32px; color: #1E2329; font-weight: 700; margin-bottom: 8px; margin-top: 10px;'>Vietnam Securities Research</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #474D57; font-size: 16px; margin-bottom: 32px;'>Cung cấp phân tích cấp tổ chức, thông tin chuyên sâu và biểu phí khách quan cho nhà đầu tư.</p>", unsafe_allow_html=True)

# --- KHỐI 2: TỔNG QUAN, BIỂU ĐỒ & PHÂN TÍCH AI (NÂNG CẤP TABS) ---
def render_hero_section():
    from backend.market_data import fetch_realtime_data # Đảm bảo đã import hàm lấy giá
    market_data, groups = fetch_realtime_data()

    # CSS Ép kiểu Tabs chuyên nghiệp (Không có viền xanh mặc định)
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

    # Khởi tạo 3 Tab chính
    tab1, tab2, tab3 = st.tabs(["TỔNG QUAN THỊ TRƯỜNG", "DỮ LIỆU GIAO DỊCH", "PHÂN TÍCH AI"])

    # --- TAB 1: TỔNG QUAN THỊ TRƯỜNG ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(4)
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
        for col, (group_name, tickers) in zip(cols, groups.items()):
            with col:
                rows_html = ""
                for t in tickers:
                    data = market_data.get(t, {"name": t, "price": "N/A", "change": 0})
                    color_class = "c-up" if data['change'] >= 0 else "c-down"
                    rows_html += f"""<div class="b-row"><div class="b-name">{data['name']}</div><div class="b-price">{data['price']}</div><div class="b-change {color_class}">{data['change']:.2f}%</div></div>"""
                card_html = f"""<div class="b-card"><div class="b-header"><div class="b-title">{group_name}</div><a href="#" class="b-more">Chi tiết ></a></div>{rows_html}</div>"""
                st.markdown(f"{css_binance}{card_html}", unsafe_allow_html=True)

    # --- TAB 2: DỮ LIỆU GIAO DỊCH ---
    with tab2:
        st.markdown("<br><div style='color: #707A8A; text-align: center; padding: 40px; font-weight: 600;'>MODULE BIỂU ĐỒ KỸ THUẬT ĐANG TRONG QUÁ TRÌNH TÍCH HỢP.</div>", unsafe_allow_html=True)

    # --- TAB 3: PHÂN TÍCH AI ---
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        # 1. KÉO CODE AI VÀO (Nhớ import thêm get_f319_sentiment trên cùng file nhé)
        from backend.ai_analysis import analyze_news_sentiment, generate_technical_alerts, get_f319_sentiment
        market_sentiment_score, top_bullish_news, top_bearish_news = analyze_news_sentiment()
        technical_alerts = generate_technical_alerts()
        f319_data = get_f319_sentiment() # Lấy data F319

        # --- KHỐI BÁO ĐỘNG KỸ THUẬT & TÂM LÝ TIN TỨC (GIỮ NGUYÊN NHƯ CŨ) ---
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

        st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase;'>Báo động Kỹ thuật (Technical Alerts)</div>", unsafe_allow_html=True)
        if technical_alerts:
            css_ai_alerts = """<style>.a-card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px;} .a-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; text-align: center; transition: all 0.2s ease;} .a-card:hover { border-color: #E65100; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08);} .a-ticker { font-size: 16px; font-weight: 700; color: #1E2329; margin-bottom: 12px;} .a-type { font-size: 11px; font-weight: 700; padding: 6px 8px; border-radius: 4px; color: #fff; text-transform: uppercase; display: inline-block; margin-bottom: 12px; width: 100%; box-sizing: border-box;} .a-details { font-size: 12px; color: #707A8A; line-height: 1.5; font-weight: 500;}</style>"""
            cards_html = "".join([f"""<div class="a-card"><div class="a-ticker">{a['ticker']}</div><div class="a-type" style="background-color: {a['color']};">{a['type']}</div><div class="a-details">{a['details']}</div></div>""" for a in technical_alerts])
            st.markdown(f"{css_ai_alerts}<div class='a-card-grid'>{cards_html}</div>", unsafe_allow_html=True)

        # --- KHỐI MỚI: RADAR MẠNG XÃ HỘI (F319) CHUẨN UI BINANCE ---
        st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase; border-top: 1px solid #EAECEF; padding-top: 32px;'>Cộng Đồng Nhà Đầu Tư (Social Sentiment)</div>", unsafe_allow_html=True)
        
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
            # Code HTML được ÉP SÁT LỀ TRÁI chống lỗi Markdown
            stats_html = f"""<div class="soc-card">
<div class="soc-title">Dữ liệu thảo luận (24h)</div>
<div class="soc-metrics">
<div class="soc-m-item"><span class="soc-m-lbl">Tương tác nổi bật</span><span class="soc-m-val">🔥</span></div>
<div class="soc-m-item"><span class="soc-m-lbl">Lượt đề cập (Mentions)</span><span class="soc-m-val">{f319_data['total_mentions']:,}</span></div>
<div class="soc-m-item"><span class="soc-m-lbl">Bài đăng liên quan</span><span class="soc-m-val">{f319_data['total_posts']}</span></div>
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
Dữ liệu được hệ thống AI rà soát và tổng hợp tự động từ các diễn đàn chứng khoán lớn tại Việt Nam (F319, F247...). Mức độ "Hưng phấn" áp đảo thường xuất hiện tại các vùng đỉnh ngắn hạn.
</div>
</div>"""
            st.markdown(f"{css_social}{stats_html}", unsafe_allow_html=True)

        with col_social_posts:
            posts_html = ""
            for p in f319_data['posts']:
                tag_class = "s-bull-tag" if p['sentiment'] == "Bullish" else "s-bear-tag"
                tag_text = "↑ Mua/Tăng" if p['sentiment'] == "Bullish" else "↓ Bán/Giảm"
                # ÉP SÁT LỀ TRÁI
                posts_html += f"""<div class="soc-post">
<div class="s-author-row">
<div class="s-author"><div class="s-avatar">{p['author'][0]}</div>{p['author']}</div>
<div class="s-time">{p['time']}</div>
</div>
<div class="s-content">{p['content']} <br><span class="{tag_class}">{tag_text}</span></div>
</div>"""
                
            st.markdown(f"""<div class="soc-card" style="height: 400px; overflow-y: auto;">
<div class="soc-title">Bài đăng mới nhất</div>
{posts_html}
</div>""", unsafe_allow_html=True)

    # --- CAROUSEL TIN TỨC NẰM DƯỚI CÙNG ---
    st.markdown("<br><div style='font-size: 14px; font-weight: 700; color: #E65100; margin-bottom: 16px; text-transform: uppercase; border-top: 1px solid #EAECEF; padding-top: 24px;'>Tin Tức Giao Dịch Nổi Bật</div>", unsafe_allow_html=True)
    
    from backend.official_news import fetch_mainstream_news
    df_news = fetch_mainstream_news()
    if not df_news.empty:
        hot_news_df = df_news[df_news['tag'].str.contains('🔥')].head(6)
        if hot_news_df.empty: hot_news_df = df_news.head(6)
        css_car = """<style>
.scroll-container { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 16px; padding-bottom: 12px; scroll-behavior: smooth; }
.scroll-container::-webkit-scrollbar { height: 4px; }
.scroll-container::-webkit-scrollbar-track { background: transparent; border-radius: 4px; }
.scroll-container::-webkit-scrollbar-thumb { background: #E5E7EB; border-radius: 4px; }
.scroll-card { scroll-snap-align: start; min-width: calc(33.333% - 11px); background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; height: 160px; transition: all 0.2s ease; }
.scroll-card:hover { border-color: #E65100; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); }
</style>"""
        cards_html = ""
        for i, row in hot_news_df.iterrows():
            summary = ' '.join(row['title'].split()[:18]) + "..."
            # ÉP SÁT LỀ TRÁI
            cards_html += f"""<a href="{row['link']}" target="_blank" class="scroll-card" style="text-decoration: none; color: inherit;">
<div>
<div style="color: #E65100; font-size: 11px; margin-bottom: 8px; font-weight: 700; text-transform: uppercase;">{row['ctck']} • {row['date']}</div>
<div style="color: #1E2329; font-size: 15px; font-weight: 700; line-height: 1.4;">{summary}</div>
</div>
</a>"""
        st.markdown(f"{css_car}<div class='scroll-container'>{cards_html}</div>", unsafe_allow_html=True)


# --- KHỐI 3: TÌM KIẾM & LƯỚI TIN TỨC ---
def render_news_section():
    df_news = fetch_mainstream_news()
    
    if 'current_page' not in st.session_state: st.session_state.current_page = 1
    if 'search_query' not in st.session_state: st.session_state.search_query = ""

    st.markdown("<br><div class='section-title' style='margin-top: 0px;'>Tra cứu Thông tin Phân Tích</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background-color: #FFF8F3; padding: 20px; border-radius: 8px; margin-bottom: 24px; border: 1px solid #FFE0B2;'>", unsafe_allow_html=True)
        col_input, col_btn = st.columns([5, 1])
        with col_input: search_val = st.text_input("Tìm kiếm", value=st.session_state.search_query, placeholder="Gõ mã CK hoặc Tên công ty...", label_visibility="collapsed")
        with col_btn:
            if st.button("🔍 Tìm kiếm", use_container_width=True):
                st.session_state.search_query = search_val
                st.session_state.current_page = 1
                
        col_radio, col_time = st.columns([4, 2])
        with col_radio: filter_type = st.radio("Phân loại:", ["Tất cả", "Công ty", "Tin tức", "Lãnh đạo", "Cổ phiếu quan tâm"], horizontal=True, label_visibility="collapsed")
        with col_time: time_filter = st.selectbox("Thời gian:", ["Mọi lúc", "Hôm nay", "Tuần này"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    if df_news.empty: return

    filtered_df = df_news.copy()
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(query) | filtered_df['tag'].str.lower().str.contains(query)]
        
    if filter_type == "Tin tức": filtered_df = filtered_df[filtered_df['tag'] == "Tin vĩ mô"]
    elif filter_type == "Cổ phiếu quan tâm": filtered_df = filtered_df[filtered_df['tag'] == "🔥 Cổ phiếu quan tâm"]

    if time_filter == "Hôm nay":
        today_str = datetime.now().strftime("%d/%m/%Y")
        filtered_df = filtered_df[filtered_df['date'].str.contains(today_str)]

    ITEMS_PER_PAGE = 8
    total_items = len(filtered_df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
    if st.session_state.current_page > total_pages: st.session_state.current_page = total_pages
        
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paged_df = filtered_df.iloc[start_idx:end_idx]

    if paged_df.empty:
        st.warning("Không tìm thấy kết quả nào phù hợp với từ khóa/bộ lọc của bạn.")
    else:
        # Hover thẻ tin tức đổi sang viền Cam
        css_grid = """<style>
        .n-card { background: #fff; border: 1px solid #EAECEF; border-radius: 8px; padding: 16px; margin-bottom: 16px; transition: all 0.2s ease; }
        .n-card:hover { border-color: #FF6B00; box-shadow: 0 4px 12px rgba(230, 81, 0, 0.08); }
        </style>"""
        st.markdown(css_grid, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        for i, row in paged_df.reset_index().iterrows():
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                card_html = f"""<a href="{row['link']}" target="_blank" style="text-decoration: none; color: inherit;">
<div class='n-card'>
<div style='color: #FF6B00; font-size: 11px; font-weight: 700; margin-bottom: 8px;'>{row['ctck']} • {row['tag']}</div>
<div style='color: #1E2329; font-size: 16px; font-weight: 600; margin-bottom: 8px; line-height: 1.4;'>{row['title']}</div>
<div style='color: #848E9C; font-size: 12px;'>{row['date']}</div>
</div></a>"""
                st.markdown(card_html, unsafe_allow_html=True)

    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        pag_cols = st.columns([3, 1, 2, 1, 3]) 
        with pag_cols[1]:
            if st.button("◀ Trước", disabled=(st.session_state.current_page <= 1), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        with pag_cols[2]: st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #474D57;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
        with pag_cols[3]:
            if st.button("Sau ▶", disabled=(st.session_state.current_page >= total_pages), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

# --- KHỐI 4: FOOTER BẢN QUYỀN ---
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
