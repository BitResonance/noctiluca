use std::collections::BTreeMap;
use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader};

const LEVELS: [&str; 5] = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"];

fn valid_timestamp(s: &str) -> bool {
    let b = s.as_bytes();
    if b.len() != 20 || b[4] != b'-' || b[7] != b'-' || b[10] != b'T'
        || b[13] != b':' || b[16] != b':' || b[19] != b'Z' {
        return false;
    }
    [0usize, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18]
        .iter().all(|&i| b[i].is_ascii_digit())
}

fn analyze(path: &str) -> io::Result<String> {
    let input = BufReader::new(File::open(path)?);
    let mut levels: BTreeMap<String, usize> = BTreeMap::new();
    let mut services: BTreeMap<String, usize> = BTreeMap::new();
    let mut failures: BTreeMap<(String, String), usize> = BTreeMap::new();
    let mut events = 0usize;
    let mut malformed = 0usize;

    for line_result in input.lines() {
        let raw = line_result?;
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') { continue; }
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() < 4 || !valid_timestamp(parts[0]) || !LEVELS.contains(&parts[1]) {
            malformed += 1;
            continue;
        }
        let level = parts[1];
        let service = parts[2];
        let message = parts[3..].join(" ");
        if service.is_empty() || message.is_empty() { malformed += 1; continue; }
        events += 1;
        *levels.entry(level.to_string()).or_insert(0) += 1;
        *services.entry(service.to_string()).or_insert(0) += 1;
        if level == "ERROR" || level == "FATAL" {
            *failures.entry((service.to_string(), message)).or_insert(0) += 1;
        }
    }

    let mut out = format!("NOCTILUCA / REPORT\nEvents: {events}\nMalformed: {malformed}\n\nLEVEL COUNTS\n");
    for level in LEVELS { out.push_str(&format!("{level}={}\n", levels.get(level).copied().unwrap_or(0))); }
    out.push_str("\nSERVICE COUNTS\n");
    let mut service_entries: Vec<(String, usize)> = services.iter()
        .map(|(service, count)| (service.clone(), *count)).collect();
    service_entries.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
    for (service, count) in service_entries { out.push_str(&format!("{service}={count}\n")); }
    out.push_str("\nREPEATED FAILURES (>=3)\n");
    let mut repeated: Vec<(String, String, usize)> = failures.iter()
        .filter(|(_, count)| **count >= 3)
        .map(|((service, message), count)| (service.clone(), message.clone(), *count)).collect();
    repeated.sort_by(|a, b| b.2.cmp(&a.2).then_with(|| a.0.cmp(&b.0)).then_with(|| a.1.cmp(&b.1)));
    for (service, message, count) in repeated {
        out.push_str(&format!("{service} | {message} | {count}\n"));
    }
    Ok(out)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() == 2 && args[1] == "--listen" {
        print!("                 .      *\n                      .\n             .-\"\"\"\"-.\n          .-'  .--.  '-.\n         /   .      .   \\\n        |     .--.      |\n         \\    '----'    /\n          '-.        .-'\n             '------'\n\n       SIGNAL SOURCE: UNKNOWN\n       SOME THINGS ARE BETTER LEFT UNPARSED.\n");
        return;
    }
    if args.len() != 2 || args[1] == "-h" || args[1] == "--help" {
        println!("Usage: noctiluca <log-file>");
        if args.len() != 2 { std::process::exit(2); }
        return;
    }
    match analyze(&args[1]) {
        Ok(report) => print!("{report}"),
        Err(error) => { eprintln!("noctiluca: {error}"); std::process::exit(1); }
    }
}
