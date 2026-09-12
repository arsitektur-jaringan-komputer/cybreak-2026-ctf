#define _GNU_SOURCE
#include <seccomp.h>
#include <stdio.h>
#include <sys/mman.h>

void init(void) {
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  setvbuf(stdin, NULL, _IONBF, 0);
}

void init_seccomp() {
  scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL_PROCESS);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(getdents), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(getdents64), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(connect), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(socket), 0);
  seccomp_load(ctx);
}

int main() {
  init();
  char buf[100] = {0};
  scanf("%99s", buf);
  puts("bye bye~ (❁´◡`❁)");
  init_seccomp();
  fclose(stdin);
  fclose(stdout);
  fclose(stderr);
  void *ptr = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  ((void (*)(void))ptr)();
}
