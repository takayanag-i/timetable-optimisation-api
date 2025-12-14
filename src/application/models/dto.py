"""
Application DTOs (Data Transfer Objects)

このファイルには、アプリケーション層で使用される全てのDTOクラスが定義されています。
"""

from typing import Any, Generic, List, Optional, Tuple, TypeVar
from pydantic import BaseModel, ConfigDict, Field

from common.constants import ViolationCode

T = TypeVar("T")


# ===== Basic DTOs =====

class SchoolDayDto(BaseModel):
    """学校曜日DTO"""
    day: str = Field(..., description="曜日名", examples=["mon", "tue", "wed"])
    available: bool = Field(..., description="授業実施日かどうか")
    am_periods: Optional[int] = Field(None, alias="amPeriods", description="午前の時限数", examples=[4])
    pm_periods: Optional[int] = Field(None, alias="pmPeriods", description="午後の時限数", examples=[3])

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "day": "mon",
                "available": True,
                "amPeriods": 4,
                "pmPeriods": 3
            }
        }
    )


class HomeroomDayDto(BaseModel):
    """学級曜日DTO"""
    day: str = Field(..., description="曜日名", examples=["mon"])
    periods: int = Field(..., description="時限数", examples=[7])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "day": "mon",
                "periods": 7
            }
        }
    )


class HomeroomDto(BaseModel):
    """学級DTO"""
    id: str = Field(..., description="学級ID", examples=["1"])
    days: List[HomeroomDayDto] = Field(..., description="学級曜日リスト")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1",
                "days": [{"day": "mon", "periods": 7}]
            }
        }
    )


class AttendanceDayDto(BaseModel):
    """勤怠曜日DTO"""
    day: str = Field(..., description="曜日名", examples=["mon"])
    unavailable_periods: List[int] = Field(..., alias="unavailablePeriods", description="欠勤時限リスト", examples=[[5, 6, 7]])

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "day": "mon",
                "unavailablePeriods": [5, 6, 7]
            }
        }
    )


class InstructorDto(BaseModel):
    """教員DTO"""
    id: str = Field(..., description="教員ID", examples=["1"])
    days: List[AttendanceDayDto] = Field(..., description="勤怠曜日リスト")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1",
                "days": [{"day": "mon", "unavailablePeriods": [5, 6, 7]}]
            }
        }
    )


class RoomDto(BaseModel):
    """教室DTO"""
    id: str = Field(..., description="教室ID", examples=["1"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1"
            }
        }
    )


# ===== Course DTOs =====

class CourseDetailDto(BaseModel):
    """講座詳細DTO"""
    instructor_id: str = Field(..., alias="instructorId", description="教員ID", examples=["1"])
    room_id: Optional[str] = Field(None, alias="roomId", description="教室ID", examples=["1"])

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "instructorId": "1",
                "roomId": "1"
            }
        }
    )


class CourseDto(BaseModel):
    """講座DTO"""
    id: str = Field(..., description="講座ID", examples=["101"])
    credits: int = Field(..., description="単位数", examples=[5])
    courseDetails: List[CourseDetailDto] = Field(..., alias="courseDetails", description="講座詳細リスト")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "101",
                "credits": 5,
                "courseDetails": [{"instructorId": "1", "roomId": "1"}]
            }
        }
    )


# ===== Curriculum DTOs =====

class LaneDto(BaseModel):
    """レーンDTO"""
    course_ids: List[str] = Field(..., alias="courseIds", description="講座IDリスト", examples=[["101", "102"]])

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "courseIds": ["101", "102"]
            }
        }
    )


class BlockDto(BaseModel):
    """ブロックDTO"""
    id: str = Field(..., description="ブロックID", examples=["20"])
    lanes: List[LaneDto] = Field(..., description="レーンリスト")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "20",
                "lanes": [{"courseIds": ["101", "102"]}]
            }
        }
    )


class CurriculumDto(BaseModel):
    """カリキュラムDTO"""
    homeroom_id: str = Field(..., alias="homeroomId", description="学級ID", examples=["1"])
    blocks: List[BlockDto] = Field(..., description="ブロックリスト")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "homeroomId": "1",
                "blocks": [
                    {
                        "id": "20",
                        "name": "1-1共通",
                        "lanes": [{"courseIds": ["101", "102"]}]
                    }
                ]
            }
        }
    )


# ===== Constraint DTOs =====

class ConstraintParameterDto(BaseModel):
    """制約パラメータDTO"""
    key: str = Field(..., description="パラメータキー")
    value: str = Field(..., description="パラメータ値")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "max_periods",
                "value": "5"
            }
        }
    )


