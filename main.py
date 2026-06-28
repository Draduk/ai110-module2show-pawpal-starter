from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule_for_pet(owner: Owner, pet: Pet, available_minutes: int | None = None) -> None:
    sched = Scheduler(owner=owner, pet=pet)
    schedule = sched.generate_schedule(available_minutes=available_minutes)
    print(f"\nSchedule for {pet.name} (owner: {owner.name}):")
    print("-" * 40)
    if not schedule:
        print("No tasks scheduled.")
        return
    print(sched.explain_schedule(schedule))


def show_tasks_for_pet(owner: Owner, pet: Pet, completed: bool | None = None, recurring_only: bool = False) -> None:
    """Print a short list of tasks for `pet`, optionally filtering by completion
    status or recurrence. Tasks are shown in preferred-time order.
    """
    sched = Scheduler(owner=owner, pet=pet)
    tasks = sched.filter_tasks(completed=completed)
    if recurring_only:
        tasks = [t for t in tasks if t.recurrence != "once"]

    tasks = sched.sort_tasks_by_time(tasks)

    header = f"Tasks for {pet.name} (owner: {owner.name})"
    if completed is True:
        header += " — completed"
    elif completed is False:
        header += " — pending"
    if recurring_only:
        header += " — recurring only"

    print(f"\n{header}")
    print("-" * 40)
    if not tasks:
        print("No tasks match the filters.")
        return

    for t in tasks:
        rec = f" [{t.recurrence}]" if t.recurrence != "once" else ""
        status = "done" if t.completed else "pending"
        time_display = t.time if t.time else "anytime"
        print(f"- {t.title} ({t.duration_minutes}min) — {time_display}, priority={t.priority}, {status}{rec}")


def main() -> None:
    # Create owner
    owner = Owner(owner_id="o1", name="Jordan", available_minutes_per_day=60)

    # Create pets
    pet1 = Pet(pet_id="p1", name="Mochi", species="dog")
    pet2 = Pet(pet_id="p2", name="Biscuit", species="cat")

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Create tasks in non-sequential order, using exact HH:MM time values.
    t1 = Task(task_id="t1", title="Grooming", duration_minutes=40, priority="medium", time="13:30", preferred_time="afternoon", recurrence="weekly")
    t2 = Task(task_id="t2", title="Feeding", duration_minutes=10, priority="high", time="08:15", preferred_time="morning", recurrence="daily")
    t3 = Task(task_id="t3", title="Play session", duration_minutes=25, priority="low", time="18:00", preferred_time="evening", recurrence="once")
    t4 = Task(task_id="t4", title="Morning walk", duration_minutes=30, priority="high", time="07:00", preferred_time="morning", recurrence="daily")
    t5 = Task(task_id="t5", title="Medication", duration_minutes=5, priority="high", time="09:00", preferred_time="morning", recurrence="daily")
    t6 = Task(task_id="t6", title="Cleanup", duration_minutes=15, priority="medium", preferred_time="any", recurrence="once")
    # Add an overlapping task to demonstrate conflict detection
    t7 = Task(task_id="t7", title="Vet checkup", duration_minutes=20, priority="high", time="08:15", preferred_time="morning", recurrence="once")
    t6.mark_complete()

    # Assign tasks to pets in a deliberately unordered sequence
    pet1.add_task(t1)
    pet1.add_task(t4)
    pet1.add_task(t2)
    pet1.add_task(t6)
    pet1.add_task(t7)  # overlaps with t2
    pet2.add_task(t3)
    pet2.add_task(t5)

    # Show all, pending, and recurring tasks for one pet
    show_tasks_for_pet(owner, pet1)
    show_tasks_for_pet(owner, pet1, completed=False)
    show_tasks_for_pet(owner, pet1, recurring_only=True)

    # Generate schedule with constrained available minutes to illustrate selection and conflicts
    print_schedule_for_pet(owner, pet1, available_minutes=40)

    # Check for scheduling conflicts
    sched = Scheduler(owner=owner, pet=pet1)
    schedule = sched.generate_schedule()
    warnings = sched.get_conflict_warnings(schedule)
    if warnings:
        print("\n" + "=" * 40)
        print("SCHEDULE CONFLICTS DETECTED:")
        print("=" * 40)
        for warning in warnings:
            print(warning)
    else:
        print("\n" + "=" * 40)
        print("✓ No scheduling conflicts detected.")
        print("=" * 40)


if __name__ == "__main__":
    main()
