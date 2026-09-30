---
layout: default
codename: ProgrammingFactoryAutomationWithAI
title: Programming Factory Automation with AI
tags: snippets mieset
authors: Charaf Mohamad
---

# Programming Factory Automation with AI
---
## Problem Statement
In industrial automation, almost every physical process – filling a tank, sorting boxes on a conveyor, palletizing products – is controlled by a Programmable Logic Controller (PLC): an industrial computer that reads sensors, executes its control logic in a fixed repeating loop called a *scan cycle*, and drives actuators such as valves, motors and conveyors. Programming a PLC is traditionally the job of a specialized automation engineer, and the difficulty is rarely the code itself. It lies in translating how a machine physically behaves into logic: which sensor marks the end of a step, what happens when a button is held down, or how the machine should react when something gets stuck. A program can run without a single error and still leave a valve open or a box stranded on a conveyor. This makes every new machine, and every change to an existing one, a time-consuming and expensive task. Before deploying on real equipment, control programs are usually tested against a simulated version of the machine, a practice known as *virtual commissioning*. Since the expected behavior of a machine can be described in plain language, AI models could take over a large part of this work. In this case study, we highlight the following question: How can AI models be used to turn a description of a machine into a working control program, and where is human judgment still needed?

## Task Description
The task requires a simulated factory, PLC software and multiple AI sessions:
| Tool | Description |
|--------|-------------|
| Factory I/O | 3D factory simulator with ready-made industrial scenes |
| OpenPLC | Open-source software PLC, used to write and run the control program |
| Structured Text | Standard PLC programming language |

The work was split across three AI sessions inside one Claude project, each with a single role:
| Session | Model | Role |
|---|-------------|-------------|
| Planner | Sonnet 5.5 | Asks clarifying questions and writes a specification of *what* the program must do |
| Executor | Opus 5.5 | Writes the PLC program from the specification |
| Independent Reviewer | Opus 5.5 | Scores the tested program without seeing how it was planned |

> All three sessions used Medium effort with Thinking enabled.

Two factory scenes were programmed, each relying on a different type of control:
| Scene | Description | Driven by | Complexity |
|--------|-------------|--------|------------|
| 1 – Filling Tank (Timers) | Fill and empty a tank using two pushbuttons; the tank has no level sensors | Timers | Simple |
| 2 – Sorting by Height (Sensors) | Measure the height of each box and sort it to the left or right conveyor using a chain transfer | Sensors | Complex |

Both scenes followed the same loop between me and the AI sessions:
1. I gave the planner screenshots of the scene, the list of inputs and outputs, and my observations from testing them.
2. The planner asked clarifying questions, then wrote a specification in a markdown file: the required behavior, safety requirements, test cases and success criteria, but no code.
3. I handed the specification to the executor, which wrote the program.
4. I loaded the program into OpenPLC and tested it in the scene.
5. I reported the results back: behavior problems went to the planner, code problems to the executor.
6. Once the scene worked, the program was sent for review against a fixed rubric.

---
## Lessons Learned
- **Separating roles makes every problem traceable** – with the planner deciding *what* the program does and the executor deciding *how*, every issue found during testing had a clear source. This kept each session focused on a single job and made the loop identical for both scenes, even when the second scene needed several iterations.
- **Receiving context is not the same as understanding it** – in the second scene, the planner had screenshots, the full I/O list and my observations, yet it interpreted some of the machine's sensors by their *names* instead of their role in the scene, and treated them as unused. It then designed a time-driven program where a sensor-driven one was both possible and necessary. Screenshots and tables are not enough for a model to build a correct picture of a physical machine.
- **Telling the model to ask instead of assume changes its behavior** – accepting the suggestion from the model for every question kept the sessions short, but it also let wrong assumptions slip into the specification. Once I explicitly instructed the planner to ask whenever it was unsure, it stopped proposing and started asking precise, structured questions, and kept doing so for the rest of the scene.
- **The executor is also an early-warning system** – beyond writing code, the executor pointed out where the specification was likely to fail in the scene, and two of these warnings came true during testing. The notes a model writes *around* its code can be as valuable as the code itself, especially when the planner never sees them.
- **Models should not grade their own plans** – when the planner reviewed a program built from its own specification, it scored it higher than the independent reviewer did and missed risks that the reviewer found, such as a communication loss leaving a valve open. Because of this bias, the second scene was evaluated by the independent reviewer only.
- **A reviewer is only as good as its reference** – the independent reviewer judges the program against the specification, not against the scene. Fixes discovered during testing change the program but not the specification, so correct behavior can be flagged as a deviation. In a multi-session architecture, the specification has to be treated as a living document that every session relies on.
- **AI still needs a human to see** – none of the sessions can observe the scene. Every breakthrough in the second scene started with an observation in the simulation that was reported back to the right session.

