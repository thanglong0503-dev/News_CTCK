import streamlit as st
from google import genai
from google.genai import types

def render_ai_sidebar(df_input):
    """
    Hàm này sẽ gắn khung chat vào Sidebar và nhận dữ liệu từ hệ thống LINANCE truyền vào.
    """
    # 1. Khởi tạo bộ nhớ tạm
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Kính chào My Lord! LINANCE AI đã sẵn sàng phân tích dữ liệu."}
        ]

    # 2. Xây dựng giao diện Sidebar
    with st.sidebar:
        st.markdown("### 🤖 LINANCE AI")
        st.caption("Cố vấn Định lượng Tốc độ cao")
        st.markdown("---")
        
        # Khung chat hiển thị lịch sử
        chat_container = st.container(height=500)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Khung nhập lệnh
        if user_prompt := st.chat_input("Nhập lệnh cho AI..."):
            
            # Hiển thị tin nhắn người dùng
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_prompt)
            
            # AI phản hồi
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("AI đang tính toán..."):
                        try:
                            # Lọc an toàn các cột cần thiết (nếu có trong bảng dữ liệu của Ngài)
                            target_cols = ['Mã CK', 'Ngành', 'Giá', 'RS_1M', 'Tech_Score', 'Trạng Thái', 'P/E', 'ROE (%)', 'RSI_14']
                            available_cols = [col for col in target_cols if col in df_input.columns]
                            
                            # Chuyển dữ liệu thành dạng thô
                            if not df_input.empty and available_cols:
                                data_csv = df_input[available_cols].to_csv(index=False)
                            else:
                                data_csv = df_input.to_csv(index=False) # Lấy đại toàn bộ nếu không có các cột trên
                                
                            sys_prompt = """
                            Bạn là Giám đốc Phân tích Định lượng của hệ thống LINANCE. 
                            SỰ THẬT TỐI THƯỢNG: Trả lời NGẮN GỌN, SẮC BÉN như một tin nhắn chat. 
                            CHỈ ĐƯỢC PHÉP dùng số liệu trong bảng CSV nội bộ bên dưới, tuyệt đối không bịa data bên ngoài.
                            """
                            full_prompt = f"{sys_prompt}\n\n📊 DỮ LIỆU:\n{data_csv}\n\n🗣️ LỆNH: {user_prompt}"
                            
                            # Triệu hồi Gemini 3.1 Flash Lite
                            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                            response = client.models.generate_content(
                                model='gemini-3.1-flash-lite',
                                contents=full_prompt,
                                config=types.GenerateContentConfig(temperature=0.1)
                            )
                            
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                            
                        except Exception as e:
                            st.error(f"Hệ thống báo lỗi: {e}")
