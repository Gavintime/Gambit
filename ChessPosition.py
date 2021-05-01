"""
Create Chess positions and calculate moves.

Classes:
    GameState: Enum class for game states.
    ChessPosition: Class for Chess Positions.

Misc variables:
    start_board: Default starting board of a game.
    WHITE: constant to refer to white as True.
    BLACK: constant to refer to black as False.
"""

import re
import copy
from enum import Enum


# reversed vertically
start_board = [list("RNBQKBNR"),
               list("PPPPPPPP"),
               list("        "),
               list("        "),
               list("        "),
               list("        "),
               list("pppppppp"),
               list("rnbqkbnr")]

WHITE = True
BLACK = False


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
            get_legal_moves():
                Return list of legal moves for the current position
            get_game_state():
                Return game state. UNFINISHED
    """

    # TODO: logic for 3 move, 5 move, 50 move?, and 75 move? repetition
    def __init__(self, board=start_board,
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
        self._board = board
        self._side_to_move = side_to_move
        self._white_long_castle = white_long_castle
        self._white_short_castle = white_short_castle
        self._black_long_castle = black_long_castle
        self._black_short_castle = black_short_castle
        self._ep_square = ep_square
        self._halfmove_count = halfmove_count
        self._fullmove_count = fullmove_count

        # is side to move in check? None if not calculated yet
        self._in_check = None

        # list of valid legal moves for the current position
        # each move is stored in token form and long algebraic notation
        # None means not calculated yet, [] means no legal moves
        self._move_list = None

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

        # skip all logic if its a null move
        if move != (0, 0, 0, 0):

            # fullmove counter, increment if this is blacks move
            if not self._side_to_move: self._fullmove_count += 1

            # halfmove counter
            # reset if pawn move or capture move
            if (self._board[move[1]][move[0]].upper() == 'P'
                    or self._board[move[3]][move[2]].isalpha()):
                self._halfmove_count = 0

            # increment every half move otherwise
            else: self._halfmove_count += 1

            # helper variables
            dest_piece = ''

            # move piece from src to dest (is overwritten when promoting)
            dest_piece = self._board[move[1]][move[0]]

            # promotion, en passant move, or double pawn move
            if len(move) == 5:

                # double first pawn moves, this is needed to set ep square
                if move[4] == 'd':
                    # set ep square to square behind the pawn
                    if self._side_to_move:
                        self._ep_square = (move[2], move[3] - 1)
                    else: self._ep_square = (move[2], move[3] + 1)

                # promotion
                elif move[4] in ('q', 'r', 'n', 'b'):
                    dest_piece = move[4]
                    # promotion piece is lowercase, make uppercase its white
                    if self._side_to_move:
                        dest_piece = dest_piece.upper()

                # en passant (or invalid move :^) )
                else:
                    # remove captured piece (depends on what side to move)
                    if self._side_to_move:
                        self._board[move[3] - 1][move[2]] = ' '
                    else: self._board[move[3] + 1][move[2]] = ' '

            # standard move or castling
            else:

                # move rook and disable castling rights if castling move
                # white short castle
                if self._white_short_castle and move == (4, 0, 6, 0):
                    self._white_short_castle = self._white_long_castle = False
                    self._board[0][7] = ' '
                    self._board[0][5] = 'R'

                # black short castle
                elif self._black_short_castle and move == (4, 7, 6, 7):
                    self._black_short_castle = self._black_long_castle = False
                    self._board[7][7] = ' '
                    self._board[7][5] = 'r'

                # white long castle
                elif self._white_long_castle and move == (4, 0, 2, 0):
                    self._white_short_castle = self._white_long_castle = False
                    self._board[0][0] = ' '
                    self._board[0][3] = 'R'

                # black long castle
                elif self._black_long_castle and move == (4, 7, 2, 7):
                    self._black_short_castle = self._black_long_castle = False
                    self._board[7][0] = ' '
                    self._board[7][3] = 'r'

            # remove src piece from src square
            self._board[move[1]][move[0]] = ' '

            # assign helper variable back to array
            self._board[move[3]][move[2]] = dest_piece

            # CASTLING LEGALITY CHECK/UPDATE
            # redundant condition checks are added to prevent grid lookups
            # disable castling rights if rook isn't on origin square
            if self._white_long_castle and self._board[0][0] != 'R':
                self._white_long_castle = False
            if self._white_short_castle and self._board[0][7] != 'R':
                self._white_short_castle = False
            if self._black_long_castle and self._board[7][0] != 'r':
                self._black_long_castle = False
            if self._black_short_castle and self._board[7][7] != 'r':
                self._black_short_castle = False

            # disable castling rights if king isn't on origin square
            if ((self._white_long_castle or self._white_short_castle)
                    and self._board[0][4] != "K"):
                self._white_long_castle = self._white_short_castle = False

            if ((self._black_long_castle or self._black_short_castle)
                    and self._board[7][4] != "k"):
                self._black_long_castle = self._black_short_castle = False

        # give turn to opposite side
        self._side_to_move = not self._side_to_move

        return

    # TODO: move the move format/cleaning to Gambit.py, this method should only
    def move(self, move):
        """
        Verify move is legal then enact the move on the position.

        Paramater:
            move (4-5 char tuple): long algebraic formatted move
                (row_src, file_src, row_dest, file_dest, [promotion piece])

        Returns:
            Boolean denoting if move was legal (and enacted) or not.

        """
        # verify matches uci format
        if re.fullmatch("([a-h][1-8]){2}[qrbn]?", move) is not None:
            # convert string move to tuple with 0 based xy coordinates
            # convert to list, add promotion, then convert to tuple
            # TODO: remove unneeded tuple conversion?
            move_tuple = [ord(move[0]) - 97, ord(move[1]) - 49,
                          ord(move[2]) - 97, ord(move[3]) - 49]
            if len(move) == 5: move_tuple.append(move[4])
            move_tuple = tuple(move_tuple)

            # clean up legal moves to compare against
            # remove d from double moves, and ep from en passant
            legal_moves = self.get_legal_moves()
            for i in range(0, len(legal_moves)):
                if (len(legal_moves[i]) == 5
                        and legal_moves[i][4] not in ('q', 'r', 'b', 'n')):
                    legal_moves[i] = legal_moves[i][0:4]

            # make the move if it is a valid move
            if move_tuple in legal_moves:
                temp_index = legal_moves.index(move_tuple)
                self._make_move(self.get_legal_moves()[temp_index])
                return True

        return False

    def get_legal_moves(self):
        """
        Get legal moves for the position.

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
    def get_game_state(self):
        """Get the game state of the current position."""
        # generate move list if not done yet
        self.get_legal_moves()

        # if no legal moves
        if not self._move_list:
            # checkmate if in check, stalemate otherwise
            if self._get_in_check(): return GameState.CHECKMATE
            else: return GameState.STALEMATE

        # Forced draw by 75 move rule (1 move = 1 turn by each side)
        # note that checkmate takes precedence
        elif self._halfmove_count >= 150: return GameState.DRAW_BY_75_MOVE

        # claimable draw by 50 move rule
        elif self._halfmove_count >= 100: return GameState.DRAW_BY_50_MOVE

        else: return GameState.ONGOING

    def _get_pseudo_moves(self):
        """Generate list of pseudo legal moves for the position."""
        pseudo_moves = []

        # iterate through chess board adding moves for each piece
        for y in range(8):        # rank
            for x in range(8):    # file

                # helper variable
                square_value = self._board[y][x]

                # check if current square has a piece owned by current side
                if (square_value.isalpha()
                        and self._side_to_move == square_value.isupper()):

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
                    pseudo_moves.extend(piece_function(y, x))

        # add en passant moves
        pseudo_moves.extend(self._get_ep_moves())

        return pseudo_moves

    def _get_knight_moves(self, y, x):
        """
        Get list of pseudo legal moves for knight at given coordinate.

            Paramaters:
                y (int): 0 based y coord
                x (int): 0 based x coord
        """
        knight_moves = []
        # y,z coords of all possible knight moves
        target_list = [(x - 2, y + 1),
                       (x - 1, y + 2),
                       (x + 1, y + 2),
                       (x + 2, y + 1),
                       (x + 2, y - 1),
                       (x + 1, y - 2),
                       (x - 1, y - 2),
                       (x - 2, y - 1)]

        for target in target_list:
            # verify target square is not OOB
            if target[0] in range(0, 8) and target[1] in range(0, 8):

                # helper variable
                target_value = self._board[target[1]][target[0]]

                # verify target is not friendly piece
                # space check is needed because space is uppercase
                if (target_value.isspace()
                        or self._side_to_move != target_value.isupper()):
                    # add move as 4 tuple, (src x, src y, dest x, dest y)
                    knight_moves.append((x, y, target[0], target[1]))

        return knight_moves

    def _get_ray_moves(self, y, x):
        """
        Get ray style pseudo legal moves for piece at given coordinate.

        Used for bishop, rook, and queen moves. Used _ray_move_helper().
        """
        ray_moves = []

        # keeps track of which directions to check
        cardinal = True
        diagonal = True

        # disable diagonal for rook
        if self._board[y][x].upper() == 'R': diagonal = False
        # disable cardinal for bishop
        elif self._board[y][x].upper() == 'B': cardinal = False
        # else keep both enabled for queen

        # get cardinal moves (north east south west)
        if cardinal:
            # north moves
            for i in range(y + 1, 8):
                # skip if piece on 8th rank
                if i > 7: break
                # use helper method to add move then break if applicable
                if not self._ray_move_helper(ray_moves, y, x, i, x): break

            # south moves
            for i in range(y - 1, -1, -1):
                # skip if piece on 1st rank
                if i < 0: break
                if not self._ray_move_helper(ray_moves, y, x, i, x): break

            # east moves
            for j in range(x + 1, 8):
                # skip if piece on h file
                if j > 7: break
                if not self._ray_move_helper(ray_moves, y, x, y, j): break

            # west moves
            for j in range(x - 1, -1, -1):
                # skip if piece on a file
                if j < 0: break
                if not self._ray_move_helper(ray_moves, y, x, y, j): break

        # get diagonal moves (ne nw se sw)
        if diagonal:

            # north east
            for i in range(y + 1, 8):
                # calculate target x
                # i-y = raw distance from piece
                j = x + (i - y)
                # skip if piece on board edge
                if i > 7 or j > 7: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

            # south east
            for i in range(y - 1, -1, -1):
                j = x + (y - i)
                if i < 0 or j > 7: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

            # north west
            for i in range(y + 1, 8):
                j = x - (i - y)
                if i > 7 or j < 0: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

            # south west
            for i in range(y - 1, -1, -1):
                j = x - (y - i)
                if i < 0 or j < 0: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

        return ray_moves

    def _get_king_moves(self, y, x):
        """
        Get list of pseudo legal moves for king at given coordinate.

            Paramaters:
                y (int): 0 based y coord
                x (int): 0 based x coord
        """
        king_moves = []

        target_list = [(x + 1, y + 1),
                       (x + 1, y - 1),
                       (x - 1, y - 1),
                       (x - 1, y + 1),
                       (x + 1, y),
                       (x - 1, y),
                       (x, y + 1),
                       (x, y - 1)]

        for target in target_list:
            # verify target square is not OOB
            if target[0] in range(0, 8) and target[1] in range(0, 8):

                # helper variable
                target_value = self._board[target[1]][target[0]]

                # verify target is not friendly piece
                # space check is needed because space is uppercase
                if (target_value.isspace()
                        or self._side_to_move != target_value.isupper()):
                    # add move as 4 tuple, (src x, src y, dest x, dest y)
                    king_moves.append((x, y, target[0], target[1]))

        return king_moves

    def _get_pawn_moves(self, y, x):
        """
        Get list of pseudo legal moves for pawn at given coordinate.

            Paramaters:
                y (int): 0 based y coord
                x (int): 0 based x coord
        """
        pawn_moves = []

        # white pawns
        if self._side_to_move:
            # non capture moves
            if self._board[y + 1][x] == ' ':
                # normal move forward
                pawn_moves.append((x, y, x, y + 1))
                # double first move
                if y == 1 and self._board[y + 2][x] == ' ':
                    pawn_moves.append((x, y, x, y + 2, 'd'))
            # capture moves
            if x > 0 and self._board[y + 1][x - 1].islower():
                pawn_moves.append((x, y, x - 1, y + 1))
            if x < 7 and self._board[y + 1][x + 1].islower():
                pawn_moves.append((x, y, x + 1, y + 1))

        # black pawns
        else:
            # non capture moves
            if self._board[y - 1][x] == ' ':
                # normal move forward
                pawn_moves.append((x, y, x, y - 1))
                # double first move
                if y == 6 and self._board[y - 2][x] == ' ':
                    pawn_moves.append((x, y, x, y - 2, 'd'))

            # capture moves
            if (x > 0 and self._board[y - 1][x - 1].isalpha()
                    and self._board[y - 1][x - 1].isupper()):
                pawn_moves.append((x, y, x - 1, y - 1))

            if (x < 7 and self._board[y - 1][x + 1].isalpha()
                    and self._board[y - 1][x + 1].isupper()):
                pawn_moves.append((x, y, x + 1, y - 1))

        # add promotion moves
        for i in range(0, len(pawn_moves)):

            # look for pawn moves landing on promotion rank
            # that haven't already been converted to promotion moves yet
            if (((pawn_moves[i][3] == 7 and self._side_to_move)
                    or (pawn_moves[i][3] == 0 and not self._side_to_move))
                    and len(pawn_moves[i]) != 5):

                # replace original promotion move with queen promotion
                pawn_moves[i] = (pawn_moves[i][0], pawn_moves[i][1],
                                 pawn_moves[i][2], pawn_moves[i][3], 'q')

                # add under promotion moves
                for p in ('r', 'b', 'n'):
                    pawn_moves.append((pawn_moves[i][0], pawn_moves[i][1],
                                       pawn_moves[i][2], pawn_moves[i][3], p))

        return pawn_moves

    def _get_ep_moves(self):
        """
        Get en passant pseudo legal moves if _ep_square is defined.

        Assumes _ep_square is valid/legal.
        Meaning if its white to move then ep target y MUST = 5, etc.
        """
        # skip if no ep target square
        if self._ep_square is None: return []

        ep_moves = []

        # just to keep things looking readable
        ep_x = self._ep_square[0]

        # white ep moves
        if self._side_to_move:
            # check left
            if ep_x > 0 and self._board[4][ep_x - 1] == 'P':
                ep_moves.append((ep_x - 1, 4, ep_x, 5, "ep"))
            # check right
            if ep_x < 7 and self._board[4][ep_x + 1] == 'P':
                ep_moves.append((ep_x + 1, 4, ep_x, 5, "ep"))

        # black ep moves
        else:
            if ep_x > 0 and self._board[3][ep_x - 1] == 'p':
                ep_moves.append((ep_x - 1, 3, ep_x, 2, "ep"))
            if ep_x < 7 and self._board[3][ep_x + 1] == 'p':
                ep_moves.append((ep_x + 1, 3, ep_x, 2, "ep"))

        return ep_moves

    def _get_castling_moves(self):
        """
        Get list of castling legal moves.

        Dest square attack check is done using get_legal_moves.
        """
        # exit if king is in check
        if self._get_in_check(): return []

        castle_moves = []

        # white
        if self._side_to_move:

            # kingside (if true then king and kingside rook haven't moved)
            if self._white_short_castle:
                # verify squares are unoccupied and add move
                if self._board[0][5] == ' ' and self._board[0][6] == ' ':
                    # check if 5,0 is not attacked, if safe then add move
                    if self._is_square_safe(5, 0):
                        castle_moves.append((4, 0, 6, 0))

            # queenside
            if self._white_long_castle:
                if (self._board[0][1] == ' ' and self._board[0][2] == ' '
                        and self._board[0][3] == ' '):
                    if self._is_square_safe(3, 0):
                        castle_moves.append((4, 0, 2, 0))

        # black
        else:
            if self._black_short_castle:
                if self._board[7][5] == ' ' and self._board[7][6] == ' ':
                    if self._is_square_safe(5, 7):
                        castle_moves.append((4, 7, 6, 7))

            if self._black_long_castle:
                if (self._board[7][1] == ' ' and self._board[7][2] == ' '
                        and self._board[7][3] == ' '):
                    if self._is_square_safe(3, 7):
                        castle_moves.append((4, 7, 2, 7))

        return castle_moves

    def _legal_move_check(self, move):
        """
        Check if given pseudo legal move is a legal move.

        A Pseudo legal move is legal iff it does not leave own king in check.

            Returns:
                Bool: True if legal, False otherwise.
        """
        # create copy of position
        position_copy = ChessPosition(copy.deepcopy(self._board),
                                      self._side_to_move,
                                      self._white_long_castle,
                                      self._white_short_castle,
                                      self._black_long_castle,
                                      self._black_short_castle,
                                      self._ep_square,
                                      self._halfmove_count,
                                      self._fullmove_count)

        # make the proposed move on the board copy
        position_copy._make_move(move)

        # iterate through move list for opponent after making the proposed move
        # if any move captures a king then the proposed move is not legal
        # note, for check validation, opponents pseudo legal moves are fine
        for test_move in position_copy._get_pseudo_moves():
            if position_copy._board[test_move[3]][test_move[2]].upper() == 'K':
                return False

        # return true if the move is fully legal
        return True

    def _ray_move_helper(self, move_list, y1, x1, y2, x2):
        """
        Use for ray move generation.

        Helper method for _get_ray_moves().
        Add move to move list as needed, return False at wall, True otherwise.
        """
        # empty square, add move and keep searching
        if self._board[y2][x2] == ' ':
            move_list.append((x1, y1, x2, y2))
            return True

        # friendly piece, don't add move and end search
        if self._side_to_move == self._board[y2][x2].isupper(): return False

        # enemy piece, add move and end search
        move_list.append((x1, y1, x2, y2))
        return False

    # TODO: store results for 4 castling squares from previous move generation?
    # TODO: merge this with _legal_move_check() somehow? very similar code
    def _is_square_safe(self, sq_x, sq_y):
        """
        Return True if square is not under attack, False if attacked.

        Helper method for castling. 0 based coords assumed to be in bounds.
        """
        # create copy of position
        position_copy = ChessPosition(copy.deepcopy(self._board),
                                      self._side_to_move,
                                      self._white_long_castle,
                                      self._white_short_castle,
                                      self._black_long_castle,
                                      self._black_short_castle,
                                      self._ep_square,
                                      self._halfmove_count,
                                      self._fullmove_count)

        # make a null move
        position_copy._make_move((0, 0, 0, 0))

        # iterate through move list for opponent
        # if any move lands on the given square, return false
        # note: opponents pseudo legal moves are fine for this check
        for test_move in position_copy._get_pseudo_moves():
            if sq_x == test_move[2] and sq_y == test_move[3]:
                return False

        # return True if the square is not attacked
        return True

    def _get_in_check(self):
        """
        Return True if king is in check, False otherwise.

        Uses stored result if available.
        """
        # calculate if not stored
        if self._in_check is None:
            # check if king is in check then store result
            self._in_check = not self._legal_move_check((0, 0, 0, 0))

        return self._in_check
