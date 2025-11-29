"""ConsecutivePeriodInstructorConstraintクラスの単体テスト。"""

import pulp
from domain.constraints.consecutive_period_instructor import ConsecutivePeriodInstructorConstraint


def test_consecutive_period_instructor_constraint(mock_annual_model) -> None:
    """ConsecutivePeriodInstructorConstraintのapplyメソッドのテスト。

    テストデータ: D=["mon", "tue"], I=["I1", "I2"], P=[1, 2, 3]
    max_consecutive_lessons=3の場合、4コマ連続をチェック
    P=[1, 2, 3]なので、4コマ連続は不可能（最大3コマ）
    したがって、制約は追加されない（len(consecutive_periods) >= 4 の条件を満たさない）
    """
    constraint = ConsecutivePeriodInstructorConstraint(max_consecutive_lessons=3)
    model = constraint.apply(mock_annual_model)

    expected_constraints = []

    actual_constraints = [c.toDict() for c in model.problem.constraints.values()]

    assert len(actual_constraints) == len(expected_constraints), (
        f"制約の数が合いません。期待={len(expected_constraints)}, 実際={len(actual_constraints)}"
    )


def test_consecutive_period_instructor_constraint_with_more_periods(mock_annual_data):
    """より多くの時限がある場合のテスト。

    テストデータ: D=["mon", "tue"], I=["I1", "I2"], P=[1, 2, 3, 4, 5]
    max_consecutive_lessons=3の場合、4コマ連続をチェック
    big_M = max(len(periods)) = 5 (H2のmonが5時限)
    各教員（I1, I2）、各曜日（mon, tue）、各開始時限（1, 2）に対して制約が追加される
    期待される制約数: 2教員 × 2曜日 × 2開始時限 = 8つの制約
    """
    from domain.models.annual_lp_model import AnnualLpModel
    from infrastructure.solvers.gurobi_solver import GurobiSolver

    extended_data = mock_annual_data.model_copy(update={
        "P": [1, 2, 3, 4, 5],
        "homeroom_day_dict": {
            "H1": {"mon": [1, 2, 3, 4], "tue": [1, 2, 3]},
            "H2": {"mon": [1, 2, 3, 4, 5], "tue": [1, 2, 3, 4]},
            "H3": {"mon": [1, 2], "tue": [1, 2]},
        },
    })

    extended_model = AnnualLpModel(extended_data, [], GurobiSolver())

    constraint = ConsecutivePeriodInstructorConstraint(max_consecutive_lessons=3)
    model = constraint.apply(extended_model)

    expected_constraints = [
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_mon_1_I1", "value": 1},
                {"name": "y_mon_2_I1", "value": 1},
                {"name": "y_mon_3_I1", "value": 1},
                {"name": "y_mon_4_I1", "value": 1},
                {"name": "v^4_mon_1_I1", "value": -5},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_mon_2_I1", "value": 1},
                {"name": "y_mon_3_I1", "value": 1},
                {"name": "y_mon_4_I1", "value": 1},
                {"name": "y_mon_5_I1", "value": 1},
                {"name": "v^4_mon_2_I1", "value": -5},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_mon_1_I2", "value": 1},
                {"name": "y_mon_2_I2", "value": 1},
                {"name": "y_mon_3_I2", "value": 1},
                {"name": "y_mon_4_I2", "value": 1},
                {"name": "v^4_mon_1_I2", "value": -5},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_mon_2_I2", "value": 1},
                {"name": "y_mon_3_I2", "value": 1},
                {"name": "y_mon_4_I2", "value": 1},
                {"name": "y_mon_5_I2", "value": 1},
                {"name": "v^4_mon_2_I2", "value": -5},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_tue_1_I1", "value": 1},
                {"name": "y_tue_2_I1", "value": 1},
                {"name": "y_tue_3_I1", "value": 1},
                {"name": "y_tue_4_I1", "value": 1},
                {"name": "v^4_tue_1_I1", "value": -5},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_tue_2_I1", "value": 1},
                {"name": "y_tue_3_I1", "value": 1},
                {"name": "y_tue_4_I1", "value": 1},
                {"name": "y_tue_5_I1", "value": 1},
                {"name": "v^4_tue_2_I1", "value": -5},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_tue_1_I2", "value": 1},
                {"name": "y_tue_2_I2", "value": 1},
                {"name": "y_tue_3_I2", "value": 1},
                {"name": "y_tue_4_I2", "value": 1},
                {"name": "v^4_tue_1_I2", "value": -5},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -3,
            "coefficients": [
                {"name": "y_tue_2_I2", "value": 1},
                {"name": "y_tue_3_I2", "value": 1},
                {"name": "y_tue_4_I2", "value": 1},
                {"name": "y_tue_5_I2", "value": 1},
                {"name": "v^4_tue_2_I2", "value": -5},
            ],
        },
    ]

    actual_constraints = [c.toDict() for c in model.problem.constraints.values()]

    assert len(actual_constraints) == len(expected_constraints), (
        f"制約の数が合いません。期待={len(expected_constraints)}, 実際={len(actual_constraints)}"
    )

    for expected, actual in zip(expected_constraints, actual_constraints):
        assert expected["sense"] == actual["sense"]
        assert expected["constant"] == actual["constant"]

        expected_coefficients = expected["coefficients"]
        actual_coefficients = actual["coefficients"]

        assert len(expected_coefficients) == len(actual_coefficients)

        for e, a in zip(expected_coefficients, actual_coefficients):
            assert e["name"] == a["name"]
            assert e["value"] == a["value"]


