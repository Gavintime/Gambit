"""
Create and modify Chess positions.

Classes:
    GameState: Enum class for game states.
    ChessPosition: Class for Chess Positions.

Misc variables:
    start_board: Default starting board of a game.
    WHITE: constant to refer to white as True.
    BLACK: constant to refer to black as False.
"""

import re
from copy import deepcopy
from enum import Enum
from collections import namedtuple


# reversed vertically
start_board = [list('RNBQKBNR'),
               list('PPPPPPPP'),
               list('        '),
               list('        '),
               list('        '),
               list('        '),
               list('pppppppp'),
               list('rnbqkbnr')]

WHITE = True
BLACK = False

Square = namedtuple('Square', ['x', 'y'])
Move = namedtuple('Move', ['x1', 'y1', 'x2', 'y2', 'special'])


class GameState(Enum):
    """Enum class for a chess position's game state."""

    ONGOING = 1
    CHECKMATE = 2
    STALEMATE = 3
    RESIGNATION = 4
    # insufficient material
    # king vs king
    # king vs king and bishop
    # king vs king and knight
    # kings with single same colored bishop
    DRAW_BY_MATERIAL = 5
    # repeated position, 3 is claim, 5 is mandatory
    DRAW_BY_3_REPETITION = 6
    DRAW_BY_5_REPETITION = 7
    # number of moves without pawn advance or capture,
    # 50 is claim, 75 is mandatory
    # this is counted using halfmove_count
    DRAW_BY_50_MOVE = 8
    DRAW_BY_75_MOVE = 9
    DRAW_BY_AGREEMENT = 10
    LOSE_ON_TIME = 11


