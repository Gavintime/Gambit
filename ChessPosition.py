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


    def get_knight_moves(self):
        knight_moves = []

        for j in range(0,8):        #rank
            for i in range(0,8):    #file
                # white knights on white's turn
                if self._side_to_move and self._board[j][i] == 'N':
                    # list of coords current knight can move on, with bool if is a capture
                    target_list = [[i-2,j+1,False],
                                    [i-1,j+2,False],
                                    [i+1,j+2,False],
                                    [i+2,j+1,False],
                                    [i+2,j-1,False],
                                    [i+1,j-2,False],
                                    [i-1,j-2,False],
                                    [i-2,j-1,False]]

                    for x in range(0,8):
                        # remove out of bound targets
                        if target_list[x][0] not in range(0,8) or target_list[x][1] not in range(0,8):
                            target_list[x] = None
                        # remove targets occupied by friendly pieces
                        elif self._board[target_list[x][1]][target_list[x][0]].isupper():
                            target_list[x] = None
                        # list as capture if capturing enemy piece
                        elif self._board[target_list[x][1]][target_list[x][0]].islower():
                            target_list[x][2] = True
                        # TODO: CHECK FOR MOVE AMBIGUITY

                    # convert target list to tokenized moves, then the tokenized moves to knight moves list
                    for target in target_list:
                        if target is not None:
                            tokenized_knight_move = ["KNIGHT"]
                            if target[2]: tokenized_knight_move.append("CAPTURE")
                            tokenized_knight_move.append(chr(target[0]+97) + chr(target[1]+49) + "_SQUARE")
                            # TODO: add check/mate, probably in another function
                            knight_moves.append(tokenized_knight_move)

        return knight_moves


    def get_bishop_moves(self):
        bishop_moves = []
        return bishop_moves


    def get_rook_moves(self):
        rook_moves = []
        return rook_moves


    def get_queen_moves(self):
        queen_moves = []
        return queen_moves


    def get_king_moves(self):
        king_moves = []
        return king_moves


    def get_pawn_moves(self):
        pawn_moves = []
        return pawn_moves


    #generate list of legal moves for the current board position
    def get_legal_moves(self):

        legal_moves = [].extend(self.get_knight_moves())
        return legal_moves
