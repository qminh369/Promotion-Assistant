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
-   PDF upload:
    -   URL: http://localhost:7001/v1/genai/hr-assistants/cv-extraction/pdf-upload
    -   Body from-data:
        -   file (File): Chọn file pdf trong máy cá nhân
    -   ![Ảnh minh hoạ](./imgs/pdf_upload_image.png)
-   PDF URL:
    -   URL: http://localhost:7001/v1/genai/hr-assistants/cv-extraction/pdf-url
    -   Body raw:
        -   file (File): Đường link url của file pdf
    -   ![Ảnh minh hoạ](./imgs/pdf_url_image.png)