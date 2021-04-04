import re

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


    # input: move as 4-5 tuple (as 0 based x y coordinates)
    # makes the give move and updated the board/other variables as nessacariy
    # assumes given move is legal (for external use, use move(self) function)
    # TODO: CASTLING, PROMOTION, EN PASSANT 
    def _make_move(self, move):


        # move src square piece to destination square
        # promotion move
        if len(move) == 5: 
            self._board[move[3]][move[2]] = move[4]
            # promotion choice comes in lowercase, make uppercase if its whites move
            if self._side_to_move: self._board[move[3]][move[2]] = self._board[move[3]][move[2]].upper()

        # standard move (or en passant?)
        else: self._board[move[3]][move[2]] = self._board[move[1]][move[0]]

        # remove src piece from src square
        self._board[move[1]][move[0]] = ' '


        # disable castling rights if rook isnt on origin square (for any move)
        # this covers the case of rook moving, and rook being captured
        if self._board[0][0] != 'R': self._white_queen_castle = False
        if self._board[0][7] != 'R': self._white_king_castle = False
        if self._board[7][0] != 'r': self._black_queen_castle = False
        if self._board[7][7] != 'r': self._black_king_castle = False
        

        # give turn to opposite side
        self._side_to_move = not self._side_to_move


        return

    # input: uci style move as string
    # verifys move is legal by generating legal moves and seeing if move given is in list
    # if move is legal, _make_move(self, move) is called, which actually makes the move on the board
    # wrapper function for _make_move(self, move)
    # return boolean denoting if move was legal (and thus moved) or not
    def move(self, move):
        
        # verify matches uci format
        if re.fullmatch("([a-h][1-8]){2}[qrbn]?", move) != None:
            # convert string move to tuple format move with 0 based xy coordinates
            # first converted to list, add promotion if needed, then convert to actual tuple
            move_tuple = [ord(move[0])-97,ord(move[1])-49,ord(move[2])-97,ord(move[3])-49]
            if len(move) == 5: move_tuple.append(move[4])
            move_tuple = tuple(move_tuple)

            # make the move if it is a valid move
            if move_tuple in self.get_legal_moves(): 
                self._make_move(move_tuple)
                return True

        return False


    def get_legal_moves(self):

        # empty the move list
        self._move_list = []


        # iterate through chess board
        for y in range(8):        #rank
            for x in range(8):    #file

                # check if piece
                if self._board[y][x].isalpha():
                    # if side to move and piece ownership are the same
                    if self._side_to_move == self._board[y][x].isupper():

                        # call relevant method to get moves for piece at current location
                        # moves generated are returned as a list, extended to moves list
                        # commented code was calling _get_pawn_moves for all piece types in addition to their proper function call for some strage reason
                        # self._move_list.extend({
                        #     'P': self._get_pawn_moves(y,x),
                        #     'N': self._get_knight_moves(y,x),
                        #     'B': self._get_ray_moves(y,x),
                        #     'R': self._get_ray_moves(y,x),
                        #     'Q': self._get_ray_moves(y,x),
                        #     'K': self._get_king_moves(y,x)
                        # }[self._board[y][x].upper()])

                        temp_piece = self._board[y][x].upper()
                        if temp_piece == 'P': self._move_list.extend(self._get_pawn_moves(y,x))
                        elif temp_piece == 'N': self._move_list.extend(self._get_knight_moves(y,x))
                        elif temp_piece == 'B': self._move_list.extend(self._get_ray_moves(y,x))
                        elif temp_piece == 'R': self._move_list.extend(self._get_ray_moves(y,x))
                        elif temp_piece == 'Q': self._move_list.extend(self._get_ray_moves(y,x))
                        elif temp_piece == 'K': self._move_list.extend(self._get_king_moves(y,x))
                        else: print("ERROR: INVALID PIECE")


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
            # kingside (if true then king and kingside rook havent moved)
            if self._white_king_castle:
                # verify squares are unoccupied and add move
                if self._board[0][5] == ' ' and self._board[0][6] == ' ': king_moves.append((4,0,6,0))
            # queenside
            if self._white_queen_castle: 
                if self._board[0][2] == ' ' and self._board[0][3] == ' ': king_moves.append((4,0,2,0))

        # black
        else:
            if self._black_king_castle:
                if self._board[7][5] == ' ' and self._board[7][6] == ' ': king_moves.append((4,7,6,7))
            if self._black_queen_castle: 
                if self._board[7][2] == ' ' and self._board[7][3] == ' ': king_moves.append((4,7,2,7))


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
            if x < 7 and self._board[y - 1][x + 1].isalpha() and self._board[y - 1][x + 1].isupper(): pawn_moves.append((x, y, x+1, y-1))

        # add promotion moves
        # TODO: optimize me?
        for i in range(0, len(pawn_moves)):
            if ((pawn_moves[i][3] == 7 and self._side_to_move) or (pawn_moves[i][3] == 0 and not self._side_to_move)) and len(pawn_moves[i]) != 5:
                pawn_moves[i] = (pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'q')
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'r'))
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'b'))
                pawn_moves.append((pawn_moves[i][0],pawn_moves[i][1], pawn_moves[i][2], pawn_moves[i][3], 'n'))




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
