from dataclasses import dataclass, asdict, fields
import csv
from uuid import uuid4
from enum import Enum, auto


class ResponseSource(str, Enum):
    ASU_CONVOCATION = "asu_convocation"
    ASU_RESEARCH_DAY = "asu_research_day"
    UCLA = "ucla"
    UCSB_UG_EVENT = "ucsb_undergraduate_event"
    UCSB_GRAD_EVENT = "ucsb_graduate_event"
    UTA = "uta"


class Meal(str, Enum):
    MEAT = "meat"
    VEG = "veg"


class Diet(str, Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    PESCATARIAN = "pescatarian"
    OMNIVORE = "omnivore"
    OTHER = "other"


class AgeRange(str, Enum):
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_54 = "45-54"
    AGE_55_64 = "55-64"
    AGE_65 = "65+"


class AgeRange(str, Enum):
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_54 = "45-54"
    AGE_55_64 = "55-64"
    AGE_65 = "65+"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"


class Race(str, Enum):
    WHITE = "white"
    BLACK_AA = "black or african american"
    ASIAN = "asian"
    ARAB = "arab"
    MULTIRACIAL = "multiracial"
    WRITTEN = "written"


class Ethnicity(str, Enum):
    LATIN = "hispanic or latinx"
    NON_LATIN = "not hispanic or latinx"


class Role(str, Enum):
    STAFF = "staff"
    GRAD = "graduate_student"
    UG = "undergraduate_student"


class Likert(int, Enum):
    STRONGLY_DISAGREE = 1
    DISAGREE = 2
    NEUTRAL = 3
    AGREE = 4
    STRONGLY_AGREE = 5


@dataclass
class SurveyResponse:
    uuid: str
    source_id: int
    source: ResponseSource
    default_meal: Meal
    selected_meal: Meal
    eaten_meal: Meal
    diet: Diet
    diet_other_text: str
    race: Race
    race_text: str
    ethnicity: Ethnicity
    gender: Gender
    is_satisfied: Likert
    veg_is_important: Likert
    importance_reason: str
    other_fields: dict

    CSV_EXCLUDED_FIELDS = ("other_fields",)
    VARIABLE_FIELDS = (
        "diet_other_text",
        "race_text",
        "importance_reason",
        "other_fields",
    )

    def dict(self):
        return asdict(self)

    def csv_tuple(self):
        obj_dict = self.dict()
        return tuple(
            (obj_dict[field] for field in SurveyResponse.ordered_field_names())
        )

    @staticmethod
    def ordered_field_names():
        return tuple(
            (
                field.name
                for field in fields(SurveyResponse)
                if field.name not in SurveyResponse.CSV_EXCLUDED_FIELDS
            )
        )
