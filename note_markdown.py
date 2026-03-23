import os
import re
import subprocess
import argparse
from dotenv import load_dotenv

load_dotenv()


def first_non_whitespace_position(s):
    return len(s) - len(s.lstrip())


def replace_spaces(line):
    # This function will be used as the replacement function in re.sub.
    # It takes a match object as argument,
    # returns a string of an underscore and spaces of length one less than the match
    def replacer(match):
        # Get the matched string
        s = match.group()
        # Return the replacement string
        return " " + " " * (len(s) - 1)

    # Use re.sub with replacer as the replacement function
    line = re.sub(" {2,}", replacer, line)
    return line


def git_file_added(file_path):
    try:
        git_log_command = ["git", "log", "--diff-filter=A", "--", file_path]
        result = subprocess.run(
            git_log_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stdout:
            lines = result.stdout.split("\n")
            for line in lines:
                if line.startswith("Date:"):
                    created_at = line[(line.find("Date:") + 6) : line.find("+")].strip()
                    return f"Created: {created_at}"
            print(
                f"No add information found for {file_path}. It may not be tracked by Git."
            )
        else:
            print(
                f"No log information found for {file_path}. It may not be tracked by Git."
            )
    except Exception as e:
        print(f"An error occurred: {e}")


def git_last_modifed(file_path):
    try:
        git_log_command = ["git", "log", "-n 1", file_path]
        result = subprocess.run(
            git_log_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        result_lines = result.stdout.split("\n")
        for line in result_lines:
            if line.startswith("Date:"):
                last_modified = line[(line.find("Date:") + 6) : line.find("+")].strip()
                return f"Modified: {last_modified}"
    except Exception as e:
        print(f"An error occurred: {e}")


def convert_to_markdown(
    input_file, output_file, preview=False, preview_output_dir=None
):
    print(f"{input_file}")
    use_date = os.getenv("USE_DATE", "False").lower() == "true"
    added_at = git_file_added(input_file) if use_date else None
    last_modified = git_last_modifed(input_file) if use_date else None

    if preview:
        preview_actions_result = {}

    with open(input_file, "r", encoding="UTF8") as infile:
        lines = infile.readlines()

    with open(output_file, "w", encoding="UTF8") as outfile:
        i = 0
        title_index = -1

        while i < len(lines):
            if i == 4 and use_date:  # add last modified time at line 4
                outfile.write(added_at + "  \n")
                outfile.write(last_modified + "  \n")
                outfile.write("  \n")

            original_line = lines[i].replace("\n", "")
            line = original_line
            actions = []

            # replace the leading spaces with code block
            if line.startswith(" "):
                first_non_whitespace_position = len(line) - len(line.lstrip())
                original_leading = line[0:first_non_whitespace_position]
                replaced_leading = original_leading.replace(" ", "░")
                line = replaced_leading + line[first_non_whitespace_position:]
                actions.append(f"replace({original_leading!r},{replaced_leading!r})")

            # replace space with non-breaking space
            # alt 0 1 6 0 or alt 2 5 5 or option space on mac
            before_replace_spaces = line
            line = replace_spaces(line)
            if line != before_replace_spaces:
                actions.append(f"replace({before_replace_spaces!r},{line!r})")

            output_line = ""

            if not line:  # If line is empty, do nothing
                output_line = ""

            # if next line is all ==== then current line is title, do nothing
            elif (
                i < len(lines) - 1
                and (lines[i + 1].replace("=", "") == "")
                and len(lines[i]) == len(lines[i + 1])
            ):
                output_line = line

            # if next line is all --- then current line is section title, do nothing
            elif (
                i < len(lines) - 1
                and (lines[i + 1].replace("-", "") == "")
                and len(lines[i]) == len(lines[i + 1])
            ):
                output_line = line

            # if line.trim() start with # then it is not a title in markdown
            # it is a comment, use \# to replace #
            elif line.startswith("#"):
                output_line = "\\" + line
                actions.append(f"replace({line!r},{output_line!r})")

            # if the line.trim() starts with $ it is not a fomular in markdown
            # it is maybe a bash input, use \$ to replace the $
            elif line.startswith("$"):
                output_line = "\\" + line
                actions.append(f"replace({line!r},{output_line!r})")

            else:
                output_line = line

            if output_line == "":
                outfile.write("\n")
            else:
                outfile.write(output_line + "  \n")

            if preview:
                if not actions:
                    actions = ["do_nothing"]
                preview_actions_result[i + 1] = (
                    f"[{','.join(actions)}],{original_line},{output_line}"
                )

            i += 1

    if preview:
        original_name = os.path.splitext(os.path.basename(input_file))[0]
        preview_filename = f"{original_name}_pr.txt"
        if preview_output_dir is None:
            preview_output_dir = os.path.dirname(output_file)
        preview_file = os.path.join(preview_output_dir, preview_filename)

        print("Preview actions:")
        with open(preview_file, "w", encoding="UTF8") as preview_outfile:
            for line_number, action_result in preview_actions_result.items():
                preview_line = f"{line_number}: {action_result}"
                print(preview_line)
                preview_outfile.write(preview_line + "\n")

        print(f"Preview output file: {preview_file}")
        return preview_actions_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview actions for one file from TARGET_DIR.",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help="Filename inside TARGET_DIR. Used with --preview to process only one file.",
    )
    args = parser.parse_args()

    # Read target directory from .env file
    input_path = os.getenv("TARGET_DIR", "./")

    # Ensure input_path is a valid directory
    if not os.path.isdir(input_path):
        print(f"Error: TARGET_DIR '{input_path}' is not a valid directory.")
        exit(1)

    # Preview
    if args.preview and args.filename:
        normalized_filename = re.sub(r"\s+", " ", args.filename).strip()
        base_name, ext = os.path.splitext(normalized_filename)
        candidate_names = [normalized_filename]

        if ext.lower() == ".md":
            candidate_names.append(base_name + ".txt")
            if not base_name.endswith(" Note"):
                candidate_names.append(base_name + " Note.txt")
        elif ext.lower() == ".txt":
            if not base_name.endswith(" Note"):
                candidate_names.append(base_name + " Note.txt")
        else:
            candidate_names.append(normalized_filename + ".txt")
            candidate_names.append(normalized_filename + " Note.txt")

        input_file = None
        for candidate_name in candidate_names:
            candidate_file = os.path.join(input_path, candidate_name)
            if os.path.isfile(candidate_file):
                input_file = candidate_file
                break

        if input_file is None:
            print(
                f"Error: file '{normalized_filename}' not found inside TARGET_DIR '{input_path}'."
            )
            exit(1)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(
            script_dir, os.path.splitext(os.path.basename(input_file))[0] + ".md"
        )
        convert_to_markdown(
            input_file,
            output_file,
            preview=True,
            preview_output_dir=script_dir,
        )
        return

    if args.preview and not args.filename:
        print(
            "Error: --preview requires a filename, e.g. python note_markdown.py --preview filename.txt"
        )
        exit(1)

    # Process files
    # Create .markdown folder in the target directory
    output_path = os.path.join(input_path, ".markdown")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Read filter setting from .env file
    use_nsfw_filter = os.getenv("USE_NSFW_FILTER", "true").lower() == "true"
    note_filter = ["Sex", "Adult"] if use_nsfw_filter else []

    for filename in os.listdir(input_path):
        # Assuming all your note files have .txt extension
        if filename.endswith(" Note.txt") and not any(
            x in filename for x in note_filter
        ):
            input_file = os.path.join(input_path, filename)
            output_file = os.path.join(output_path, filename.replace(".txt", ".md"))

            convert_to_markdown(input_file, output_file)


if __name__ == "__main__":
    main()
