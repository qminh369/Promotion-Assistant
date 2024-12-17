import os
from fastapi import APIRouter, File, UploadFile, Header, HTTPException, Form
import logging
import uuid
import json
from fastapi.responses import JSONResponse
from dotenv import dotenv_values  # Để đọc tệp .env
from promotion_assistant.kip_promotion_extraction.utils.processing import read_content_openparse, read_content_pymupdf, AI_parsing, AI_output

# Load môi trường từ tệp .env
env = dotenv_values(".env")

router = APIRouter()

# Constants
TEMP_PATH =  os.path.join(env["STORAGE_PATH"]) + '/tmp'
HOST_TASKINGAI = os.path.join(env["HOST_TASKINGAI"])
KIP_PDF_EXTRACTION_ASSISTANT_ID = os.path.join(env["KIP_PDF_EXTRACTION_ASSISTANT_ID"])
KIP_DMS_PROMOTION_ASSISTANT_ID = os.path.join(env["KIP_DMS_PROMOTION_ASSISTANT_ID"])
API_KEY = os.path.join(env["OPENAI_API_KEY"])

os.makedirs(TEMP_PATH,exist_ok=True)

@router.post(
    "/genai/promotion-assistants/kip-promotion-extraction/pdf-upload",
    tags=["Read PDF From Upfile"],
)
def upload_pdf(
    # kip_pdf_extraction_assistant_id: str = Form(None),
    # kip_dms_promotion_assistant_id: str = Form(None),
    file: UploadFile = File(...),
    # authorization: str = Header(...),
):
    """
    Upload and process a PDF file using an AI assistant.

    Args:
        kip_pdf_extraction_assistant_id: ID of the KIP PDF extraction assistant
        kip_dms_promotion_assistant_id: ID of the KIP DMS promotion assistant
        file: Uploaded PDF file
        authorization: Authorization header

    Returns:
        Dict containing processed data
    """
    try:
        # Validate authorization
        # if not authorization:
        #     raise HTTPException(status_code=401, detail="Authorization header is missing")

        # Extract API key
        try:
            # _, api_key = authorization.split(" ", 1)
            api_key = API_KEY
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid authorization format")

        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Assign default assistant IDs if not provided
        kip_pdf_extraction_assistant_id = KIP_PDF_EXTRACTION_ASSISTANT_ID 
        kip_dms_promotion_assistant_id = KIP_DMS_PROMOTION_ASSISTANT_ID 
        # print(CONFIG.PATH_TO_VOLUME)
        # Create unique request directory
        request_id = str(uuid.uuid4())
        request_dir = TEMP_PATH+"/"+request_id
        os.makedirs(request_dir, exist_ok=True)
        # Create temporary file
        temp_pdf_path = request_dir+"/temp.pdf"
        temp_text_pdf_path = request_dir+"/content_pdf.txt"
        temp_text_assistant_response_path = request_dir+"/assistant_response.txt"
        temp_response_path = request_dir+"/response.json"

        try:
            print("Temp PDF Path:",temp_pdf_path)
            with open(temp_pdf_path, 'wb') as temp_file:
                temp_file.write(file.file.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

        try:
            content_openparse = read_content_openparse(temp_pdf_path)
            content_pymupdf = read_content_pymupdf(temp_pdf_path)
            parsing_message = f"Dưới đây là nội dung văn bản trích xuất theo dạng markdown (văn bản 1): {content_openparse}\n\nDưới đây là nội dung văn bản trích xuất theo dạng text (văn bản 2): {content_pymupdf}"
            content = AI_parsing(parsing_message, kip_pdf_extraction_assistant_id, api_key, HOST_TASKINGAI)

            # Lưu file txt của PDF
            with open(temp_text_pdf_path, "w") as f:
                f.write(content)

            print(content)
            # Generate AI output
            json_data = AI_output(content, kip_dms_promotion_assistant_id, api_key, HOST_TASKINGAI)

            # Lưu phản hồi từ Assistant
            json_data_str = json.dumps(json_data, indent=4, ensure_ascii=False)
            with open(temp_text_assistant_response_path, "w") as f:
                f.write(json_data_str)
    
            
            # Lưu response
            result_str = json.dumps(json_data, indent=4, ensure_ascii=False)
            with open(temp_response_path, "w") as f:
                    f.write(result_str)
            
            return json_data

        except Exception as e:
            logging.error(f"Error call Assistant: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
