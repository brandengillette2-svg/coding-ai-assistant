from app.task_planner import TaskPlanner


def test_plan_has_expected_steps():
    planner = TaskPlanner()
    plan = planner.plan("fix the login bug")
    assert any(step["name"] == "reproduce_issue" for step in plan)
    assert any(step["name"] == "verify" for step in plan)
