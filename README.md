# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Sample output
Schedule for Mochi (owner: Jordan):
----------------------------------------
Daily schedule explanation:
Morning — Morning walk (30 min, priority: high)
Morning — Feeding (10 min, priority: high)

Schedule for Biscuit (owner: Jordan):
----------------------------------------
Daily schedule explanation:
Afternoon — Grooming (40 min, priority: medium)
Evening — Play session (25 min, priority: low)

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Description:

- Tests cover basic `Task` behavior, `Pet` and `Owner` relationships, and core
	scheduler logic: chronological sorting (`Scheduler.sort_tasks_by_time()`),
	recurrence handling (`Scheduler.mark_task_complete_with_recurrence()`), and
	lightweight conflict detection (`Scheduler.get_conflict_warnings()`).

Sample test run (captured output from `python -m pytest`):

```console
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: /Users/tenzindraduk/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.10.0
collected 5 items                                                              

tests/test_pawpal.py .....                                               [100%]

============================== 5 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks_by_time()` | Sorts tasks by exact `time` (HH:MM) when present, then by preferred period, priority, and duration. Uses a numeric minutes-since-midnight key for reliable chronological ordering.
| Filtering | `Scheduler.filter_tasks()` / `Scheduler.filter_tasks_by_time()` | `filter_tasks()` filters by `completed` status and by pet name when scheduling across an owner. `filter_tasks_by_time()` greedily selects tasks that fit into available minutes.
| Conflict detection | `Scheduler.detect_conflicts()` / `Scheduler.get_conflict_warnings()` | `detect_conflicts()` checks pairwise interval overlaps for tasks with exact `time`. `get_conflict_warnings()` returns human-readable warnings instead of raising errors.
| Recurring tasks | `Task.create_next_occurrence()` / `Scheduler.mark_task_complete_with_recurrence()` | When a recurring task (`daily` or `weekly`) is marked complete, `mark_task_complete_with_recurrence()` creates a new `Task` instance for the next occurrence and attaches it to the same pet.

## ✨ Features

Based on the current implementation in `app.py`, `main.py`, and `pawpal_system.py`, PawPal+ includes the following core capabilities:

- Sorting by time: `Scheduler.sort_tasks_by_time()` orders tasks by exact HH:MM start time when available, then by preferred time period, priority, and duration.
- Priority-based scheduling: `Scheduler.filter_tasks_by_time()` greedily selects tasks that fit within the available daily minutes.
- Conflict warnings: `Scheduler.detect_conflicts()` and `Scheduler.get_conflict_warnings()` identify overlapping exact-time tasks and surface clear warnings.
- Daily and weekly recurrence: `Task.create_next_occurrence()` and `Scheduler.mark_task_complete_with_recurrence()` support recurring tasks for future occurrences.
- Pet and owner management: `Owner`, `Pet`, and `Task` work together to keep task lists, pet ownership, and schedule data connected.

## 📋 Demo Walkthrough

The Streamlit app gives a pet owner a simple way to plan care tasks for a pet from start to finish.

1. Main UI features: users can create an owner, add one or more pets, create tasks with a title, duration, priority, preferred time, and optional exact time. They can also generate a daily schedule and review the results in table form.
2. Example workflow: a user can add a pet such as Mochi, create a few tasks like a morning walk or feeding, and then generate a schedule to see which tasks fit into the available time for the day.
3. Scheduler behaviors shown: tasks are sorted by time when exact start times are present, the scheduler selects tasks that fit within the available minutes, and overlapping exact-time tasks trigger conflict warnings so the user can adjust the plan.
4. Recurring tasks are also supported: if a task is marked as daily or weekly, the app can create the next occurrence when that task is completed.

Example CLI output from running `main.py`:

```console
Tasks for Mochi (owner: Jordan)
----------------------------------------
- Morning walk (30min) — 07:00, priority=high, pending [daily]
- Feeding (10min) — 08:15, priority=high, pending [daily]
- Vet checkup (20min) — 08:15, priority=high, pending
- Grooming (40min) — 13:30, priority=medium, pending [weekly]
- Cleanup (15min) — anytime, priority=medium, done

Tasks for Mochi (owner: Jordan) — pending
----------------------------------------
- Morning walk (30min) — 07:00, priority=high, pending [daily]
- Feeding (10min) — 08:15, priority=high, pending [daily]
- Vet checkup (20min) — 08:15, priority=high, pending
- Grooming (40min) — 13:30, priority=medium, pending [weekly]

Tasks for Mochi (owner: Jordan) — recurring only
----------------------------------------
- Morning walk (30min) — 07:00, priority=high, pending [daily]
- Feeding (10min) — 08:15, priority=high, pending [daily]
- Grooming (40min) — 13:30, priority=medium, pending [weekly]

Schedule for Mochi (owner: Jordan):
----------------------------------------
Daily schedule explanation:
07:00 — Morning walk (30 min, priority: high)
08:15 — Feeding (10 min, priority: high)

========================================
SCHEDULE CONFLICTS DETECTED:
========================================
⚠️  CONFLICT: 'Feeding' (at 08:15, 10min) overlaps with 'Vet checkup' (at 08:15, 20min)
```
