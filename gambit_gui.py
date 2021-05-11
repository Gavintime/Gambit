"""Main File of the Gambit GUI."""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtSvg import QSvgWidget


# get directories
path = os.path.dirname(os.path.abspath(__file__))
res_path = os.path.join(path, 'res')


class GambitWindow(QMainWindow):
    """Create main window of the Gambit GUI."""

    def __init__(self):
        """Create main window, then create the elements."""
        super().__init__()

        # setup window properties
        self.setGeometry(800, 300, 800, 800)
        # self.setFixedSize(800, 800)
        self.setMinimumSize(300, 300)
        self.setMaximumSize(1000, 1000)
        self.setWindowTitle("Gambit")
        self.setWindowIcon(QIcon(os.path.join(res_path, "window_icon.svg")))

        # add widgets to window
        self.initUI()

    def initUI(self):
        """Create the elements of the GUI."""
        # create required central widget (game board)
        self.board = QWidget()
        self.setCentralWidget(self.board)

        # create board grid to hold each square
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.heightForWidth(1)
        self.board.setLayout(self.grid)

        # create each board square and add it to the board
        start_board = [list('RNBQKBNR'),
                       list('PPPPPPPP'),
                       list('        '),
                       list('        '),
                       list('        '),
                       list('        '),
                       list('pppppppp'),
                       list('rnbqkbnr')]
        start_board.reverse()

        # set piece image
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

        # add each square and piece to the grid
        for x in range(8):
            for y in range(8):

                square = QWidget()
                square.setFixedSize(100, 100)
                # set checkerboard pattern
                if (x + y) % 2 != 0:
                    square.setStyleSheet('background-color: #B58863') # light
                else: square.setStyleSheet('background-color: #F0D9B5') # dark
                self.grid.addWidget(square, x, y)

                # add piece to square if not empty
                if piece_images[start_board[x][y]] != "":
                    piece_image = QSvgWidget(os.path.join(res_path, piece_images[start_board[x][y]]))
                    piece_image.setFixedSize(91, 91)
                    piece_image.setParent(square)

                    # move piece to center of square
                    p = square.geometry().center() - QRect(QPoint(1, 0), piece_image.size()).center()
                    piece_image.move(p)




def main():
    """Start the GUI."""
    # start gui app
    app = QApplication(sys.argv)
    win = GambitWindow()

    # display window
    win.show()
    # exit program when closing window
    sys.exit(app.exec_())


if __name__ == '__main__': main()
