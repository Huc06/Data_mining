import streamlit as st
import pandas as pd
import os
import mimetypes
from PIL import Image
# Import moviepy với error handling
try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from pdfminer.high_level import extract_text
from docx import Document
import tempfile
from datetime import datetime
import io

# Cấu hình trang
st.set_page_config(
    page_title="File Classification App",
    page_icon="📁",
    layout="wide"
)

# Khởi tạo session state để lưu trữ kết quả
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame(columns=[
        'Tên file', 'Kích thước (KB)', 'Loại file', 'MIME type', 
        'Thông tin chi tiết', 'Thời gian xử lý'
    ])

def get_file_info(uploaded_file):
    """Lấy thông tin cơ bản của file"""
    file_size = len(uploaded_file.getvalue()) / 1024  # KB
    mime_type = uploaded_file.type
    return file_size, mime_type

def process_image(uploaded_file):
    """Xử lý file ảnh bằng PIL"""
    try:
        image = Image.open(uploaded_file)
        info = {
            'Định dạng': image.format,
            'Kích thước': f"{image.width}x{image.height}",
            'Chế độ màu': image.mode
        }
        return 'image', info
    except Exception as e:
        return 'unknown', {'Lỗi': str(e)}

def process_video(uploaded_file):
    """Xử lý file video bằng moviepy"""
    if not MOVIEPY_AVAILABLE:
        # Nếu moviepy không khả dụng, trả về thông tin cơ bản
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        info = {
            'Kích thước file (KB)': round(file_size, 2),
            'Trạng thái': 'MoviePy không khả dụng - chỉ có thông tin cơ bản',
            'Định dạng': os.path.splitext(uploaded_file.name)[1].upper()
        }
        return 'video', info
    
    try:
        # Lưu file tạm thời để moviepy có thể đọc
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Đọc metadata video
        video = mp.VideoFileClip(tmp_file_path)
        info = {
            'Thời lượng (giây)': round(video.duration, 2),
            'FPS': video.fps,
            'Kích thước': f"{video.w}x{video.h}",
            'Codec': 'Không xác định'
        }
        
        # Đóng video và xóa file tạm
        video.close()
        os.unlink(tmp_file_path)
        
        return 'video', info
    except Exception as e:
        return 'unknown', {'Lỗi': str(e)}

def process_text(uploaded_file, file_extension):
    """Xử lý file văn bản"""
    try:
        if file_extension.lower() == '.pdf':
            # Xử lý PDF
            text = extract_text(io.BytesIO(uploaded_file.getvalue()))
            word_count = len(text.split())
            info = {
                'Số từ': word_count,
                'Số ký tự': len(text),
                'Loại': 'PDF'
            }
        elif file_extension.lower() in ['.docx', '.doc']:
            # Xử lý Word document
            doc = Document(io.BytesIO(uploaded_file.getvalue()))
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            word_count = len(text.split())
            info = {
                'Số từ': word_count,
                'Số ký tự': len(text),
                'Số đoạn': len(doc.paragraphs),
                'Loại': 'Word Document'
            }
        elif file_extension.lower() == '.txt':
            # Xử lý text file
            text = uploaded_file.getvalue().decode('utf-8')
            word_count = len(text.split())
            info = {
                'Số từ': word_count,
                'Số ký tự': len(text),
                'Số dòng': len(text.split('\n')),
                'Loại': 'Text File'
            }
        else:
            return 'unknown', {'Lỗi': 'Định dạng văn bản không được hỗ trợ'}
        
        return 'text', info
    except Exception as e:
        return 'unknown', {'Lỗi': str(e)}

