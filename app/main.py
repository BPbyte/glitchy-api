from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.glitch import glitch_text, glitch_preview
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Initialize FastAPI app
app = FastAPI()

# Load environment variables
load_dotenv()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Glitchy Text Generator API"}

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Request models
class GlitchRequest(BaseModel):
    text: str = Field(..., max_length=50)
    style: str
    font: str = "cour"

class GlitchImageRequest(BaseModel):
    glitchedText: str
    font: str = "cour"

# Helper function for font size
def get_optimal_font_size(text, font_path, max_width, start_size=10, step=1, max_size=200):
    font_size = start_size
    while font_size <= max_size:
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width > max_width:
            break
        font_size += step
    return font_size - step if font_size > start_size else start_size

# Glitch text endpoint
@app.post("/glitch")
@limiter.limit("10/minute")
async def glitch(request: Request, body: GlitchRequest):
    glitched = glitch_text(body.text, body.style)
    return {"glitched_text": glitched}

# Glitch preview endpoint
@app.post("/glitch/preview")
async def glitch_preview_endpoint(body: GlitchRequest):
    print(f"Received: text={body.text}, style={body.style}, font={body.font}")
    preview = glitch_preview(body.text, body.style)
    return {"glitched_text": preview}

# Glitch image endpoint
@app.post("/glitch/image")
async def glitch_image(request: GlitchImageRequest):
    glitched = request.glitchedText
    print(f"Rendering: {glitched} with font: {request.font}")

    margin = 20
    image_width = 1200
    max_text_width = image_width - 2 * margin

    font_map = {
        "cour": "fonts/cour.ttf",
        "vt323": "fonts/vt323.ttf",
        "orbitron": "fonts/orbitron.ttf",
        "creepster": "fonts/creepster.ttf",
        "press-start": "fonts/press-start-2p.ttf"
    }
    font_path = font_map.get(request.font, "fonts/cour.ttf")

    # Use the helper function to get optimal font size
    font_size = get_optimal_font_size(glitched, font_path, max_text_width)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        print("Font fallback to default")
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    bbox = draw.textbbox((0, 0), glitched, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    image_height = text_height + 2 * margin
    img = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    text_x = (image_width - text_width) / 2
    text_y = margin
    draw.text((text_x, text_y), glitched, font=font, fill=(0, 255, 0, 255))

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return {"image_base64": f"data:image/png;base64,{img_base64}"}

# Global exception handler
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})