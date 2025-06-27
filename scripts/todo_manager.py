import argparse
import datetime
import os
import re
import uuid

TODO_FILE = "TODO.md"


def generate_uuid() -> str:
    """Generates a unique ID for a TODO item."""
    return str(uuid.uuid4())


def add_todo_to_file(
    description: str,
    location: str = "",
    context: str = "",
    priority: str = "Medium",
    section: str = "General TODOs",
) -> None:
    """
    Adds a new TODO item to the TODO.md file.
    """
    new_id = generate_uuid()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    # Default to Medium priority if not specified or invalid
    valid_priorities = ["High", "Medium", "Low"]
    if priority not in valid_priorities:
        priority = "Medium"

    todo_entry = f"- [ ] **UUID: {new_id}** — {description}\n"
    if priority:
        todo_entry += f"  - Priority: {priority}\n"
    if location:
        todo_entry += f"  - Location: {location}\n"
    if context:
        todo_entry += f"  - Context: {context}\n"
    todo_entry += f"  - Added: {timestamp}\n\n"  # Added timestamp

    if not os.path.exists(TODO_FILE):
        with open(TODO_FILE, "w") as f:
            f.write(f"# TODOs for Codebase Quality and Conformance\n\n")
            f.write(
                f"This file tracks actionable TODOs in the codebase. Each TODO is linked to a unique UUID and references the exact code location. Please check off items as you address them.\n\n"
            )
            f.write("---\n\n")

    with open(TODO_FILE, "r+") as f:
        content = f.readlines()

        # Find the target section or append at the end
        section_header = f"## {section}\n"
        section_index = -1
        hr_index = -1

        for i, line in enumerate(content):
            if line.strip() == section_header.strip():
                section_index = i
                break
            if line.strip() == "---":
                hr_index = i  # Keep track of horizontal rulers

        if section_index != -1:
            # Insert before the next section or at the end of the current section
            insert_at = section_index + 1
            # Skip any blank lines after the header
            while insert_at < len(content) and content[insert_at].strip() == "":
                insert_at += 1
            # Move past existing items in the section
            while insert_at < len(content) and (
                content[insert_at].startswith("- [")
                or content[insert_at].startswith("  - ")
            ):
                # Find the end of the current multi-line TODO item
                if content[insert_at].startswith("- ["):
                    insert_at += 1  # move to first sub-line
                    while insert_at < len(content) and content[insert_at].startswith(
                        "  - "
                    ):
                        insert_at += 1
                    # check for blank line after item
                    if insert_at < len(content) and content[insert_at].strip() == "":
                        insert_at += 1  # move past blank line
                else:  # Should not happen if parsing correctly
                    insert_at += 1

            content.insert(insert_at, todo_entry)
        else:
            # Section not found, add it before the last '---' or at the end
            new_section_content = f"{section_header}\n{todo_entry}"
            if hr_index != -1 and any(
                line.startswith("## ") for line in content[hr_index:]
            ):
                # Insert before the last '---' if there are sections after it
                # Find the last '---' that is followed by a section
                last_hr_before_section = -1
                for i in range(len(content) - 1, -1, -1):
                    if content[i].strip() == "---":
                        # Check if there's a section header after this HR
                        is_last_hr = True
                        for j in range(i + 1, len(content)):
                            if content[j].strip().startswith("## "):
                                is_last_hr = False
                                break
                        if not is_last_hr:  # this HR is followed by a section
                            last_hr_before_section = i
                            break
                if last_hr_before_section != -1:
                    content.insert(
                        last_hr_before_section, new_section_content + "---\n\n"
                    )
                else:  # No '---' before a section, append to end
                    content.append("---\n\n" + new_section_content)

            else:  # No sections or no '---' found, or last '---' is truly the end
                content.append("---\n\n" + new_section_content)

        f.seek(0)
        f.writelines(content)
        f.truncate()
    print(
        f"Added TODO: {description} (UUID: {new_id}) to section '{section}' in {TODO_FILE}"
    )


