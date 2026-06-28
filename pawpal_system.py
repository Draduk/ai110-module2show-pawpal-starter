from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

PRIORITY_SCORE = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

PREFERRED_TIME_ORDER = {
    "morning": 1,
    "afternoon": 2,
    "evening": 3,
    "any": 4,
}

DEFAULT_TIME_PERIODS = ["morning", "afternoon", "evening"]
VALID_RECURRENCE = {"once", "daily", "weekly"}
VALID_PRIORITIES = set(PRIORITY_SCORE.keys())
VALID_TIME_PERIODS = set(DEFAULT_TIME_PERIODS)


@dataclass
class Task:
    task_id: str
    title: str
    duration_minutes: int
    priority: str
    preferred_time: str = "any"
    recurrence: str = "once"
    notes: Optional[str] = None
    completed: bool = False

    def __post_init__(self) -> None:
        """Normalize and validate task fields after initialization."""
        self.priority = self.priority.lower()
        self.preferred_time = self.preferred_time.lower()
        self.recurrence = self.recurrence.lower()

        if self.priority not in VALID_PRIORITIES:
            self.priority = "low"

        if self.preferred_time not in VALID_TIME_PERIODS and self.preferred_time != "any":
            self.preferred_time = "any"

        if self.recurrence not in VALID_RECURRENCE:
            self.recurrence = "once"

        if self.duration_minutes < 0:
            self.duration_minutes = 0

    def get_priority_score(self) -> int:
        """Return numeric score for this task's priority."""
        return PRIORITY_SCORE.get(self.priority, 0)

    def get_preferred_time_order(self) -> int:
        """Return ordering index for the task's preferred time period."""
        return PREFERRED_TIME_ORDER.get(self.preferred_time, PREFERRED_TIME_ORDER["any"])

    def matches_time_period(self, period: str) -> bool:
        """Check whether this task can be scheduled in the given period."""
        return self.preferred_time == period or self.preferred_time == "any"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class ScheduleItem:
    task: Task
    time_of_day: str
    explanation: str = ""

    def formatted_time_range(self) -> str:
        return self.time_of_day.capitalize()


@dataclass
class Owner:
    owner_id: str
    name: str
    available_minutes_per_day: int = 120
    preferences: Dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner (keeps bidirectional link)."""
        if any(existing.pet_id == pet.pet_id for existing in self.pets):
            return
        self.pets.append(pet)
        pet.owner = self

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet by id and clear its owner link."""
        removed_pets = [pet for pet in self.pets if pet.pet_id == pet_id]
        self.pets = [pet for pet in self.pets if pet.pet_id != pet_id]
        for pet in removed_pets:
            pet.owner = None


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    owner: Optional[Owner] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet, ignoring duplicates."""
        if any(existing.task_id == task.task_id for existing in self.tasks):
            return
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by id from this pet."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def get_task(self, task_id: str) -> Optional[Task]:
        """Return a task by id if it exists, otherwise None."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None


@dataclass
class Scheduler:
    owner: Optional[Owner] = None
    pet: Optional[Pet] = None
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.pet and self.pet.owner and self.owner is None:
            self.owner = self.pet.owner

    def _get_task_source(self) -> List[Task]:
        """Return the list of tasks to schedule (explicit list or pet.tasks)."""
        if self.tasks:
            return self.tasks
        if self.pet:
            return self.pet.tasks
        return []

    def generate_schedule(self, available_minutes: Optional[int] = None) -> List[ScheduleItem]:
        """Generate a simple schedule (assign tasks to morning/afternoon/evening).

        The scheduler selects tasks by priority and fits them into the available
        minutes, then assigns each to a time period (respecting preferred_time
        when possible).
        """
        tasks = self._get_task_source()
        if not tasks:
            return []

        available_minutes = available_minutes if available_minutes is not None else (
            self.owner.available_minutes_per_day if self.owner else sum(task.duration_minutes for task in tasks)
        )

        tasks = self.sort_tasks_by_priority(tasks)
        selected_tasks = self.filter_tasks_by_time(tasks, available_minutes)

        schedule: List[ScheduleItem] = []
        fallback_index = 0
        for task in selected_tasks:
            if task.preferred_time in DEFAULT_TIME_PERIODS:
                period = task.preferred_time
            else:
                period = DEFAULT_TIME_PERIODS[min(fallback_index, len(DEFAULT_TIME_PERIODS) - 1)]
                fallback_index += 1

            schedule.append(
                ScheduleItem(
                    task=task,
                    time_of_day=period,
                    explanation=f"Scheduled for {period} because priority is {task.priority}.",
                )
            )

        return schedule

    def sort_tasks_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks ordered by priority, preferred time, and duration."""
        tasks = tasks if tasks is not None else self._get_task_source()
        return sorted(
            [task for task in tasks if task.duration_minutes > 0],
            key=lambda task: (
                -task.get_priority_score(),
                task.get_preferred_time_order(),
                task.duration_minutes,
            ),
        )

    def filter_tasks_by_time(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        """Select tasks that fit into the available minutes (greedy by order)."""
        selected_tasks: List[Task] = []
        remaining_minutes = max(0, available_minutes)
        for task in tasks:
            if task.duration_minutes <= remaining_minutes:
                selected_tasks.append(task)
                remaining_minutes -= task.duration_minutes
        return selected_tasks

    def explain_schedule(self, schedule: List[ScheduleItem]) -> str:
        """Return a human-readable explanation of the schedule."""
        if not schedule:
            return "No tasks could be scheduled with the available time."

        explanation_lines = ["Daily schedule explanation:"]
        for item in schedule:
            explanation_lines.append(
                f"{item.formatted_time_range()} — {item.task.title} "
                f"({item.task.duration_minutes} min, priority: {item.task.priority})"
            )
        return "\n".join(explanation_lines)