class ConstraintDefinitionDto(BaseModel):
    """制約定義DTO"""
    constraint_definition_code: str = Field(
        ..., alias="constraintDefinitionCode", description="制約定義コード", examples=["C001"]
    )
    soft_flag: bool = Field(..., alias="softFlag", description="ソフト制約かどうか")
    penalty_weight: Optional[float] = Field(None, alias="penaltyWeight", description="ペナルティ重み", examples=[0.5])
    parameters: Optional[List[ConstraintParameterDto]] = Field(default_factory=list, description="制約パラメータリスト")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "constraintDefinitionCode": "C001",
                "softFlag": False,
                "penaltyWeight": None,
                "parameters": []
            }
        }
    )


class ConstraintViolationDto(BaseModel, Generic[T]):
    """制約違反DTO"""
    violation_code: str
    violation_keys: List[T]


class V1ConstraintViolationDto(ConstraintViolationDto[str]):
    """午前午後制約違反DTO"""
    violation_code: str = ViolationCode.V1.value


class V2ConstraintViolationDto(ConstraintViolationDto[str]):
    """連続曜日制約違反DTO"""
    violation_code: str = ViolationCode.V2.value


class V3ConstraintViolationDto(ConstraintViolationDto[Tuple[str, str]]):
    """教員コマ数（１日）制約違反DTO"""
    violation_code: str = ViolationCode.V3.value


class V4ConstraintViolationDto(ConstraintViolationDto[Tuple[str, int, str]]):
    """教員連続コマ数制約違反DTO"""
    violation_code: str = ViolationCode.V4.value


# ===== Timetable DTOs =====

class TimetableEntryDto(BaseModel):
    """時間割エントリDTO"""
    homeroom: str = Field(..., description="学級ID", examples=["1"])
    day: str = Field(..., description="曜日名", examples=["mon"])
    period: int = Field(..., description="時限", examples=[1])
    course: str = Field(..., description="講座ID", examples=["101"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "homeroom": "1",
                "day": "mon",
                "period": 1,
                "course": "101"
            }
        }
    )


class AnnualTimetableResultDto(BaseModel):
    """年次時間割編成結果DTO"""
    entries: List[TimetableEntryDto] = Field(..., description="時間割エントリリスト")
    violations: List[ConstraintViolationDto[Any]] = Field(..., description="制約違反リスト")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entries": [
                    {"homeroom": "1", "day": "mon", "period": 1, "course": "101"}
                ],
                "violations": []
            }
        }
    )


# ===== Main DTOs =====

class AnnualDataDto(BaseModel):
    """年次データDTO"""
    school_days: List[SchoolDayDto] = Field(..., alias="schoolDays", description="学校曜日リスト")
    homerooms: List[HomeroomDto] = Field(..., description="学級リスト")
    instructors: List[InstructorDto] = Field(..., description="教員リスト")
    rooms: List[RoomDto] = Field(..., description="教室リスト")
    courses: List[CourseDto] = Field(..., description="講座リスト")
    curriculums: List[CurriculumDto] = Field(..., description="カリキュラムリスト")

    model_config = ConfigDict(populate_by_name=True)


class OptimiseAnnualTimetableDto(BaseModel):
    """年次時間割編成DTO"""
    ttid: str = Field(..., description="時間割ID（TTID）", examples=["550e8400-e29b-41d4-a716-446655440000"])
    annual_data: AnnualDataDto = Field(..., alias="annualData", description="年次データ")
    constraint_definitions: List[ConstraintDefinitionDto] = Field(
        ..., alias="constraintDefinitions", description="制約定義リスト"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "ttid": "demo",
                "annualData": {
                    "schoolDays": [
                        {"day": "mon", "available": True, "amPeriods": 4, "pmPeriods": 3}
                    ],
                    "homerooms": [
                        {"id": "1", "days": [{"day": "mon", "periods": 7}]}
                    ],
                    "instructors": [
                        {"id": "1", "days": [{"day": "mon", "unavailablePeriods": [5, 6, 7]}]}
                    ],
                    "rooms": [
                        {"id": "1"}
                    ],
                    "courses": [
                        {"id": "101", "credits": 5, "courseDetails": [{"instructorId": "1", "roomId": "1"}]}
                    ],
                    "curriculums": [
                        {"homeroomId": "1", "blocks": [{"id": "20", "lanes": [{"courseIds": ["101"]}]}]}
                    ]
                },
                "constraintDefinitions": [
                    {"constraintDefinitionCode": "C001", "softFlag": False}
                ]
            }
        }
    )
