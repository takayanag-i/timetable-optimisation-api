from domain.logics.constraint_logic import get_enrolled_homeroom
from domain.constraints._base import ConstraintApplierBase
from domain.models.annual_lp_model import AnnualLpModel
import pulp


class CoursesPerDayConstraint(ConstraintApplierBase):
    """同日開講制約の制約定義クラス。"""

    def __init__(self, twice_course_list: list):
        self.twice_course_list = twice_course_list

    def apply(self, model: AnnualLpModel) -> AnnualLpModel:
        constraints = [
            pulp.lpSum(
                model.x[h, d, p, c] for p in model.data.homeroom_day_dict[h][d]
            ) <= self.get_max(c)
            for c in model.data.C
            if (h := get_enrolled_homeroom(model.data, c)) is not None
            for d in model.data.homeroom_day_dict[h]
        ]

        for constraint in constraints:
            model.problem += constraint

        return model

    def get_max(self, course: str) -> int:
        return 2 if course in self.twice_course_list else 1
