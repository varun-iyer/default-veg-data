from dataclasses import dataclass, asdict, fields
from typing import Union
import csv
from uuid import uuid4
from enum import Enum, auto
import re

DATA_ROOT = "./"
ASU_CONVOCATION_PATH = f"{DATA_ROOT}/asu/convocation_defaultveg_deidentified.csv"
ASU_RESEARCH_DAY_PATH = f"{DATA_ROOT}/asu/researchday_defaultveg_deidentified.csv"
UCLA_PATH = f"{DATA_ROOT}/ucla/combined_data.csv"
UTA_PATH = f"{DATA_ROOT}/uta/Pre v Post Responses.csv"
UCSB_UG_EVENT_PATH = f"{DATA_ROOT}/ucsb/undergraduate.csv"
UCSB_GRAD_EVENT_PATH = f"{DATA_ROOT}/ucsb/graduate.csv"


class ResponseSource(str, Enum):
    ASU_CONVOCATION = "asu_convocation"
    ASU_RESEARCH_DAY = "asu_research_day"
    UCLA = "ucla"
    UCSB_UG_EVENT = "ucsb_undergraduate_event"
    UCSB_GRAD_EVENT = "ucsb_graduate_event"
    UTA = "uta"

    @staticmethod
    def path(source: "ResponseSource"):
        return ({
            ResponseSource.ASU_CONVOCATION: ASU_CONVOCATION_PATH,
            ResponseSource.ASU_RESEARCH_DAY: ASU_RESEARCH_DAY_PATH,
            ResponseSource.UCLA: UCLA_PATH,
            ResponseSource.UCSB_UG_EVENT: UCSB_UG_EVENT_PATH,
            ResponseSource.UCSB_GRAD_EVENT: UCSB_GRAD_EVENT_PATH,
            ResponseSource.UTA: UTA_PATH,
        })[source]


class Meal(str, Enum):
    MEAT = "meat"
    VEG = "veg"

    @staticmethod
    def other(meal: "Meal"):
        if meal == Meal.MEAT:
            return Meal.VEG
        return Meal.MEAT

    @staticmethod
    def parse(text: str) -> Union["Meal", None]:
        text = text.lower()
        if re.search(r"\bmeat\b", text):
            return Meal.MEAT
        if "plant" in text or "veg" in text:
            return Meal.VEG
        return None


