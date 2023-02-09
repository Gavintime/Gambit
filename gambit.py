"""
Text Interface for Gambit Chess Program.

    Functions:
        print_board: print the given board to stdout.
        print_moves: convert and print move list to stdout.
        print_info: print position info to stdout.
        import_fen: create position from fen string.
        main: Text Interface Entry Point.
"""
import sys
from chess_position import ChessPosition


def print_board(board):
    """Print given board with border to stdout."""
    print('╔════════╗')

    for y in range(7, -1, -1):
        for x in range(0, 8):
            if x == 0: print('║', end='')
            # if (x + y)% 2 == 0: print("\033[1;44m", end ='')
            print(board[y][x], end='')
            # if (x + y)% 2 == 0: print("\033[0m", end ='')
            if x == 7: print('║')

    print('╚════════╝')


def print_moves(move_list):
    """Convert and print given move list to stdout."""
    for move in move_list:
        print(chr(move[0] + 1 + 96), move[1] + 1,
              chr(move[2] + 1 + 96), move[3] + 1, sep='', end='')

        # print promotion part
        if len(move) == 5 and move[4] in ('q', 'r', 'b', 'n'): print(move[4])
        else: print()


# TODO: print check status, end condition status
def print_info(position, side=True, rights=False, ep=False, move_count=False):
    """Print position info to stdout."""
    # side to move
    if side:
        if position.side_to_move: print("White to Move")
        else: print("Black to Move")

    # castling rights
    if rights:
        print("Castling Rights: ", end='')
        if position.white_short_castle: print('K', end='')
        if position.white_long_castle: print('Q', end='')
        if position.black_short_castle: print('k', end='')
        if position.black_long_castle: print('q', end='')
        print()

    # en passant square
    if ep:
        if position._ep_square is None: print("EP Square: -")
        else:
            print(chr(position._ep_square[0] + 1 + 96),
                  position._ep_square[1] + 1, sep='')

    # half/fullmove count
    if move_count:
        print("Halfmove Count:", position.halfmove_count)
        print("Fullmove Count:", position.fullmove_count)


def move_parser(position, move):
    """Convert short notation move into long notation."""
    pass


def main():
    """Entry point for Gambit Text Interface."""
    # create position from fen
    position = ChessPosition.import_fen(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    if not position:
        print("Invalid FEN, exiting...")
        sys.exit(1)

    # move input loop
    invalid_move = False
    info_request = False
    while True:
        # clear screen
        print("\033[2J")
        print_moves(position.move_list)
        print_board(position.board)
        print_info(position, side=True)

        # special commands
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
        if move_input == "exit": sys.exit(0)
        elif move_input == "info": info_request = True
        elif not position.move(move_input): invalid_move = True


# Run main on program start
if __name__ == '__main__': main()
