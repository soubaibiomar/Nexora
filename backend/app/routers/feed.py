"""
Feed / Posts API Router
Provides social feed functionality with posts, likes, comments, and media uploads.
Uses in-memory storage with fallback data from JSONL files.
"""

import json
import uuid
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from pydantic import BaseModel
import random
from ..auth_guards import require_auth

router = APIRouter(prefix="/api/feed", tags=["Feed"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg", "video/quicktime"}
ALLOWED_FILE_TYPES = {
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/zip", "text/plain", "text/csv",
}
ALL_ALLOWED = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES | ALLOWED_FILE_TYPES

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ── Models ──────────────────────────────────────────────────────────

class PostCreate(BaseModel):
    author_id: str = ""
    author_name: str = "You"
    content: str
    post_type: str = "text"  # text, article, celebration, job_change, media

class CommentCreate(BaseModel):
    author_name: str = "You"
    content: str

class LikeRequest(BaseModel):
    user_id: str = "current_user"


# ── In-memory store ────────────────────────────────────────────────

_posts: List[dict] = []
_initialized = False


def _load_employees():
    path = DATA_DIR / "employees.jsonl"
    employees = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    employees.append(json.loads(line))
    return employees


def _get_media_type(content_type: str) -> str:
    """Determine media type (image, video, file) from content-type."""
    if content_type in ALLOWED_IMAGE_TYPES:
        return "image"
    elif content_type in ALLOWED_VIDEO_TYPES:
        return "video"
    else:
        return "file"


def _init_feed():
    global _posts, _initialized
    if _initialized:
        return
    employees = _load_employees()
    if not employees:
        _initialized = True
        return

    post_templates = [
        {"type": "celebration", "template": "🎉 Excited to announce that I've been promoted to {role}! Thank you to everyone who supported me on this journey. #growth #career"},
        {"type": "text", "template": "Great session today on cloud architecture patterns. Key takeaway: always design for failure. #engineering #cloud"},
        {"type": "article", "template": "Just published my thoughts on the future of {dept}. The industry is evolving rapidly and we need to stay ahead. What do you think?"},
        {"type": "text", "template": "Looking for recommendations on the best practices for microservices. Any suggestions from the community?"},
        {"type": "celebration", "template": "Thrilled to join the {dept} team! Can't wait to contribute and learn from such talented colleagues. #newbeginnings"},
        {"type": "text", "template": "Attended an amazing workshop on machine learning today. The possibilities are endless! #AI #ML"},
        {"type": "text", "template": "Tip of the day: Always write tests before refactoring. Saved me hours of debugging this week. #SoftwareEngineering"},
        {"type": "article", "template": "Why {dept} is the most critical function in modern organizations — a thread 🧵"},
        {"type": "text", "template": "Incredible talk by our CTO on innovation and disruption. Feeling inspired to build something great! 🚀"},
        {"type": "celebration", "template": "5 years at the company today! Time flies when you're working with amazing people. #workanniversary"},
        {"type": "text", "template": "Exploring new tools for data visualization. D3.js vs Recharts — what's your preference?"},
        {"type": "text", "template": "The importance of code reviews cannot be overstated. Just caught a critical bug thanks to a peer review. #teamwork"},
        {"type": "article", "template": "How we reduced our deployment time by 60% using CI/CD pipelines. Full writeup coming soon!"},
        {"type": "text", "template": "Remote work has taught me so much about async communication. Here are my top 3 tips..."},
        {"type": "celebration", "template": "Our team just shipped a major feature! Proud of what we accomplished together. 🎊 #teamwork"},
    ]

    # Sample media for some posts (free stock images via picsum.photos)
    post_media = {
        0: [  # celebration post
            {"id": "media_1", "filename": "celebration.jpg", "url": "https://picsum.photos/seed/celebrate/800/500", "content_type": "image/jpeg", "media_type": "image", "size": 120000},
        ],
        1: [  # cloud architecture
            {"id": "media_2", "filename": "architecture.jpg", "url": "https://picsum.photos/seed/cloud-arch/800/450", "content_type": "image/jpeg", "media_type": "image", "size": 95000},
        ],
        4: [  # new team
            {"id": "media_3", "filename": "team_welcome.jpg", "url": "https://picsum.photos/seed/team-welcome/800/500", "content_type": "image/jpeg", "media_type": "image", "size": 110000},
        ],
        5: [  # ML workshop — two images
            {"id": "media_4", "filename": "ml_workshop.jpg", "url": "https://picsum.photos/seed/ml-workshop/800/450", "content_type": "image/jpeg", "media_type": "image", "size": 88000},
            {"id": "media_5", "filename": "ai_demo.jpg", "url": "https://picsum.photos/seed/ai-demo/800/450", "content_type": "image/jpeg", "media_type": "image", "size": 92000},
        ],
        8: [  # CTO talk
            {"id": "media_6", "filename": "keynote.jpg", "url": "https://picsum.photos/seed/keynote-talk/800/450", "content_type": "image/jpeg", "media_type": "image", "size": 105000},
        ],
        9: [  # anniversary
            {"id": "media_7", "filename": "anniversary.jpg", "url": "https://picsum.photos/seed/anniversary/800/500", "content_type": "image/jpeg", "media_type": "image", "size": 98000},
        ],
        12: [  # CI/CD — video
            {"id": "media_8", "filename": "cicd_demo.mp4", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "content_type": "video/mp4", "media_type": "video", "size": 2500000},
        ],
        14: [  # team ship — two images
            {"id": "media_9", "filename": "feature_launch.jpg", "url": "https://picsum.photos/seed/launch-day/800/450", "content_type": "image/jpeg", "media_type": "image", "size": 115000},
            {"id": "media_10", "filename": "team_party.jpg", "url": "https://picsum.photos/seed/team-party/800/500", "content_type": "image/jpeg", "media_type": "image", "size": 130000},
        ],
    }

    now = datetime.utcnow()
    for i, tmpl in enumerate(post_templates):
        emp = employees[i % len(employees)]
        content = tmpl["template"].format(
            role=emp.get("role", "Senior Engineer"),
            dept=emp.get("department", "Engineering"),
        )
        likes = random.randint(5, 120)
        comments_count = random.randint(0, 15)

        # Generate avatar URL from employee name
        emp_name = emp.get("name", f"Employee {i}")
        avatar_url = f"https://ui-avatars.com/api/?name={emp_name.replace(' ', '+')}&background=0A66C2&color=fff&size=128&bold=true"

        post = {
            "id": str(uuid.uuid4()),
            "author_id": emp.get("id", f"emp_{i}"),
            "author_name": emp_name,
            "author_role": emp.get("role", "Engineer"),
            "author_department": emp.get("department", "Engineering"),
            "author_location": emp.get("location", ""),
            "author_avatar": avatar_url,
            "content": content,
            "post_type": tmpl["type"],
            "media": post_media.get(i, []),
            "created_at": (now - timedelta(hours=i * 3 + random.randint(0, 5))).isoformat(),
            "likes": likes,
            "liked_by": [],
            "comments": [],
            "comments_count": comments_count,
            "shares": random.randint(0, 20),
        }
        _posts.append(post)

    _initialized = True


# ── Endpoints ───────────────────────────────────────────────────────

@router.get("")
async def get_feed(skip: int = 0, limit: int = 10, _user: dict = Depends(require_auth)):
    _init_feed()
    sorted_posts = sorted(_posts, key=lambda p: p["created_at"], reverse=True)
    return {
        "posts": sorted_posts[skip:skip + limit],
        "total": len(sorted_posts),
        "has_more": skip + limit < len(sorted_posts),
    }


@router.post("/posts")
async def create_post(post: PostCreate, _user: dict = Depends(require_auth)):
    _init_feed()
    new_post = {
        "id": str(uuid.uuid4()),
        "author_id": post.author_id or "current_user",
        "author_name": post.author_name,
        "author_role": "Professional",
        "author_department": "",
        "author_location": "",
        "content": post.content,
        "post_type": post.post_type,
        "media": [],
        "created_at": datetime.utcnow().isoformat(),
        "likes": 0,
        "liked_by": [],
        "comments": [],
        "comments_count": 0,
        "shares": 0,
    }
    _posts.insert(0, new_post)
    return new_post


@router.post("/posts/with-media")
async def create_post_with_media(
    content: str = Form(""),
    post_type: str = Form("text"),
    author_name: str = Form("You"),
    files: List[UploadFile] = File(default=[]),
):
    """
    Create a post with optional media attachments (images, videos, files).
    Accepts multipart/form-data.
    """
    _init_feed()

    media_items = []

    for uploaded_file in files:
        # Validate content type
        ct = uploaded_file.content_type or "application/octet-stream"
        if ct not in ALL_ALLOWED:
            # Still accept it as a generic file
            ct = "application/octet-stream"

        # Generate unique filename
        ext = Path(uploaded_file.filename or "file").suffix or ".bin"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / unique_name

        # Save file
        with open(file_path, "wb") as buffer:
            content_bytes = await uploaded_file.read()
            if len(content_bytes) > MAX_FILE_SIZE:
                continue  # skip oversized files
            buffer.write(content_bytes)

        media_type = _get_media_type(ct)

        media_items.append({
            "id": str(uuid.uuid4()),
            "filename": uploaded_file.filename,
            "stored_name": unique_name,
            "url": f"/uploads/{unique_name}",
            "content_type": ct,
            "media_type": media_type,  # image | video | file
            "size": len(content_bytes),
        })

    # Determine post type based on media
    effective_type = post_type
    if media_items and post_type == "text":
        first_type = media_items[0]["media_type"]
        if first_type == "image":
            effective_type = "photo"
        elif first_type == "video":
            effective_type = "video"
        else:
            effective_type = "document"

    new_post = {
        "id": str(uuid.uuid4()),
        "author_id": "current_user",
        "author_name": author_name,
        "author_role": "Professional",
        "author_department": "",
        "author_location": "",
        "content": content,
        "post_type": effective_type,
        "media": media_items,
        "created_at": datetime.utcnow().isoformat(),
        "likes": 0,
        "liked_by": [],
        "comments": [],
        "comments_count": 0,
        "shares": 0,
    }
    _posts.insert(0, new_post)
    return new_post


@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, req: LikeRequest, _user: dict = Depends(require_auth)):
    _init_feed()
    for post in _posts:
        if post["id"] == post_id:
            if req.user_id in post["liked_by"]:
                post["liked_by"].remove(req.user_id)
                post["likes"] = max(0, post["likes"] - 1)
                return {"liked": False, "likes": post["likes"]}
            else:
                post["liked_by"].append(req.user_id)
                post["likes"] += 1
                return {"liked": True, "likes": post["likes"]}
    return {"error": "Post not found"}


@router.post("/posts/{post_id}/comment")
async def comment_post(post_id: str, comment: CommentCreate, _user: dict = Depends(require_auth)):
    _init_feed()
    for post in _posts:
        if post["id"] == post_id:
            new_comment = {
                "id": str(uuid.uuid4()),
                "author_name": comment.author_name,
                "content": comment.content,
                "created_at": datetime.utcnow().isoformat(),
                "likes": 0,
            }
            post["comments"].append(new_comment)
            post["comments_count"] = len(post["comments"])
            return new_comment
    return {"error": "Post not found"}
