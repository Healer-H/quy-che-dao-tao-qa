from pathlib import Path
import os
import requests
import chainlit as cl
# from chainlit.playground.config import PlaygroundConfig
# from chainlit.playground.providers.openai import OpenAISettings
from chainlit.element import Element
import json
from typing import Dict, List, Any

# API settings
API_URL = os.getenv("API_URL", "http://localhost:8051")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

# Customize UI


@cl.on_settings_update
async def setup_agent(settings):
    print(f"Settings updated: {settings}")

# Upload handler


# @cl.on_upload
# async def handle_upload(files):
#     for file in files:
#         if not file.name.lower().endswith(".pdf"):
#             await cl.Message(
#                 content=f"Chỉ chấp nhận file PDF. {file.name} không phải là file PDF.",
#                 author="System"
#             ).send()
#             continue

#         # Upload file to API
#         files_data = {"file": (file.name, file.content)}
#         response = requests.post(
#             f"{API_URL}{API_PREFIX}/upload",
#             files=files_data
#         )

#         if response.status_code == 200:
#             result = response.json()
#             await cl.Message(
#                 content=f"Đã tải lên file `{file.name}` thành công. Hệ thống đang xử lý...",
#                 author="System"
#             ).send()
#         else:
#             error_msg = "Lỗi không xác định"
#             try:
#                 error_data = response.json()
#                 error_msg = error_data.get("detail", error_msg)
#             except:
#                 pass

#             await cl.Message(
#                 content=f"Lỗi khi tải lên file `{file.name}`: {error_msg}",
#                 author="System"
#             ).send()

# Message handler

def process_message_element(element):
    extension = Path(element.path).suffix.lower()
    if extension == ".pdf":
        # Đọc file PDF dưới dạng nhị phân
        with open(element.path, "rb") as f:
            pdf_content = f.read()

        # Chuẩn bị dữ liệu gửi
        files_data = {
            "file": (Path(element.path).name, pdf_content, "application/pdf")
        }
        data = {
            "document_id": element.name  # Gửi document_id trong form-data
        }

        # Gửi request đến API
        response = requests.post(
            f"{API_URL}{API_PREFIX}/upload",
            files=files_data,
            data=data
        )

        # Kiểm tra phản hồi từ server
        if response.status_code == 200:
            return response.json()  # Trả về dữ liệu JSON từ server
        else:
            return {"error": f"Failed to upload file. Status: {response.status_code}, Message: {response.text}"}

    else:
        return {"error": "Unsupported file format"}
@cl.on_message
async def on_message(message: cl.Message):
    # Set up loading message
    msg = cl.Message(content="", author="Chatbot")
    await msg.send()

    try:
        elements = message.elements
        for element in elements:
            if element.type == "file":
                extension = Path(element.path).suffix.lower()
                if extension == ".pdf":
                    # Handle PDF file
                    pdf_content = process_message_element(element)
                    await cl.Message(
                        content=f"Đã tải lên file `{element.name}` thành công. Hệ thống đang xử lý...",
                        author="System"
                    )
                else:
                    await cl.Message(
                        content=f"Chỉ chấp nhận file PDF. {element.name} không phải là file PDF.",
                        author="System"
                    )
            
        # Send request to API
        response = requests.post(
            f"{API_URL}{API_PREFIX}/chat",
            json={"message": message.content}
        )

        if response.status_code != 200:
            error_msg = "Lỗi không xác định"
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", error_msg)
            except:
                pass
            
            await cl.Message(
                content=f"Lỗi khi gửi câu hỏi: {error_msg}",
                author="System"
            ).send()
            return

        result = response.json()

        # Create response with sources
        response_text = result["response"]
        sources = result.get("sources", [])

        # Update message with response
        await msg.update()

        # Add source elements if available
        if sources:
            elements = []
            for i, source in enumerate(sources):
                source_text = source["text"]
                metadata = source["metadata"]
                source_name = metadata.get("source", "Unknown")

                # Create element for source
                source_element = Element(
                    name=f"source_{i}",
                    type="text",
                    content=f"Nguồn: {source_name}\n\n{source_text}",
                    display="side"
                )
                elements.append(source_element)

            await cl.Message(
                content=response_text,
                author="Chatbot",
                elements=elements
            ).send()

    except Exception as e:
        await msg.update()

# Startup message


@cl.on_chat_start
async def on_chat_start():
    # Send welcome message
    await cl.Message(
        content="""
# 👋 Chào mừng đến với Chatbot Quy chế Đào tạo

Tôi là trợ lý AI chuyên trả lời các câu hỏi về quy chế đào tạo của trường đại học.

## 📚 Cách sử dụng:
1. Tải lên file PDF quy chế đào tạo bằng nút tải lên ở góc dưới bên trái
2. Đặt câu hỏi về quy chế đào tạo và nhận câu trả lời dựa trên nội dung trong tài liệu

## 🔍 Lưu ý:
- Mỗi câu trả lời sẽ đi kèm với trích dẫn từ quy chế đào tạo
- Nếu câu hỏi không liên quan đến quy chế, chatbot có thể không trả lời được

Hãy bắt đầu bằng cách tải lên file quy chế đào tạo!
        """,
        author="System"
    ).send()

    # Get list of available documents
    try:
        response = requests.get(f"{API_URL}{API_PREFIX}/documents")
        if response.status_code == 200:
            documents = response.json()
            if documents:
                doc_list = "\n".join(
                    [f"- {doc['filename']}" for doc in documents])
                await cl.Message(
                    content=f"Các tài liệu sẵn có trong hệ thống:\n{doc_list}",
                    author="System"
                ).send()
            else:
                await cl.Message(
                    content="Hiện chưa có tài liệu nào trong hệ thống. Vui lòng tải lên file PDF quy chế đào tạo.",
                    author="System"
                ).send()
    except Exception as e:
        print(f"Error fetching documents: {str(e)}")

if __name__ == "__main__":
    cl.run()
