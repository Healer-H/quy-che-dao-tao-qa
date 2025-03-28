# Chatbot Hỏi Đáp Quy Chế Đào Tạo 🎓

Hệ thống chatbot thông minh để hỏi đáp về quy chế đào tạo của trường đại học, xây dựng trên kiến trúc RAG (Retrieval Augmented Generation) với FastAPI, Chainlit, và LangChain/LlamaIndex.

## 🚀 Tính năng

- **UI thân thiện**: Giao diện web đơn giản, dễ sử dụng xây dựng bằng Chainlit
- **Xử lý tài liệu PDF**: Tự động xử lý, chunk và lưu trữ văn bản từ file PDF
- **Truy xuất thông tin chính xác**: Sử dụng kiến trúc RAG để tìm và trích xuất thông tin liên quan
- **Trích dẫn nguồn**: Cung cấp nguồn trích dẫn chính xác cho mỗi câu trả lời
- **Hỗ trợ tiếng Việt**: Tối ưu hóa cho ngôn ngữ tiếng Việt

## 🔧 Cài đặt

### Yêu cầu

- Python 3.10+
- OpenAI API key
- Docker và Docker Compose (tùy chọn)

### Cài đặt thủ công

1. Clone repository:
```bash
git clone https://github.com/Healer-H/quy-che-dao-tao-qa.git
cd quy-che-dao-tao-qa
```

2. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

3. Tạo file `.env` với các biến môi trường:
```
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-3.5-turbo
```

4. Khởi chạy FastAPI backend:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. Khởi chạy Chainlit UI (trong terminal mới):
```bash
cd ui
chainlit run app.py
```

### Sử dụng Docker

1. Clone repository:
```bash
git clone https://github.com/Healer-H/quy-che-dao-tao-qa.git
cd quy-che-dao-tao-qa
```

2. Tạo file `.env` với các biến môi trường:
```
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-3.5-turbo
```

3. Khởi chạy với Docker Compose:
```bash
cd docker
docker-compose up -d
```

## 💻 Sử dụng

1. Mở trình duyệt và truy cập vào Chainlit UI tại `http://localhost:8501`
2. Tải lên file PDF quy chế đào tạo
3. Đặt câu hỏi và nhận câu trả lời từ hệ thống

### Xử lý tài liệu

Bạn có thể xử lý tài liệu PDF thủ công bằng script `scripts/ingest.py`:

```bash
python scripts/ingest.py --file quy_che_dao_tao.pdf
```

## 🧠 Kiến trúc hệ thống

Hệ thống được xây dựng dựa trên kiến trúc RAG (Retrieval Augmented Generation):

1. **Xử lý tài liệu**:
   - Đọc và extract văn bản từ PDF
   - Chia nhỏ thành các chunks với kích thước phù hợp
   - Lưu trữ metadata và nội dung

2. **Embedding và Vector Store**:
   - Chuyển đổi chunks thành vectors
   - Lưu trữ vectors vào ChromaDB

3. **Retrieval**:
   - Nhận câu hỏi từ người dùng
   - Tìm kiếm các chunks phù hợp nhất

4. **Generation**:
   - Kết hợp câu hỏi và contexts để tạo prompt
   - Sử dụng LLM để tạo câu trả lời
   - Kèm theo trích dẫn nguồn

## 📁 Cấu trúc dự án

```
university-rag-chatbot/
├── app/                       # Backend code
│   ├── main.py                # FastAPI main application
│   ├── config.py              # Configuration
│   ├── rag/                   # RAG components
│   ├── api/                   # API endpoints
│   └── utils/                 # Helper functions
├── ui/                        # Chainlit UI
│   ├── app.py                 # UI application
│   └── chainlit.md            # Welcome message
├── data/                      # Data storage
├── scripts/                   # Utility scripts
├── docker/                    # Docker configuration
└── requirements.txt           # Dependencies
```

## 🛠️ Tùy chỉnh

### Thay đổi model

Bạn có thể thay đổi model bằng cách cập nhật biến môi trường `MODEL_NAME`.

### Tùy chỉnh chunking

Điều chỉnh kích thước chunk trong `app/config.py` hoặc thông qua biến môi trường:

```
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Sử dụng embedding model khác

Thay đổi embedding model trong `app/config.py` hoặc thông qua biến môi trường:

```
EMBEDDING_MODEL_NAME=keepitreal/vietnamese-sbert
```

## 👥 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo pull request hoặc mở issue để thảo luận về các thay đổi.