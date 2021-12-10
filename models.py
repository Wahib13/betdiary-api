from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, HttpUrl, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class League(BaseModel):
    common_name: str
    url_upcoming_matches: HttpUrl
    url_current_data: HttpUrl
    current_data_filename: str


class Team(BaseModel):
    # name as appears in current data on their league
    dataframe_name: str
    # name as appears in upcoming matches
    upcoming_match_name: str
    league: League


class BetInfo(BaseModel):
    league: str
    home_team_name: str
    away_team_name: str
    home_team_form: float
    away_team_form: float
    form_difference: float
    scoring_probabilities: List[float]
    conceding_probabilities: List[float]
    job_id: str


class BetInfoInDB(BetInfo):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    # username: str
    email: str
    super_user: bool = False
    full_name: Optional[str] = ""
    enabled: Optional[bool] = True


# class UserInDB(User):
#     hashed_password: str