---
## Workflow Details
### Establishing Context and Constraints
The planner session started with a prompt that defined the platform, the scope and, most importantly, what the planner was *not* allowed to do:
#### ***User***
```text
I want to program PLC control logic for ready-made Factory I/O scenes. [...]
We start with Level 1 only: "Filling Tank (Timers)". Do not move to the next level before I confirm.
[...]
Your role is planning only. Do NOT write the PLC program, variable declarations or code.
A separate programming session will implement it.
```
The same prompt also listed what the specification must contain and the rubric that would be used for the review. Keeping the planner away from code was deliberate: a model that only describes behavior is forced to think about the machine and its safety, rather than jumping ahead to an implementation. The executor, on the other hand, was started with a single instruction: read and follow the specification file.

### Scene 1: Filling Tank (Timers)
The first scene is a tank with a fill valve, a discharge valve and two pushbuttons with lamps. Since the tank has no level sensors, the only thing that prevents it from overflowing is how long the valve stays open.

![Filling Tank Scene](assets/filling_tank_scene.gif)

The planner asked five clarifying questions, each with a proposed default (e.g., one press starts a fixed-duration cycle, and the two cycles can never run at the same time). It is worth noting that it identified a subtle trap on its own: the Discharge button is *normally closed*, meaning it reads "pressed" when the scene starts, which could trigger a discharge by accident. It added a safety requirement for this, together with others such as never opening both valves at once, and wrote a specification with 16 test cases.

The executor delivered the program in a single response, organized into clearly commented sections, with notes linking its design choices to the test cases. The program worked on the first attempt and required no changes. For a timer-based process with few inputs, the planner-executor loop needed only one pass.

### Scene 2: Sorting by Height (Sensors)
The second scene is considerably harder. Boxes arrive on an entry conveyor, pass two height sensors, are pulled onto a chain transfer, and are moved to the left conveyor (short boxes) or the right conveyor (tall boxes). Every step of the process can be detected by a sensor, so the program should be driven by sensors rather than timers.

![Sorting by Height Scene](assets/sorting_by_height_scene.gif)

#### *Where the Planner Struggled*
Even with the same kind of materials as in the first scene, the planner misread the setup. It labelled the sensors and rollers of the chain transfer as leftovers from another scene and proposed to ignore them. Without these sensors, it had no way of knowing when a box was in position, so it filled the gaps with timers that *guess* when each step is finished, which resulted in a time-driven program. The executor implemented this, and in the scene the boxes stopped at the edge of the transfer and never got onto it, because the rollers that pull them in were never switched on.

When I corrected the planner, I added one instruction that changed how the rest of the scene went:
#### ***User***
```text
[...] Update the spec to use these signals. If you are unsure how any of them behave,
ask me instead of assuming.
```
From that point, the planner refused to update the specification until its questions were answered, and asked about each sensor and roller individually. The rewritten specification was fully sensor-driven, with timers used only to detect faults (e.g., a box that takes too long to arrive).

#### *Iterating Through Testing*
The sensor-driven program still needed several iterations before it worked in the scene:
| Iteration | Session | What changed | Found by |
|---|---|---|---|
| 1 | Planner | Time-driven sequence, transfer sensors and rollers ignored | – |
| 2 | Planner | Sensor-driven sequence using all transfer sensors | Boxes never got onto the transfer |
| 3 | Planner | Boxes can queue while a side conveyor is busy; fault codes can be monitored | The machine stopped with a timeout fault |
| 4 | Executor | Transfer and side conveyors stop only after the box has fully passed their sensor | Transfer stopped too early; a box was left stranded at the end of a conveyor |

