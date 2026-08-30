#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>

void _helper_() {
    asm("pop %rdi; ret");
}

int is_valid_number(const char *s) {
    if (*s == '\0') return 0;

    int i = 0;
    if (s[0] == '-') i = 1;
    if (s[i] == '\0') return 0;

    for (; s[i] != '\0'; i++) {
        if (!isdigit((unsigned char)s[i])) {
            return 0;
        }
    }
    return 1;
}

int read_number(int *out) {
    char buf[20];
    if (!fgets(buf, sizeof(buf), stdin)) return 0;

    buf[strcspn(buf, "\n")] = '\0';

    if (!is_valid_number(buf)) {
        puts("Blacklisted input detected! Numbers only.");
        return 0;
    }

    *out = atoi(buf);
    return 1;
}

void vuln() {
    int something[10];
    int num_elements;

    printf("How many numbers do you want to enter?: ");
    if (!read_number(&num_elements)) return;

    if (num_elements + 2 > 12) {
        puts("Too many numbers! Max is 10.");
        return;
    }

    printf("Enter your numbers as raw bytes now: ");
    read(0, something, num_elements * sizeof(int));
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    puts("Gk ada ide mo bikin challs apa, keknya ini aja deh menarik.");
    puts("Semoga mudah");
    vuln();
    puts("oke byee!!\n");
    return 0;
}