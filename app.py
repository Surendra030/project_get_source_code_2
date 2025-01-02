import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific domains for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def fetch_html(url: str):
    """
    Fetch the HTML content of a given URL.

    Args:
        url (str): The URL to fetch HTML from.

    Returns:
        JSONResponse: A JSON response containing the cleaned HTML content.
    """
    # Validate the URL format
    url_pattern = re.compile(
        r"^(https?://)"  # Must start with http or https
        r"([\w.-]+)"     # Domain name
        r"(\.[a-z]{2,6})"  # Top-level domain
        r"(:\d+)?(/.*)?$"  # Optional port and path
    )
    if not url_pattern.match(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            html_content = response.text
            
            # Clean up the HTML content by removing escape sequences
            cleaned_html = html_content.replace("\\n", "\n").replace('\\"', '"')
        
        return JSONResponse({"html": cleaned_html})
    except httpx.RequestError as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    except httpx.HTTPStatusError as e:
        return JSONResponse({"error": f"HTTP error: {e.response.status_code}"}, status_code=e.response.status_code)
