#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef struct {
    char* prefix;
    char* name;
} greet_t;

char* hello = "Hello, ";
char* goodbye = "Good bye.. ";
char* lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean venenatis metus, ";

void win() {
    system("/bin/sh");
}

void init() {
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}

void read_greet(greet_t* greet) {
    int type;
    printf("Greet type: ");
    if(scanf("%d", &type) != 1) {
        puts("Invalid input");
        exit(-1);
    }
    if(type == 0) {
        greet->prefix = hello;
    } else if(type == 1) {
        greet->prefix = goodbye;
    }

    char* name = (char*) malloc(0x30);
    printf("Name: ");
    read(0, name, 0x30);
    greet->name = name;
}

int main() {
    init();

    greet_t greet;
    char greet_string_buf[0x30];
    char* tmp = greet_string_buf;
    int x;

    x = 1;
    read_greet(&greet);
    tmp = greet_string_buf;
    strcpy(tmp, greet.prefix);
    tmp += strlen(greet.prefix);
    strcpy(tmp, greet.name);
    tmp += strlen(greet.name);
    *tmp = '\0';

    puts(greet_string_buf);

    if(x != 1) {
        win();
    }
}
