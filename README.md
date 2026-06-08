*This project has been created as part of the 42 curriculum by aalnahas.*

# Fly-in

## Description
Fly-in is a drone routing simulation written in Python. The goal is to move all drones from a start zone to an end zone in the fewest possible simulation turns. The program reads a map file defining zones and connections, then routes multiple drones simultaneously while respecting zone capacity, connection capacity, and movement cost rules.

## Instructions

**Install dependencies:**
```bash
make install
```

**Run the simulation:**
```bash
python3 main.py <map_file>
```

**Example:**
```bash
python3 main.py maps/easy1.txt
```

**Run linter:**
```bash
make lint
```

**Clean cache:**
```bash
make clean
```

## Algorithm

The pathfinding uses **Dijkstra's algorithm** with weighted edges based on zone types — normal and priority zones cost 1 turn, restricted zones cost 2 turns, blocked zones are skipped entirely. Priority zones are given a slight cost advantage (0.9) so they are preferred when paths have equal cost.

For multi-drone routing, a **Scheduler** runs on top of Dijkstra. It discovers multiple distinct paths by repeatedly running Dijkstra while excluding previously found middle zones. Drones are distributed across all available paths using round-robin assignment so they move in parallel rather than queuing on a single path.

Each turn the engine plans all moves before applying any of them. This ensures drones leaving a zone free up capacity for drones entering on the same turn, matching the subject rules exactly.

## Visual Representation

The terminal output uses ANSI color codes to make the simulation easy to follow:

- **Yellow** — turn headers
- **Cyan** — drone labels (D1, D2, ...)
- **Green** — priority zone destinations
- **Red** — restricted zone destinations and mid-flight connections
- **White** — normal zone destinations

A summary is printed at the end showing total drones delivered and total turns taken.

## Resources

- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)
- [Graph theory basics — Khan Academy](https://www.khanacademy.org/computing/computer-science/algorithms)
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)

**AI usage:** Claude (Anthropic) was used throughout this project as a learning tool and coding assistant. It was used to explain concepts (graph theory, Dijkstra, BFS, OOP, type hints), review code for correctness, help debug issues, and guide the overall project structure. All code was written and understood by the student — AI was never used to blindly generate and submit code.
