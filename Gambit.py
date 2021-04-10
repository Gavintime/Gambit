from ChessPosition import ChessPosition


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
        if len(move) == 5 and move[4] != 'd': print(move[4])
        else: print()


# main function, entry point
def main():
    # create position with default start
    position = ChessPosition()

    # move input loop
    invalid_move = False
    while(True):
        # clear screen
        print("\033[2J")
        print_moves(position.get_legal_moves())
        print_board(position._board)
        # print(position._ep_square)

        # ask use for input
        if invalid_move:
            print("Invalid Move, please Enter a move: ", end='')
            invalid_move = False
        else: print("Please Enter a move: ", end='')
        # receive input from user
        move_input = input()
        if move_input == "exit": exit()
        if not position.move(move_input): invalid_move = True


# tells python to run main on program start
if __name__ == "__main__": main()
