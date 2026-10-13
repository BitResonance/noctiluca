#define _POSIX_C_SOURCE 200809L
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *LEVELS[] = {"DEBUG", "INFO", "WARN", "ERROR", "FATAL"};
#define LEVEL_COUNT 5

typedef struct { char *name; int count; } Count;
typedef struct { char *service; char *message; int count; } Failure;
typedef struct { Count *items; size_t len; size_t cap; } CountList;
typedef struct { Failure *items; size_t len; size_t cap; } FailureList;

static void fail_usage(void) {
    fprintf(stderr, "Usage: noctiluca <log-file>\n");
}

static char *copy_string(const char *s) {
    size_t n = strlen(s) + 1;
    char *result = malloc(n);
    if (result != NULL) memcpy(result, s, n);
    return result;
}

static int valid_timestamp(const char *s) {
    static const int digits[] = {0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18};
    if (strlen(s) != 20 || s[4] != '-' || s[7] != '-' || s[10] != 'T' ||
        s[13] != ':' || s[16] != ':' || s[19] != 'Z') return 0;
    for (size_t i = 0; i < sizeof(digits) / sizeof(digits[0]); ++i) {
        if (s[digits[i]] < '0' || s[digits[i]] > '9') return 0;
    }
    return 1;
}

static int level_index(const char *level) {
    for (int i = 0; i < LEVEL_COUNT; ++i) if (strcmp(level, LEVELS[i]) == 0) return i;
    return -1;
}

static char *next_token(char **cursor) {
    while (**cursor != '\0' && isspace((unsigned char)**cursor)) ++(*cursor);
    if (**cursor == '\0') return NULL;
    char *start = *cursor;
    while (**cursor != '\0' && !isspace((unsigned char)**cursor)) ++(*cursor);
    if (**cursor != '\0') { **cursor = '\0'; ++(*cursor); }
    return start;
}

static int increment_count(CountList *list, const char *name) {
    for (size_t i = 0; i < list->len; ++i) {
        if (strcmp(list->items[i].name, name) == 0) { list->items[i].count++; return 1; }
    }
    if (list->len == list->cap) {
        size_t next = list->cap == 0 ? 8 : list->cap * 2;
        Count *resized = realloc(list->items, next * sizeof(*resized));
        if (resized == NULL) return 0;
        list->items = resized; list->cap = next;
    }
    char *name_copy = copy_string(name);
    if (name_copy == NULL) return 0;
    list->items[list->len++] = (Count){name_copy, 1};
    return 1;
}

static int increment_failure(FailureList *list, const char *service, const char *message) {
    for (size_t i = 0; i < list->len; ++i) {
        if (strcmp(list->items[i].service, service) == 0 && strcmp(list->items[i].message, message) == 0) {
            list->items[i].count++; return 1;
        }
    }
    if (list->len == list->cap) {
        size_t next = list->cap == 0 ? 8 : list->cap * 2;
        Failure *resized = realloc(list->items, next * sizeof(*resized));
        if (resized == NULL) return 0;
        list->items = resized; list->cap = next;
    }
    char *service_copy = copy_string(service);
    char *message_copy = copy_string(message);
    if (service_copy == NULL || message_copy == NULL) { free(service_copy); free(message_copy); return 0; }
    list->items[list->len++] = (Failure){service_copy, message_copy, 1};
    return 1;
}

static int compare_counts(const void *left, const void *right) {
    const Count *a = left, *b = right;
    if (a->count != b->count) return b->count - a->count;
    return strcmp(a->name, b->name);
}

static int compare_failures(const void *left, const void *right) {
    const Failure *a = left, *b = right;
    if (a->count != b->count) return b->count - a->count;
    int by_service = strcmp(a->service, b->service);
    return by_service != 0 ? by_service : strcmp(a->message, b->message);
}

static void free_counts(CountList *list) {
    for (size_t i = 0; i < list->len; ++i) free(list->items[i].name);
    free(list->items);
}

