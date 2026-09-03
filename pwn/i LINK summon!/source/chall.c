#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#define MAX_CARDS 4

struct card {
    char title[16];
    int atk;
    char *link_arrow;
    char description;
};

void setup(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
}

void win(void) {
    puts("Your point arrow effect each other, congrats! here");
    system("/bin/sh");
}

static void read_line(char *buf, size_t n) {
    if (fgets(buf, (int)n, stdin)) {
        buf[strcspn(buf, "\n")] = 0;
    }
}

void create(struct card *cards, int idx) {
    if (idx < 0 || idx >= MAX_CARDS) { puts("Invalid slot."); return; }
    printf("Title: ");
    read_line(cards[idx].title, sizeof(cards[idx].title));
    printf("ATK: ");
    if (scanf("%d", &cards[idx].atk) != 1) { puts("Bad input."); exit(1); }
    getchar();
    cards[idx].link_arrow = NULL;
    cards[idx].description = 0;
    puts("Card created.");
}

void point_effect_1(struct card *cards, int idx, long offset) {
    if (idx < 0 || idx >= MAX_CARDS) { puts("Invalid slot."); return; }
    cards[idx].link_arrow = (char *)cards + offset;
    puts("Arrow pointed!");
}

void point_effect_2(struct card *cards, int idx, long value) {
    if (idx < 0 || idx >= MAX_CARDS) { puts("Invalid slot."); return; }
    if (!cards[idx].link_arrow) { puts("No arrow set!"); return; }
    struct card *target = (struct card *)cards[idx].link_arrow;
    target->link_arrow = (char *)value;
    puts("Chain reaction triggered!");
}

void trigger(int *running) {
    puts("Triggering all effects...");
    *running = 0;
}

int menu(void) {
    int choice;
    puts("\n1. Create your link card monster");
    puts("2. point card effect - 1");
    puts("3. point card effect - 2");
    puts("4. try to trigger it");
    puts("5. exit");
    printf("> ");
    if (scanf("%d", &choice) != 1) return 5;
    getchar();
    if (choice > 5 || choice < 1) return 0;
    return choice;
}

int main(void) {
    setup();

    struct card cards[MAX_CARDS];
    memset(cards, 0, sizeof(cards));
    int idx;
    long off, val;
    int running = 1;

    puts("welcome to my database of yugioh card");
    puts("there are many things in here but you can customize yourself!");
    puts("You can try by yourself:");

    while (running) {
        int choice = menu();
        switch (choice) {
            case 1:
                printf("Slot (0-%d): ", MAX_CARDS - 1);
                if (scanf("%d", &idx) != 1) return 0;
                getchar();
                create(cards, idx);
                break;
            case 2:
                printf("Slot (0-%d): ", MAX_CARDS - 1);
                if (scanf("%d", &idx) != 1) return 0;
                getchar();
                printf("Offset: ");
                if (scanf("%ld", &off) != 1) return 0;
                getchar();
                point_effect_1(cards, idx, off);
                break;
            case 3:
                printf("Slot (0-%d): ", MAX_CARDS - 1);
                if (scanf("%d", &idx) != 1) return 0;
                getchar();
                printf("Value: ");
                if (scanf("%ld", &val) != 1) return 0;
                getchar();
                point_effect_2(cards, idx, val);
                break;
            case 4:
                trigger(&running);
                break;
            case 5:
                puts("Bye.");
                return 0;
            default:
                break;
        }
    }
    return 0;
}