def classify_file(uploaded_file):
    """Phân loại file dựa trên extension và MIME type"""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    mime_type = uploaded_file.type
    
    # Phân loại dựa trên MIME type và extension
    image_types = ['image/', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    video_types = ['video/', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
    text_types = ['text/', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                  '.txt', '.pdf', '.docx', '.doc']
    
    # Kiểm tra ảnh
    if any(img_type in mime_type for img_type in image_types if img_type.startswith('image/')) or \
       any(file_extension == ext for ext in image_types if ext.startswith('.')):
        return process_image(uploaded_file)
    
    # Kiểm tra video
    elif any(vid_type in mime_type for vid_type in video_types if vid_type.startswith('video/')) or \
         any(file_extension == ext for ext in video_types if ext.startswith('.')):
        return process_video(uploaded_file)
    
    # Kiểm tra văn bản
    elif any(txt_type in mime_type for txt_type in text_types if not txt_type.startswith('.')) or \
         any(file_extension == ext for ext in text_types if ext.startswith('.')):
        return process_text(uploaded_file, file_extension)
    
    else:
        return 'unknown', {'Thông tin': 'Loại file không được hỗ trợ'}

def main():
    st.title("📁 Ứng dụng Phân loại File Tự động")
    st.markdown("---")
    
    # Sidebar với thông tin
    with st.sidebar:
        st.header("📋 Hướng dẫn sử dụng")
        
        # Hiển thị trạng thái MoviePy
        if not MOVIEPY_AVAILABLE:
            st.error("⚠️ MoviePy không khả dụng - chức năng video hạn chế")
        else:
            st.success("✅ Tất cả module hoạt động bình thường")
        
        st.markdown("""
        **Các loại file được hỗ trợ:**
        - 🖼️ **Ảnh**: JPG, PNG, GIF, BMP, TIFF, WebP
        - 🎥 **Video**: MP4, AVI, MOV, WMV, FLV, WebM, MKV  
        - 📄 **Văn bản**: TXT, PDF, DOCX, DOC
        
        **Cách sử dụng:**
        1. Upload file bằng nút bên dưới
        2. Hệ thống sẽ tự động phân loại
        3. Xem kết quả trong bảng
        """)
        
        if st.button("🗑️ Xóa tất cả kết quả"):
            st.session_state.results_df = pd.DataFrame(columns=[
                'Tên file', 'Kích thước (KB)', 'Loại file', 'MIME type', 
                'Thông tin chi tiết', 'Thời gian xử lý'
            ])
            st.success("Đã xóa tất cả kết quả!")
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📤 Upload File")
        uploaded_files = st.file_uploader(
            "Chọn file để phân loại:",
            accept_multiple_files=True,
            type=None
        )
        
        if uploaded_files:
            if st.button("🔍 Phân tích tất cả file", type="primary"):
                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    # Cập nhật progress bar
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    # Lấy thông tin file
                    file_size, mime_type = get_file_info(uploaded_file)
                    
                    # Phân loại file
                    file_type, details = classify_file(uploaded_file)
                    
                    # Thêm vào DataFrame
                    new_row = {
                        'Tên file': uploaded_file.name,
                        'Kích thước (KB)': round(file_size, 2),
                        'Loại file': file_type,
                        'MIME type': mime_type,
                        'Thông tin chi tiết': str(details),
                        'Thời gian xử lý': datetime.now().strftime("%H:%M:%S")
                    }
                    
                    st.session_state.results_df = pd.concat([
                        st.session_state.results_df, 
                        pd.DataFrame([new_row])
                    ], ignore_index=True)
                
                st.success(f"✅ Đã phân tích xong {len(uploaded_files)} file!")
    
    with col2:
        st.header("📊 Kết quả phân loại")
        
        if not st.session_state.results_df.empty:
            # Hiển thị thống kê
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                total_files = len(st.session_state.results_df)
                st.metric("📁 Tổng file", total_files)
            
            with col_stat2:
                image_count = len(st.session_state.results_df[st.session_state.results_df['Loại file'] == 'image'])
                st.metric("🖼️ Ảnh", image_count)
            
            with col_stat3:
                video_count = len(st.session_state.results_df[st.session_state.results_df['Loại file'] == 'video'])
                st.metric("🎥 Video", video_count)
            
            with col_stat4:
                text_count = len(st.session_state.results_df[st.session_state.results_df['Loại file'] == 'text'])
                st.metric("📄 Văn bản", text_count)
            
            # Hiển thị bảng kết quả
            st.dataframe(
                st.session_state.results_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Nút download CSV
            csv = st.session_state.results_df.to_csv(index=False)
            st.download_button(
                label="📥 Tải xuống kết quả (CSV)",
                data=csv,
                file_name=f"file_classification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("🔍 Chưa có file nào được phân tích. Hãy upload file và nhấn nút 'Phân tích'!")

if __name__ == "__main__":
    main() 