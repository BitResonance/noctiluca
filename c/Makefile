CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Wpedantic

.PHONY: all clean
all: noctiluca

noctiluca: src/main.c
	$(CC) $(CFLAGS) -D_POSIX_C_SOURCE=200809L -o $@ $<

clean:
	rm -f noctiluca
