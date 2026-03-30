use std::fs;
use std::path::{Path, PathBuf};

fn replace_spaces(line: &str) -> String {
    let mut out = String::with_capacity(line.len());
    let chars: Vec<char> = line.chars().collect();
    let mut i = 0;

    while i < chars.len() {
        if chars[i] == ' ' {
            let start = i;
            while i < chars.len() && chars[i] == ' ' {
                i += 1;
            }
            let run = i - start;
            if run >= 2 {
                out.push(' ');
                for _ in 1..run {
                    out.push('\u{00A0}');
                }
            } else {
                out.push(' ');
            }
        } else {
            out.push(chars[i]);
            i += 1;
        }
    }

    out
}

fn prefix_tofu(line: &str) -> String {
    format!("□{}", line)
}

fn is_underline_candidate(line: &str) -> bool {
    !line.is_empty() && (line.chars().all(|c| c == '=') || line.chars().all(|c| c == '-'))
}

fn trim_crlf(s: &str) -> String {
    s.trim_end_matches(['\n', '\r']).to_string()
}

pub fn run(input_file: &Path, output_file: &Path, preview: bool) -> Result<(), String> {
    println!("{}", input_file.display());

    let content = fs::read_to_string(input_file)
        .map_err(|e| format!("failed to read '{}': {}", input_file.display(), e))?;

    let lines: Vec<String> = if content.is_empty() {
        Vec::new()
    } else {
        content.lines().map(trim_crlf).collect()
    };

    let mut output_lines: Vec<String> = Vec::with_capacity(lines.len());
    let mut preview_lines: Vec<String> = Vec::new();

    let mut p = 0usize;
    while p < lines.len() {
        let line_orig = lines[p].clone();
        let mut line = line_orig.clone();
        let mut actions: Vec<String> = Vec::new();

        if line.starts_with(' ') {
            let leading_ws_count = line.chars().take_while(|c| *c == ' ').count();
            let leading = "░".repeat(leading_ws_count);
            let rest: String = line.chars().skip(leading_ws_count).collect();
            line = format!("{}{}", leading, rest);
            if preview {
                actions.push("leading_whitespace_░".to_string());
            }
        }

        let before = line.clone();
        line = replace_spaces(&line);
        if preview && line != before {
            actions.push("replace_spaces".to_string());
        }

        let mut output_line = String::new();
        let mut add_2_spaces = true;

        if line.is_empty() {
            output_line.clear();
        } else if p < lines.len() - 1
            && (lines[p + 1].replace('=', "").is_empty()
                || lines[p + 1].replace('-', "").is_empty())
            && lines[p].chars().count() == lines[p + 1].chars().count()
        {
            output_line = line.clone();
            add_2_spaces = false;
            if preview {
                actions.push("title_or_section_title".to_string());
            }
        } else if is_underline_candidate(&line)
            && (p == 0
                || line.chars().count() != lines[p - 1].trim_end_matches(['\n', '\r']).chars().count())
        {
            output_line = prefix_tofu(&line);
            if preview {
                actions.push("prefix_tofu".to_string());
            }
        } else if is_underline_candidate(&line)
            && (p == 0
                || line.chars().count() == lines[p - 1].trim_end_matches(['\n', '\r']).chars().count())
        {
            output_line = line.clone();
            add_2_spaces = false;
            if preview {
                actions.push("title_underline".to_string());
            }
        } else if line.starts_with('>') {
            output_line = prefix_tofu(&line);
            if preview {
                actions.push("prefix_tofu,escape_blockquote".to_string());
            }
        } else if line.starts_with('#') {
            output_line = prefix_tofu(&line);
            if preview {
                actions.push("prefix_tofu,escape_#".to_string());
            }
        } else if line.starts_with('$') {
            output_line = prefix_tofu(&line);
            if preview {
                actions.push("prefix_tofu,escape_$".to_string());
            }
        } else {
            output_line = line.clone();
        }

        if add_2_spaces {
            if preview {
                actions.push("add_2_spaces".to_string());
            }
            output_line.push_str("  ");
        }
        output_lines.push(format!("{}\n", output_line));

        if preview {
            if actions.is_empty() {
                actions.push("do_nothing".to_string());
            }
            preview_lines.push(format!(
                "{}: [{}],{},{}",
                p + 1,
                actions.join(","),
                line_orig,
                output_line
            ));
        }

        p += 1;
    }

    fs::write(output_file, output_lines.concat())
        .map_err(|e| format!("failed to write '{}': {}", output_file.display(), e))?;

    if preview {
        let original_name = input_file
            .file_stem()
            .and_then(|s| s.to_str())
            .ok_or_else(|| "invalid input filename".to_string())?;
        let preview_filename = format!("{}_pr.txt", original_name);
        let preview_dir = output_file
            .parent()
            .ok_or_else(|| "invalid output path".to_string())?;
        let preview_file = preview_dir.join(preview_filename);
        fs::write(preview_file, format!("{}\n", preview_lines.join("\n")))
            .map_err(|e| format!("failed to write preview file: {}", e))?;
    }

    Ok(())
}

pub fn main(argv: &[String]) {
    let _ = dotenvy::dotenv();

    let mut preview = false;
    let mut file: Option<String> = None;

    let mut i = 0usize;
    while i < argv.len() {
        match argv[i].as_str() {
            "--preview" => {
                preview = true;
                i += 1;
            }
            arg if !arg.starts_with('-') => {
                file = Some(arg.to_string());
                i += 1;
            }
            arg => {
                eprintln!("Error: unrecognized argument '{}'.", arg);
                std::process::exit(1);
            }
        }
    }

    let mut file_path = match file {
        Some(f) => f.trim().to_string(),
        None => {
            eprintln!("Error: no file path provided.");
            std::process::exit(1);
        }
    };

    if !file_path.ends_with(".txt") {
        file_path.push_str(".txt");
    }

    let input_file = PathBuf::from(&file_path);
    if !input_file.is_file() {
        eprintln!("Error: file '{}' not found.", file_path);
        std::process::exit(1);
    }

    let output_path = std::env::current_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
        .join(".markdown");
    if !output_path.exists() {
        if let Err(e) = fs::create_dir_all(&output_path) {
            eprintln!("Error creating output directory: {}", e);
            std::process::exit(1);
        }
    }

    let stem = input_file
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("output");
    let output_file = output_path.join(format!("{}.md", stem));

    if let Err(e) = run(&input_file, &output_file, preview) {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
    println!("Processed files: 1");
}
