# Timetable Generator

A system capable of building a timetable while respecting user-defined constraints.

## Main Features
- Define teachers, time slots, available rooms, courses and seminars, student groups, etc.
- Add constraints specific to each teacher.
- Verify if the current constraints allow the construction of a timetable that satisfies all users' requirements.
- Generate a timetable if possible, or provide a set of unsatisfiable constraints.
- A graphical interface is optional. If not implemented, the result should be output as a plain text file.
- Domains can be defined either through a graphical interface or via a file in a specified format. They can be either a list of values or a range of integer values.
- The system uses some predefined constraints, e.g., certain sets of variables require unique values (for example, an event — the tuple `(room, day, time)` must be unique).

## Teacher Constraints
Teacher constraints can be introduced either through a graphical interface or via a file. They will be described in natural language. Constraints should include at least the following types:
- **Forbidden values** in a specific list/range (e.g., no courses on Mondays).
- **Required values** in a specific list/range (e.g., all hours on Tuesday or Wednesday).
- **Variable dependencies** (e.g., all lectures scheduled before seminars).
- **Global limits** (e.g., no more than 3 events per day).

## Modeling Task
- Propose a list of variables that represent the specific information for the problem. Indicate the domain for each variable.
- Propose a list of types of constraints defined for the variables above. Constraints can be soft or hard, associated with a user, or global.
- Provide examples for all modeled information above.
- Implement reading from a file and from the prompt for an instance of the problem.
