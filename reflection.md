# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    The main classes or objects that the UML diagram is built around are the user/owner class, pet class and task class.
- What classes did you include, and what responsibilities did you assign to each?
    Owner class will have the basic owner information
    The pet class will have the pet's information
    Task class will have the type of task or what needs ot be done with the time and priority 
**b. Design changes**

- Did your design change during implementation?
    Yes.
- If yes, describe at least one change and why you made it.
    I added a scheduler class which will gather all the tasks and arrange them into a proper schedule accordingly.
    I decided to add userID and petID attributes which are unique id for each user and pet to make the system better when lookin up the user or the pet with same name.
---

Updated after implementation:

- I kept the core classes from the initial UML (`Owner`, `Pet`, `Task`) and added two important production-ready elements:
  - `Scheduler`: encapsulates sorting, selection, conflict detection, and recurrence handling.
  - `ScheduleItem`: a small value object produced by `Scheduler.generate_schedule()` that pairs a `Task` with a scheduled time and explanation.

These changes moved scheduling behavior out of the UI and into `pawpal_system.py`, which made the design clearer and easier to test.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    Time and Priority
- How did you decide which constraints mattered most?
    A task need to be done at a certain time and if there are multiple tasks to be done, it will depend on the priority to figure out which tasks need to be done first.
 
Updated after implementation:

- Constraints considered: exact start `time` (HH:MM) when provided, `duration_minutes`, `priority`, `preferred_time` (morning/afternoon/evening/any), and available minutes per day.
- Decisions: exact `time` takes precedence for chronological ordering; otherwise the scheduler orders by preferred time period, priority (high→low), and duration.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    The `detect_conflicts()` method uses an O(n²) nested loop to check all pairs of tasks for time overlaps. A more concise Pythonic version using list comprehensions was suggested, but the current implementation prioritizes readability over brevity. The nested loops make the overlap logic transparent—comparing interval pairs `(a0, a1)` and `(b0, b1)` with the non-overlap condition `a1 <= b0 or b1 <= a0`. The alternative list comprehension approach compresses this into a single expression, making it harder for team members to quickly verify the conflict detection logic.

    Additionally, the scheduler only detects exact-time conflicts (tasks with `time` attributes set to HH:MM). Tasks without explicit times are treated as flexible ("anytime"), so no conflicts are flagged for them. This simplifies the algorithm but may miss user intent if two flexible tasks should not run concurrently.

- Why is that tradeoff reasonable for this scenario?
    Pet care scheduling is typically small-scale (5–20 tasks per pet per day), so O(n²) performance is acceptable. Readability is prioritized because future maintainers (or the user reviewing code) need to quickly understand how conflicts are detected. Exact-time detection is reasonable because users can opt into precision scheduling by specifying times; flexible tasks represent lower-priority activities that are easier to reschedule.
---

## 3. AI Collaboration

**a. How you used AI**

I used an AI coding assistant as a collaborative pair programmer across several phases:

- Design brainstorming: helped iterate UML and suggested class responsibilities and relations.
- Implementation scaffolding: generated initial `Task`, `Scheduler`, and `ScheduleItem` method stubs and small helper functions.
- Refactoring and small patches: applied focused edits to `app.py`, `README.md`, and `diagrams/uml_draft.mmd` so code and documentation matched the implementation.
- Testing and verification: ran `main.py` and used the CLI output to capture a realistic sample to include in the README.

Prompts that worked well were concrete, phase-scoped requests like: "Sort tasks by exact time then by priority," or "Generate readable conflict warnings for overlapping tasks." These led to implementable code suggestions rather than vague, high-level advice.

**b. Judgment and verification**


One AI suggestion condensed the conflict detection into a compact list comprehension that was clever but harder to read during review. I rejected that compact form in favor of the clear O(n²) pairwise loop so future maintainers could quickly follow the overlap logic. I verified correctness by running `main.py` and manually inspecting the warnings output; the explicit loops made debugging the overlap intervals easier.

Another minor suggestion the AI gave was to auto-assign times to flexible tasks; I rejected that because it would hide scheduling choices from the user. Instead I kept "anytime" flexible tasks visible and left exact-time scheduling explicit.

Using the AI for incremental edits and running the code after each change helped validate suggestions quickly.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I ran the provided tests and used the `main.py` demo as an integration sanity check. Key behaviors exercised:

- Chronological sorting by exact `time` via `Scheduler.sort_tasks_by_time()`.
- Greedy selection of tasks that fit within available minutes via `Scheduler.filter_tasks_by_time()`.
- Conflict detection and human-readable warnings via `Scheduler.detect_conflicts()` and `Scheduler.get_conflict_warnings()`.
- Recurrence handling via `Task.create_next_occurrence()` and `Scheduler.mark_task_complete_with_recurrence()`.

These tests are important because they validate the scheduler's core responsibilities: order, fit, and safety (no silent overlaps) for the user's day.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence: moderate. The basic behaviors are covered and the demo output matches expectations for the provided scenarios.

Next edge cases to test:

- Multiple overlapping tasks with varying durations and partially overlapping intervals.
- Mixing flexible tasks and exact-time tasks when total available minutes is tight.
- Recurrence edge cases (marking complete across an `Owner` with multiple pets and ensuring the next occurrence attaches to the right pet).
- Invalid time strings passed into `Task.time`—ensure robust normalization and error handling.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I’m most satisfied that the scheduler logic was kept inside `pawpal_system.py` and that `app.py` became a thin UI layer. That separation made it easy to test scheduling behavior independently, capture realistic CLI output with `main.py`, and keep the README and UML aligned with the implementation.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add more fine-grained scheduling constraints (user-defined priorities per day, time windows rather than single HH:MM start times), and a small UI affordance for editing scheduled times to resolve conflicts interactively.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Key takeaway: treat the AI as a capable assistant that proposes solutions, but keep the role of lead architect. Accept suggestions that make code clearer, test them quickly, and reject or modify clever-but-opaque shortcuts to preserve maintainability. Using separate, phase-focused chat sessions helped keep changes scoped (design → implementation → docs), making it easier to reason about each artifact and to validate the system incrementally.

AI-specific summary:

- Most effective AI features: quick scaffolding of class/method stubs, targeted patches (`apply_patch` style edits), and generating human-readable messages (warnings/explanations).
- One suggestion I rejected: compressing conflict detection into a single list comprehension — rejected for readability and debuggability.
- Benefit of separate chat sessions: they created clear checkpoints (UML/design, then code, then UI, then docs) that reduced context switching and made reviews simpler.
