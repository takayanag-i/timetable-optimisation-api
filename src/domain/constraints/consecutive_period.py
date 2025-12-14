from domain.logics.constraint_logic import is_enrolled
from domain.constraints._base import ConstraintApplierBase
from domain.models.annual_lp_model import AnnualLpModel
import pulp
import math


class ConsecutivePeriodConstraint(ConstraintApplierBase):
    """2コマ連続開講制約の制約定義クラス。"""

    def __init__(self, courseId: str):
        self.course: str = courseId

    def apply(self, model: AnnualLpModel) -> AnnualLpModel:

        triple_constraints = [
            self._generate_triple_consecutive_constraint(model, h, d, p1, p2, p3)
            for h in model.data.H
            if is_enrolled(model.data, h, self.course)
            for d in model.data.D
            for p1, p2, p3 in zip(model.data.homeroom_day_dict[h][d], model.data.homeroom_day_dict[h][d][1:], model.data.homeroom_day_dict[h][d][2:])
        ]

        credit_constraint = pulp.lpSum(
            model.w[h, d, p1, p2, c]
            for (h, d, p1, p2, c) in model.w.keys()
            if c == self.course
        ) == math.floor(model.data.credit_dict[self.course] / 2)

        for constraint in triple_constraints:
            model.problem += constraint

        model.problem += credit_constraint

        return model

    def _generate_triple_consecutive_constraint(
        self,
        model: AnnualLpModel,
        h: str,
        d: str,
        p1: int,
        p2: int,
        p3: int
    ) -> pulp.LpConstraint:
        """3時限連続を拒否する制約を生成する"""
        return (
            model.x[h, d, p1, self.course] + model.x[h, d, p2, self.course] + model.x[h, d, p3, self.course] <= 2
        )
