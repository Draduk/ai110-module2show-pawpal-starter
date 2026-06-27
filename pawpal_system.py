from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    task_id: str
    title: str
    duration_minutes: int
    priority: str
    notes: Optional[str] = None
    completed: bool = False

    def get_priority_score(self) -> int:
        """Return a numeric score for the task priority."""
        raise NotImplementedError


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    owner: Optional[Owner] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError


@dataclass
class Owner:
    owner_id: str
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet_id: str) -> None:
        raise NotImplementedError


@dataclass
class Scheduler:
    owner: Optional[Owner] = None
    pet: Optional[Pet] = None
    tasks: List[Task] = field(default_factory=list)

    def generate_schedule(self) -> List[Task]:
        """Build the daily schedule for the assigned pet."""
        raise NotImplementedError

    def sort_tasks_by_priority(self) -> List[Task]:
        raise NotImplementedError

    def filter_tasks_by_time(self, available_minutes: int) -> List[Task]:
        raise NotImplementedError

    def explain_schedule(self, schedule: List[Task]) -> str:
        raise NotImplementedError
