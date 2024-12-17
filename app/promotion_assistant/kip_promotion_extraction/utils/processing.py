from fastapi import HTTPException
import json
import re
import fitz # PyMuPDF
import openparse # OpenParse
from openparse import processing
import os
from openai import OpenAI

# Các hàm hỗ trợ
def clean_pages_content(pages: list[str]): # Hàm hỗ trợ 1
    cleaned_pages = []
    for page in pages:
        cleaned_content = page.replace("\x00", "")
        cleaned_content = re.sub(r'(?<=\b[A-Z])\s(?=[A-Z]\b)', '', cleaned_content)
        # cleaned_content = re.sub(r'([A-ZÀ-Ỹ]+)\s*\n\s*([A-ZÀ-Ỹ]+)', r'\1 \2', cleaned_content)
        cleaned_pages.append(cleaned_content)

    content = "\n\n".join(cleaned_pages).strip()
    if not content:
        print(
            "There is no textual content in the file.",
        )
        return
    return content

# Tạo pipeline parsing Openparse
class MyIngestionPipeline(processing.IngestionPipeline):
    def __init__(self):
        self.transformations = [
            processing.RemoveTextInsideTables(),
            processing.CombineNodesSpatially(criteria="either_stub"),
            processing.CombineBullets(),
            processing.CombineHeadingsWithClosestText(),
            processing.RemoveFullPageStubs(max_area_pct=0.2), 
        ]

def read_content_openparse(file):
    parser = openparse.DocumentParser(
        processing_pipeline=MyIngestionPipeline(),
        table_args={"parsing_algorithm": "pymupdf",
                "table_output_format": "markdown"}
    )

    parsed_doc = parser.parse(file)
    json_parsing = parsed_doc.json()
    final_json_parsing = json.loads(json_parsing)

    nodes = final_json_parsing['nodes']
    full_text = ""
    for node in nodes:
        full_text += node['text'] + "\n\n"
    
    return full_text

def read_content_pymupdf(file): # Hàm hỗ trợ 2
    try:
        # Attempt to load the PDF using Fitz - PyMuPDF
        document = fitz.open(file)
        pages = []

        # Iterate through each page
        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            text = page.get_text()
            pages.append(text)
        
        document.close()
    
        # result = convert_to_markdown(clean_pages_content(pages))
        result = clean_pages_content(pages)
    except HTTPException as http_exc:
        if http_exc.status_code == 400 and 'encoding error' in str(http_exc):
            print(f"Encoding error in {file}: {http_exc}")
        else:
            raise  # Re-raise the exception if it's not the specific error we're handling
    except Exception as e:
        # Log the exception or handle it accordingly
        print(f"Failed to load PDF content: {e}")
        print("Failed to load PDF content due to encoding error.")
        
    return result

def clean_data(data): # Hàm hỗ trợ 4
    """Xóa các trường không có thông tin và loại bỏ ký tự không cần thiết."""
    if isinstance(data, str):
        # Remove unwanted characters (e.g., backslashes, newlines)
        data = data.replace('\\', '').replace('\n', '').strip()
    
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items() if v not in (None, [], {}, "")}
    elif isinstance(data, list):
        return [clean_data(item) for item in data if item not in (None, [], {}, "")]
    return data

def AI_gened_Message(text, assistant_id, api_key, host): # Hàm hỗ trợ 5
    client = OpenAI(
        api_key=api_key,
        base_url=f"{host}/v1",
    )
    response = client.chat.completions.create(
        model=assistant_id,
        messages=[
            {"role": "user", "content": text},
        ]
    )
    
    return response.choices[0].message.content

def AI_parsing(message, assistant_id, api_key, host):
    user_message = f'{message}'
    # print(user_message)
    AI_message = AI_gened_Message(user_message, assistant_id, api_key, host)
    return AI_message

def AI_output(message, assistant_id, api_key, host): # Hàm hỗ trợ 5
    user_message = f'Phân tích nội dung sau:\n{message}'
    # print(user_message)
    AI_message = AI_gened_Message(user_message, assistant_id, api_key, host)
    
    # AI_message = extract_structure(AI_message)
    # Fix các lỗi ký tự 
    # Chuyền về string bình thường
    cleaned_json_string = AI_message.replace("```json", "").replace("```", "").strip()

    # Loại bỏ các dấu ',' thừa
    cleaned_json_string = cleaned_json_string.replace(',}', '}').replace(',]', ']')
    cleaned_json_string = cleaned_json_string.replace(',\n\s+}', '\n\s+}').replace(',\n\s+]', '\n\s+]')
    cleaned_json_string = cleaned_json_string.replace('\n', ' ')
    # Check if the cleaned JSON string is empty or malformed
    if not cleaned_json_string:
        print("Error: The cleaned JSON string is empty.")
        return   # or handle the error as needed

    try:
        json_data = json.loads(cleaned_json_string)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return  # or handle the error as needed
    json_data = clean_data(json_data)
    # Trả về nội dung PDF dạng JSON
    final_str = json.dumps(json_data, ensure_ascii=False)
    # print(type(final_dict))
    final_json = json.loads(final_str)
    
    return final_json