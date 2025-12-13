from domain.vo.annual_data import AnnualDataVo


def is_enrolled(data: AnnualDataVo, h: str, c: str) -> bool:
    """学級 h が講座 c を履修しているか"""
    return any(c in lane for block in data.curriculum_dict[h] for lane in block)


def get_enrolled_homeroom(data: AnnualDataVo, c: str) -> str | None:
    """講座 c を履修している学級を1つ取得する。該当する学級がない場合はNoneを返す"""
    enrolled_homerooms = [h for h in data.H if is_enrolled(data, h, c)]
    return min(enrolled_homerooms) if enrolled_homerooms else None


def is_instructor_of_course(data: AnnualDataVo, i: str, c: str) -> bool:
    """教員 i が講座 c を担当しているか"""
    return any(i == detail.instructor_id for detail in data.course_details_dict[c])
