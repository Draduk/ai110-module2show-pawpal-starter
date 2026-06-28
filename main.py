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


def main() -> None:
    # Create owner
    owner = Owner(owner_id="o1", name="Jordan", available_minutes_per_day=90)

    # Create pets
    pet1 = Pet(pet_id="p1", name="Mochi", species="dog")
    pet2 = Pet(pet_id="p2", name="Biscuit", species="cat")

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Create tasks (different preferred times and priorities)
    t1 = Task(task_id="t1", title="Morning walk", duration_minutes=30, priority="high", preferred_time="morning")
    t2 = Task(task_id="t2", title="Feeding", duration_minutes=10, priority="high", preferred_time="any")
    t3 = Task(task_id="t3", title="Grooming", duration_minutes=40, priority="medium", preferred_time="afternoon")
    t4 = Task(task_id="t4", title="Play session", duration_minutes=25, priority="low", preferred_time="evening")

    # Assign tasks to pets
    pet1.add_task(t1)
    pet1.add_task(t2)
    pet2.add_task(t3)
    pet2.add_task(t4)

    # Print schedules for each pet
    for pet in owner.pets:
        print_schedule_for_pet(owner, pet)


if __name__ == "__main__":
    main()
