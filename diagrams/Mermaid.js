// Mermaid.js class diagram for the PawPal+ project
// Paste this into a Mermaid-enabled viewer or use it as a module export.

const pawpalClassDiagram = `
classDiagram
    class Owner {
        +str owner_id
        +str name
        +int available_minutes_per_day
        +dict preferences
        +list pets
        +add_pet(pet)
        +remove_pet(pet_id)
    }

    class Pet {
        +str pet_id
        +str name
        +str species
        +Owner owner
        +list tasks
        +add_task(task)
        +remove_task(task_id)
    }

    class Task {
        +str task_id
        +str title
        +int duration_minutes
        +str priority
        +str preferred_time
        +str recurrence
        +str notes
        +bool completed
        +get_priority_score()
    }

    class ScheduleItem {
        +Task task
        +str time_of_day
        +str explanation
        +formatted_time_range()
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +list tasks
        +generate_schedule(available_minutes)
        +sort_tasks_by_priority(tasks)
        +filter_tasks_by_time(tasks, available_minutes)
        +explain_schedule(schedule)
    }

    Owner "1" o-- "*" Pet : owns
    Pet "1" o-- "*" Task : has
    Scheduler --> Owner : uses
    Scheduler --> Pet : uses
    Scheduler --> Task : schedules
    Scheduler --> ScheduleItem : creates
`;

export default pawpalClassDiagram;
