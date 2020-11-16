class ChessPosition:

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

        #internal untokenized move list
        self._move_list = []


    # helper method to add move to movelist if not a friendly square
    # returns true if to continue searching, false otherwise
    def _add_move(self, piece, f, r):
        # empty square, add move and keep searching
        if self._board[r][f] == ' ':
            self._move_list.append((f,r,piece))
            return True
        # friendly piece, end search
        elif self._board[r][f].isupper(): return False
        # enemy piece, add move and end search
        elif self._board[r][f].islower():
            self._move_list.append((f,r,piece))
            return False


    # generate list of moves for knights of the current player, does not check for capture or friendly pawns
    # only verifies move locations are on the board
    def _get_knight_moves(self):

        for y in range(0,8):        #rank
            for x in range(0,8):    #file
                # white knights on white's turn
                if self._side_to_move and self._board[y][x] == 'N':
                    # list of coords current knight can move on
                    target_list = [(x-2,y+1),
                                    (x-1,y+2),
                                    (x+1,y+2),
                                    (x+2,y+1),
                                    (x+2,y-1),
                                    (x+1,y-2),
                                    (x-1,y-2),
                                    (x-2,y-1)]

                    # create move using target if not out of bound and not attacking friendly piece
                    for target in target_list:
                        if target[0] in range(0,8) and target[1] in range(0,8) and not self._board[target[1]][target[0]].isupper():
                            self._move_list.append((target[0], target[1], "KNIGHT"))


    def _get_bishop_moves(self):

        for y in range(0,8):        #rank
            for x in range(0,8):    #file
                if self._side_to_move and self._board[y][x] == 'B':

                    # northeast moves
                    for i in range(x+1, 8):
                        j = y + i - x
                        # skip if on board edge
                        if i > 7 or j > 7: break
                        # add move to list if legal, end search if applicable
                        elif not self._add_move("BISHOP", i, j): break

                    # southeast moves
                    for i in range(x+1, 8):
                        j = y - i + x
                        if i > 7 or j < 0 : break
                        elif not self._add_move("BISHOP", i, j): break

                    # northwest moves
                    for i in range(x-1, -1, -1):
                        j = y + x - i
                        if i < 0 or j > 7: break
                        elif not self._add_move("BISHOP", i, j): break

                    # southwest moves
                    for i in range(x-1, -1, -1):
                        j = y - x + i
                        if i < 0 or j < 0: break
                        elif not self._add_move("BISHOP", i, j): break


    def _get_rook_moves(self):

        for y in range(0,8):        #rank
            for x in range(0,8):    #file
                if self._side_to_move and self._board[y][x] == 'R':

                    # north moves
                    for i in range(y+1, 8):
                        # skip if on edge of board
                        if i > 7: break
                        # add move to list if legal, end search if applicable
                        elif not self._add_move("ROOK", x, i): break

                    # south moves
                    for i in range(y-1, -1, -1):
                        if i < 0: break
                        elif not self._add_move("ROOK", x, i): break

                    # east moves
                    for i in range(x+1, 8):
                        if i > 7: break
                        elif not self._add_move("ROOK", i, y): break

                    # west moves
                    for i in range(x-1, -1,-1):
                        if i < 0: break
                        elif not self._add_move("ROOK", i, y): break


    def _get_queen_moves(self):
        queen_moves = []
        return queen_moves


    # does not check for castling
    def _get_king_moves(self):

        for y in range(0,8):        #rank
            for x in range(0,8):    #file
                # white king on white's turn
                if self._side_to_move and self._board[y][x] == 'K':
                    # list of coords king can move on
                    target_list = [(x,y+1),
                                    (x+1,y+1),
                                    (x+1,y),
                                    (x+1,y-1),
                                    (x,y-1),
                                    (x-1,y-1),
                                    (x-1,y),
                                    (x-1,y+1)]

                    # create move using target if not out of bound and not attacking friendly piece
                    for target in target_list:
                        if target[0] in range(0,8) and target[1] in range(0,8) and not self._board[target[1]][target[0]].isupper():
                            self._move_list.append([target[0], target[1], "KING"])

                    # can end after finding first (only) king
                    return

        # error if never found the king
        raise Exception()

    # TODO: check fo en passant
    def _get_pawn_moves(self):

        for y in range(0,8):        #rank
            for x in range(0,8):    #file
                if self._side_to_move and self._board[y][x] == 'P':

                    # non capture moves
                    if y < 7 and self._board[y + 1][x] == ' ':
                        # normal move forward
                        self._move_list.append((x,y + 1, "PAWN"))
                        # double first move
                        if y == 1 and self._board[y + 2][x] == ' ': self._move_list.append((x,y + 2, "PAWN"))

                    # capture moves
                    if y < 7 and x > 0 and self._board[y + 1][x - 1].islower(): self._move_list.append((x - 1,y + 1, "PAWN"))
                    if y < 7 and x < 7 and self._board[y + 1][x + 1].islower(): self._move_list.append((x + 1,y + 1, "PAWN"))


    #generate list of legal moves for the current board position
    def get_legal_moves(self):

        tokenized_legal_moves = []

        # get moves for each piece type, results are placed in self._move_list, move list is cleared first
        self._move_list = []
        self._get_bishop_moves()
        self._get_knight_moves()
        self._get_rook_moves()
        self._get_king_moves()
        self._get_pawn_moves()
        # self._get_queen_moves()



        # validate move then tokenize it
        for move in self._move_list:

            # TODO: CHECK FOR MOVE AMBIGUITY and putting self in check

            # create tokenized move
            # add piece name
            tokenized_move = [move[2]]
            # add capture token if attacking opponent piece
            if self._board[move[1]][move[0]].islower(): tokenized_move.append("CAPTURE")
            # add square of arrival
            tokenized_move.append(chr(move[0]+97) + chr(move[1]+49) + "_SQUARE")

            # TODO add check/mate tokens

            # add tokenized move to list of tokenized moves
            tokenized_legal_moves.append(tokenized_move)



        return tokenized_legal_moves
