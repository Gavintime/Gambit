"""Main File of the Gambit GUI."""

import sys
import os
from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QGridLayout
from PyQt6.QtSvgWidgets import QSvgWidget
from chess_position import ChessPosition


# get directories
path = os.path.dirname(os.path.abspath(__file__))
res_path = os.path.join(path, 'res')

piece_images = {
    'R': "wr.svg",
    'r': "br.svg",
    'B': "wb.svg",
    'b': "bb.svg",
    'Q': "wq.svg",
    'q': "bq.svg",
    'K': "wk.svg",
    'k': "bk.svg",
    'N': "wn.svg",
    'n': "bn.svg",
    'P': "wp.svg",
    'p': "bp.svg",
    ' ': ""
}


class GambitWindow(QMainWindow):
    """Create main window of the Gambit GUI."""

    def __init__(self, position):
        """Create main window, then create the elements."""
        super().__init__()

        # game position
        self.position = position

        self.src_click = None
        self.dest_click = None

        # setup window properties
        self.setGeometry(800, 300, 820, 820)
        self.setFixedSize(820, 820)
        # self.setMinimumSize(300, 300)
        # self.setMaximumSize(1000, 1000)
        self.setWindowTitle("Gambit")
        self.setWindowIcon(QIcon(os.path.join(res_path, "window_icon.svg")))

        # add widgets to window
        self.initUI()

        # focus window
        self.activateWindow()

    def initUI(self):
        """Create the elements of the GUI."""
        # create required central widget (game board)
        self.board = QWidget()
        self.board.setStyleSheet('background-color: #684a31')
        self.setCentralWidget(self.board)

        # create grid for board to hold each square
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.heightForWidth(1)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.board.setLayout(self.grid)

        # add each square and piece to the grid
        for x in range(8):
            for y in range(8):

                square = GambitWindow.SquareWidget(self, y, 7-x)
                square.setFixedSize(100, 100)
                # set checkerboard pattern
                if (x + y) % 2 != 0:
                    square.setStyleSheet('background-color: #B58863') # dark
                else: square.setStyleSheet('background-color: #F0D9B5') # light

                self.grid.addWidget(square, x, y)

                # add piece to square if not empty
                pos_board = self.position.board[::-1]   # need to reverse board
                if piece_images[pos_board[x][y]] != "":
                    piece_image = QSvgWidget(os.path.join(res_path, piece_images[pos_board[x][y]]))
                    piece_image.setFixedSize(90, 90)
                    piece_image.setParent(square)

                    # move piece to center of square
                    p = square.geometry().center()
                    p -= QRect(QPoint(0, 0), piece_image.size()).center()
                    piece_image.move(p)


    class SquareWidget(QLabel):

        def __init__(self, win, x, y):
            super().__init__()
            self.win = win
            self.x = x
            self.y = y

        # TODO: CLEAN THIS UP
        def mouseReleaseEvent(self, event):

            if self.win.src_click is None:
                self.win.src_click = (self.x, self.y)

                # highlight square
                # TODO: highlight legal moves
                if (self.x + self.y) % 2 != 0:
                    self.setStyleSheet('background-color: #646F40') # dark
                else: self.setStyleSheet('background-color: #829769') # light

            elif self.win.dest_click is None:
                self.win.dest_click = (self.x, self.y)

                # TODO: select different square immediately if dest square is not legal

                src = self.win.src_click
                dest = self.win.dest_click

                move = ''.join(str(x) for x in src + dest)
                move = (chr(int(move[0]) + 97)
                       + str(int(move[1]) + 1)
                       + chr(int(move[2]) + 97)
                       + str(int(move[3]) + 1))

                # add promotion (only queen for now)
                if (self.win.position.board[src[1]][src[0]].upper() == 'P'
                        and dest[1] in (0,7)):
                    move = move + 'q'

                # TODO: use proper update method
                self.win.position.move(move)
                self.win.initUI()
                self.win.src_click = self.win.dest_click = None

            event.accept()


def main():
    """Start the GUI."""
    # create position from fen
    position = ChessPosition.import_fen(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    if not position:
        print("Invalid FEN, exiting...")
        sys.exit(1)

    app = QApplication(sys.argv)
    win = GambitWindow(position)

    win.show()
    # exit program when closing window
    sys.exit(app.exec())


if __name__ == '__main__': main()
