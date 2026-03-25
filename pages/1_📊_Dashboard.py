import streamlit as st
from backend.ssi_api import fetch_ssi_margin_news

st.set_page_config(page_title="Phân tích & Tin tức", layout="wide")
st.header("📊 Phân tích Danh mục & Chính sách CTCK")

# Khu vực theo dõi danh mục ưu tiên
st.subheader("🎯 Theo dõi Margin Danh mục mục tiêu")
cols = st.columns(2)
with cols[0]:
    st.metric("PLX (Petrolimex)", "Tỷ lệ ký quỹ tối đa: 50%", "SSI: Đang mở Room")
with cols[1]:
    st.metric("MBB (MB Bank)", "Tỷ lệ ký quỹ tối đa: 40%", "TCBS: Đang mở Room")

st.divider()

# Khu vực hiển thị tin tức cào được
st.subheader("📰 Cập nhật chính sách & Phí mới nhất")
df_news = fetch_ssi_margin_news()

if not df_news.empty:
    # Hiển thị bảng dữ liệu với giao diện xịn của Streamlit
    st.dataframe(
        df_news,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Đường dẫn chi tiết")
        }
    )
else:
    st.warning("Hiện tại không có tin tức mới nào về Margin hoặc Phí dịch vụ.")
