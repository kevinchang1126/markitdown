
import asyncio
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ._markitdown import MarkItDown

app = FastAPI()
md = MarkItDown()

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    """
    Accepts a file upload, converts it to Markdown using markitdown,
    and returns the result as JSON.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    temp_file_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        markdown_result = await asyncio.to_thread(md.convert, Path(temp_file_path))
        markdown_content = markdown_result.text_content

        return JSONResponse(content={"filename": file.filename, "markdown": markdown_content})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during conversion: {str(e)}")

    finally:
        # Clean up the temporary file
        if temp_file_path and Path(temp_file_path).exists():
            Path(temp_file_path).unlink()

@app.get("/")
def read_root():
    return {"message": "Markitdown API is running. Use the /convert endpoint to process files."}

# To run this server locally for testing:
# uvicorn packages.markitdown.src.markitdown.api_server:app --reload