class Diet(str, Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    PESCATARIAN = "pescatarian"
    OMNIVORE = "omnivore"
    WRITTEN = "written"

    @staticmethod
    def parse(text: str) -> Union["Diet", None]:
        text = text.lower()
        diet_map = {
            "other": Diet.WRITTEN,
            "vegetarian": Diet.VEGETARIAN,
            "vegan": Diet.VEGAN,
            "none of the above": Diet.OMNIVORE,
            "pescatarian": Diet.PESCATARIAN,
            "na": Diet.OMNIVORE,
            "none": Diet.OMNIVORE,
            "omnivorous": Diet.OMNIVORE,
            "flexitarian": Diet.OMNIVORE,
        }
        if text in diet_map:
            return diet_map[text]
        return None


class AgeRange(str, Enum):
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_54 = "45-54"
    AGE_55_64 = "55-64"
    AGE_65_74 = "65-74"

    @staticmethod
    def parse(text: str) -> Union["AgeRange", None]:
        ages = re.search("\d\d-\d\d", text)
        try:
            return AgeRange(ages.group())
        except (ValueError, AttributeError):
            return None


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"

    @staticmethod
    def parse(text: str) -> Union["Gender", None]:
        try:
            return Gender(text.lower())
        except ValueError:
            pass
        return None


class Race(str, Enum):
    WHITE = "white"
    BLACK_AA = "black or african american"
    ASIAN = "asian"
    ARAB = "arab"
    MULTIRACIAL = "multiracial"
    WRITTEN = "written"

    @staticmethod
    def parse(text: str) -> Union["Race", None]:
        try:
            return Race(text.lower())
        except ValueError:
            pass
        try:
            return ({
                "black of african American": Race.BLACK_AA,
                "other": Race.WRITTEN,
                "mixed (mestiza)": Race.MULTIRACIAL,
            })[text.lower()]
        except KeyError:
            pass
        return None


class Ethnicity(str, Enum):
    LATIN = "hispanic or latinx"
    NON_LATIN = "not hispanic or latinx"

    @staticmethod
    def parse(text: str) -> Union["Ethnicity", None]:
        text = text.lower()
        if "non" in text or "not" in text or "no" in text:
            return Ethnicity.NON_LATIN
        if "latin" in text or "yes" in text:
            return Ethnicity.LATIN
        return None


class Role(str, Enum):
    STAFF = "staff"
    GRAD = "graduate_student"
    UG = "undergraduate_student"

    @staticmethod
    def parse(text: str):
        text = text.lower()
        for role in Role:
            if role.value.replace("_", " ") == text:
                return role
        return None


class Likert(int, Enum):
    VERY_STRONGLY_DISAGREE = 0
    STRONGLY_DISAGREE = 1
    DISAGREE = 2
    NEUTRAL = 3
    AGREE = 4
    STRONGLY_AGREE = 5
    VERY_STRONGLY_AGREE = 6

    @staticmethod
    def parse(text: str) -> Union['Likert', None]:
        satisfaction_map = {
            "very unsatisfied": Likert.STRONGLY_DISAGREE,
            "extremely dissatisfied": Likert.VERY_STRONGLY_DISAGREE,
            "unsatisfied": Likert.DISAGREE,
            "moderately dissatisfied": Likert.STRONGLY_DISAGREE,
            "slightly dissatisfied": Likert.DISAGREE,
            "neither satisfied nor unsatisfied": Likert.NEUTRAL,
            "neither satisfied nor dissatisfied": Likert.NEUTRAL,
            "satisfied": Likert.AGREE,
            "moderately satisfied": Likert.STRONGLY_AGREE,
            "slightly satisfied": Likert.AGREE,
            "very satisfied": Likert.STRONGLY_AGREE,
            "extremely satisfied": Likert.VERY_STRONGLY_AGREE,
            "": None,
            "not important": Likert.STRONGLY_DISAGREE,
            "not too important": Likert.DISAGREE,
            # "Not too important": Likert.NEUTRAL,
            "important": Likert.AGREE,
            "very important": Likert.STRONGLY_AGREE,
        }
        try:
            return satisfaction_map[text.lower()]
        except KeyError:
            return None


@dataclass
class SurveyResponse:
    uuid: str
    source_id: int | str | None
    source: ResponseSource
    default_meal: Meal
    selected_meal: Meal
    eaten_meal: Meal | None
    diet: Diet | None
    diet_text: str
    race: Race | None
    race_text: str
    ethnicity: Ethnicity | None
    gender: Gender | None
    age: AgeRange | None
    role: Role | None
    is_satisfied: Likert | None
    veg_is_important: Likert | None
    importance_reason: str
    other_fields: dict

    CSV_EXCLUDED_FIELDS = ("other_fields",)
    VARIABLE_FIELDS = (
        "diet_other_text",
        "race_text",
        "importance_reason",
        "other_fields",
    )

    def dict(self) -> dict:
        return asdict(self)

    def csv_tuple(self) -> tuple:
        obj_dict = self.dict()
        return tuple(
            (obj_dict[field] for field in SurveyResponse.ordered_field_names())
        )

    @staticmethod
    def ordered_field_names() -> tuple:
        return tuple(
            (
                field.name
                for field in fields(SurveyResponse)
                if field.name not in SurveyResponse.CSV_EXCLUDED_FIELDS
            )
        )

    @staticmethod
    def init_asu(asu_dict: dict, source: ResponseSource) -> "SurveyResponse":
        return SurveyResponse(
            uuid=uuid4(),
            source_id=asu_dict["ID"],
            source=source,
            default_meal=Meal.parse(asu_dict["Group"]),
            selected_meal=Meal.parse(asu_dict["DefaultVeg"]),
            eaten_meal=Meal.parse(asu_dict["MealServed"]),
            diet=Diet.parse(asu_dict["Default_Selection"]),
            diet_text=asu_dict["Diet"],
            race=Race.parse(asu_dict["Gender"]),
            race_text=asu_dict["Race"],
            ethnicity=Ethnicity.parse(asu_dict["Race_6_TEXT"]),
            gender=Gender.parse(asu_dict["AgeGroup"]),
            age=AgeRange.parse(asu_dict["Diet_4_TEXT"]),
            role=Role.parse(asu_dict["Hispanic"]),
            is_satisfied=AgeRange.parse(asu_dict["Satisfaction"]),
            veg_is_important=Likert.parse(asu_dict["Plant_Importance"]),
            importance_reason=Likert.parse(asu_dict["Plant_Importance_Why"]),
            other_fields={},
        )

    @staticmethod
    def init_ucla(ucla_dict: dict, source=ResponseSource.UCLA) -> "SurveyResponse":
        selected = Meal.parse(ucla_dict["mealSelection"])
        return SurveyResponse(
            uuid=uuid4(),
            source_id=None,
            source=source,
            default_meal=selected if "Stay" in ucla_dict["mealSelection"] else Meal.other(selected),
            selected_meal=selected,
            eaten_meal=Meal.parse(ucla_dict["mealEaten"]),
            diet=Diet.parse(ucla_dict["dietaryInfo"]),
            diet_text=ucla_dict["dietaryInfo"],
            race=Race.parse(ucla_dict["race"]),
            race_text=ucla_dict["race"],
            ethnicity=Ethnicity.parse(ucla_dict["ethnicity"]),
            gender=None,
            age=AgeRange.parse(ucla_dict["age"]),
            role=Role.parse(ucla_dict["employment"]),
            is_satisfied=Likert.parse(ucla_dict["satisfaction"]),
            veg_is_important=None,
            importance_reason=ucla_dict["rationale"],
            other_fields={"importance": ucla_dict["importance"]},
        )

    @staticmethod
    def init_uta(uta_dict: dict, source=ResponseSource.UTA) -> "SurveyResponse":
        default = Meal.MEAT if uta_dict["Animal"] else Meal.VEG
        return SurveyResponse(
            uuid=uuid4(),
            source_id=uta_dict.pop("ID"),
            source=source,
            default_meal=default,
            selected_meal=Meal.parse(uta_dict.pop("Animal")) or Meal.parse(uta_dict.pop("Plant")),
            eaten_meal=Meal.parse(uta_dict.pop("Meal Provided")),
            diet=Diet.parse(uta_dict["Diet pattern"]),
            diet_text=uta_dict.pop("Diet pattern"),
            race=Race.parse(uta_dict["Ethnicity"]),
            race_text=uta_dict.pop("Ethnicity"),
            ethnicity=Ethnicity.parse(uta_dict.pop("Hispanic")),
            gender=Gender.parse(uta_dict.pop("Gender")),
            age=None,
            role=None,
            is_satisfied=Likert.parse(uta_dict.pop("Meal Satisfaction")),
            veg_is_important=None,
            importance_reason=uta_dict.pop("Plant-based Importance"),
            other_fields=uta_dict,
        )

    @staticmethod
    def init_ucsb(ucsb_dict: dict, source: ResponseSource) -> "SurveyResponse":
        default = Meal.MEAT if ucsb_dict["meat_default"] else Meal.VEG
        return SurveyResponse(
            uuid=uuid4(),
            source_id=None,
            source=source,
            default_meal=default,
            selected_meal=Meal.parse(ucsb_dict.pop("plant_default")) or Meal.parse(ucsb_dict.pop("meat_default")),
            eaten_meal=None,
            diet=Diet.parse(ucsb_dict["diet"]),
            diet_text=ucsb_dict.pop("diet"),
            race=None,
            race_text=None,
            ethnicity=None,
            gender=Gender.FEMALE,
            age=AgeRange.parse(ucsb_dict.pop("age")),
            role=Role.GRAD if source == ResponseSource.UCSB_GRAD_EVENT else Role.UG,
            is_satisfied=None,
            veg_is_important=None,
            importance_reason=None,
            other_fields=None,
        )

    @staticmethod
    def init_method(source: ResponseSource):
        return ({
            ResponseSource.ASU_CONVOCATION: SurveyResponse.init_asu,
            ResponseSource.ASU_RESEARCH_DAY: SurveyResponse.init_asu,
            ResponseSource.UCLA: SurveyResponse.init_ucla,
            ResponseSource.UCSB_UG_EVENT: SurveyResponse.init_ucsb,
            ResponseSource.UCSB_GRAD_EVENT: SurveyResponse.init_ucsb,
            ResponseSource.UTA: SurveyResponse.init_uta,
        })[source]

    @staticmethod
    def load(source: ResponseSource) -> list["SurveyResponse"]:
        function = SurveyResponse.init_method(source)
        path_to_csv = ResponseSource.path(source)
        reader = csv.DictReader(open(path_to_csv))
        return [function(row, source) for row in reader]