static void free_failures(FailureList *list) {
    for (size_t i = 0; i < list->len; ++i) { free(list->items[i].service); free(list->items[i].message); }
    free(list->items);
}

static int analyze(const char *path) {
    FILE *file = fopen(path, "r");
    if (file == NULL) { perror("noctiluca"); return 1; }
    int level_counts[LEVEL_COUNT] = {0};
    CountList services = {0};
    FailureList failures = {0};
    char *buffer = NULL;
    size_t buffer_size = 0;
    ssize_t read_size;
    int events = 0, malformed = 0, allocation_error = 0;

    while ((read_size = getline(&buffer, &buffer_size, file)) != -1) {
        while (read_size > 0 && (buffer[read_size - 1] == '\n' || buffer[read_size - 1] == '\r')) buffer[--read_size] = '\0';
        char *line_start = buffer;
        while (*line_start != '\0' && isspace((unsigned char)*line_start)) ++line_start;
        if (*line_start == '\0' || *line_start == '#') continue;

        char *cursor = line_start;
        char *timestamp = next_token(&cursor);
        char *level = next_token(&cursor);
        char *service = next_token(&cursor);
        while (*cursor != '\0' && isspace((unsigned char)*cursor)) ++cursor;
        char *message = cursor;
        int idx = level == NULL ? -1 : level_index(level);
        if (timestamp == NULL || level == NULL || service == NULL || *message == '\0' ||
            !valid_timestamp(timestamp) || idx < 0) {
            malformed++;
            continue;
        }
        char *readp = message, *writep = message;
        int previous_space = 0;
        while (*readp != '\0') {
            int is_space = isspace((unsigned char)*readp);
            if (!is_space || !previous_space) *writep++ = is_space ? ' ' : *readp;
            previous_space = is_space;
            ++readp;
        }
        if (writep > message && writep[-1] == ' ') --writep;
        *writep = '\0';
        if (*message == '\0') { malformed++; continue; }

        events++;
        level_counts[idx]++;
        if (!increment_count(&services, service)) { allocation_error = 1; break; }
        if ((idx == 3 || idx == 4) && !increment_failure(&failures, service, message)) { allocation_error = 1; break; }
    }
    free(buffer);
    fclose(file);
    if (allocation_error) {
        fprintf(stderr, "noctiluca: out of memory\n");
        free_counts(&services); free_failures(&failures); return 1;
    }

    qsort(services.items, services.len, sizeof(*services.items), compare_counts);
    qsort(failures.items, failures.len, sizeof(*failures.items), compare_failures);
    printf("NOCTILUCA / REPORT\nEvents: %d\nMalformed: %d\n\nLEVEL COUNTS\n", events, malformed);
    for (int i = 0; i < LEVEL_COUNT; ++i) printf("%s=%d\n", LEVELS[i], level_counts[i]);
    printf("\nSERVICE COUNTS\n");
    for (size_t i = 0; i < services.len; ++i) printf("%s=%d\n", services.items[i].name, services.items[i].count);
    printf("\nREPEATED FAILURES (>=3)\n");
    for (size_t i = 0; i < failures.len; ++i) {
        if (failures.items[i].count >= 3) printf("%s | %s | %d\n", failures.items[i].service, failures.items[i].message, failures.items[i].count);
    }
    free_counts(&services); free_failures(&failures);
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--listen") == 0) {
        fputs("                 .      *\n                      .\n             .-\"\"\"\"-.\n          .-'  .--.  '-.\n         /   .      .   \\\n        |     .--.      |\n         \\    '----'    /\n          '-.        .-'\n             '------'\n\n       SIGNAL SOURCE: UNKNOWN\n       SOME THINGS ARE BETTER LEFT UNPARSED.\n", stdout);
        return 0;
    }
    if (argc != 2 || strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0) {
        fail_usage();
        return argc == 2 ? 0 : 2;
    }
    return analyze(argv[1]);
}
