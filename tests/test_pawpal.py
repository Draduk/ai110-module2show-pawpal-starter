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
