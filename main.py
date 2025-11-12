import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

from database import create_document, get_documents, db
from schemas import CreatorPost

app = FastAPI(title="Instagram Content Creator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Instagram Content Creator Backend"}


# Simple utilities for AI-like text generation placeholders
class CaptionRequest(BaseModel):
    topic: str = Field(..., description="What the post is about")
    tone: Optional[str] = Field(None, description="Tone of voice, e.g., playful, professional")
    audience: Optional[str] = Field(None, description="Target audience")
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to include")


class HashtagRequest(BaseModel):
    caption: str
    max_tags: int = 10


@app.post("/api/generate-caption")
def generate_caption(req: CaptionRequest):
    # Basic deterministic templated generation so it works offline
    tone = f" in a {req.tone} tone" if req.tone else ""
    audience = f" for {req.audience}" if req.audience else ""
    keywords = (
        " ".join([f"#{k.replace(' ', '')}" for k in req.keywords]) if req.keywords else ""
    )
    caption = (
        f"{req.topic.title()} — behind the scenes{tone}{audience}. "
        f"Crafted with passion, captured with intention. {keywords}"
    ).strip()
    return {"caption": caption}


@app.post("/api/suggest-hashtags")
def suggest_hashtags(req: HashtagRequest):
    base = [
        "#photography",
        "#instagood",
        "#creativelife",
        "#behindthescenes",
        "#contentcreator",
        "#reels",
        "#camera",
        "#studio",
        "#lightroom",
        "#capturethemoment",
    ]
    # Prioritize words in caption
    words = [w.strip(".,!?:;()[]{}\"'") for w in req.caption.lower().split()]
    extras = [f"#{w}" for w in words if w.isalpha() and len(w) > 4]
    seen = set()
    tags: List[str] = []
    for t in extras + base:
        if t not in seen:
            seen.add(t)
            tags.append(t)
        if len(tags) >= req.max_tags:
            break
    return {"hashtags": tags}


# Persistence endpoints
class SavePostRequest(CreatorPost):
    pass


@app.post("/api/posts")
def save_post(payload: SavePostRequest):
    try:
        post_id = create_document("creatorpost", payload)
        return {"id": post_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/posts")
def list_posts(limit: int = 50, status: Optional[str] = None):
    try:
        filt = {"status": status} if status else {}
        docs = get_documents("creatorpost", filt, limit)
        # Convert ObjectId to string for frontend
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
