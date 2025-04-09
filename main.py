from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# Enable CORS so your frontend can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.post("/api/fetch")
async def fetch_video(data: VideoRequest):
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "force_generic_extractor": False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)
        formats = [
            {
                "format_id": f["format_id"],
                "format_note": f.get("format_note", ""),
                "ext": f["ext"],
                "url": f["url"],
                "resolution": f.get("resolution") or f"{f.get('width')}x{f.get('height')}",
            }
            for f in info["formats"]
            if f["ext"] == "mp4"
            and "audio only" not in f.get("format_note", "").lower()
        ]
        return {
            "title": info["title"],
            "thumbnail": info["thumbnail"],
            "formats": formats,
        }
    except Exception as e:
        return {"error": str(e)}
