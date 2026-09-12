"""
=========================================
TalentIQ AI
Smart Resume Parser
Version 5.0
=========================================
"""

import os
import re
import pdfplumber
from docx import Document


# -----------------------------------------------------
# Clean Resume Text
# -----------------------------------------------------

def clean_text(text):

    if not text:
        return ""

    # Remove unwanted spaces between letters
    text = re.sub(r'(?<=\b[A-Za-z])\s(?=[A-Za-z]\b)', '', text)

    # Replace tabs/newlines/multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove strange characters
    text = text.replace("\x00", "")

    return text.strip()


# -----------------------------------------------------
# PDF Extraction
# -----------------------------------------------------

def extract_pdf(file_path):

    text = ""
    pages = 0

    with pdfplumber.open(file_path) as pdf:

        pages = len(pdf.pages)

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

    return clean_text(text), pages

# -----------------------------------------------------
# DOCX Extraction
# -----------------------------------------------------

def extract_docx(file_path):

    doc = Document(file_path)

    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    pages = 1

    return clean_text(text), pages


# -----------------------------------------------------
# Resume Parser
# -----------------------------------------------------

def extract_text(file_path):

    result = {

        "success": False,

        "text": "",

        "metadata": {

            "file_name": "",

            "file_type": "",

            "file_size_kb": 0,

            "pages": 0,

            "word_count": 0,

            "character_count": 0

        },

        "message": ""

    }

    # ---------------- File Exists ----------------

    if not os.path.exists(file_path):

        result["message"] = "File not found."

        return result

    # ---------------- File Size ----------------

    file_size = os.path.getsize(file_path)

    if file_size > 10 * 1024 * 1024:

        result["message"] = "File size exceeds 10 MB."

        return result

    extension = os.path.splitext(file_path)[1].lower()

    result["metadata"]["file_name"] = os.path.basename(file_path)
    result["metadata"]["file_type"] = extension.replace(".", "").upper()
    result["metadata"]["file_size_kb"] = round(file_size / 1024, 2)

    try:

        if extension == ".pdf":

            text, pages = extract_pdf(file_path)

        elif extension == ".docx":

            text, pages = extract_docx(file_path)

        else:

            result["message"] = "Unsupported file format."

            return result

        if text == "":

            result["message"] = "No readable text found in resume."

            return result

        result["success"] = True

        result["text"] = text

        result["metadata"]["pages"] = pages

        result["metadata"]["word_count"] = len(text.split())

        result["metadata"]["character_count"] = len(text)

        result["message"] = "Resume parsed successfully."

        return result

    except Exception as e:

        result["message"] = f"Parser Error : {str(e)}"

        return result