def update_todo_status_in_file(uuid_to_update: str, new_status: str) -> None:
    """
    Updates the status of a TODO item in TODO.md.
    new_status can be 'open' or 'closed'.
    """
    if not os.path.exists(TODO_FILE):
        print(f"Error: {TODO_FILE} not found.")
        return

    status_marker_map = {"open": "[ ]", "closed": "[x]"}
    if new_status.lower() not in status_marker_map:
        print(f"Error: Invalid status '{new_status}'. Must be 'open' or 'closed'.")
        return

    target_marker = status_marker_map[new_status.lower()]
    updated = False

    with open(TODO_FILE, "r+") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if f"**UUID: {uuid_to_update}**" in line:
                # Regex to find and replace the status marker, e.g., - [ ] or - [x]
                # It should handle potential variations in spacing around the marker.
                current_marker_match = re.search(r"^- \[( |x|X)\] ", line)
                if current_marker_match:
                    current_marker_full = current_marker_match.group(
                        0
                    )  # e.g., "- [ ] "
                    # Construct the new line with the updated marker
                    # Ensure we keep the rest of the line intact after the marker
                    rest_of_line = line[len(current_marker_full) :]
                    lines[i] = f"- {target_marker} {rest_of_line}"
                    updated = True
                    break

        if updated:
            f.seek(0)
            f.writelines(lines)
            f.truncate()
            print(f"Updated status of TODO UUID {uuid_to_update} to '{new_status}'.")
        else:
            print(
                f"Error: TODO with UUID {uuid_to_update} not found or line format incorrect."
            )


