# Task description

This is the source of a Jekyll based static website visible at https://bmeaut.github.io/snippets/index.html.
The subpages are located in the "snippets" directory, all of them identified by a unique ID in the beginning of the directory name.
Some of them have syntax errors and so they are not visible in the compiled html output.

## Task 1: check for errors 

Your task is to
- fetch the generated html website from the above URL, and
- go along all the subdirectories (snippets) of the "snippets" directory and check whether they are visible in the html output
- also open all the snippets from the web and check whether all the referenced images are visible and there are no formatting issues like unrecognized markup remaining somehow in the html output.
- Create a log of the findings in the "Check log" subsection of this file. Enumerate all snippets in a table here are describe their status as "OK", "invisible", or "visible but misformatted".

### Clarifications

- Check all subdirectories under `snippets/`.
- A snippet is considered visible when it appears on the starting page.
- If it appears on the starting page as a link but its content is rendered incorrectly, classify it as "visible but misformatted".
- For this pass, complete only Task 1 and wait for approval before fixing any errors in Task 2.

## Task 2: fix the errors

Here your task is to go along the "check log" and fix the issues.

# Check log

