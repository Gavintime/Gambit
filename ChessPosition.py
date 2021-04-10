import re
import copy


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


class ChessPosition:

    # TODO: counter for repetition
    def __init__(self, board = start_board,
                        side_to_move = WHITE,
                        white_long_castle = True,
                        white_short_castle = True,
                        black_long_castle = True,
                        black_short_castle = True,
                        ep_square = None):
        """
            2d 8x8 list of chars representing pieces on a chess board
            K = White king
            Q = White queen
            R = White rook
            B = White bishop
            N = White knight
            P = White pawn

            k = Black king
            q = Black queen
            r = Black rook
            b = Black bishop
            n = Black knight
            p = black pawn
            (SPACE) = empty square
        """
        self._board = board

        # booleans to store info about the board state
        # True for white to move, False for black to move
        self._side_to_move = side_to_move
        self._white_long_castle = white_long_castle
        self._white_short_castle = white_short_castle
        self._black_long_castle = black_long_castle
        self._black_short_castle = black_short_castle

        # target square of any possible en passant captures
        # None denotes no en passants
        # otherwise, format is 0 based x,y coordinate of ep destination square as 2 tuple
        self._ep_square = ep_square

        # list of valid legal moves for the current position
        # each move is stored in token form and long algebraic notation
        self._move_list = []


    # input: move as 4-5 tuple (as 0 based x y coordinates)
    # makes the give move and updated the board/other variables as necessarily
    # assumes given move is legal (for external use, use move(self) function)
    def _make_move(self, move):


        self._ep_square = None

        # skip all logic if its a null move
        if move != (0,0,0,0):

            # promotion (q,r,n, or b), en passant move (ep), or double first pawn move (d)
            if len(move) == 5:

                # double first pawn moves, this is needed to set ep square
                if move[4] == 'd':
                    # move piece from src to dest
                    self._board[move[3]][move[2]] = self._board[move[1]][move[0]]
                    # set ep square to square behind the pawn
                    if self._side_to_move: self._ep_square = (move[2], move[3]-1)
                    else: self._ep_square = (move[2], move[3]+1)

                # promotion
                elif move[4] in ('q','r','n','b'):
                    self._board[move[3]][move[2]] = move[4]
                    # promotion choice comes in lowercase, make uppercase if its whites move
                    if self._side_to_move: self._board[move[3]][move[2]] = self._board[move[3]][move[2]].upper()

                # en passant (or invalid move :^) )
                else:
                    # move piece from src to dest
                    self._board[move[3]][move[2]] = self._board[move[1]][move[0]]
                    # remove captured piece (depends on what side to move)
                    if self._side_to_move: self._board[move[3]-1][move[2]] = ' '
                    else: self._board[move[3]+1][move[2]] = ' '



            # standard move or castling
            else:
                # move piece from src to dest
                self._board[move[3]][move[2]] = self._board[move[1]][move[0]]


                # move rook and disable castling rights if castling move
                # white short castle
                if self._white_short_castle and move == (4,0,6,0):
                    self._white_short_castle = self._white_long_castle = False
                    self._board[0][7] = ' '
                    self._board[0][5] = 'R'

                # black short castle
                elif self._black_short_castle and move == (4,7,6,7):
                    self._black_short_castle = self._black_long_castle = False
                    self._board[7][7] = ' '
                    self._board[7][5] = 'r'

                # white long castle
                elif self._white_long_castle and move == (4,0,2,0):
                    self._white_short_castle = self._white_long_castle = False
                    self._board[0][0] = ' '
                    self._board[0][3] = 'R'

                # black long castle
                elif self._black_long_castle and move == (4,7,2,7):
                    self._black_short_castle = self._black_long_castle = False
                    self._board[7][0] = ' '
                    self._board[7][3] = 'r'


            # remove src piece from src square
            self._board[move[1]][move[0]] = ' '


            # CASTLING LEGALITY CHECK/UPDATE (redundant condition checks are added to beginning to prevent unnecessary grid lookups)
            # disable castling rights if rook isn't on origin square (for any move)
            if self._white_long_castle and self._board[0][0] != 'R': self._white_long_castle = False
            if self._white_short_castle and self._board[0][7] != 'R': self._white_short_castle = False
            if self._black_long_castle and self._board[7][0] != 'r': self._black_long_castle = False
            if self._black_short_castle and self._board[7][7] != 'r': self._black_short_castle = False
            # disable castling rights if king isn't on origin square (for any move)
            if (self._white_long_castle or self._white_short_castle) and self._board[0][4] != "K":
                self._white_long_castle = self._white_short_castle = False
            if (self._black_long_castle or self._black_short_castle) and self._board[7][4] != "k":
                self._black_long_castle = self._black_short_castle = False


        # give turn to opposite side
        self._side_to_move = not self._side_to_move

        return


    # input: uci style move as string
    # verifies move is legal by comparing against generated list of legal moves
    # if move is legal, _make_move(self, move) is called, which actually makes the move on the board
    # output: boolean denoting if move was legal (and thus moved) or not
    # TODO: PROPER SOLUTION TO IGNORING "helper symbols" when comparing inputted string
    def move(self, move):

        # verify matches uci format
        if re.fullmatch("([a-h][1-8]){2}[qrbn]?", move) != None:
            # convert string move to tuple format move with 0 based xy coordinates
            # first converted to list, add promotion if needed, then convert to actual tuple
            move_tuple = [ord(move[0])-97,ord(move[1])-49,ord(move[2])-97,ord(move[3])-49]
            if len(move) == 5: move_tuple.append(move[4])
            move_tuple = tuple(move_tuple)


            # clean up legal moves to compare against
            # remove d from double moves, and ep from en passant
            legal_moves = self.get_legal_moves()
            for i in range(0,len(legal_moves)):
                if len(legal_moves[i]) == 5 and legal_moves[i][4] not in ('q','r','b','n'):
                    legal_moves[i] = legal_moves[i][0:4]


            # make the move if it is a valid move
            if move_tuple in legal_moves:
                temp_index = legal_moves.index(move_tuple)
                self._make_move(self.get_legal_moves()[temp_index])
                return True

        return False


    # calculate all legal moves for the current game position
    # output: list of legal moves as tuples (start x, start y, dest x, dest y) counting from 0
    def get_legal_moves(self):

        # empty the move list
        self._move_list = []

        # generate pseudo legal moves
        pseudo_move_list = self._get_pseudo_moves()

        # add pseudo move to move list if it is a full legal move
        # as in it doesn't put it's own king in check
        for move in pseudo_move_list:
            if self._legal_move_check(move): self._move_list.append(move)


        # if there are no legal moves do stale/check mate checks
        if not self._move_list:

            # check if in check(mate) by doing a null move and seeing if opponent can capture king
            if self._legal_move_check((0,0,0,0)):
                # TODO: set some game state flag denoting how game ended
                print("STALEMATE")
            else: print("CHECKMATE: ", not self._side_to_move, " wins!")


        return self._move_list


    # generate list of pseudo legal moves (doesn't check if king goes in check)
    # TODO: create methods for castling (move code from king function), call methods here
    def _get_pseudo_moves(self):

        pseudo_moves = []

        # iterate through chess board adding the moves for each piece owned by side to move
        for y in range(8):        #rank
            for x in range(8):    #file

                # check if current square has a piece owned by the player to move
                if self._board[y][x].isalpha() and self._side_to_move == self._board[y][x].isupper():

                        # call relevant method to get moves for piece at current location
                        # moves generated are returned as a list, extended to moves list
                        piece_function = {
                            'P': self._get_pawn_moves,
                            'N': self._get_knight_moves,
                            'B': self._get_ray_moves,
                            'R': self._get_ray_moves,
                            'Q': self._get_ray_moves,
                            'K': self._get_king_moves
                        }[self._board[y][x].upper()]
                        pseudo_moves.extend(piece_function(y,x))

        # add en passant moves
        pseudo_moves.extend(self._get_ep_moves())

        return pseudo_moves


    def _get_knight_moves(self, y, x):

        knight_moves = []
        # y,z coords of all possible knight moves
        target_list = [(x-2,y+1),
                        (x-1,y+2),
                        (x+1,y+2),
                        (x+2,y+1),
                        (x+2,y-1),
                        (x+1,y-2),
                        (x-1,y-2),
                        (x-2,y-1)]

        for target in target_list:
            # verify target square is not OOB
            if target[0] in range(0,8) and target[1] in range(0,8):
                # verify target is not friendly piece
                if self._board[target[1]][target[0]].isspace() or self._side_to_move != self._board[target[1]][target[0]].isupper():
                    # add move as 4 tuple, (src x, src y, dest x, dest y)
                    knight_moves.append((x,y, target[0], target[1]))

        return knight_moves


    # directional moves (for bishop, rook, and queen)
    def _get_ray_moves(self, y, x):

        ray_moves = []
        # do we calculate these directions?
        cardinal = False
        diagonal = False


        # enable all directions
        if self._board[y][x].upper() == 'Q':
            cardinal = True
            diagonal = True
        # enable only cardinal directions
        elif self._board[y][x].upper() == 'R': cardinal = True
        # enable only diagonal directions (must be bishop)
        else: diagonal = True

        # get cardinal moves (north east south west)
        if cardinal:
            # north moves
            for i in range(y+1, 8):
                # skip if piece on 8th rank
                if i > 7: break
                # use helper to add move if applicable (done in helper method), then break from loop if applicable
                if not self._ray_move_helper(ray_moves, y, x, i, x): break

            # south moves
            for i in range(y-1, -1, -1):
                # skip if piece on 1st rank
                if i < 0: break
                if not self._ray_move_helper(ray_moves, y, x, i, x): break

            # east moves
            for j in range(x+1, 8):
                # skip if piece on h file
                if j > 7 : break
                if not self._ray_move_helper(ray_moves, y, x, y, j): break

            # west moves
            for j in range(x-1, -1, -1):
                # skip if piece on h file
                if j < 0 : break
                if not self._ray_move_helper(ray_moves, y, x, y, j): break

        # get diagonal moves (ne nw se sw)
        if diagonal:

            # north east
            for i in range(y+1,8):
                # calculate target x
                # i-y = raw distance from piece
                j = x + (i - y)
                # skip if piece on board edge
                if i > 7 or j > 7: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

            # south east
            for i in range(y-1, -1, -1):
                j = x + (y - i)
                if i < 0 or j > 7: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

            # north west
            for i in range(y+1, 8):
                j = x - (i - y)
                if i > 7 or j < 0: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

            # south west
            for i in range(y-1, -1, -1):
                j = x - (y - i)
                if i < 0 or j < 0: break
                if not self._ray_move_helper(ray_moves, y, x, i, j): break

        return ray_moves


    def _get_king_moves(self, y, x):
        king_moves = []

        target_list = [(x,y+1),
                        (x+1,y+1),
                        (x+1,y),
                        (x+1,y-1),
                        (x,y-1),
                        (x-1,y-1),
                        (x-1,y),
                        (x-1,y+1)]


        for target in target_list:
            # verify target square is not OOB
            if target[0] in range(0,8) and target[1] in range(0,8):
                # verify target is not friendly piece
                if self._board[target[1]][target[0]].isspace() or self._side_to_move != self._board[target[1]][target[0]].isupper():
                    # add move as 4 tuple, (src x, src y, dest x, dest y)
                    king_moves.append((x,y, target[0], target[1]))


        # castling moves
        # TODO: CHECK IF SQUARES ARE ATTACKED/CHECKING (cannot castle if in check), move to other function?
        # white
        if self._side_to_move:
            # kingside (if true then king and kingside rook haven't moved)
            if self._white_short_castle:
                # verify squares are unoccupied and add move
                if self._board[0][5] == ' ' and self._board[0][6] == ' ': king_moves.append((4,0,6,0))
            # queenside
            if self._white_long_castle:
                if self._board[0][2] == ' ' and self._board[0][3] == ' ': king_moves.append((4,0,2,0))

        # black
        else:
            if self._black_short_castle:
                if self._board[7][5] == ' ' and self._board[7][6] == ' ': king_moves.append((4,7,6,7))
            if self._black_long_castle:
                if self._board[7][2] == ' ' and self._board[7][3] == ' ': king_moves.append((4,7,2,7))


        return king_moves


    def _get_pawn_moves(self, y, x):
        pawn_moves = []

        # white pawns
        if self._side_to_move:
            # non capture moves
            if self._board[y + 1][x] == ' ':
                # normal move forward
                pawn_moves.append((x, y, x, y+1))
                # double first move
                if y == 1 and self._board[y + 2][x] == ' ': pawn_moves.append((x, y, x, y+2, 'd'))
            # capture moves
            if x > 0 and self._board[y + 1][x - 1].islower(): pawn_moves.append((x, y, x-1, y+1))
            if x < 7 and self._board[y + 1][x + 1].islower(): pawn_moves.append((x, y, x+1, y+1))


        # black pawns
        else:
            # non capture moves
            if self._board[y - 1][x] == ' ':
                # normal move forward
                pawn_moves.append((x, y, x, y-1))
                # double first move
                if y == 6 and self._board[y - 2][x] == ' ': pawn_moves.append((x, y, x, y-2, 'd'))
            # capture moves
            if x > 0 and self._board[y - 1][x - 1].isalpha() and self._board[y - 1][x - 1].isupper(): pawn_moves.append((x, y, x-1, y-1))
            if x < 7 and self._board[y - 1][x + 1].isalpha() and self._board[y - 1][x + 1].isupper(): pawn_moves.append((x, y, x+1, y-1))

        # add promotion moves
        for i in range(0, len(pawn_moves)):
            if ((pawn_moves[i][3] == 7 and self._side_to_move) or (pawn_moves[i][3] == 0 and not self._side_to_move)) and len(pawn_moves[i]) != 5:
                pawn_moves[i] = (pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'q')
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'r'))
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'b'))
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'n'))


        return pawn_moves


    # assumes _ep_square is valid if not None (meaning if its white to move then ep target y MUST = 5)
    # ep target square format: 0 based xy coordinate as 2 tuple
    def _get_ep_moves(self):

        # skip if no ep target square
        if self._ep_square is None: return []

        ep_moves = []

        # just to keep things looking readable
        ep_x = self._ep_square[0]

        # white ep moves
        if self._side_to_move:
            # check left
            if ep_x > 0 and self._board[4][ep_x-1] == 'P':
                ep_moves.append((ep_x-1, 4, ep_x, 5, "ep"))
            # check right
            if ep_x < 7 and self._board[4][ep_x+1] == 'P':
                ep_moves.append((ep_x+1, 4, ep_x, 5, "ep"))

        # black ep moves
        else:
            if ep_x > 0 and self._board[3][ep_x-1] == 'p':
                ep_moves.append((ep_x-1, 3, ep_x, 2, "ep"))
            if ep_x < 7 and self._board[3][ep_x+1] == 'p':
                ep_moves.append((ep_x+1, 3, ep_x, 2, "ep"))

        return ep_moves


    # return false if the move leaves the movers king in check, true otherwise
    def _legal_move_check(self, move):

        # create copy of position
        position_copy = ChessPosition(copy.deepcopy(self._board),
                                        self._side_to_move,
                                        self._white_long_castle,
                                        self._white_short_castle,
                                        self._black_long_castle,
                                        self._black_short_castle,
                                        self._ep_square)

        # make the proposed move on the board copy
        position_copy._make_move(move)

        # iterate through move list for opposite side after making the proposed move,
        # if any moves captures a king then the proposed move is not legal
        # note, for check validation, opponents pseudo legal moves are fine
        for test_move in position_copy._get_pseudo_moves():
            if position_copy._board[test_move[3]][test_move[2]].upper() == 'K':
                return False

        # return true if the move is fully legal
        return True


    # helper method for calculating ray moves
    # adds move to move list if applicable then returns bool if should keep searching or not
    # y,x = src square, r,f = dest square
    def _ray_move_helper(self, move_list, y, x, r, f):


        # empty square, add move and keep searching
        if self._board[r][f] == ' ':
            move_list.append((x,y,f,r))
            return True

        # friendly piece, don't add move and end search
        if self._side_to_move == self._board[r][f].isupper(): return False

        # enemy piece, add move and end search
        move_list.append((x,y,f,r))
        return False
