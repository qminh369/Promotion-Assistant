# **Thay đổi trong file .env**
-   Copy file .env.example đã được cấu hình từ trước
-   cp .env.example .env
# **Tạo folder "storage"**
-   Tạo folder "storage" ngay trong thư mục MBW_GenAI project
# **Cài đặt các thư viện cần thiết**
-    pip install -r requirements.txt
# **Chạy API**
-   Chạy API bằng 1 trong 2 lệnh sau:
    -   python3 app/main.py
    -   PYTHONPATH=$(pwd) python app/main.py
# **Test api trên Postman**
-   PDF URL:
    -   URL: http://localhost:8000/v2/genai/promotion-assistants/kip-promotion-extraction/pdf-upload

