from ChessPosition import ChessPosition


# prints the given board to the console
def print_board(board):

    print("╔════════╗")

    for y in range(7, -1, -1):
        for x in range(0, 8):
            if x == 0: print('║', end='')
            # if (x + y)% 2 == 0: print("\033[1;44m", end ='')
            print(board[y][x], end='')
            # if (x + y)% 2 == 0: print("\033[0m", end ='')
            if x == 7: print('║')

    print("╚════════╝")


def print_moves(move_list):
    for move in move_list:
        print(chr(move[0] + 1 + 96), move[1] + 1,
              chr(move[2] + 1 + 96), move[3] + 1, sep="", end='')

        # print promotion part
        if len(move) == 5 and move[4] in ('q', 'r', 'b', 'n'): print(move[4])
        else: print()


# returns a chess position of the game state
# fen_string is the uncleaned input from console or text box
# TODO: essential checks for position legality so it plays well with program
def import_fen(fen_string):

    # remove leading/training whitespace
    fen_clean = fen_string.strip()
    # exit if incorrect number of slashes or spaces
    if fen_clean.count('/') != 7 or fen_clean.count(' ') != 5: return False


    # index of the current char to be processed
    index = 0
    # 0 based xy coordinate of the current board square
    x, y = 0, 7

    # board from the fen, defaults to all blanks
    board = [list("        "),
             list("        "),
             list("        "),
             list("        "),
             list("        "),
             list("        "),
             list("        "),
             list("        ")]
    # True for white, False for Black
    side_to_move = True
    # Castling Rights
    ws = wl = bs = bl = False
    # en passant square, 0 based x,y coordinate of ep dest square as tuple
    ep_square = None
    # halfmove count since last capture/pawn advance
    # used for 50 move rule
    halfmove_count = 0
    # fullmove count, starts at 1 and increments every time black moves
    fullmove_count = 1


    # iterate through the fen to get board info
    while(True):

        # if current index is at a piece, add it to the board
        if fen_clean[index].upper() in ('P', 'R', 'B', 'N', 'K', 'Q'):
            board[y][x] = fen_clean[index]
            x += 1
            index += 1

        # skip past squares if index is at a number
        elif (ord(fen_clean[index]) - 49) in range(0, 8):
            x += ord(fen_clean[index]) - 49 + 1
            index += 1

        # not a legal fen
        else: return False

        # end of a rank
        if x == 8:

            # next rank
            if y > 0:

                # need a / at the end of every non last rank
                if fen_clean[index] != '/': return False

                index += 1
                x = 0
                y -= 1
                continue    # this is redundant, for better readability

            # end of board info
            # y must be 0
            else: break

        # invalid rank count
        elif x > 8: return False



    # board part done, grab rest of the info
    if fen_clean[index] != ' ': return False
    index += 1

    # side to move
    if fen_clean[index] == 'w': side_to_move = True
    elif fen_clean[index] == 'b': side_to_move = False
    else: return False
    index += 1

    if fen_clean[index] != ' ': return False
    index += 1


    # castling rights
    # - if none at all
    if fen_clean[index] == '-':
        ws = wl = bs = bl = False
        index += 1

    else:
        if fen_clean[index] == 'K':
            ws = True
            index += 1

        if fen_clean[index] == 'Q':
            wl = True
            index += 1

        if fen_clean[index] == 'k':
            bs = True
            index += 1

        if fen_clean[index] == 'q':
            bl = True
            index += 1

        # invalid if no castling rights but also no - sign
        if (not ws
            and not wl
            and not bs
            and not bl): return False


    if fen_clean[index] != ' ': return False
    index += 1


    # en passant square
    if fen_clean[index] == '-':
        ep_square = None
        index += 1

    elif ((ord(fen_clean[index]) - 97) in range(0, 8)
            and (ord(fen_clean[index + 1]) - 49) in range(0, 8)):

        ep_square = (ord(fen_clean[index]) - 97,
                     ord(fen_clean[index + 1]) - 49)
        index += 2

    # invalid ep square value
    else: return False


    if fen_clean[index] != ' ': return False
    index += 1


    # TODO: multi digit move counts!

    # half move count
    if (ord(fen_clean[index]) - 48) in range(0, 1000):
        halfmove_count = ord(fen_clean[index]) - 49
        index += 1
    else: return False

    if fen_clean[index] != ' ': return False
    index += 1

    # full move count
    if (ord(fen_clean[index]) - 48) in range(0, 1000):
        fullmove_count = ord(fen_clean[index]) - 49


    # anything (like meta data) after this is ignored for now


    # create game position and return
    return ChessPosition(board, side_to_move, wl, ws, bl, bs, ep_square,
                         halfmove_count, fullmove_count)


# main function, entry point
def main():
    # create position from fen

    position = import_fen(
        "8/8/8/8/4kp2/1R6/P2q1PPK/8 w - - 0 1")

    if not position:
        print("INVALID FEN!")
        exit(1)

    # move input loop
    invalid_move = False
    while(True):
        # clear screen
        print("\033[2J")
        print_moves(position.get_legal_moves())
        print_board(position._board)

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
