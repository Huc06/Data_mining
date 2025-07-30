# 📁 Ứng dụng Phân loại File Tự động

Ứng dụng này được xây dựng dựa trên flowchart phân loại file tự động, sử dụng Streamlit để tạo giao diện web thân thiện với người dùng.

## 🚀 Tính năng

- **Phân loại tự động**: Tự động nhận diện và phân loại file dựa trên MIME type và file extension
- **Hỗ trợ nhiều loại file**:
  - 🖼️ **Ảnh**: JPG, PNG, GIF, BMP, TIFF, WebP
  - 🎥 **Video**: MP4, AVI, MOV, WMV, FLV, WebM, MKV
  - 📄 **Văn bản**: TXT, PDF, DOCX, DOC
- **Thông tin chi tiết**: Trích xuất metadata và thông tin chi tiết cho từng loại file
- **Giao diện thân thiện**: Sử dụng Streamlit với UI hiện đại
- **Xử lý nhiều file**: Upload và phân tích nhiều file cùng lúc
- **Xuất kết quả**: Tải xuống kết quả dưới dạng CSV

## 📋 Quy trình hoạt động

```
User chọn file → Streamlit nhận file → Check MIME type/extension → Phân loại
    ↓
[Ảnh] PIL xác minh → Gán label "image"
[Video] MoviePy đọc metadata → Gán label "video"  
[Văn bản] PDFMiner/python-docx → Gán label "text"
    ↓
Lưu vào Pandas DataFrame → Hiển thị kết quả
```

## 🛠️ Cài đặt

### 1. Clone repository (hoặc tạo thư mục mới)
```bash
git clone <repository-url>
cd Data_mining
```

### 2. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
streamlit run app.py
```

Ứng dụng sẽ mở trong trình duyệt tại địa chỉ: `http://localhost:8501`

## 📚 Cách sử dụng

1. **Upload file**: Sử dụng nút "Browse files" để chọn một hoặc nhiều file
2. **Phân tích**: Nhấn nút "🔍 Phân tích tất cả file" 
3. **Xem kết quả**: Kết quả sẽ hiển thị trong bảng với các thông tin:
   - Tên file
   - Kích thước (KB)
   - Loại file (image/video/text/unknown)
   - MIME type
   - Thông tin chi tiết
   - Thời gian xử lý
4. **Tải xuống**: Sử dụng nút "📥 Tải xuống kết quả (CSV)" để lưu kết quả

## 🔧 Thư viện sử dụng

- **Streamlit**: Tạo giao diện web
- **Pillow (PIL)**: Xử lý ảnh
- **MoviePy**: Xử lý video và trích xuất metadata
- **PDFMiner**: Đọc nội dung file PDF
- **python-docx**: Xử lý file Word
- **Pandas**: Lưu trữ và quản lý dữ liệu
- **python-magic**: Xác định MIME type (tùy chọn)

## 📊 Ví dụ Output

| Tên file | Kích thước (KB) | Loại file | MIME type | Thông tin chi tiết |
|----------|----------------|-----------|-----------|-------------------|
| photo.jpg | 245.67 | image | image/jpeg | {'Định dạng': 'JPEG', 'Kích thước': '1920x1080', 'Chế độ màu': 'RGB'} |
| video.mp4 | 5432.10 | video | video/mp4 | {'Thời lượng (giây)': 120.5, 'FPS': 30.0, 'Kích thước': '1280x720'} |
| document.pdf | 89.23 | text | application/pdf | {'Số từ': 1250, 'Số ký tự': 7890, 'Loại': 'PDF'} |

## 🚨 Lưu ý

- Ứng dụng cần quyền truy cập file tạm thời để xử lý video
- Một số định dạng video có thể yêu cầu codec đặc biệt
- File PDF được bảo vệ bằng mật khẩu có thể không đọc được
- Kích thước file lớn có thể làm chậm quá trình xử lý

## 🤝 Đóng góp

Mọi đóng góp và cải thiện đều được hoan nghênh! Hãy tạo pull request hoặc báo cáo lỗi thông qua Issues.

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết. 