def remove_todo_from_file(uuid_to_remove: str) -> None:
    """
    Removes a TODO item and its associated details from TODO.md.
    """
    if not os.path.exists(TODO_FILE):
        print(f"Error: {TODO_FILE} not found.")
        return

    lines_to_keep = []
    removed = False
    in_removal_block = False

    with open(TODO_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        if f"**UUID: {uuid_to_remove}**" in line:
            removed = True
            in_removal_block = True  # Start of the block to remove
            continue  # Skip this line (the main TODO line)

        if in_removal_block:
            # Check if it's a sub-item of the TODO to remove
            if line.strip().startswith("- ") and not line.strip().startswith(
                "- ["
            ):  # A new top-level item starts
                in_removal_block = False
            elif line.strip() == "" and any(
                next_line.strip().startswith("- [")
                for next_line in lines[lines.index(line) + 1 :]
            ):
                # This is a blank line likely separating TODO items
                in_removal_block = (
                    False  # Stop removing if it's a blank line before another item
                )
            elif (
                not line.startswith("  - ") and line.strip() != ""
            ):  # Not a sub-item and not blank
                in_removal_block = False

            if (
                line.strip().startswith("## ") or line.strip() == "---"
            ):  # New section or separator
                in_removal_block = False

            if (
                in_removal_block and line.strip() == ""
            ):  # remove blank line after todo item
                # only remove if it's truly the blank line after the item, not before a new section
                current_index = lines.index(line)
                if current_index + 1 < len(lines):
                    next_line_strip = lines[current_index + 1].strip()
                    if (
                        next_line_strip.startswith("## ")
                        or next_line_strip == "---"
                        or next_line_strip.startswith("- [")
                    ):
                        pass  # keep this blank line as it's before a new section/item
                    else:
                        continue  # skip this blank line as it's part of the item
                else:  # this is the last blank line
                    continue

            if in_removal_block:
                continue  # Skip sub-lines of the TODO to remove

        lines_to_keep.append(line)

    if removed:
        with open(TODO_FILE, "w") as f:
            f.writelines(lines_to_keep)
        print(f"Removed TODO with UUID {uuid_to_remove}.")
    else:
        print(f"Error: TODO with UUID {uuid_to_remove} not found.")


def generate_report_from_file() -> None:
    """
    Parses TODO.md and prints a report of TODO items by status and location.
    """
    if not os.path.exists(TODO_FILE):
        print(f"Error: {TODO_FILE} not found.")
        return

    open_todos = 0
    closed_todos = 0
    todos_by_location = {}  # Store counts of todos per location
    current_location = None

    with open(TODO_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        line_strip = line.strip()

        # Check for TODO item start
        if line_strip.startswith("- [ ]"):
            open_todos += 1
            current_location = None  # Reset for new TODO item
        elif line_strip.startswith("- [x]") or line_strip.startswith("- [X]"):
            closed_todos += 1
            current_location = None  # Reset for new TODO item

        # Check for location if we are inside a TODO item context
        if (
            line_strip.startswith("- [ ]")
            or line_strip.startswith("- [x]")
            or line_strip.startswith("- [X]")
        ) or (
            current_location is None and (line.startswith("  - Location:"))
        ):  # if we just started a todo or are looking for location
            if line.startswith("  - Location:"):
                current_location = line_strip.split("Location:", 1)[1].strip()
                if current_location:
                    if current_location not in todos_by_location:
                        todos_by_location[current_location] = {
                            "open": 0,
                            "closed": 0,
                            "total": 0,
                        }

        # If we have identified a location for the current TODO item, increment its status
        if current_location and (
            line_strip.startswith("- [ ]")
            or line_strip.startswith("- [x]")
            or line_strip.startswith("- [X]")
        ):
            status_key = "open" if line_strip.startswith("- [ ]") else "closed"
            if (
                current_location in todos_by_location
            ):  # ensure location was set from a "Location:" line
                todos_by_location[current_location][status_key] += 1
                todos_by_location[current_location]["total"] += 1

    print("\n--- TODO Report ---")
    total_todos = open_todos + closed_todos
    print(f"Total TODOs: {total_todos}")
    print(f"  Open: {open_todos}")
    print(f"  Closed: {closed_todos}")

    if todos_by_location:
        print("\nTODOs by Location:")
        # Sort locations for consistent output, e.g., by total TODOs descending
        sorted_locations = sorted(
            todos_by_location.items(), key=lambda item: item[1]["total"], reverse=True
        )
        for loc, counts in sorted_locations:
            print(
                f"  - {loc}: {counts['total']} (Open: {counts['open']}, Closed: {counts['closed']})"
            )
    else:
        print("\nNo location data found for TODOs.")
    print("-------------------\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI Tool to manage TODOs in TODO.md")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add TODO command
    add_parser = subparsers.add_parser("add", help="Add a new TODO item")
    add_parser.add_argument(
        "description", type=str, help="Description of the TODO item"
    )
    add_parser.add_argument(
        "--location",
        type=str,
        default="",
        help="Code location (e.g., path/to/file.py:line_number)",
    )
    add_parser.add_argument(
        "--context", type=str, default="", help="Context or details for the TODO"
    )
    add_parser.add_argument(
        "--priority",
        type=str,
        default="Medium",
        choices=["High", "Medium", "Low"],
        help="Priority of the TODO (High, Medium, Low)",
    )
    add_parser.add_argument(
        "--section",
        type=str,
        default="General TODOs",
        help="Section in TODO.md to add this item (e.g., 'General TODOs', 'New Features')",
    )

    # Update TODO status command
    update_parser = subparsers.add_parser(
        "update", help="Update the status of an existing TODO item"
    )
    update_parser.add_argument("uuid", type=str, help="UUID of the TODO item to update")
    update_parser.add_argument(
        "status",
        type=str,
        choices=["open", "closed"],
        help="New status for the TODO (open, closed)",
    )

    # Remove TODO command
    remove_parser = subparsers.add_parser("remove", help="Remove an existing TODO item")
    remove_parser.add_argument("uuid", type=str, help="UUID of the TODO item to remove")

    # Report TODOs command
    report_parser = subparsers.add_parser(
        "report", help="Generate a report of TODO items"
    )

    args = parser.parse_args()

    if args.command == "add":
        add_todo_to_file(
            args.description, args.location, args.context, args.priority, args.section
        )
    elif args.command == "update":
        update_todo_status_in_file(args.uuid, args.status)
    elif args.command == "remove":
        remove_todo_from_file(args.uuid)
    elif args.command == "report":
        generate_report_from_file()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
