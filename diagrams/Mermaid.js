
const pawpalClassDiagram = `
classDiagram
    class Owner {
        +str owner_id
        +str name
        +list pets
        +add_pet(pet)
        +remove_pet(pet)
    }

    class Pet {
        +str pet_id
        +str name
        +str species
        +Owner owner
        +list tasks
        +add_task(task)
        +remove_task(task)
    }

    class Task {
        +str task_id
        +str title
        +int duration_minutes
        +str priority
        +str notes
        +bool completed
        +get_priority_score()
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +list tasks
        +generate_schedule()
        +sort_tasks_by_priority()
        +filter_tasks_by_time()
        +explain_schedule()
    }

    Owner "1" o-- "*" Pet : owns
    Pet "1" o-- "*" Task : has
    Scheduler --> Owner : uses
    Scheduler --> Pet : uses
    Scheduler --> Task : schedules
`;

export default pawpalClassDiagram;
