import requests
from bs4 import BeautifulSoup
import pandas as pd

def test_scrape_kafi():
    url = "https://kafi.vn/notification"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    print(f"🚀 Đang chuyển hướng radar sang mục tiêu mới: {url}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("✅ Xuyên thủng Firewall thành công! (Mã 200 OK)")
            
            # Đo dung lượng HTML để bắt bệnh web động (SPA)
            html_length = len(response.text)
            print(f"📦 Dung lượng HTML tải về: {html_length} ký tự.\n")
            
            if html_length < 10000:
                print("⚠️ CẢNH BÁO: HTML rất ngắn! Khả năng 99% Kafi dùng Web động (React/Vue).")
                print("Dữ liệu thông báo đã bị giấu trong API ngầm, BeautifulSoup sẽ không đọc được.\n")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            
            # Quét rộng: Tìm tất cả thẻ <a> có link
            links = soup.find_all('a', href=True)
            
            for link in links:
                text = link.text.strip()
                href = link['href']
                
                # Lọc sơ bộ: Text đủ dài và không phải là các link rác
                if text and len(text) > 15 and not href.startswith('javascript'):
                    full_link = "https://kafi.vn" + href if href.startswith('/') else href
                    news_items.append({
                        "Tiêu đề (Bắt tạm)": text,
                        "Đường dẫn": full_link
                    })
            
            df = pd.DataFrame(news_items).drop_duplicates()
            
            if not df.empty:
                print(f"🎉 BẮT ĐƯỢC {len(df)} MỤC TRÊN HTML:")
                print("-" * 50)
                print(df.head(5).to_string(index=False))
                print("-" * 50)
            else:
                print("❌ KHÔNG TÌM THẤY DỮ LIỆU BẰNG HTML!")
                print("👉 Kết luận: Web Kafi tải dữ liệu bằng API ngầm. Code cào HTML truyền thống đã bị vô hiệu hóa.")
                
        elif response.status_code == 403:
            print("❌ Thất bại! Mã 403 Forbidden. Kafi đã dùng Cloudflare chặn IP của ngươi.")
        else:
            print(f"❌ Thất bại! Lỗi HTTP: {response.status_code}")

    except Exception as e:
        print(f"🔥 Lỗi hệ thống: {e}")

if __name__ == "__main__":
    test_scrape_kafi()
