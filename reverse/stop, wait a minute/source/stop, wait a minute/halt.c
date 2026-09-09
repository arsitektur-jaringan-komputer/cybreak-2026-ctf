#define _GNU_SOURCE

#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

#include <string.h>
#include <sys/mman.h>
#include <ucontext.h>
#include <unistd.h>

#include "shellcode.h"

static char g_key[33];

static void hlt_handler(int sig, siginfo_t *si, void *uc_) {
    ucontext_t *uc = (ucontext_t *)uc_;
    unsigned char *rip = (unsigned char *)uc->uc_mcontext.gregs[REG_RIP];
    uc->uc_mcontext.gregs[REG_RIP] = (greg_t)(rip + 2 + rip[1]);
}

int main(int argc, char **argv) {
    struct sigaction sa;
    int (*sc)(const char *) = NULL;
    int status;

    if (argc != 2) {
        printf("%s <key>\n", argv[0]);
        return 1;
    }
    if (strlen(argv[1]) != 32) {
        puts("Invalid key length.");
        return 1;
    }

    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = hlt_handler;
    sa.sa_flags = SA_SIGINFO | SA_NODEFER;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGILL, &sa, NULL);

    sc = (int (*)(const char *))mmap(NULL, SHELLCODE_BLOB_SIZE + 16,
                                     PROT_READ | PROT_WRITE | PROT_EXEC,
                                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (sc == MAP_FAILED) {
        perror("mmap");
        return 1;
    }
    memcpy(sc, shellcode_blob, SHELLCODE_BLOB_SIZE);

    strcpy(g_key, argv[1]);
    status = sc(g_key);

    if (status == 0)
        printf("CYB26{%s}\n", g_key);
    else
        puts("Wrong key");
    return 0;
}
