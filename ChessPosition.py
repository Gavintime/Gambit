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


    # generate list of moves for knights of the current player, does not check for capture or friendly pawns
    # only verifies move locations are on the board
    def get_knight_moves(self):

        knight_moves = []

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
                            knight_moves.append((target[0], target[1], "KNIGHT"))

        return knight_moves


    def get_bishop_moves(self):
        bishop_moves = []


        for y in range(0,8):        #rank
            for x in range(0,8):    #file
                if self._side_to_move and self._board[y][x] == 'B':

                    # find northeast moves
                    for i in range(x+1, 8):
                        # skip if on board edge
                        if i > 7 or y + i - x > 7: break
                        # empty square, add move and keep searching
                        elif self._board[y + i - x][i] == ' ':
                            bishop_moves.append((i,y + i - x,"BISHOP"))
                        # friendly piece, end search
                        elif self._board[y + i - x][i].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[y + i - x][i].islower():
                            bishop_moves.append((i,y + i - x,"BISHOP"))
                            break

                    # find southeast moves
                    for i in range(x+1, 8):
                        # skip if on board edge
                        if i > 7 or y - i + x < 0 : break
                        # empty square, add move and keep searching
                        elif self._board[y - i + x][i] == ' ':
                            bishop_moves.append((i,y - i + x,"BISHOP"))
                        # friendly piece, end search
                        elif self._board[y - i + x][i].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[y - i + x][i].islower():
                            bishop_moves.append((i,y - i + x,"BISHOP"))
                            break

                    # find northwest moves
                    for i in range(x-1, -1, -1):
                        # skip if on board edge
                        if i < 0 or y + x - i > 7: break
                        # empty square, add move and keep searching
                        elif self._board[y + x - i][i] == ' ':
                            bishop_moves.append((i,y + x - i,"BISHOP"))
                        # friendly piece, end search
                        elif self._board[y + x - i][i].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[y + x - i][i].islower():
                            bishop_moves.append((i,y + x - i,"BISHOP"))
                            break

                    # find southwest moves
                    for i in range(x-1, -1, -1):
                        # skip if on board edge
                        if i < 0 or y - x + i < 0: break
                        # empty square, add move and keep searching
                        elif self._board[y - x + i][i] == ' ':
                            bishop_moves.append((i,y - x + i,"BISHOP"))
                        # friendly piece, end search
                        elif self._board[y - x + i][i].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[y - x + i][i].islower():
                            bishop_moves.append((i,y - x + i,"BISHOP"))
                            break

        return bishop_moves


    def get_rook_moves(self):
        rook_moves = []

        for y in range(0,8):        #rank
            for x in range(0,8):    #file
                if self._side_to_move and self._board[y][x] == 'R':

                    # find valid north moves
                    for i in range(y+1, 8):
                        # skip if on edge of board
                        if i > 7: break
                        # empty square, add move and keep searching
                        elif self._board[i][x] == ' ':
                            rook_moves.append((x,i,"ROOK"))
                        # friendly piece, end search
                        elif self._board[i][x].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[i][x].islower():
                            rook_moves.append((x,i,"ROOK"))
                            break

                    # find valid south moves
                    for i in range(y-1, -1, -1):
                        # skip if on edge of board
                        if i < 0:
                            break
                        # empty square, add move and keep searching
                        elif self._board[i][x] == ' ':
                            rook_moves.append((x,i,"ROOK"))
                        # friendly piece, end search
                        elif self._board[i][x].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[i][x].islower():
                            rook_moves.append((x,i,"ROOK"))
                            break

                    # find valid east moves
                    for i in range(x+1, 8):
                        # skip if on edge of board
                        if i > 7: break
                        # empty square, add move and keep searching
                        elif self._board[y][i] == ' ':
                            rook_moves.append((i,y,"ROOK"))
                        # friendly piece, end search
                        elif self._board[y][i].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[y][i].islower():
                            rook_moves.append((i,y,"ROOK"))
                            break

                    # find valid west moves
                    for i in range(x-1, -1,-1):
                        # skip if on edge of board
                        if i < 0: break
                        # empty square, add move and keep searching
                        elif self._board[y][i] == ' ':
                            rook_moves.append((i,y,"ROOK"))
                        # friendly piece, end search
                        elif self._board[y][i].isupper(): break
                        # enemy piece, add move and end search
                        elif self._board[y][i].islower():
                            rook_moves.append((i,y,"ROOK"))
                            break

        return rook_moves


    def get_queen_moves(self):
        queen_moves = []
        return queen_moves


    # does not check for castling
    def get_king_moves(self):
        king_moves = []


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
                            king_moves.append([target[0], target[1], "KING"])

                    # can end after finding first (only) king
                    return king_moves

        # error if never found the king
        raise Exception()


    def get_pawn_moves(self):
        pawn_moves = []
        return pawn_moves


    #generate list of legal moves for the current board position
    def get_legal_moves(self):

        # list of moves each as its own list
        moves = []
        moves.extend(self.get_bishop_moves())
        tokenized_legal_moves = []


        # validate move then tokenize it
        for move in moves:

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
