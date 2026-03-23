import os
import re
import subprocess
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


def convert_to_markdown(input_file, output_file):
    print(f"{input_file}")
    use_date = os.getenv("USE_DATE", "False").lower() == "true"
    added_at = git_file_added(input_file) if use_date else None
    last_modified = git_last_modifed(input_file) if use_date else None

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

            line = lines[i]

            # remove new line, will be added later
            line = line.replace("\n", "")

            # replace the leading spaces with code block
            if line.startswith(" "):
                first_non_whitespace_position = len(line) - len(line.lstrip())
                line = (
                    line[0:first_non_whitespace_position].replace(" ", "░")
                    + line[first_non_whitespace_position:]
                )

            # replace space with non-breaking space
            # alt 0 1 6 0 or alt 2 5 5 or option space on mac
            line = replace_spaces(line)

            if not line:  # If line is empty, do nothing
                outfile.write("\n")

            # if next line is all ==== then current line is title, do nothing
            elif (
                i < len(lines) - 1
                and (lines[i + 1].replace("=", "") == "")
                and len(lines[i]) == len(lines[i + 1])
            ):
                outfile.write(line + "  \n")

            # if next line is all --- then current line is section title, do nothing
            elif (
                i < len(lines) - 1
                and (lines[i + 1].replace("-", "") == "")
                and len(lines[i]) == len(lines[i + 1])
            ):
                outfile.write(line + "  \n")

            # if line.trim() start with # then it is not a title in markdown
            # it is a comment, use \# to replace #
            elif line.startswith("#"):
                outfile.write("\\" + line + "  \n")

            # if the line.trim() starts with $ it is not a fomular in markdown
            # it is maybe a bash input, use \$ to replace the $
            elif line.startswith("$"):
                outfile.write("\\" + line + "  \n")

            else:
                outfile.write(line + "  \n")

            i += 1


def main():
    # Read target directory from .env file
    input_path = os.getenv("TARGET_DIR", "./")

    # Ensure input_path is a valid directory
    if not os.path.isdir(input_path):
        print(f"Error: TARGET_DIR '{input_path}' is not a valid directory.")
        exit(1)

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
