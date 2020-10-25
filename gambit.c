/*
 * gambit.c
 * This is a terminal based chess game.
 * The TUI is powered by ncurses.
 * Written by Gavintime at Github.com
 */

#include <ctype.h>
#include <form.h>
#include <ncurses.h>

//color pairs
#define WHITE_LIGHT 1
#define WHITE_DARK 2
#define BLACK_LIGHT 3
#define BLACK_DARK 4
//table size
#define BOARDROW 8
#define BOARDCOL 8


//global stuff
int screenRow, screenCol;   //vars to store size of screen to use for formatting
WINDOW *boardWindow, *moveWindow;


//function prototype delcarations
void printTable(char[BOARDROW][BOARDCOL]);
bool isValidMove(char[]);


int main(int argc, char *argv[]) {

    //ncurses setup
    initscr();                              //initialize ncurses screen called stdscr
    //TODO: allow for screen size adjustments
    getmaxyx(stdscr, screenRow, screenCol); //set screen size vars, metmaxyx is a macro not a function so pointers are not used
    cbreak();                               //disable buffer for input, use raw() instead if wanting to change control char behaviors like ctrl z or ctrl c
    noecho();                               //disable normal input echo, can be done manually as needed
    //keypad(stdscr, true);                   //enable usable of F keys and arrow keys to the default screen
    start_color();                          //enable color usage
    //set color pairs
    init_pair(WHITE_LIGHT, COLOR_MAGENTA,COLOR_WHITE);
    init_pair(WHITE_DARK, COLOR_MAGENTA,COLOR_GREEN);
    init_pair(BLACK_LIGHT, COLOR_BLACK,COLOR_WHITE);
    init_pair(BLACK_DARK, COLOR_BLACK,COLOR_GREEN);


    //create window to hold the chess board and refresh so that window is now on the screen
    boardWindow = newwin(BOARDROW+1, BOARDCOL+1, (screenRow/2-BOARDROW)/2, (screenCol-BOARDCOL)/2);
    refresh();


    //initialize chess board. lowercase is black, uppercase is white
    char table[BOARDROW][BOARDCOL] = {"rnbqkbnr",
                                      "pppppppp",
                                      "        ",
                                      "        ",
                                      "        ",
                                      "        ",
                                      "PPPPPPPP",
                                      "RNBQKBNR"};
    printTable(table);


    //get move from user
    printw("Please enter a move.\n");
    refresh();


    //initialize move input window, give it a box
    moveWindow = newwin(3, 10, (screenRow/2-BOARDROW)/2+BOARDROW+1, (screenCol-BOARDCOL)/2);
    keypad(moveWindow, true);
    box(moveWindow,0,0);


    //create a null terminated array of fields with 1 field to read in a move
    FIELD *fields[2];
    fields[0] = new_field(1,8,0,0,0,0);
    //disable auto skip to next field at end of field
    field_opts_off(fields[0], O_AUTOSKIP);
    fields[1] = NULL;
    //add the null terminated array of field(s) to a form
    FORM *moveForm = new_form(fields);


    //set the moveform to the move window, enable the form, then refresh the main and move windows
    set_form_win(moveForm, moveWindow);
    set_form_sub(moveForm, derwin(moveWindow, 1, 8, 1, 1));
    //make the form active and refresh the relevent windows
    post_form(moveForm);
    refresh();
    wrefresh(moveWindow);


    //get input here, enter key exits
    int ch, moveFormIndex=0;
    char moveInput[8] = "\0\0\0\0\0\0\0\0";
    while ((ch = wgetch(moveWindow)) != '\n') {

        switch (ch) {

            //backspace key
            case KEY_BACKSPACE :
                if(moveFormIndex > 0) {
                    form_driver(moveForm, REQ_DEL_PREV);
                    moveInput[moveFormIndex-1] = '\0';
                    moveFormIndex--;
                }
                break;

            //alphanumeric keys, ignore anything else
            default:
                if (isalnum(ch) && moveFormIndex < 7) {
                    form_driver(moveForm, ch);
                    moveInput[moveFormIndex] = ch;
                    moveFormIndex++;
                }
                break;
        }
    }


    //clear screen and print move entered by user
    clear();
    printw("%s", moveInput);
    getch();


    //unpost form from screen and free memory from the form and field
    unpost_form(moveForm);
    free_form(moveForm);
    free_field(fields[0]);


    //exit program
    endwin();   //end curses mode
    return 0;
}


//print out 2d table array to center of screen
void printTable(char table1[BOARDROW][BOARDCOL]) {
    for (int i = 0; i < BOARDROW; i++) {
        wstandend(boardWindow);
        for (int j = 0; j < BOARDCOL+1; j++) {

            //print vertical numbers
            if(j==0) {
                mvwprintw(boardWindow, i, 0, "%d", BOARDROW-i);

            }else {

                //print light squares
                if((i+j)%2!=0) {

                    //print light squares with white pieces
                    if(isupper(table1[i][j-1])) wattron(boardWindow, COLOR_PAIR(WHITE_LIGHT));
                    //print light squares with black pieces
                    else wattron(boardWindow, COLOR_PAIR(BLACK_LIGHT));

                //print dark squares
                } else {
                    //print light squares with white pieces
                    if(isupper(table1[i][j-1])) wattron(boardWindow, COLOR_PAIR(WHITE_DARK));
                    //print light squares with black pieces
                    else wattron(boardWindow, COLOR_PAIR(BLACK_DARK));
                }

                //print pieces
                mvwprintw(boardWindow, i, j, "%c", toupper(table1[i][j-1]));
            }
        }
    }

    //set attributes to normal
    wstandend(boardWindow);
    //print horizontal letters
    mvwprintw(boardWindow, BOARDROW, 0, " abcdefgh");
    wrefresh(boardWindow); //update screen with new text
}


//returns true if the string "move" is a valid move
bool isValidMove(char move[8]) {

    return true;
}
