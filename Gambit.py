from ChessPosition import ChessPosition

# reversed vertically
start_board = [list("RNBQKBNR"),
               list("PPpPPPPP"),
               list("        "),
               list("        "),
               list("        "),
               list("        "),
               list("ppPppppp"),
               list("rnbqkbnr")]


# prints the given board to the console
def print_board(board):
    print("╔════════╗")
    for y in range(7,-1,-1):
        for x in range(0,8):
            if x == 0: print('║', end = '')
            #if (x + y)% 2 == 0: print("\033[1;44m", end ='')
            print(board[y][x], end='')
            #if (x + y)% 2 == 0: print("\033[0m", end ='')
            if x == 7: print('║')
    print("╚════════╝")


def print_moves(move_list):
    for move in move_list:
        print(chr(move[0]+1 + 96), move[1]+1, chr(move[2]+1 + 96), move[3]+1, sep="", end='')
        # print promotion part
        if len(move) == 5: print(move[4])
        else: print()


# main function, entry point
def main():
    # clear screen and print starting board
    print("\033[2J")
    print_board(start_board)
    # create starting position
    position = ChessPosition(start_board, False, True, True, True, True)
    print_moves(position.get_legal_moves())



    view_board_moves = position._board
    # display avail moves as .
    for move in position._move_list:
        view_board_moves[move[3]][move[2]] = '.'
    print_board(view_board_moves)


# tells python to run main on program start
if __name__ == "__main__":
    main()
