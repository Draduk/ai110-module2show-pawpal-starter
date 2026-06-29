import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")

# Initialize session state for owner and pets (persist across reruns)
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []
if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = None

# Owner name input (used when creating the Owner object)
owner_name = st.text_input("Owner name", value="Jordan")

# Button creates the Owner once and stores it in session_state.owner
if st.button("Initialize Owner"):
    st.session_state.owner = Owner(owner_id="o1", name=owner_name)
    st.success(f"Created owner: {owner_name}")

# Show current owner when available
if st.session_state.owner:
    st.info(f"Owner: {st.session_state.owner.name}")

# Add pets section
st.markdown("### Add Pets")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # Create a new Pet and register it with the Owner and session state.
    # Uses Owner.add_pet() to keep bidirectional link consistent.
    if st.session_state.owner is None:
        st.error("Please create an owner first.")
    else:
        new_pet = Pet(pet_id=f"p{len(st.session_state.pets) + 1}", name=pet_name, species=species)
        st.session_state.owner.add_pet(new_pet)  # owner.pets updated by method
        st.session_state.pets.append(new_pet)    # add to session list for UI
        st.session_state.selected_pet = new_pet
        st.success(f"Added pet: {pet_name}")

if st.session_state.pets:
    st.write("**Your pets:**")
    for pet in st.session_state.pets:
        st.write(f"- {pet.name} ({pet.species})")
    
    pet_names = [p.name for p in st.session_state.pets]
    selected_name = st.selectbox("Select pet for tasks:", pet_names)
    st.session_state.selected_pet = next(p for p in st.session_state.pets if p.name == selected_name)
else:
    st.warning("Add at least one pet to continue.")

st.markdown("### Tasks")
st.caption("Add tasks to the selected pet's schedule.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"], index=0)

if st.button("Add task"):
    # Build a Task instance and attach it to the selected Pet.
    # Pet.add_task() ensures duplicates are ignored and the pet's task list is updated.
    if st.session_state.selected_pet is None:
        st.error("Please select a pet first.")
    else:
        task = Task(
            task_id=f"t{len(st.session_state.tasks) + 1}",
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            preferred_time=preferred_time
        )
        st.session_state.selected_pet.add_task(task)  # update pet.tasks
        st.session_state.tasks.append(task)           # keep UI list in session_state
        st.success(f"Added task '{task_title}' to {st.session_state.selected_pet.name}")


if st.session_state.tasks:
    st.write("**Current tasks:**")
    # Use Scheduler to present tasks in a sorted, professional table
    scheduler = Scheduler(owner=st.session_state.owner, pet=st.session_state.selected_pet)
    tasks_for_table = []
    if st.session_state.selected_pet:
        sorted_tasks = scheduler.sort_tasks_by_time(st.session_state.selected_pet.tasks)
        for task in sorted_tasks:
            tasks_for_table.append({
                "Title": task.title,
                "Duration (min)": task.duration_minutes,
                "Time": task.time or "anytime",
                "Priority": task.priority,
                "Recurrence": task.recurrence,
                "Status": "done" if task.completed else "pending",
            })
    else:
        # fallback to unsorted session list
        for task in st.session_state.tasks:
            tasks_for_table.append({
                "Title": task.title,
                "Duration (min)": task.duration_minutes,
                "Time": task.time or "anytime",
                "Priority": task.priority,
                "Recurrence": task.recurrence,
                "Status": "done" if task.completed else "pending",
            })

    if tasks_for_table:
        st.table(tasks_for_table)
else:
    st.info("No tasks yet. Add one above.")


st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily schedule based on task priority and available time.")

available_min = st.slider("Available minutes per day:", min_value=30, max_value=480, value=120, step=10)

if st.button("Generate schedule"):
    # Use the Scheduler class to build a simple period-based schedule.
    # Pass the owner and selected pet; available minutes are taken from the slider.
    if st.session_state.selected_pet is None or not st.session_state.tasks:
        st.warning("Please add a pet and at least one task first.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner, pet=st.session_state.selected_pet)
        # Generate schedule and present as table
        schedule = scheduler.generate_schedule(available_minutes=available_min)
        if schedule:
            st.success("Schedule generated!")

            # Present schedule as a table with columns for time, title, duration, priority
            schedule_rows = []
            for item in schedule:
                schedule_rows.append({
                    "Time": item.time_of_day,
                    "Title": item.task.title,
                    "Duration (min)": item.task.duration_minutes,
                    "Priority": item.task.priority,
                    "Note": item.explanation,
                })
            st.table(schedule_rows)

            # Show human-readable explanation
            with st.expander("Why these tasks were chosen", expanded=False):
                st.text(scheduler.explain_schedule(schedule))

            # Conflict warnings: show prominently but non-blocking
            warnings = scheduler.get_conflict_warnings(schedule)
            if warnings:
                st.warning("Conflicts detected in this schedule. Review and adjust times:")
                for w in warnings:
                    st.error(w)
            else:
                st.success("No exact-time conflicts detected.")
        else:
            st.info("No tasks could be scheduled with the available time.")

