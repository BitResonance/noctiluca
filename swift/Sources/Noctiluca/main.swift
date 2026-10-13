import Foundation

let levels = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]

struct FailureKey: Hashable {
    let service: String
    let message: String
}

func validTimestamp(_ value: String) -> Bool {
    let bytes = Array(value.utf8)
    guard bytes.count == 20,
          bytes[4] == 45, bytes[7] == 45, bytes[10] == 84,
          bytes[13] == 58, bytes[16] == 58, bytes[19] == 90 else { return false }
    for i in [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18] {
        if bytes[i] < 48 || bytes[i] > 57 { return false }
    }
    return true
}

func analyze(_ path: String) throws -> String {
    let content = try String(contentsOfFile: path, encoding: .utf8)
    var levelCounts: [String: Int] = [:]
    var serviceCounts: [String: Int] = [:]
    var failureCounts: [FailureKey: Int] = [:]
    var events = 0
    var malformed = 0

    for raw in content.components(separatedBy: .newlines) {
        let line = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        if line.isEmpty || line.hasPrefix("#") { continue }
        let parts = line.split(whereSeparator: { $0.isWhitespace }).map(String.init)
        guard parts.count >= 4, validTimestamp(parts[0]), levels.contains(parts[1]) else {
            malformed += 1
            continue
        }
        let level = parts[1]
        let service = parts[2]
        let message = parts[3...].joined(separator: " ")
        guard !service.isEmpty, !message.isEmpty else { malformed += 1; continue }
        events += 1
        levelCounts[level, default: 0] += 1
        serviceCounts[service, default: 0] += 1
        if level == "ERROR" || level == "FATAL" {
            failureCounts[FailureKey(service: service, message: message), default: 0] += 1
        }
    }

    var lines = ["NOCTILUCA / REPORT", "Events: \(events)", "Malformed: \(malformed)", "", "LEVEL COUNTS"]
    lines += levels.map { "\($0)=\(levelCounts[$0, default: 0])" }
    lines += ["", "SERVICE COUNTS"]
    let sortedServices = serviceCounts.keys.sorted {
        let left = serviceCounts[$0, default: 0]
        let right = serviceCounts[$1, default: 0]
        if left != right { return left > right }
        return $0 < $1
    }
    for service in sortedServices { lines.append("\(service)=\(serviceCounts[service]!)") }
    lines += ["", "REPEATED FAILURES (>=3)"]
    let repeated = failureCounts.filter { $0.value >= 3 }.sorted {
        if $0.value != $1.value { return $0.value > $1.value }
        if $0.key.service != $1.key.service { return $0.key.service < $1.key.service }
        return $0.key.message < $1.key.message
    }
    for item in repeated { lines.append("\(item.key.service) | \(item.key.message) | \(item.value)") }
    return lines.joined(separator: "\n") + "\n"
}

let args = CommandLine.arguments
if args.count == 2 && args[1] == "--listen" {
    let signal = [
        "                 .      *",
        "                      .",
        "             .-\"\"\"\"-.",
        "          .-'  .--.  '-.",
        "         /   .      .   \\",
        "        |     .--.      |",
        "         \\    '----'    /",
        "          '-.        .-'",
        "             '------'",
        "",
        "       SIGNAL SOURCE: UNKNOWN",
        "       SOME THINGS ARE BETTER LEFT UNPARSED."
    ].joined(separator: "\n") + "\n"
    print(signal, terminator: "")
    exit(0)
}
if args.count != 2 || args[1] == "-h" || args[1] == "--help" {
    print("Usage: noctiluca <log-file>")
    if args.count != 2 { exit(2) }
} else {
    do {
        print(try analyze(args[1]), terminator: "")
    } catch {
        fputs("noctiluca: \(error.localizedDescription)\n", stderr)
        exit(1)
    }
}
