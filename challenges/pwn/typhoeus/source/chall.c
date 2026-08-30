#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

char saved_bow[0x64];

void vuln() {

    char bow[0x14];
    puts("Typhoeus, shoot it!!");
    gets(bow);
    // puts("Alright, save that training result");
    // memcpy(saved_bow, bow, sizeof(saved_bow));
}

void helper() {

    puts("i appreciate you're helping my typhoeus to practice, that's nice.");
    printf("here: ");
    printf(saved_bow);
}

void opt() {
    int milih;

    puts("\nHi!");
    puts("My typhoeus will come at endfield soon, so i'm prepare to give her some exclusive bow for training");
    puts("Here are the program:");
    puts("1. result training");
    puts("2. help typhoeus practice");
    puts("3. exit");
    printf("Help me: ");
    scanf("%d", &milih);
    getchar();

        if(milih == 1) {
            helper();
        } else if(milih == 2) {
            vuln();
        } else if(milih == 3) {
            puts("Oke byee!");
            exit(0);
        } else {
            puts("That's not valid option!");
    }
}


int main() {

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    while(true) {
    opt();
    }
    return 0;
}
