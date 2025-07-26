# Label Types

## Goal

When declaring / managing a given label, we would like to assert that it
is a given type, such as Theorem, Question, Exercise, Table, Figure, etc.

This list of types *should* be maintained in the database itself, however,
we might not provide a UI for editing this list on the website itself.

We do not provide a UI for two reasons:

1. On the grounds that it would add complexity for an action which won't be done
   very often.

2. We want to discourage type changes.

## Solution

1. Update / normalise the database to record the type of each label where
   the types are kept in a types table.

2. Provide a command line tool which:
  - adds / removes / renames entries from the types table
  - updates all uses of a given type to reflect any changes.

