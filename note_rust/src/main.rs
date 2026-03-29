mod commands;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let argv = &args[1..];

    if argv.is_empty() {
        eprintln!("Usage: note <command> [options]");
        eprintln!("Commands: format, markdown, create");
        std::process::exit(1);
    }

    let command = argv[0].as_str();
    let command_args = &argv[1..];

    match command {
        "format" => commands::format::main(command_args),
        "markdown" => commands::markdown::main(command_args),
        "create" => commands::create::main(command_args),
        // fallback: treat all args as format arguments (e.g. note -f file.txt)
        _ => commands::format::main(argv),
    }
}
