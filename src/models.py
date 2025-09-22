from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum

class Platform(str, Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    GITHUB = "github"

class ProfileData(BaseModel):
    """Normalized profile data schema"""
    platform: Platform
    handle: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    verified: Optional[bool] = None
    posts_sample: List[str] = Field(default_factory=list)
    profile_image_url: Optional[str] = None
    website: Optional[str] = None
    joined_date: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    email: Optional[str] = None
    additional_data: Dict[str, Any] = Field(default_factory=dict)

class VerificationRequest(BaseModel):
    """Input request for profile verification"""
    profiles: List[HttpUrl]
    user_id: Optional[str] = None

class TrustScore(BaseModel):
    """Trust score breakdown"""
    overall: int = Field(..., ge=0, le=100)
    reputation: int = Field(..., ge=0, le=100)
    consistency: int = Field(..., ge=0, le=100)
    content_quality: int = Field(..., ge=0, le=100)

class Discrepancy(BaseModel):
    """Identified discrepancy between profiles"""
    field: str
    platforms: List[Platform]
    values: Dict[Platform, str]
    severity: str  # "low", "medium", "high"

class VerificationReport(BaseModel):
    """Final verification report"""
    trust_score: TrustScore
    profiles_analyzed: List[ProfileData]
    consistency_score: int = Field(..., ge=0, le=100)
    discrepancies: List[Discrepancy] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    analysis_summary: str
    same_person_confidence: int = Field(..., ge=0, le=100)
