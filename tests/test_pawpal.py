import pytest
from pawpal_system import Owner, Pet, Task


def test_add_task_increases_count():
    owner = Owner(owner_id="o-test", name="Tester")
    pet = Pet(pet_id="p-test", name="Buddy", species="dog")
    owner.add_pet(pet)

    initial_count = len(pet.tasks)
    t = Task(task_id="t-test", title="Walk", duration_minutes=20, priority="high", preferred_time="morning")
    pet.add_task(t)

    assert len(pet.tasks) == initial_count + 1
    # ensure the task is the one we added
    assert pet.tasks[-1].task_id == "t-test"


def test_mark_complete_changes_status():
    t = Task(task_id="t2", title="Feed", duration_minutes=10, priority="medium")
    assert not t.completed
    t.mark_complete()
    assert t.completed


def test_sorting_correctness_by_time():
    # tasks added out of order should be returned in chronological order
    t1 = Task(task_id="a", title="A", duration_minutes=5, priority="low", time="09:15")
    t2 = Task(task_id="b", title="B", duration_minutes=5, priority="low", time="07:05")
    t3 = Task(task_id="c", title="C", duration_minutes=5, priority="low", time="12:30")

    from pawpal_system import Scheduler
    sched = Scheduler(tasks=[t1, t2, t3])
    ordered = sched.sort_tasks_by_time([t1, t2, t3])
    assert [t.task_id for t in ordered] == ["b", "a", "c"]


def test_recurrence_creates_next_daily_instance():
    owner = Owner(owner_id="o-test", name="RecTester")
    pet = Pet(pet_id="p-test", name="Buddy", species="dog")
    owner.add_pet(pet)

    t = Task(task_id="t-daily", title="Med", duration_minutes=5, priority="high", time="08:00", recurrence="daily")
    pet.add_task(t)

    from pawpal_system import Scheduler
    sched = Scheduler(owner=owner, pet=pet)
    new_task = sched.mark_task_complete_with_recurrence("t-daily")

    assert t.completed
    assert new_task is not None
    assert new_task.recurrence == "daily"
    assert not new_task.completed
    # new task should be attached to the same pet
    assert any(tt.task_id == new_task.task_id for tt in pet.tasks)


def test_conflict_detection_flags_duplicate_times():
    pet = Pet(pet_id="p-c", name="Conflicty", species="cat")
    t1 = Task(task_id="t1", title="Feed", duration_minutes=10, priority="high", time="09:00")
    t2 = Task(task_id="t2", title="Vet", duration_minutes=15, priority="high", time="09:00")
    pet.add_task(t1)
    pet.add_task(t2)

    from pawpal_system import Scheduler
    sched = Scheduler(pet=pet)
    schedule = sched.generate_schedule()
    warnings = sched.get_conflict_warnings(schedule)
    assert warnings, "Expected conflict warnings for overlapping tasks"
    # ensure the warning mentions both task titles
    joined = " ".join(warnings)
    assert "Feed" in joined and "Vet" in joined