When the machine stopped for no visible reason, the planner did not guess. It asked for specific values from the running program, narrowing the cause down in a few exchanges to a timeout fault. Interestingly, the executor had already predicted this exact failure in the notes attached to its code, but since the two sessions only communicate through me, the planner never saw it. The executor predicted the stranded box as well, and when the last issues came up during testing, I resolved them directly with the executor, which explained the cause, proposed options and applied the chosen fix.

In the final program, the entry conveyor stops once a pallet reaches the load sensor at the transfer rather than the entry sensor, and a pallet waits before moving onto the left or right conveyor if another pallet is already there. This doesn't affect the functionality of the program, but details like this one damage the overall efficiency of the process, especially when scaled up to bigger production lines.

### Evaluation
Each tested program was scored from 1 to 5 in seven categories, with one line of evidence per score and a list of issues rated as Blocking or Minor. The first scene was reviewed by both the planner and the independent reviewer. Because the planner showed a bias towards its own work, the second scene was reviewed by the independent reviewer only.
#### **Brief Category Descriptions**:
- ***Spec Compliance*** — Does the program implement every requirement and deliverable in the specification?
- ***Functional Correctness*** — Does the logic produce the expected result for every test case in the specification?
- ***Safety & Interlocks*** — Are outputs blocked when the machine is stopped or in an emergency, and are dangerous output combinations prevented?
- ***Scan-Cycle Correctness*** — Are button presses and sensor changes detected exactly once, and is each output written in one place per cycle?
- ***Fault Handling*** — Are abnormal situations (timeouts, blocked boxes, invalid readings) detected and reported rather than ignored?
- ***Compilability*** — Does the program compile and run without manual edits?
- ***Documentation*** — Is the program commented, and is it clear where the tunable values are changed?

The scoring of each review was gathered into a table, and an average was calculated:
| Review | Spec Compliance | Functional Correctness | Safety & Interlocks | Scan-Cycle Correctness | Fault Handling | Compilability | Documentation | **Average** |
|---|---|---|---|---|---|---|---|---|
| Scene 1 — Planner | 5 | 5 | 5 | 5 | 4 | 5 | 5 | **4.86** |
| Scene 1 — Independent Reviewer | 5 | 5 | 4 | 5 | 4 | 5 | 5 | **4.71** |
| Scene 2 — Independent Reviewer | 3 | 4 | 5 | 5 | 4 | 5 | 4 | **4.29** |

For the first scene, the difference between the two reviewers was small in numbers but not in content: the independent reviewer lowered Safety & Interlocks because a loss of communication with the simulation would leave an open valve open, a risk the planner never raised. For the second scene, the lowest score was Spec Compliance. Both of its Blocking issues pointed to the final fixes made during testing: the program behaved correctly in the scene, but differently from what the specification described.

---
## Summary & Conclusion
This case study explored how AI models can turn a description of a machine into a working PLC program. The work was divided between three sessions: a planner that turned my observations into a specification, an executor that wrote the program, and an independent reviewer that scored the result. Two factory scenes were programmed this way: a timer-driven filling tank and a sensor-driven box sorter.

For the timer-driven scene, the workflow succeeded on the first attempt. For the sensor-driven scene, the difficulty was not writing the code but **understanding the machine**. The planner had all the necessary context but did not build a correct picture of the physical setup, and the executor, following its role, implemented that misunderstanding faithfully. What moved the project forward each time was an observation from the scene, followed by a model that either asked the right questions or explained the failure precisely.

#### How the AI Performed
- **The executor was the most reliable session** – its programs worked without syntax problems in both scenes, and it anticipated failures before they happened in testing.
- **The planner was strong on safety but weak on the physical setup** – it consistently thought through emergency stops, stuck buttons and forbidden output combinations, but it struggled to understand a more complex machine from screenshots and tables alone.
- **The independent reviewer was stricter and more thorough** – it found risks that the planner missed, which confirmed that the author of a plan should not be the one evaluating it.
> Based on this experience, instead of separate chat sessions, I would use an AI model built into OpenPLC itself. Having direct access to the programming environment and the machine's setup would give the model a better understanding of the physical process, which is essential to avoid these mistakes in more complex scenes.

**Author:** Charaf Mohamad