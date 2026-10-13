package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strings"
	"unicode"
)

var levels = []string{"DEBUG", "INFO", "WARN", "ERROR", "FATAL"}

type failureKey struct{ service, message string }
type repeatedFailure struct {
	service, message string
	count            int
}

func validTimestamp(s string) bool {
	if len(s) != 20 || s[4] != '-' || s[7] != '-' || s[10] != 'T' || s[13] != ':' || s[16] != ':' || s[19] != 'Z' {
		return false
	}
	for _, i := range []int{0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18} {
		if !unicode.IsDigit(rune(s[i])) { return false }
	}
	return true
}

func analyze(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil { return "", err }
	defer file.Close()

	levelCounts := map[string]int{}
	serviceCounts := map[string]int{}
	failureCounts := map[failureKey]int{}
	validLevels := map[string]bool{}
	for _, l := range levels { validLevels[l] = true }
	events, malformed := 0, 0
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") { continue }
		parts := strings.Fields(line)
		if len(parts) < 4 || !validTimestamp(parts[0]) || !validLevels[parts[1]] {
			malformed++
			continue
		}
		level, service, message := parts[1], parts[2], strings.Join(parts[3:], " ")
		if service == "" || message == "" { malformed++; continue }
		events++
		levelCounts[level]++
		serviceCounts[service]++
		if level == "ERROR" || level == "FATAL" { failureCounts[failureKey{service, message}]++ }
	}
	if err := scanner.Err(); err != nil { return "", err }

	var out strings.Builder
	fmt.Fprintf(&out, "NOCTILUCA / REPORT\nEvents: %d\nMalformed: %d\n\nLEVEL COUNTS\n", events, malformed)
	for _, level := range levels { fmt.Fprintf(&out, "%s=%d\n", level, levelCounts[level]) }
	out.WriteString("\nSERVICE COUNTS\n")
	services := make([]string, 0, len(serviceCounts))
	for service := range serviceCounts { services = append(services, service) }
	sort.Slice(services, func(i, j int) bool {
		if serviceCounts[services[i]] != serviceCounts[services[j]] { return serviceCounts[services[i]] > serviceCounts[services[j]] }
		return services[i] < services[j]
	})
	for _, service := range services { fmt.Fprintf(&out, "%s=%d\n", service, serviceCounts[service]) }
	out.WriteString("\nREPEATED FAILURES (>=3)\n")
	repeated := make([]repeatedFailure, 0)
	for key, count := range failureCounts {
		if count >= 3 { repeated = append(repeated, repeatedFailure{key.service, key.message, count}) }
	}
	sort.Slice(repeated, func(i, j int) bool {
		a, b := repeated[i], repeated[j]
		if a.count != b.count { return a.count > b.count }
		if a.service != b.service { return a.service < b.service }
		return a.message < b.message
	})
	for _, item := range repeated { fmt.Fprintf(&out, "%s | %s | %d\n", item.service, item.message, item.count) }
	return out.String(), nil
}

func main() {
	if len(os.Args) == 2 && os.Args[1] == "--listen" {
		fmt.Print("                 .      *\n                      .\n             .-\"\"\"\"-.\n          .-'  .--.  '-.\n         /   .      .   \\\n        |     .--.      |\n         \\    '----'    /\n          '-.        .-'\n             '------'\n\n       SIGNAL SOURCE: UNKNOWN\n       SOME THINGS ARE BETTER LEFT UNPARSED.\n")
		return
	}
	if len(os.Args) != 2 || os.Args[1] == "-h" || os.Args[1] == "--help" {
		fmt.Println("Usage: noctiluca <log-file>")
		if len(os.Args) != 2 { os.Exit(2) }
		return
	}
	output, err := analyze(os.Args[1])
	if err != nil { fmt.Fprintf(os.Stderr, "noctiluca: %v\n", err); os.Exit(1) }
	fmt.Print(output)
}
