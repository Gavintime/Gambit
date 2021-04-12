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


# prints ep square, castling rights, half/fullmove, side to move
# TODO: print check status, end condition status
def print_info(position, side=True, rights=False, ep=False, move_count=False):

    # side to move
    if side:
        if position._side_to_move: print("White to Move")
        else: print("Black to Move")

    # castling rights
    if rights:
        print("Castling Rights: ", end='')
        if position._white_short_castle: print('K', end='')
        if position._white_long_castle: print('Q', end='')
        if position._black_short_castle: print('k', end='')
        if position._black_long_castle: print('q', end='')
        print()

    # en passant square
    if ep:
        if position._ep_square is None: print("EP Square: -")
        else:
            print(chr(position._ep_square[0] + 1 + 96),
                  position._ep_square[1] + 1, sep='')

    # half/fullmove count
    if move_count:
        print("Halfmove Count:", position._halfmove_count)
        print("Fullmove Count:", position._fullmove_count)


# returns a chess position of the game state
# fen_string is the uncleaned input from console or text box
# TODO: essential checks for position legality so it plays well with program
def import_fen(fen_string):

    # remove leading/training whitespace
    fen_clean = fen_string.strip()
    # exit if incorrect number of slashes or spaces
    if fen_clean.count('/') != 7 or fen_clean.count(' ') != 5: return False
    # split fen into list of 5+ fields (must be at least 5 because of above)
    # [board, side to move, castling, ep square, halfmove, fullmove, meta data]
    fen_list = fen_clean.split()


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
    # used for 50 and 75 move rule
    halfmove_count = 0
    # fullmove count, starts at 1 and increments every time black moves
    fullmove_count = 1


    # iterate through fen board info
    # ranks are reversed, the final board needs to be reverse()-ed
    fen_ranks = fen_list[0].split('/')  # list of ranks as strings
    # 0 based xy coordinate of the current board square
    board_x, fen_x, y = 0, 0, 0
    while(True):

        # if current index is at a piece, add it to the board
        if fen_ranks[y][fen_x].upper() in ('P', 'R', 'B', 'N', 'K', 'Q'):
            board[y][board_x] = fen_ranks[y][fen_x]
            board_x += 1
            fen_x += 1

        # skip past squares if index is at a number
        elif (ord(fen_ranks[y][fen_x]) - 48) in range(1, 9):
            # verify number doesn't make x go oob
            if (board_x + ord(fen_ranks[y][fen_x]) - 48) > 8: return False
            else:
                board_x += ord(fen_ranks[y][fen_x]) - 48
                fen_x += 1

        # not a legal board rank
        else: return False


        # end of a rank
        if board_x == 8:

            # next rank
            if y < 7:
                board_x = fen_x = 0
                y += 1
                continue    # this is redundant, for better readability

            # end of board info
            # y must be 7
            else: break

        # invalid square count
        elif board_x > 8: return False

        # x < 8, keep filling current rank
        else: continue

    # board was entered rank revered, reverse it
    board.reverse()



    # board part done, grab rest of the info
    # side to move
    if fen_list[1] == 'w': side_to_move = True
    elif fen_list[1] == 'b': side_to_move = False
    else: return False


    # castling rights
    # - if none at all
    if fen_list[2] == '-':
        ws = wl = bs = bl = False
    else:
        castle_index = 0

        if fen_list[2][castle_index] == 'K':
            ws = True
            castle_index += 1

        if fen_list[2][castle_index] == 'Q':
            wl = True
            castle_index += 1

        if fen_list[2][castle_index] == 'k':
            bs = True
            castle_index += 1

        if fen_list[2][castle_index] == 'q':
            bl = True
            castle_index += 1

        # exit of not end of castling rights field
        if len(fen_list[2]) != castle_index: return False

        # invalid if no castling rights but also no - sign
        if (not ws
            and not wl
            and not bs
            and not bl): return False


    # en passant square
    if fen_list[3] == '-':
        ep_square = None
    elif (len(fen_list[3]) == 2
            and (ord(fen_list[3][0]) - 97) in range(0, 8)
            and (ord(fen_list[3][1]) - 49) in range(0, 8)):

        ep_square = (ord(fen_list[3][0]) - 97, ord(fen_list[3][1]) - 49)

    # invalid ep square value
    else: return False


    # half move count
    if fen_list[4].isdigit() and int(fen_list[4]) >= 0:
        halfmove_count = int(fen_list[4])
    # invalid half move
    else: return False


    # full move count
    if fen_list[5].isdigit() and int(fen_list[5]) >= 1:
        fullmove_count = int(fen_list[5])
    # invalid full move
    else: return False


    # anything (like meta data) after this is ignored for now

    # create game position and return
    return ChessPosition(board, side_to_move, wl, ws, bl, bs, ep_square,
                         halfmove_count, fullmove_count)


# main function, entry point
def main():

    # create position from fen
    position = import_fen(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e6 0 1")
    if not position:
        print("Invalid FEN, exiting...")
        exit(1)

    # move input loop
    invalid_move = False
    info_request = False
    while(True):
        # clear screen
        print("\033[2J")
        print_moves(position.get_legal_moves())
        print_board(position._board)
        print_info(position, side=True)

        # special inputs
        if invalid_move:
            print("Invalid Move")
            invalid_move = False

        elif info_request:
            # side to move is printed above, no need to print again
            print_info(position, False, True, True, True)
            info_request = False

        print("Please Enter a move: ", end='')

        # receive input from user
        move_input = input()
        if move_input == "exit": exit()
        elif move_input == "info": info_request = True
        elif not position.move(move_input): invalid_move = True


# tells python to run main on program start
if __name__ == "__main__": main()
