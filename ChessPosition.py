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

        for j in range(0,8):        #rank
            for i in range(0,8):    #file
                # white knights on white's turn
                if self._side_to_move and self._board[j][i] == 'N':
                    # list of coords current knight can move on
                    target_list = [(i-2,j+1),
                                    (i-1,j+2),
                                    (i+1,j+2),
                                    (i+2,j+1),
                                    (i+2,j-1),
                                    (i+1,j-2),
                                    (i-1,j-2),
                                    (i-2,j-1)]

                    # create move using target if not out of bound
                    for target in target_list:
                        if target[0] in range(0,8) and target[1] in range(0,8):
                            knight_moves.append([target[0], target[1], "KNIGHT"])

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


    # does not check for castling
    def get_king_moves(self):
        king_moves = []


        for j in range(0,8):        #rank
            for i in range(0,8):    #file
                # white king on white's turn
                if self._side_to_move and self._board[j][i] == 'K':
                    # list of coords king can move on
                    target_list = [(i,j+1),
                                    (i+1,j+1),
                                    (i+1,j),
                                    (i+1,j-1),
                                    (i,j-1),
                                    (i-1,j-1),
                                    (i-1,j),
                                    (i-1,j+1)]

                    # create move using target if not out of bound
                    for target in target_list:
                        if target[0] in range(0,8) and target[1] in range(0,8):
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
        moves.extend(self.get_king_moves())
        tokenized_legal_moves = []


        # validate move then tokenize it
        for move in moves:
            # skip if moving to friendly piece
            if self._board[move[1]][move[0]].isupper(): continue

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
