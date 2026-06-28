from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import re

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
    # Optional exact start time in 24-hour HH:MM format (e.g. "07:30").
    # If provided, scheduler will prefer exact-time ordering and conflict
    # detection will use these times.
    time: Optional[str] = None
    recurrence: str = "once"
    notes: Optional[str] = None
    completed: bool = False

    def __post_init__(self) -> None:
        """Normalize and validate task fields after initialization."""
        self.priority = self.priority.lower()
        self.preferred_time = self.preferred_time.lower()
        self.recurrence = self.recurrence.lower()
        # Normalize and validate time if provided. Accept only HH:MM 24-hour.
        if self.time is not None:
            if isinstance(self.time, str):
                m = re.match(r"^(\d{1,2}):(\d{2})$", self.time)
                if m:
                    hh = int(m.group(1))
                    mm = int(m.group(2))
                    if 0 <= hh < 24 and 0 <= mm < 60:
                        # store zero-padded
                        self.time = f"{hh:02d}:{mm:02d}"
                    else:
                        self.time = None
                else:
                    self.time = None
            else:
                self.time = None

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

    def get_start_minutes(self) -> Optional[int]:
        """Return minutes since midnight for the task's exact `time`, or None."""
        if not self.time:
            return None
        try:
            hh, mm = self.time.split(":")
            return int(hh) * 60 + int(mm)
        except Exception:
            return None

    def get_interval(self) -> Optional[Tuple[int, int]]:
        """Return (start_minute, end_minute) if time is set, otherwise None."""
        start = self.get_start_minutes()
        if start is None:
            return None
        return (start, start + max(0, self.duration_minutes))

    def matches_time_period(self, period: str) -> bool:
        """Check whether this task can be scheduled in the given period."""
        return self.preferred_time == period or self.preferred_time == "any"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def create_next_occurrence(self) -> Task:
        """Create a new Task instance for the next occurrence of this recurring task.

        Returns a new Task with the same properties but a new task_id and completed=False.
        """
        import time
        # Generate a unique task_id suffix using timestamp
        timestamp_suffix = str(int(time.time() * 1000) % 1000000)
        new_task_id = f"{self.task_id}_next_{timestamp_suffix}"

        return Task(
            task_id=new_task_id,
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            time=self.time,
            recurrence=self.recurrence,
            notes=self.notes,
            completed=False,
        )



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

        # prefer tasks with exact times when sorting
        tasks = self.sort_tasks_by_time(tasks)
        selected_tasks = self.filter_tasks_by_time(tasks, available_minutes)

        schedule: List[ScheduleItem] = []
        for task in selected_tasks:
            # Use exact HH:MM time when available; otherwise mark as 'anytime'.
            time_label = task.time if task.time else "anytime"
            schedule.append(
                ScheduleItem(
                    task=task,
                    time_of_day=time_label,
                    explanation=f"Scheduled at {time_label} because priority is {task.priority}.",
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

    def sort_tasks_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by exact `time` first, then preferred period order, then
        priority (desc), then duration.
        """
        tasks = tasks if tasks is not None else self._get_task_source()

        def time_key(task: Task) -> int:
            if task.time is None:
                return 24 * 60
            hh, mm = task.time.split(":")
            return int(hh) * 60 + int(mm)

        return sorted(
            [t for t in tasks if t.duration_minutes > 0],
            key=lambda task: (
                time_key(task),
                task.get_preferred_time_order(),
                -task.get_priority_score(),
                task.duration_minutes,
            ),
        )

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion status and/or pet name.

        If pet_name is provided, tasks are gathered from the owner's pets that
        match that name. If no owner is set, this acts on the current pet or
        explicit task list only.
        """
        if self.tasks:
            task_list = list(self.tasks)
        elif self.pet:
            task_list = list(self.pet.tasks)
        elif self.owner:
            task_list = []
            for pet in self.owner.pets:
                if pet_name is None or pet.name.lower() == pet_name.lower():
                    task_list.extend(pet.tasks)
        else:
            task_list = []

        if pet_name is not None and self.owner is None and self.pet:
            if self.pet.name.lower() != pet_name.lower():
                task_list = []

        if completed is not None:
            task_list = [task for task in task_list if task.completed is completed]

        return task_list

    def filter_tasks_by_time(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        """Select tasks that fit into the available minutes (greedy by order)."""
        selected_tasks: List[Task] = []
        remaining_minutes = max(0, available_minutes)
        for task in tasks:
            if task.duration_minutes <= remaining_minutes:
                selected_tasks.append(task)
                remaining_minutes -= task.duration_minutes
        return selected_tasks

    def detect_conflicts(self, schedule: List[ScheduleItem]) -> List[Tuple[str, str]]:
        """Detect overlapping tasks based on exact times. Returns list of pairs
        of task_ids that conflict. Only tasks with explicit `time` are considered.
        """
        intervals: List[Tuple[int, int, str]] = []  # (start, end, task_id)
        for item in schedule:
            iv = item.task.get_interval()
            if iv is not None:
                intervals.append((iv[0], iv[1], item.task.task_id))

        conflicts: List[Tuple[str, str]] = []
        # simple O(n^2) overlap detection (small n expected)
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                a0, a1, id_a = intervals[i]
                b0, b1, id_b = intervals[j]
                if not (a1 <= b0 or b1 <= a0):
                    conflicts.append((id_a, id_b))
        return conflicts

    def get_conflict_warnings(self, schedule: List[ScheduleItem]) -> List[str]:
        """Generate human-readable warning messages for conflicting tasks.

        Returns a list of warning strings describing overlapping tasks.
        """
        conflicts = self.detect_conflicts(schedule)
        warnings = []

        # Build a lookup from task_id to ScheduleItem for quick access
        task_lookup = {item.task.task_id: item for item in schedule}

        for id_a, id_b in conflicts:
            item_a = task_lookup.get(id_a)
            item_b = task_lookup.get(id_b)
            if item_a and item_b:
                start_a = item_a.task.get_start_minutes()
                start_b = item_b.task.get_start_minutes()
                if start_a is not None and start_b is not None:
                    time_a = item_a.task.time or "unknown"
                    time_b = item_b.task.time or "unknown"
                    warning = (
                        f"⚠️  CONFLICT: '{item_a.task.title}' (at {time_a}, "
                        f"{item_a.task.duration_minutes}min) overlaps with "
                        f"'{item_b.task.title}' (at {time_b}, {item_b.task.duration_minutes}min)"
                    )
                    warnings.append(warning)

        return warnings

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

    def mark_task_complete_with_recurrence(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed and auto-create the next occurrence if recurring.

        For tasks with recurrence="daily" or "weekly", creates a new Task instance
        and adds it to the same pet. Returns the newly created task, or None if the
        task was not recurring or not found.
        """
        task = None
        if self.pet:
            task = self.pet.get_task(task_id)
        elif self.owner:
            for pet in self.owner.pets:
                task = pet.get_task(task_id)
                if task:
                    break
        elif self.tasks:
            for t in self.tasks:
                if t.task_id == task_id:
                    task = t
                    break

        if task is None:
            return None

        # Mark the task as complete
        task.mark_complete()

        # If the task is recurring (daily or weekly), create and add the next occurrence
        if task.recurrence in {"daily", "weekly"}:
            next_task = task.create_next_occurrence()
            if self.pet:
                self.pet.add_task(next_task)
            elif self.owner:
                for pet in self.owner.pets:
                    if pet.get_task(task_id):
                        pet.add_task(next_task)
                        break
            return next_task

        return None
