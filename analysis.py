from dataclasses import dataclass, asdict, fields
import csv
from uuid import uuid4
from enum import Enum, auto


DATA_ROOT = "./"
ASU_CONVOCATION_PATH = f"{DATA_ROOT}/asu/convocation_defaultveg_deidentified.csv"
ASU_RESEARCH_DAY_PATH = f"{DATA_ROOT}/asu/researchday_defaultveg_deidentified.csv"


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
    WRITTEN = "written"


class AgeRange(str, Enum):
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_54 = "45-54"
    AGE_55_64 = "55-64"
    AGE_65_74 = "65-74"


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
    def init_asu(asu_dict, source: ResponseSource) -> "SurveyResponse":
        diet_map = {
            "Other": Diet.WRITTEN,
            "Vegetarian": Diet.VEGETARIAN,
            "Vegan": Diet.VEGAN,
            "None of the above": Diet.OMNIVORE,
            "Pescatarian": Diet.PESCATARIAN,
            "": None,
        }
        race_map = {
            "White": Race.WHITE,
            "Asian": Race.ASIAN,
            "Black of African American": Race.BLACK_AA,
            "Other": Race.WRITTEN,
            "Prefer not to say": None,
            "": None,
        }
        satisfaction_map = {
            "Very unsatisfied": Likert.STRONGLY_DISAGREE,
            "Unsatisfied": Likert.DISAGREE,
            "Neither satisfied nor unsatisfied": Likert.NEUTRAL,
            "Satisfied": Likert.AGREE,
            "Very satisfied": Likert.STRONGLY_AGREE,
            "": None,
        }
        importance_map = {
            "Not important": Likert.STRONGLY_DISAGREE,
            "Not too important": Likert.DISAGREE,
            # "Not too important": Likert.NEUTRAL,
            "Important": Likert.AGREE,
            "Very important": Likert.STRONGLY_AGREE,
            "": None,
        }
        return SurveyResponse(
            uuid=uuid4(),
            source_id=asu_dict["ID"],
            source=source,
            default_meal=Meal.MEAT if "Meat" in asu_dict["Group"] else Meal.VEG,
            selected_meal=Meal.MEAT
            if "meat" in (asu_dict["DefaultVeg"] or asu_dict["DefaultMeat"])
            else Meal.VEG,
            eaten_meal=(
                asu_dict["MealServed"]
                and (Meal.MEAT if "meat" in asu_dict["MealServed"] else Meal.VEG)
            )
            or None,
            diet=diet_map[asu_dict["Default_Selection"]],
            diet_text=asu_dict["Diet"],
            race=race_map[asu_dict["Gender"]],
            race_text=asu_dict["Race"],
            ethnicity=Ethnicity.NON_LATIN
            if "Non" in asu_dict["Race_6_TEXT"]
            else (Ethnicity.LATIN if "Latin" in asu_dict["Race_6_TEXT"] else None),
            gender=Gender.MALE
            if "Male" == asu_dict["AgeGroup"]
            else (Gender.FEMALE if "Female" == asu_dict["AgeGroup"] else None),
            age=(asu_dict["Diet_4_TEXT"][:5] and AgeRange(asu_dict["Diet_4_TEXT"][:5]))
            or None,
            role=(asu_dict["Hispanic"] and Role(asu_dict["Hispanic"].lower())) or None,
            is_satisfied=satisfaction_map[asu_dict["Satisfaction"]],
            veg_is_important=importance_map[asu_dict["Plant_Importance"]],
            importance_reason=asu_dict["Plant_Importance_Why"],
            other_fields={},
        )

    @staticmethod
    def load_asu(path_to_csv: str, source: ResponseSource) -> list["SurveyResponse"]:
        reader = csv.DictReader(open(path_to_csv))
        return [SurveyResponse.init_asu(row, source) for row in reader]
