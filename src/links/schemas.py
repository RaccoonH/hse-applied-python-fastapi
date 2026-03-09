from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LinkCreate(BaseModel):
    orig_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkUpdate(BaseModel):
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None
