package dev.noctiluca;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public final class Main {
    private static final List<String> LEVELS = List.of("DEBUG", "INFO", "WARN", "ERROR", "FATAL");

    private record FailureKey(String service, String message) {}
    private record RepeatedFailure(String service, String message, int count) {}

    private static boolean validTimestamp(String value) {
        if (value.length() != 20 || value.charAt(4) != '-' || value.charAt(7) != '-'
                || value.charAt(10) != 'T' || value.charAt(13) != ':'
                || value.charAt(16) != ':' || value.charAt(19) != 'Z') return false;
        int[] indexes = {0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18};
        for (int index : indexes) {
            char c = value.charAt(index);
            if (c < '0' || c > '9') return false;
        }
        return true;
    }

    private static String analyze(Path path) throws IOException {
        Map<String, Integer> levelCounts = new HashMap<>();
        Map<String, Integer> serviceCounts = new TreeMap<>();
        Map<FailureKey, Integer> failureCounts = new HashMap<>();
        int events = 0;
        int malformed = 0;

        for (String raw : Files.readAllLines(path)) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] parts = line.split("\\s+");
            if (parts.length < 4 || !validTimestamp(parts[0]) || !LEVELS.contains(parts[1])) {
                malformed++;
                continue;
            }
            String level = parts[1];
            String service = parts[2];
            String message = String.join(" ", java.util.Arrays.copyOfRange(parts, 3, parts.length));
            if (service.isEmpty() || message.isEmpty()) { malformed++; continue; }
            events++;
            levelCounts.merge(level, 1, Integer::sum);
            serviceCounts.merge(service, 1, Integer::sum);
            if (level.equals("ERROR") || level.equals("FATAL")) {
                failureCounts.merge(new FailureKey(service, message), 1, Integer::sum);
            }
        }

        StringBuilder out = new StringBuilder();
        out.append("NOCTILUCA / REPORT\nEvents: ").append(events)
                .append("\nMalformed: ").append(malformed).append("\n\nLEVEL COUNTS\n");
        for (String level : LEVELS) out.append(level).append('=').append(levelCounts.getOrDefault(level, 0)).append('\n');
        out.append("\nSERVICE COUNTS\n");
        serviceCounts.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey()))
                .forEach(entry -> out.append(entry.getKey()).append('=').append(entry.getValue()).append('\n'));
        out.append("\nREPEATED FAILURES (>=3)\n");
        List<RepeatedFailure> repeated = new ArrayList<>();
        failureCounts.forEach((key, count) -> {
            if (count >= 3) repeated.add(new RepeatedFailure(key.service(), key.message(), count));
        });
        repeated.sort(Comparator.comparingInt(RepeatedFailure::count).reversed()
                .thenComparing(RepeatedFailure::service).thenComparing(RepeatedFailure::message));
        for (RepeatedFailure item : repeated) {
            out.append(item.service()).append(" | ").append(item.message()).append(" | ")
                    .append(item.count()).append('\n');
        }
        return out.toString();
    }

    public static void main(String[] args) {
        if (args.length == 1 && args[0].equals("--listen")) {
            System.out.print(String.join("\n", List.of(
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
            )) + "\n");
            return;
        }
        if (args.length != 1 || args[0].equals("-h") || args[0].equals("--help")) {
            System.out.println("Usage: noctiluca <log-file>");
            if (args.length != 1) System.exit(2);
            return;
        }
        try {
            System.out.print(analyze(Path.of(args[0])));
        } catch (IOException | RuntimeException error) {
            System.err.println("noctiluca: " + error.getMessage());
            System.exit(1);
        }
    }
}
