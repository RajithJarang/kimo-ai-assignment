import json
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID, uuid4

from pydantic import Field, BaseModel

from .mongo_model import MongoModel


class CreatedUpdatedMixin(BaseModel):
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)


class RatingModel(BaseModel):
    rating: Dict[str, int] = {
        "total_ratings": 0,
        "positive_ratings": 0,
        "negative_ratings": 0
    }


class ChapterModel(CreatedUpdatedMixin, RatingModel, MongoModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    text: str


class CourseModel(CreatedUpdatedMixin, MongoModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    date: datetime
    description: str
    domain: List[str]
    rating: float = Field(default=0.0)
    chapters: List[ChapterModel]


class CourseModelList(MongoModel):
    count: int
    courses: List[CourseModel]
