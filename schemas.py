"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

# Example schemas (retain for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Instagram Content Creator core schema
class CreatorPost(BaseModel):
    """
    Content posts created in the studio
    Collection name: "creatorpost"
    """
    title: str = Field(..., description="Working title for the content")
    image_url: Optional[HttpUrl] = Field(None, description="Reference image URL to use for preview/publishing")
    caption: str = Field("", description="Final caption text")
    hashtags: List[str] = Field(default_factory=list, description="Selected hashtags")
    platforms: List[str] = Field(default_factory=lambda: ["instagram"], description="Target platforms")
    keywords: List[str] = Field(default_factory=list, description="Inspiration keywords")
    tone: Optional[str] = Field(None, description="Tone used for generation")
    audience: Optional[str] = Field(None, description="Target audience description")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publish datetime (ISO)")
    status: str = Field("draft", description="draft | scheduled | published")
