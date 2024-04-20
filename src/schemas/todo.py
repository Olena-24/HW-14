from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=250)
    completed: Optional[bool] = False


class ContactUpdateSchema(ContactSchema):
    completed: bool


class ContactResponse(ContactSchema):
    id: int = 1
    # title: str
    # description: str
    # completed: bool
    created_at: datetime | None
    updated_at: datetime | None
    user_id: int | None

    model_config = ConfigDict(from_attributes = True)  # noqa