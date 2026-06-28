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

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    Time and Priority
- How did you decide which constraints mattered most?
    A task need to be done at a certain time and if there are multiple tasks to be done, it will depend on the priority to figure out which tasks need to be done first.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    The `detect_conflicts()` method uses an O(n²) nested loop to check all pairs of tasks for time overlaps. A more concise Pythonic version using list comprehensions was suggested, but the current implementation prioritizes readability over brevity. The nested loops make the overlap logic transparent—comparing interval pairs `(a0, a1)` and `(b0, b1)` with the non-overlap condition `a1 <= b0 or b1 <= a0`. The alternative list comprehension approach compresses this into a single expression, making it harder for team members to quickly verify the conflict detection logic.

    Additionally, the scheduler only detects exact-time conflicts (tasks with `time` attributes set to HH:MM). Tasks without explicit times are treated as flexible ("anytime"), so no conflicts are flagged for them. This simplifies the algorithm but may miss user intent if two flexible tasks should not run concurrently.

- Why is that tradeoff reasonable for this scenario?
    Pet care scheduling is typically small-scale (5–20 tasks per pet per day), so O(n²) performance is acceptable. Readability is prioritized because future maintainers (or the user reviewing code) need to quickly understand how conflicts are detected. Exact-time detection is reasonable because users can opt into precision scheduling by specifying times; flexible tasks represent lower-priority activities that are easier to reschedule.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
