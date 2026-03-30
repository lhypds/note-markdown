
.note
=====


`note` is a format for `txt` files.  

Basiclly it is free to write. There are few rules to follow:  
- Note file name should be `ABC Note`, `ABC` is the topic.  
- Title with double underline (`=`), section title with a underline (`-`).  
- The First section title will be `ABC`. Describes the topic.  


note
----

Executable.  

Use `setup.sh` to setup and use `build.sh` to build.  

* Python version  
`python` and `pip` is required.  

* Rust version  
Locate at `rust` folder.  
Rust version is faster.  
`cargo` is required, use `brew install rust` to install.  

Run `build.sh` to select Python or Rust.  
Either python or rust version generates `note` executable.  
Run `note` command with commands.  

Release  
`release.sh` to build `dot_note.zip` to `release` folder.


command: format
---------------

`format` - Format the note file.  
`./note format [-f|--file] abc_note.txt`  
It will format the note.  

* Format on Save  
Refer [doc](./doc) to setup `Format on Save` for text editors.  
Support setup for VS Code and Sublime Text.  


command: create
---------------

`create` - Create a new note file.  
`./note create --name "Abc`  
It will create a new note file with name `Abc Note.txt`.

`[-d|--directory]`  
Specify the directory to create the note in. Defaults to parent directory.  
`./note create --name "Abc" --directory path/to/directory`  


command: markdown
-----------------

`markdown` - Convert note to Markdown format.  
`./note markdown [-f|--file] path/to/note.txt`  
It will convert `note.txt` to `note.md`.  

`--preview`  
`./note markdown --preview path/to/note.txt` will generate `note_pr.md` and `note_pr.txt` for preview.  


tools scripts
-------------

underline_fix.py  
Fix the unederline, make the underline the same length as the title.  
`underline_fix.py` to genreate `scan_result.json`.  
Review and edit the `scan_result.json`.  
Then run `underline_fix.py --fix` to execute the fix.  

line_ending_check.py  
Check the line ending.  
