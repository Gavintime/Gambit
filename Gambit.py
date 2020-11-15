from ChessPosition import ChessPosition


def print_board(board):
    for rank in reversed(board):
        print(*rank, sep = "")


# return false if move is not a valid move (does not check for legality)
# return tokenized list of move if valid
def move_tokenizer(move):

    # verify string has minimum size
    if len(move) < 2: return False
    # remove white space, then fill string to length 11 (1 more then max move length) with space for easier parsing
    move = ''.join(move.split()).ljust(11)



    # create tokenized move list and iterator through move
    tokens = []
    move_spot = 0


    # castling
    if move.strip() == "0-0":
        tokens.append("KINGS_CASTLE")
        return tokens
    elif move.strip() == "0-0-0":
        tokens.append("QUEENS_CASTLE")
        return tokens


    # get piece being moved
    if move[0] == 'K':
        tokens.append("KING")
        move_spot += 1
    elif move[0] == 'Q':
        tokens.append("QUEEN")
        move_spot += 1
    elif move[0] == 'B':
        tokens.append("BISHOP")
        move_spot += 1
    elif move[0] == 'N':
        tokens.append("KNIGHT")
        move_spot += 1
    elif move[0] == 'R':
        tokens.append("ROOK")
        move_spot += 1
    else: tokens.append("PAWN")


    # pawn moves
    if tokens[0] == "PAWN":

        # named pawn captures
        if move[move_spot] in "abcdefgh" and move[move_spot + 1] == 'x':
            tokens.append(move[move_spot].upper() + "_FILE")
            tokens.append("CAPTURE")
            move_spot += 2

        # pawn square of arrival
        if move[move_spot] in "abcdefgh" and move[move_spot + 1] in "12345678":
            tokens.append(move[move_spot].upper() + move[move_spot + 1] + "_SQUARE")
            move_spot += 2
        else: return False

        # pawn promotion
        if move[move_spot] in "QNBR":
            tokens.append(move[move_spot].upper() + "_PROMOTE")
            move_spot += 1
        elif move[move_spot] == "=" and move[move_spot + 1] in "QNBR":
            tokens.append(move[move_spot + 1].upper() + "_PROMOTE")
            move_spot += 2

        # en passant
        elif move[move_spot:move_spot + 4] == "e.p.":
            tokens.append("EN_PASSANT")


    # piece moves
    else:

        # named piece moves
        # must check for bishop because of pawn promotion to bishop...
        if tokens[0] in ["QUEEN", "KNIGHT", "ROOK", "BISHOP"]:
            if move[move_spot] in "abcdefgh" and move[move_spot + 1] in "xabcdefgh":
                tokens.append(move[move_spot].upper() + "_FILE")
                move_spot += 1
            elif move[move_spot] in "12345678":
                tokens.append(move[move_spot] + "_RANK")
                move_spot += 1

        # piece captures
        if move[move_spot] == 'x':
            tokens.append("CAPTURE")
            move_spot += 1

        # piece square of arrival
        if move[move_spot] in "abcdefgh" and move[move_spot + 1] in "12345678":
            tokens.append(move[move_spot].upper() + move[move_spot + 1] + "_SQUARE")
            move_spot += 2
        else:
            return False


    # check and mate
    if move[move_spot] == '+':
        tokens.append("CHECK")
        move_spot += 1
    elif move[move_spot:move_spot + 1] == "++":
        tokens.append("MATE")
        move_spot += 2
    elif move[move_spot] == '#':
        tokens.append("MATE")
        move_spot += 1

    # verify end of move
    if move[move_spot] == ' ':
        return tokens
    else:  return False


# create starting position chess board
start_board = [list("RNBQKBNR"),
               list("PPPPPPPP"),
               list("        "),
               list("        "),
               list("        "),
               list("        "),
               list("pppppppp"),
               list("rnbqkbnr")]



# create new starting chess position
start_position = ChessPosition(start_board, True, True, True, True, True)

# get move from user and print board
current_move = input("Enter your move: ")
print(move_tokenizer(current_move))
print(start_position.get_knight_moves())
print_board(start_position._board)
