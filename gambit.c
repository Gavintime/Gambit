/*
 * gambit.c
 * This is a terminal based chess game.
 * The TUI is powered by ncurses.
 * Written by Gavintime at Github.com
 */

#include <ctype.h>
#include <ncurses.h>

//color pairs
#define WHITE_LIGHT 1
#define WHITE_DARK 2
#define BLACK_LIGHT 3
#define BLACK_DARK 4
//table size
#define TABLEROW 8
#define TABLECOL 8+1


int screenRow, screenCol;   //vars to store size of screen to use for formatting


void printTable(char[TABLEROW][TABLECOL]);


int main(int argc, char *argv[]) {

    initscr();                              //initialize ncurses screen
    getmaxyx(stdscr, screenRow, screenCol); //set screen size vars, metmaxyx is a macro not a function so pointers are not used
    cbreak();                               //disable buffer for input, use raw() instead if wanting to change control char behaviors like ctrl z or ctrl c
    noecho();                               //disable normal input echo, can be done manually as needed
    keypad(stdscr, true);                   //enable usable of F keys and arrow keys to the default screen
    start_color();                          //enable color usage
    //set color pairs
    init_pair(WHITE_LIGHT, COLOR_MAGENTA,COLOR_WHITE);
    init_pair(WHITE_DARK, COLOR_MAGENTA,COLOR_GREEN);
    init_pair(BLACK_LIGHT, COLOR_BLACK,COLOR_WHITE);
    init_pair(BLACK_DARK, COLOR_BLACK,COLOR_GREEN);

    //lowercase is black, uppercase is white
    char table[TABLEROW][TABLECOL] = {{'r','n','b','q','k','b','n','r','\0'},
                        {'p','p','p','p','p','p','p','p','\0'},
                        {' ',' ',' ',' ',' ',' ',' ',' ','\0'},
                        {' ',' ',' ',' ',' ',' ',' ',' ','\0'},
                        {' ',' ',' ',' ',' ',' ',' ',' ','\0'},
                        {' ',' ',' ',' ',' ',' ',' ',' ','\0'},
                        {'P','P','P','P','P','P','P','P','\0'},
                        {'R','N','B','Q','K','B','N','R','\0'}};


    printTable(table);
    printw("Press any key to exit program.\n");
    refresh();
    getch();    //wait for user to enter a char
    endwin();   //end curses mode


    return 0;
}


//print out 2d table array to center of screen
void printTable(char table1[TABLEROW][TABLECOL]) {
    for (int i = 0; i < TABLEROW; i++){
        standend();
        for (int j = 0; j < TABLECOL+1; j++){

            //print vertical numbers
            if(j==0) mvprintw((screenRow-TABLEROW)/2+i, (screenCol-TABLECOL)/2+j, "%d", TABLEROW-i);

            //print light squares
            else if((i+j)%2!=0) {

                //print light squares with white pieces
                if(isupper(table1[i][j-1])) attron(COLOR_PAIR(WHITE_LIGHT));
                //print light squares with black pieces
                else attron(COLOR_PAIR(BLACK_LIGHT));

            //print dark squares
            } else {
                //print light squares with white pieces
                if(isupper(table1[i][j-1])) attron(COLOR_PAIR(WHITE_DARK));
                //print light squares with black pieces
                else attron(COLOR_PAIR(BLACK_DARK));
            }

            //print pieces
            mvprintw((screenRow-TABLEROW)/2+i, (screenCol-TABLECOL)/2+j, "%c", toupper(table1[i][j-1]));
        }

        //mvprintw((screenRow-TABLEROW)/2+i, (screenCol-TABLECOL)/2, "%d%s\n", TABLEROW-i, table1[i]);

    }
    standend();
    //print horizontal numbers
    mvprintw((screenRow-TABLEROW)/2+TABLEROW, (screenCol-TABLECOL)/2, " abcdefgh\n");
    refresh(); //update screen with new text
}
