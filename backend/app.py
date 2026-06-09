from fastapi import FastAPI, UploadFile, File
import pdfplumber
import tempfile
import re

app = FastAPI()


def extract_features(text):

    # -------------------------
    # CGPA Extraction
    # -------------------------

    cgpa = None

    cgpa_patterns = [
        r'(\d+\.\d+)\s*CGPA',
        r'CGPA[:\s]+(\d+\.\d+)',
        r'Aggregate[:\s]+(\d+\.\d+)'
    ]

    for pattern in cgpa_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            cgpa = float(match.group(1))
            break

    # -------------------------
    # Publication Detection
    # -------------------------

    publication_keywords = [
        "paper",
        "publication",
        "published",
        "conference",
        "journal",
        "accepted",
        "research"
    ]

    publication_mentions = 0

    for keyword in publication_keywords:

        publication_mentions += text.lower().count(
            keyword.lower()
        )

    # -------------------------
    # Leadership Detection
    # -------------------------

    leadership_keywords = [
        "head",
        "lead",
        "leader",
        "captain",
        "chair",
        "president",
        "coordinator",
        "manager"
    ]

    leadership_mentions = 0

    for keyword in leadership_keywords:

        leadership_mentions += text.lower().count(
            keyword.lower()
        )

    # -------------------------
    # Project Detection
    # -------------------------

    project_keywords = [
        "project",
        "developed",
        "built",
        "implemented",
        "designed"
    ]

    project_mentions = 0

    for keyword in project_keywords:

        project_mentions += text.lower().count(
            keyword.lower()
        )

    return {
        "cgpa": cgpa,
        "publication_mentions": publication_mentions,
        "leadership_mentions": leadership_mentions,
        "project_mentions": project_mentions
    }


@app.get("/")
def home():

    return {
        "message": "AI Masters Advisor Running"
    }


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    # Validate file type

    if not file.filename.endswith(".pdf"):

        return {
            "error": "Please upload a PDF file."
        }

    try:

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:

            temp_file.write(
                await file.read()
            )

            extracted_text = ""

            with pdfplumber.open(temp_file.name) as pdf:

                for page in pdf.pages:

                    text = page.extract_text()

                    if text:
                        extracted_text += text + "\n"

        # Extract features

        features = extract_features(
            extracted_text
        )

        return {

            "status": "success",

            "features": features,

            "resume_preview":
                extracted_text[:1000]

        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }