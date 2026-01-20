from typing import BinaryIO, Any, Union
import base64
import mimetypes
from ._exiftool import exiftool_metadata
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

ACCEPTED_MIME_TYPE_PREFIXES = [
    "image/jpeg",
    "image/png",
]

ACCEPTED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


class ImageConverter(DocumentConverter):
    """
    Converts images to markdown via extraction of metadata (if `exiftool` is installed), and description via a multimodal LLM (if an llm_client is configured).
    """

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        md_content = ""

        # Add metadata
        metadata = exiftool_metadata(
            file_stream, exiftool_path=kwargs.get("exiftool_path")
        )

        if metadata:
            for f in [
                "ImageSize",
                "Title",
                "Caption",
                "Description",
                "Keywords",
                "Artist",
                "Author",
                "DateTimeOriginal",
                "CreateDate",
                "GPSPosition",
            ]:
                if f in metadata:
                    md_content += f"{f}: {metadata[f]}\n"

        # Try describing the image with GPT
        llm_client = kwargs.get("llm_client")
        llm_model = kwargs.get("llm_model")
        if llm_client is not None and llm_model is not None:
            llm_description = self._get_llm_description(
                file_stream,
                stream_info,
                client=llm_client,
                model=llm_model,
                prompt=kwargs.get("llm_prompt"),
                max_tokens=kwargs.get("llm_max_tokens"),
                detail=kwargs.get("llm_image_detail"),
            )

            if llm_description is not None:
                md_content += "\n# Description:\n" + llm_description.strip() + "\n"

        return DocumentConverterResult(
            markdown=md_content,
        )

    def _get_llm_description(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        *,
        client,
        model,
        prompt=None,
        max_tokens=None,
        detail=None,
    ) -> Union[None, str]:
        if prompt is None or prompt.strip() == "":
            prompt = "Write a detailed caption for this image."

        # Get the content type
        content_type = stream_info.mimetype
        if not content_type:
            content_type, _ = mimetypes.guess_type(
                "_dummy" + (stream_info.extension or "")
            )
        if not content_type:
            content_type = "application/octet-stream"

        # Convert to base64
        cur_pos = file_stream.tell()
        try:
            base64_image = base64.b64encode(file_stream.read()).decode("utf-8")
        except Exception as e:
            return None
        finally:
            file_stream.seek(cur_pos)

        # Helper to check if it's a Gemini client (duck typing or class check)
        is_gemini = hasattr(client, "generate_content")

        if is_gemini:
             # For Gemini, we can pass the image data directly
             import PIL.Image
             import io

             try:
                 # Decode base64 to bytes
                 image_data = base64.b64decode(base64_image)
                 image = PIL.Image.open(io.BytesIO(image_data))
                 
                 # Gemini doesn't use max_tokens in the same way in generate_content (generation_config needed)
                 # configuring generation config
                 from google.generativeai import GenerationConfig
                 generation_config = GenerationConfig(
                     max_output_tokens=max_tokens
                 ) if max_tokens else None

                 response = client.generate_content([prompt, image], generation_config=generation_config)
                 return response.text
             except Exception as e:
                 # Fallback or error logging could happen here, but we'll return None for now
                 return f"Gemini Error: {e}"

        # Prepare the data-uri for OpenAI
        data_uri = f"data:{content_type};base64,{base64_image}"

        # Prepare the OpenAI API request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri,
                            "detail": detail or "auto",
                        },
                    },
                ],
            }
        ]

        # Call the OpenAI API
        response = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens)
        return response.choices[0].message.content
