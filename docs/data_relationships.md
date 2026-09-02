# Data Relationships

How the five raw tables connect. Written after actually confirming each key lines up -- not assumed from matching column names.

## Entity diagram

```
EMPLOYEE
  |
  +-- Employee ID ---- Engagement Data      (one-to-one, via EmployeeID)
  |
  +-- Job Role ------- Occupation Data      (many-to-one, via JobRole <-> RoleName)
        |
        +-- Essential Skills                 (one-to-many, via OccupationID)
        +-- Software Skills                  (one-to-many, via OccupationID)
```

## Join key table

| table_a            | table_b                   | join_key                                      | relationship   | reason                                                                                                                                                                                                                           |
|:-------------------|:--------------------------|:----------------------------------------------|:---------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| employee_attrition | hr_performance_engagement | EmployeeID                                    | one-to-one     | Same employee's performance/engagement record.                                                                                                                                                                                   |
| employee_attrition | occupation_data           | JobRole (attrition) <-> RoleName (occupation) | many-to-one    | Many employees share the same JobRole. Note: this is a TEXT join, not an ID join -- JobRole and RoleName must match exactly after cleaning, which is riskier than an ID join and worth double-checking (see verification below). |
| occupation_data    | essential_skills          | OccupationID                                  | one-to-many    | Each role requires several essential (non-software) skills.                                                                                                                                                                      |
| occupation_data    | software_skills           | OccupationID                                  | one-to-many    | Each role requires several software/tool skills.                                                                                                                                                                                 |

## Verification notes

- `EmployeeID`: 600 IDs confirmed present in both `employee_attrition` and `hr_performance_engagement`.
- `JobRole` <-> `RoleName`: all 7 distinct JobRole values in `employee_attrition` have a matching `RoleName` in `occupation_data` after cleaning (Section 3 standardized casing on both).
