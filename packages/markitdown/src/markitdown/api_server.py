
import io
import os
import logging
import traceback
import uvicorn
from fastapi import FastAPI, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from openai import OpenAI
from ._markitdown import MarkItDown
from ._stream_info import StreamInfo

app = FastAPI(
    title="Markitdown API",
    description="A web API for the Markitdown file conversion tool.",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/", tags=["Health Check"])
async def read_root():
    """
    Root endpoint for health checks.
    """
    return {"status": "ok", "message": "Markitdown API is running"}

@app.post("/convert", tags=["Conversion"])
async def convert_file(file: UploadFile = File(...)):
    """
    Accepts a file, converts it to Markdown using Markitdown,
    and returns the result as a streaming response.
    """
    try:
        # Initialize OpenAI client if API key is present
        api_key = os.environ.get("OPENAI_API_KEY")
        llm_client = None
        llm_model = None

        if api_key:
            try:
                llm_client = OpenAI(api_key=api_key)
                llm_model = "gpt-4o"
                logger.info("OpenAI client initialized for image analysis.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OPENAI_API_KEY not found. Image analysis will be disabled.")

        # Create a MarkItDown instance
        md = MarkItDown(llm_client=llm_client, llm_model=llm_model)

        # Get file content
        file_content = await file.read()
        
        # Create StreamInfo manually (StreamInfo.from_bytes does not exist)
        extension = os.path.splitext(file.filename)[1] if file.filename else None
        stream_info = StreamInfo(filename=file.filename, extension=extension)

        # Perform the conversion using io.BytesIO as source
        result = md.convert(io.BytesIO(file_content), stream_info=stream_info)

        # Return the markdown content
        return Response(content=result.text_content, media_type="text/markdown")

    except Exception as e:
        # Log the full traceback for debugging
        logger.error(f"Error converting file: {e}")
        logger.error(traceback.format_exc())
        
        return Response(
            content=f"An error occurred during conversion: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

def serve(host="0.0.0.0", port=None):
    """
    Starts the uvicorn server for the FastAPI application.
    """
    if port is None:
        port = int(os.environ.get("PORT", os.environ.get("WEB_PORT", 8080)))
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    serve()
