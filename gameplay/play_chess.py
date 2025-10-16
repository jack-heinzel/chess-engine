import sys
import chess
import chess.svg
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QInputDialog, QMessageBox
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt

class ChessGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Chess")
        self.board = chess.Board()
        self.selected_square = None
        self.board_size = 480

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.svg_widget = QSvgWidget()
        self.svg_widget.setFixedSize(self.board_size, self.board_size)
        self.svg_widget.mousePressEvent = self.handle_click
        layout.addWidget(self.svg_widget)

        self.update_board()

    def update_board(self, highlight=None):
        svg = chess.svg.board(
            self.board,
            size=self.board_size,
            squares=[highlight] if highlight else None,
            lastmove=self.board.move_stack[-1] if self.board.move_stack else None
        )
        self.svg_widget.load(svg.encode("utf-8"))
        self.svg_widget.repaint()  # Force redraw

    def handle_click(self, event):
        file = int(event.position().x() * 8 / self.board_size)
        rank = 7 - int(event.position().y() * 8 / self.board_size)
        sq = chess.square(file, rank)

        if self.selected_square is None:
            self.selected_square = sq
            self.update_board(highlight=sq)
        else:
            move = chess.Move(self.selected_square, sq)
            piece = self.board.piece_at(self.selected_square)

            # Promotion
            if piece and piece.piece_type == chess.PAWN and chess.square_rank(sq) in [0,7]:
                promotion, ok = QInputDialog.getItem(
                    self, "Promotion", "Promote to:", ["Queen","Rook","Bishop","Knight"], editable=False
                )
                if ok:
                    promo_map = {"Queen":chess.QUEEN,"Rook":chess.ROOK,"Bishop":chess.BISHOP,"Knight":chess.KNIGHT}
                    move.promotion = promo_map[promotion]

            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.update_board()
                self.check_game_end()
            else:
                self.selected_square = None
                self.update_board()

    def check_game_end(self):
        if self.board.is_checkmate():
            QMessageBox.information(self, "Game Over", "Checkmate!")
        elif self.board.is_stalemate():
            QMessageBox.information(self, "Game Over", "Stalemate!")
        elif self.board.can_claim_fifty_moves():
            QMessageBox.information(self, "Game Over", "50-move rule draw!")
        elif self.board.can_claim_threefold_repetition():
            QMessageBox.information(self, "Game Over", "Threefold repetition draw!")
        elif self.board.is_insufficient_material():
            QMessageBox.information(self, "Game Over", "Draw by insufficient material!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessGUI()
    window.show()
    sys.exit(app.exec())
