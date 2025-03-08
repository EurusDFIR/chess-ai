#src/ai/opening_book.py
import chess.polyglot

class OpeningBook:
    def __init__(self, book_path):
        self.book_path = book_path

    def get_move(self, board):
        with chess.polyglot.open_reader(self.book_path) as reader:
            try:
                entry = reader.find(board)
                return entry.move
            except IndexError:
                return None