class ChessPosition:
    """
    Chess position with methods to calculate and enact moves.

        Public Methods:
            move(move):
                Verifies and enacts a given move on the position

        Attributes:
            board (2d char list): the board of a position
            side_to_move (bool): True is White, False is Black
            white_long_castle (bool): castling rights
            white_short_castle (bool): castling rights
            black_long_castle (bool): castling rights
            black_short_castle (bool): castling rights
            halfmove_count (int): Num
            fullmove_count (int):
            in_check (bool):
            move_list (list):
            state (GameState Enum):
    """

    # TODO: logic for 3 move, 5 move, 50 move?, and 75 move? repetition
    # TODO: store last move
    def __init__(self, board=deepcopy(start_board),
                 side_to_move=WHITE,
                 white_long_castle=True,
                 white_short_castle=True,
                 black_long_castle=True,
                 black_short_castle=True,
                 ep_square=None,
                 halfmove_count=0,
                 fullmove_count=1):
        """
        Create a chess position object with given position data.

            Paramaters:
                board (2D Char Array): The board flipped vertically
                side_to_move (bool): White is true, Black is False
                white_long_castle (bool): castling legality
                white_short_castle (bool): castling legality
                black_long_castle (bool): castling legality
                black_short_castle (bool): castling legality
                ep_square (2 int tuple):
                    0 based xy coord of eq target square, None if no eq square
                halfmove_count (int): halfmoves since last capture/pawn move
                fullmove_count (int): number of moves a game has lasted
                state (GameState enum): status of the game

            Returns:
                ChessPosition Object built from given position data
        """
        # K = White king
        # Q = White queen
        # R = White rook
        # B = White bishop
        # N = White knight
        # P = White pawn
        # k = Black king
        # q = Black queen
        # r = Black rook
        # b = Black bishop
        # n = Black knight
        # p = black pawn
        # (SPACE) = empty square
        self.board = board
        self.side_to_move = side_to_move
        self.white_long_castle = white_long_castle
        self.white_short_castle = white_short_castle
        self.black_long_castle = black_long_castle
        self.black_short_castle = black_short_castle
        self._ep_square = ep_square
        self.halfmove_count = halfmove_count
        self.fullmove_count = fullmove_count

        # is side to move in check? None if not calculated yet
        self._in_check = None

        # list of valid legal moves for the current position
        # each move is stored in token form and long algebraic notation
        # None means not calculated yet, [] means no legal moves
        self._move_list = None

        # current status of game, None if not calculated yet
        self._state = None

        # TODO: calculate state, check, movelist

    # TODO: essential checks for legality so it plays well with program/engine
    @classmethod
    def import_fen(cls, fen_string):
        """Return ChessPosition built from fen string, minimal validation."""
        # remove leading/training whitespace
        fen_clean = fen_string.strip()
        # exit if incorrect number of slashes or spaces
        if fen_clean.count('/') != 7 or fen_clean.count(' ') != 5: return False
        # split fen into list of 5+ fields
        # [board, side to move, castling, ep square,
        # halfmove, fullmove, meta data]
        fen_list = fen_clean.split()

        # board from the fen, defaults to all blanks
        board = [list('        '),
                 list('        '),
                 list('        '),
                 list('        '),
                 list('        '),
                 list('        '),
                 list('        '),
                 list('        ')]
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
        # ranks are reversed
        fen_ranks = fen_list[0].split('/')  # list of ranks as strings
        # 0 based xy coordinate of the current board square
        board_x, fen_x, y = 0, 0, 0
        while True:

            # check if rank size is correct
            if len(fen_ranks[y]) <= fen_x: return False

            # if current index is at a piece, add it to the board
            if fen_ranks[y][fen_x].upper() in ('P', 'R', 'B', 'N', 'K', 'Q'):
                board[y][board_x] = fen_ranks[y][fen_x]
                board_x += 1
                fen_x += 1

            # skip past squares if index is at a number
            elif ord(fen_ranks[y][fen_x]) - 48 in range(1, 9):
                # verify number doesn't make x go oob
                if (board_x + ord(fen_ranks[y][fen_x]) - 48) > 8: return False

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
        return cls(board, side_to_move, wl, ws, bl, bs, ep_square,
                   halfmove_count, fullmove_count)

    # TODO: add gamestate check
    def move(self, move):
        """
        Verify move is legal then enact the move on the position.

        Paramater:
            move (4-5 length string): long algebraic formatted move
                (row_src, file_src, row_dest, file_dest, [promotion piece])

        Returns:
            Boolean denoting if move was legal (and enacted) or not.

        """
        # verify matches uci format
        if re.fullmatch("([a-h][1-8]){2}[qrbn]?", move) is not None:
            # convert string move to tuple with 0 based xy coordinates
            # convert to list, add promotion, then convert to tuple

            # add blank "special" if none given
            if len(move) == 4: move += ' '
            move_tuple = Move(ord(move[0]) - 97, ord(move[1]) - 49,
                              ord(move[2]) - 97, ord(move[3]) - 49,
                              move[4])

            # clean up legal moves to compare against
            # remove d from double moves, and ep from en passant
            legal_moves = deepcopy(self.move_list)
            for i, l_move in enumerate(legal_moves):
                if l_move.special not in ('q', 'r', 'b', 'n', ' '):
                    legal_moves[i] = l_move[0:4] + (' ',)

            # make the move if it is a valid move
            if move_tuple in legal_moves:
                temp_index = legal_moves.index(move_tuple)
                self._make_move(self.move_list[temp_index])
                return True

        return False

    @property
    def move_list(self):
        """
        Getter for legal moves of the position.

        Use stored moves if available, if not then calculate moves.

        Returns:
            Legal Moves (list):
                4-5 int tuples
                (x_src, y_src, x_dest, y_dest, [promotion_symbol]) 0 based
        """
        # Generate move list if not stored
        if self._move_list is None:

            self._move_list = []

            # generate pseudo legal moves
            pseudo_move_list = self._get_pseudo_moves()

            # add castling moves
            # this has to be done here instead of _get_pseudo_moves to prevent
            # infinite recursion
            pseudo_move_list.extend(self._get_castling_moves())

            # add pseudo move to legal move list if it is a full legal move
            # as in it doesn't put it's own king in check
            for move in pseudo_move_list:
                if self._legal_move_check(move): self._move_list.append(move)

        return self._move_list

    # TODO: be called by relevant code
    # TODO: draw by material, 3, 5
    @property
    def state(self):
        """Getter for the game state of the position."""
        # calculate state if not stored
        if self._state is None:

            # if no legal moves, this generates move list if not done
            if not self.move_list:
                # checkmate if in check, stalemate otherwise
                if self.in_check:
                    self._state = GameState.CHECKMATE
                else:
                    self._state = GameState.STALEMATE

            # Forced draw by 75 move rule (1 move = 1 turn by each side)
            # note that checkmate takes precedence
            elif self.halfmove_count >= 150:
                self._state = GameState.DRAW_BY_75_MOVE

            # claimable draw by 50 move rule
            elif self.halfmove_count >= 100:
                self._state = GameState.DRAW_BY_50_MOVE

            else:
                self._state = GameState.ONGOING

        return self._state

    @property
    def in_check(self):
        """
        Getter for in check status.

        True if king is in check, False otherwise.

        Uses stored result if available.
        """
        # calculate if not stored
        if self._in_check is None:
            # check if king is in check then store result
            self._in_check = not self._legal_move_check(Move(0, 0, 0, 0, ' '))

        return self._in_check

    def _make_move(self, move):
        """
        Take in an assumed legal move and enact it on the position.

        Updates all Chess position variables as needed.

            Paramater:
                move (4-5 int 0-7 tuple):
                    (x_src, y_src, x_dest, y_dest, [special_pawn_symbol])
        """
        # reset position specific values
        self._ep_square = None
        self._in_check = None
        self._move_list = None
        self._state = None

        # skip all logic if its a null move
        if move != Move(0, 0, 0, 0, ' '):

            # fullmove counter, increment if this is blacks move
            if not self.side_to_move: self.fullmove_count += 1

            # halfmove counter
            # reset if pawn move or capture move
            if (self.board[move.y1][move.x1].upper() == 'P'
                    or self.board[move.y2][move.x2].isalpha()):
                self.halfmove_count = 0

            # increment every half move otherwise
            else: self.halfmove_count += 1

            # helper variable
            # move piece from src to dest (is overwritten when promoting)
            dest_piece = self.board[move.y1][move.x1]

            # promotion, en passant move, or double pawn move
            if move.special != ' ':

                # double first pawn moves, this is needed to set ep square
                if move.special == 'd':
                    # set ep square to square behind the pawn
                    if self.side_to_move:
                        self._ep_square = Square(move.x2, move.y2 - 1)
                    else: self._ep_square = Square(move.x2, move.y2 + 1)

                # promotion
                elif move.special in ('q', 'r', 'n', 'b'):
                    dest_piece = move.special
                    # promotion piece is lowercase, make uppercase its white
                    if self.side_to_move:
                        dest_piece = dest_piece.upper()

                # en passant (or invalid move)
                else:
                    # remove captured piece (depends on what side to move)
                    if self.side_to_move:
                        self.board[move.y2 - 1][move.x2] = ' '
                    else: self.board[move.y2 + 1][move.x2] = ' '

            # standard move or castling
            else:

                # move rook and disable castling rights if castling move
                # white short castle
                if self.white_short_castle and move == (4, 0, 6, 0, ' '):
                    self.white_short_castle = self.white_long_castle = False
                    self.board[0][7] = ' '
                    self.board[0][5] = 'R'

                # black short castle
                elif self.black_short_castle and move == (4, 7, 6, 7, ' '):
                    self.black_short_castle = self.black_long_castle = False
                    self.board[7][7] = ' '
                    self.board[7][5] = 'r'

                # white long castle
                elif self.white_long_castle and move == (4, 0, 2, 0, ' '):
                    self.white_short_castle = self.white_long_castle = False
                    self.board[0][0] = ' '
                    self.board[0][3] = 'R'

                # black long castle
                elif self.black_long_castle and move == (4, 7, 2, 7, ' '):
                    self.black_short_castle = self.black_long_castle = False
                    self.board[7][0] = ' '
                    self.board[7][3] = 'r'

            # remove src piece from src square
            self.board[move.y1][move.x1] = ' '

            # assign helper variable back to array
            self.board[move.y2][move.x2] = dest_piece

            # CASTLING LEGALITY CHECK/UPDATE
            # redundant condition checks are added to prevent grid lookups
            # disable castling rights if rook isn't on origin square
            if self.white_long_castle and self.board[0][0] != 'R':
                self.white_long_castle = False
            if self.white_short_castle and self.board[0][7] != 'R':
                self.white_short_castle = False
            if self.black_long_castle and self.board[7][0] != 'r':
                self.black_long_castle = False
            if self.black_short_castle and self.board[7][7] != 'r':
                self.black_short_castle = False

            # disable castling rights if king isn't on origin square
            if ((self.white_long_castle or self.white_short_castle)
                    and self.board[0][4] != 'K'):
                self.white_long_castle = self.white_short_castle = False

            if ((self.black_long_castle or self.black_short_castle)
                    and self.board[7][4] != 'k'):
                self.black_long_castle = self.black_short_castle = False

        # give turn to opposite side
        self.side_to_move = not self.side_to_move

        # TODO: return new gamestate (without infinite recursion?)
        return

    def _legal_move_check(self, move):
        """
        Check if given pseudo legal move is a legal move.

        A Pseudo legal move is legal iff it does not leave own king in check.

            Returns:
                Bool: True if legal, False otherwise.
        """
        # create copy of position
        position_copy = ChessPosition(deepcopy(self.board),
                                      self.side_to_move,
                                      self.white_long_castle,
                                      self.white_short_castle,
                                      self.black_long_castle,
                                      self.black_short_castle,
                                      self._ep_square,
                                      self.halfmove_count,
                                      self.fullmove_count)

        # make the proposed move on the board copy
        position_copy._make_move(move)

        # iterate through move list for opponent after making the proposed move
        # if any move captures a king then the proposed move is not legal
        # note, for check validation, opponents pseudo legal moves are fine
        for test_move in position_copy._get_pseudo_moves():
            if position_copy.board[test_move.y2][test_move.x2].upper() == 'K':
                return False

        # return true if the move is fully legal
        return True

    def _get_pseudo_moves(self):
        """Generate list of pseudo legal moves for the position."""
        pseudo_moves = []

        # iterate through chess board adding moves for each piece
        for y in range(8):        # rank
            for x in range(8):    # file

                # helper variable
                square_value = self.board[y][x]

                # check if current square has a piece owned by current side
                if (square_value.isalpha()
                        and self.side_to_move == square_value.isupper()):

                    # get moves for piece at current location
                    # moves are returned as a list, extended to moves list
                    piece_function = {
                        'P': self._get_pawn_moves,
                        'N': self._get_knight_moves,
                        'B': self._get_ray_moves,
                        'R': self._get_ray_moves,
                        'Q': self._get_ray_moves,
                        'K': self._get_king_moves
                    }[square_value.upper()]
                    pseudo_moves.extend(piece_function(Square(x, y)))

        # add en passant moves
        pseudo_moves.extend(self._get_ep_moves())

        return pseudo_moves

    def _get_knight_moves(self, loc):
        """
        Get list of pseudo legal moves for knight at given coordinate.

            Paramaters:
                y (int): 0 based y coord
                x (int): 0 based x coord
        """
        knight_moves = []
        # y,z coords of all possible knight moves
        target_list = [Square(loc.x - 2, loc.y + 1),
                       Square(loc.x - 1, loc.y + 2),
                       Square(loc.x + 1, loc.y + 2),
                       Square(loc.x + 2, loc.y + 1),
                       Square(loc.x + 2, loc.y - 1),
                       Square(loc.x + 1, loc.y - 2),
                       Square(loc.x - 1, loc.y - 2),
                       Square(loc.x - 2, loc.y - 1)]

        for target in target_list:
            # verify target square is not OOB
            if target.x in range(0, 8) and target.y in range(0, 8):

                # helper variable
                target_value = self.board[target.y][target.x]

                # verify target is not friendly piece
                # space check is needed because space is uppercase
                if (target_value.isspace()
                        or self.side_to_move != target_value.isupper()):
                    # add move as 4 tuple, (src x, src y, dest x, dest y)
                    knight_moves.append(Move(loc.x, loc.y, target.x, target.y,
                                             ' '))

        return knight_moves

    def _get_ray_moves(self, loc):
        """
        Get ray style pseudo legal moves for piece at given coordinate.

        Used for bishop, rook, and queen moves. Used _ray_move_helper().
        """
        ray_moves = []

        # keeps track of which directions to check
        cardinal = True
        diagonal = True

        # disable diagonal for rook
        if self.board[loc.y][loc.x].upper() == 'R': diagonal = False
        # disable cardinal for bishop
        elif self.board[loc.y][loc.x].upper() == 'B': cardinal = False
        # else keep both enabled for queen

        # get cardinal moves (north east south west)
        if cardinal:
            # north moves
            for i in range(loc.y + 1, 8):
                # skip if piece on 8th rank
                if i > 7: break
                # use helper method to add move then break if applicable
                if not self._ray_move_helper(ray_moves, loc.y,
                                             loc.x, i, loc.x):
                    break

            # south moves
            for i in range(loc.y - 1, -1, -1):
                # skip if piece on 1st rank
                if i < 0: break
                if not self._ray_move_helper(ray_moves, loc.y, loc.x,
                                             i, loc.x):
                    break

            # east moves
            for j in range(loc.x + 1, 8):
                # skip if piece on h file
                if j > 7: break
                if not self._ray_move_helper(ray_moves, loc.y,
                                             loc.x, loc.y, j):
                    break

            # west moves
            for j in range(loc.x - 1, -1, -1):
                # skip if piece on a file
                if j < 0: break
                if not self._ray_move_helper(ray_moves, loc.y, loc.x,
                                             loc.y, j):
                    break

        # get diagonal moves (ne nw se sw)
        if diagonal:

            # north east
            for i in range(loc.y + 1, 8):
                # calculate target x
                # i-y = raw distance from piece
                j = loc.x + (i - loc.y)
                # skip if piece on board edge
                if i > 7 or j > 7: break
                if not self._ray_move_helper(ray_moves, loc.y, loc.x, i, j):
                    break

            # south east
            for i in range(loc.y - 1, -1, -1):
                j = loc.x + (loc.y - i)
                if i < 0 or j > 7: break
                if not self._ray_move_helper(ray_moves, loc.y, loc.x, i, j):
                    break

            # north west
            for i in range(loc.y + 1, 8):
                j = loc.x - (i - loc.y)
                if i > 7 or j < 0: break
                if not self._ray_move_helper(ray_moves, loc.y, loc.x, i, j):
                    break

            # south west
            for i in range(loc.y - 1, -1, -1):
                j = loc.x - (loc.y - i)
                if i < 0 or j < 0: break
                if not self._ray_move_helper(ray_moves, loc.y, loc.x, i, j):
                    break

        return ray_moves

    def _ray_move_helper(self, move_list, y1, x1, y2, x2):
        """
        Use for ray move generation.

        Helper method for _get_ray_moves().
        Add move to move list as needed, return False at wall, True otherwise.
        """
        # empty square, add move and keep searching
        if self.board[y2][x2] == ' ':
            move_list.append(Move(x1, y1, x2, y2, ' '))
            return True

        # friendly piece, don't add move and end search
        if self.side_to_move == self.board[y2][x2].isupper(): return False

        # enemy piece, add move and end search
        move_list.append(Move(x1, y1, x2, y2, ' '))
        return False

    def _get_pawn_moves(self, loc):
        """
        Get list of pseudo legal moves for pawn at given coordinate.

            Paramaters:
                y (int): 0 based y coord
                x (int): 0 based x coord
        """
        pawn_moves = []

        # white pawns
        if self.side_to_move:
            # non capture moves
            if self.board[loc.y + 1][loc.x] == ' ':
                # normal move forward
                pawn_moves.append(Move(loc.x, loc.y, loc.x, loc.y + 1, ' '))
                # double first move
                if loc.y == 1 and self.board[loc.y + 2][loc.x] == ' ':
                    pawn_moves.append(Move(loc.x, loc.y, loc.x, loc.y + 2,
                                           'd'))
            # capture moves
            if loc.x > 0 and self.board[loc.y + 1][loc.x - 1].islower():
                pawn_moves.append(Move(loc.x, loc.y, loc.x - 1, loc.y + 1,
                                       ' '))
            if loc.x < 7 and self.board[loc.y + 1][loc.x + 1].islower():
                pawn_moves.append(Move(loc.x, loc.y, loc.x + 1, loc.y + 1,
                                       ' '))

        # black pawns
        else:
            if self.board[loc.y - 1][loc.x] == ' ':
                pawn_moves.append(Move(loc.x, loc.y, loc.x, loc.y - 1, ' '))
                if loc.y == 6 and self.board[loc.y - 2][loc.x] == ' ':
                    pawn_moves.append(Move(loc.x, loc.y, loc.x, loc.y - 2,
                                           'd'))

            if (loc.x > 0 and self.board[loc.y - 1][loc.x - 1].isalpha()
                    and self.board[loc.y - 1][loc.x - 1].isupper()):
                pawn_moves.append(Move(loc.x, loc.y, loc.x - 1, loc.y - 1,
                                       ' '))

            if (loc.x < 7 and self.board[loc.y - 1][loc.x + 1].isalpha()
                    and self.board[loc.y - 1][loc.x + 1].isupper()):
                pawn_moves.append(Move(loc.x, loc.y, loc.x + 1, loc.y - 1,
                                       ' '))

        # add promotion moves
        for i, move in enumerate(pawn_moves):

            # look for pawn moves landing on promotion rank
            # that haven't already been converted to promotion moves yet
            if (((move.y2 == 7 and self.side_to_move)
                    or (move.y2 == 0 and not self.side_to_move))
                    and move.special == ' '):

                # replace original promotion move with queen promotion
                pawn_moves[i] = Move(move.x1, move.y1, move.x2, move.y2, 'q')

                # add under promotion moves
                for p in ('r', 'b', 'n'):
                    pawn_moves.append(Move(move.x1, move.y1, move.x2, move.y2, p))

        return pawn_moves

    def _get_king_moves(self, loc):
        """
        Get list of pseudo legal moves for king at given coordinate.

            Paramaters:
                y (int): 0 based y coord
                x (int): 0 based x coord
        """
        king_moves = []

        target_list = [Square(loc.x + 1, loc.y + 1),
                       Square(loc.x + 1, loc.y - 1),
                       Square(loc.x - 1, loc.y - 1),
                       Square(loc.x - 1, loc.y + 1),
                       Square(loc.x + 1, loc.y),
                       Square(loc.x - 1, loc.y),
                       Square(loc.x, loc.y + 1),
                       Square(loc.x, loc.y - 1)]

        for target in target_list:
            # verify target square is not OOB
            if target.x in range(0, 8) and target.y in range(0, 8):

                # helper variable
                target_value = self.board[target.y][target.x]

                # verify target is not friendly piece
                # space check is needed because space is uppercase
                if (target_value.isspace()
                        or self.side_to_move != target_value.isupper()):
                    # add move as 4 tuple, (src x, src y, dest x, dest y)
                    king_moves.append(Move(loc.x, loc.y, target.x, target.y,
                                           ' '))

        return king_moves

    def _get_ep_moves(self):
        """
        Get en passant pseudo legal moves if _ep_square is defined.

        Assumes _ep_square is valid/legal.
        Meaning if its white to move then ep target y MUST = 5, etc.
        """
        # skip if no ep target square
        ep_moves = []
        if self._ep_square is not None:

            # just to keep things looking readable
            ep_x = self._ep_square.x

            # white ep moves
            if self.side_to_move:
                # check left
                if ep_x > 0 and self.board[4][ep_x - 1] == 'P':
                    ep_moves.append(Move(ep_x - 1, 4, ep_x, 5, 'ep'))
                # check right
                if ep_x < 7 and self.board[4][ep_x + 1] == 'P':
                    ep_moves.append(Move(ep_x + 1, 4, ep_x, 5, 'ep'))

            # black ep moves
            else:
                if ep_x > 0 and self.board[3][ep_x - 1] == 'p':
                    ep_moves.append(Move(ep_x - 1, 3, ep_x, 2, 'ep'))
                if ep_x < 7 and self.board[3][ep_x + 1] == 'p':
                    ep_moves.append(Move(ep_x + 1, 3, ep_x, 2, 'ep'))

        return ep_moves

    def _get_castling_moves(self):
        """
        Get list of castling legal moves.

        Dest square attack check is done using get_legal_moves.
        """
        # exit if king is in check
        if self.in_check: return []

        castle_moves = []

        # white
        if self.side_to_move:

            # kingside (if true then king and kingside rook haven't moved)
            if self.white_short_castle:
                # verify squares are unoccupied and add move
                if self.board[0][5] == ' ' and self.board[0][6] == ' ':
                    # check if 5,0 is not attacked, if safe then add move
                    if self._is_square_safe(Square(5, 0)):
                        castle_moves.append(Move(4, 0, 6, 0, ' '))

            # queenside
            if self.white_long_castle:
                if (self.board[0][1] == ' ' and self.board[0][2] == ' '
                        and self.board[0][3] == ' '):
                    if self._is_square_safe(Square(3, 0)):
                        castle_moves.append(Move(4, 0, 2, 0, ' '))

        # black
        else:
            if self.black_short_castle:
                if self.board[7][5] == ' ' and self.board[7][6] == ' ':
                    if self._is_square_safe(Square(5, 7)):
                        castle_moves.append(Move(4, 7, 6, 7, ' '))

            if self.black_long_castle:
                if (self.board[7][1] == ' ' and self.board[7][2] == ' '
                        and self.board[7][3] == ' '):
                    if self._is_square_safe(Square(3, 7)):
                        castle_moves.append(Move(4, 7, 2, 7, ' '))

        return castle_moves

    # TODO: store results for 4 castling squares from previous move generation?
    # TODO: merge this with _legal_move_check() somehow? very similar code
    def _is_square_safe(self, square):
        """
        Return True if square is not under attack, False if attacked.

        Helper method for castling. 0 based coords assumed to be in bounds.
        """
        # create copy of position
        position_copy = ChessPosition(deepcopy(self.board),
                                      self.side_to_move,
                                      self.white_long_castle,
                                      self.white_short_castle,
                                      self.black_long_castle,
                                      self.black_short_castle,
                                      self._ep_square,
                                      self.halfmove_count,
                                      self.fullmove_count)

        # make a null move
        position_copy._make_move(Move(0, 0, 0, 0, ' '))

        # iterate through move list for opponent
        # if any move lands on the given square, return false
        # note: opponents pseudo legal moves are fine for this check
        for test_move in position_copy._get_pseudo_moves():
            if square.x == test_move.x2 and square.y == test_move.y2:
                return False

        # return True if the square is not attacked
        return True
