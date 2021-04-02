class ChessPosition:

    # TODO: add en passant storage, counter for repetition
    def __init__(self, board, side_to_move, white_queen_castle, white_king_castle, black_queen_castle, black_king_castle):
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
        self._white_queen_castle = white_queen_castle
        self._white_king_castle = white_king_castle
        self._black_queen_castle = black_queen_castle
        self._black_king_castle = black_king_castle

        # list of valid legal moves for the current position
        # each move is stored in token form and long algebraic notation
        self._move_list = []


    def get_legal_moves(self):

        # empty the moves list
        self._move_list = []

        # iterate through chess board
        for y in range(8):        #rank
            for x in range(8):    #file

                # check if piece
                if self._board[y][x].isalpha():
                    # if side to move and piece ownership are the same
                    if (self._side_to_move == self._board[y][x].isupper()):

                        # call relevant method to get moves for piece at current location
                        # moves generated are returned as a list, extended to moves list
                        self._move_list.extend({
                            'P': self._get_pawn_moves(y,x),
                            'N': self._get_knight_moves(y,x),
                            'B': self._get_ray_moves(y,x),
                            'R': self._get_ray_moves(y,x),
                            'Q': self._get_ray_moves(y,x),
                            'K': self._get_king_moves(y,x)
                        }.get(self._board[y][x].upper()))


        return self._move_list


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


    # TODO: finish me
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


        return king_moves


    # TODO: en passant
    def _get_pawn_moves(self, y, x):
        pawn_moves = []

        # white pawns
        if self._side_to_move:
            # non capture moves
            if self._board[y + 1][x] == ' ':
            # normal move forward
                pawn_moves.append((x, y, x, y+1))
            # double first move
                if y == 1 and self._board[y + 2][x] == ' ': pawn_moves.append((x, y, x, y+2))

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
                if y == 6 and self._board[y - 2][x] == ' ': pawn_moves.append((x, y, x, y-2))
            # capture moves
            if x > 0 and self._board[y - 1][x - 1].isalpha() and self._board[y - 1][x - 1].isupper(): pawn_moves.append((x, y, x-1, y-1))
            if x < 7 and self._board[y - 1][x - 1].isalpha() and self._board[y - 1][x + 1].isupper(): pawn_moves.append((x, y, x+1, y-1))

        # add promotion moves
        # TODO: optimize me?
        for i in range(0, len(pawn_moves)):
            if ((pawn_moves[i][3] == 7 and self._side_to_move) or (pawn_moves[i][3] == 0 and not self._side_to_move)) and len(pawn_moves[i]) != 5:
                pawn_moves[i] = (pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'Q')
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'R'))
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'B'))
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'N'))




        return pawn_moves


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
