# 📊 News_CTCK - Nền Tảng Tổng Hợp & Phân Tích Dữ Liệu Chứng Khoán Toàn Diện

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org/)

**News_CTCK** là một hệ thống phân tích và quản lý dữ liệu chứng khoán toàn diện tại thị trường Việt Nam. Ứng dụng tự động hóa quy trình thu thập dữ liệu (tin tức, báo cáo, biểu phí, margin) từ các Công ty Chứng khoán (CTCK) và các nguồn uy tín, tích hợp công nghệ AI để cung cấp góc nhìn sâu sắc cho nhà đầu tư.

Giao diện Dashboard được xây dựng trực quan trên nền tảng **Streamlit**, phân chia thành các tab chức năng chuyên sâu giúp tối ưu hóa trải nghiệm phân tích dữ liệu thị trường.

---

## ✨ Các Tính Năng/Phân Hệ Chính

Ứng dụng được thiết kế tối ưu với các phân hệ chức năng (Tab) rõ ràng:

- 📈 **Tổng Quan Thị Trường:** Cập nhật diễn biến thị trường, các chỉ số chung và luồng tin tức nóng hổi từ các CTCK theo thời gian thực.
- 🗄️ **Dữ Liệu Giao Dịch:** Thống kê chi tiết khối lượng, giá trị giao dịch, biến động kỹ thuật và lịch sử giá của thị trường.
- 🤖 **Phân Tích AI:** Tích hợp mô hình trí tuệ nhân tạo (AI) giúp phân tích xu hướng thị trường, đọc hiểu và tóm tắt nhanh thông tin cốt lõi.
- 📑 **Báo Cáo Tổ Chức:** Tổng hợp, lưu trữ và hệ thống hóa các báo cáo phân tích chiến lược, báo cáo vĩ mô từ các tổ chức tài chính lớn.
- ⚖️ **So Sánh Dịch Vụ:** Công cụ đối chiếu trực quan về tỷ lệ cho vay ký quỹ (Margin rates), biểu phí giao dịch cơ sở/phái sinh và các chính sách ưu đãi giữa các CTCK.
- 🔍 **Phân Tích Cổ Phiếu:** Đi sâu vào từng mã cổ phiếu cụ thể (sức khỏe tài chính, định giá, tin tức liên quan trực tiếp đến doanh nghiệp).
- ⚙️ **Bộ Lọc Cổ Phiếu:** Công cụ lọc và tìm kiếm cơ hội đầu tư dựa trên các tiêu chí kỹ thuật, cơ bản hoặc các điều kiện tùy chỉnh của người dùng.

---

## 📂 Cấu trúc dự án

```text
News_CTCK/
│
├── .github/workflows/   # Cấu hình tự động hóa (GitHub Actions cho worker)
├── assets/              # Lưu trữ hình ảnh, logo và tài liệu minh họa ứng dụng
├── backend/             # Source code phần xử lý logic cào dữ liệu, xử lý dữ liệu và database
├── frontend/            # Các component, module hỗ trợ hiển thị giao diện các tab
├── app.py               # File khởi chạy chính của ứng dụng Streamlit
├── rs_worker.py         # Worker chạy ngầm phục vụ tác vụ tự động quét/cập nhật dữ liệu
├── requirements.txt     # Danh sách các thư viện Python phụ thuộc
└── README.md            # Tài liệu hướng dẫn dự án


Hướng dẫn cài đặt và Chạy ứng dụng dưới Local
1. Yêu cầu hệ thống
Máy tính đã cài đặt sẵn Python 3.9+
Git (để clone project)

Clone repository này về máy local:
git clone [https://github.com/thanglong0503-dev/News_CTCK.git](https://github.com/thanglong0503-dev/News_CTCK.git)
cd News_CTCK
Tạo một môi trường ảo (Virtual Environment) để tránh xung đột thư viện:
# Trên Windows
python -m venv venv
venv\Scripts\activate

# Trên macOS/Linux
python3 -m venv venv
source venv/bin/activate
Cài đặt các thư viện cần thiết:
pip install -r requirements.txt
Chạy worker để kích hoạt tác vụ quét và cập nhật dữ liệu mới:
python rs_worker.py
Khởi chạy giao diện Dashboard Streamlit:
streamlit run app.py
Sau khi chạy lệnh trên, trình duyệt sẽ tự động mở ứng dụng tại địa chỉ mặc định http://localhost:8501.


🛠️ Công nghệ sử dụng
Ngôn ngữ chính: Python

Framework Giao diện: Streamlit

Cào dữ liệu (Data Scraping): BeautifulSoup4, Requests, Selenium...

Xử lý & Phân tích dữ liệu: Pandas, NumPy

Mô hình AI: (Bổ sung thêm thư viện/API AI bạn dùng vào đây, ví dụ: OpenAI API, Gemini API, LangChain...)

🔗 Liên kết Dự án
Mã nguồn GitHub: https://github.com/thanglong0503-dev/News_CTCK

Ứng dụng Trực tuyến: newsctck-fwynyibuz6nanj3iynasmh.streamlit.app

📄 Giấy phép (License)
Dự án này được phân phối dưới giấy phép MIT License - xem file LICENSE để biết thêm chi tiết.