def test_consecutive_period_instructor_constraint_with_custom_max(mock_annual_data):
    """カスタムmax_consecutive_lessons値でのテスト。

    テストデータ: D=["mon", "tue"], I=["I1", "I2"], P=[1, 2, 3, 4]
    max_consecutive_lessons=2の場合、3コマ連続をチェック
    big_M = max(len(periods)) = 4 (H1, H2のmonが4時限)
    各教員（I1, I2）、各曜日（mon, tue）、各開始時限（1, 2）に対して制約が追加される
    """
    from domain.models.annual_lp_model import AnnualLpModel
    from infrastructure.solvers.gurobi_solver import GurobiSolver

    extended_data = mock_annual_data.model_copy(update={
        "P": [1, 2, 3, 4],
        "homeroom_day_dict": {
            "H1": {"mon": [1, 2, 3, 4], "tue": [1, 2, 3]},
            "H2": {"mon": [1, 2, 3, 4], "tue": [1, 2, 3]},
            "H3": {"mon": [1, 2], "tue": [1, 2]},
        },
    })

    extended_model = AnnualLpModel(extended_data, [], GurobiSolver())

    constraint = ConsecutivePeriodInstructorConstraint(max_consecutive_lessons=2)
    model = constraint.apply(extended_model)

    expected_constraints = [
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_mon_1_I1", "value": 1},
                {"name": "y_mon_2_I1", "value": 1},
                {"name": "y_mon_3_I1", "value": 1},
                {"name": "v^4_mon_1_I1", "value": -4},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_mon_2_I1", "value": 1},
                {"name": "y_mon_3_I1", "value": 1},
                {"name": "y_mon_4_I1", "value": 1},
                {"name": "v^4_mon_2_I1", "value": -4},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_mon_1_I2", "value": 1},
                {"name": "y_mon_2_I2", "value": 1},
                {"name": "y_mon_3_I2", "value": 1},
                {"name": "v^4_mon_1_I2", "value": -4},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_mon_2_I2", "value": 1},
                {"name": "y_mon_3_I2", "value": 1},
                {"name": "y_mon_4_I2", "value": 1},
                {"name": "v^4_mon_2_I2", "value": -4},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_tue_1_I1", "value": 1},
                {"name": "y_tue_2_I1", "value": 1},
                {"name": "y_tue_3_I1", "value": 1},
                {"name": "v^4_tue_1_I1", "value": -4},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_tue_2_I1", "value": 1},
                {"name": "y_tue_3_I1", "value": 1},
                {"name": "y_tue_4_I1", "value": 1},
                {"name": "v^4_tue_2_I1", "value": -4},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_tue_1_I2", "value": 1},
                {"name": "y_tue_2_I2", "value": 1},
                {"name": "y_tue_3_I2", "value": 1},
                {"name": "v^4_tue_1_I2", "value": -4},
            ],
        },
        {
            "sense": pulp.LpConstraintLE,
            "constant": -2,
            "coefficients": [
                {"name": "y_tue_2_I2", "value": 1},
                {"name": "y_tue_3_I2", "value": 1},
                {"name": "y_tue_4_I2", "value": 1},
                {"name": "v^4_tue_2_I2", "value": -4},
            ],
        },
    ]

    actual_constraints = [c.toDict() for c in model.problem.constraints.values()]

    assert len(actual_constraints) == len(expected_constraints), (
        f"制約の数が合いません。期待={len(expected_constraints)}, 実際={len(actual_constraints)}"
    )

    for expected, actual in zip(expected_constraints, actual_constraints):
        assert expected["sense"] == actual["sense"]
        assert expected["constant"] == actual["constant"]

        expected_coefficients = expected["coefficients"]
        actual_coefficients = actual["coefficients"]

        assert len(expected_coefficients) == len(actual_coefficients)

        for e, a in zip(expected_coefficients, actual_coefficients):
            assert e["name"] == a["name"]
            assert e["value"] == a["value"]
