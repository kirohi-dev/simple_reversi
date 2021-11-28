import math
from typing import List

import numpy as np
import PySimpleGUI as sg


class Engine:
    def __init__(self, white, black, rows, cols) -> None:
        self.board = None
        self.white = white
        self.black = black
        self.rows = rows
        self.cols = cols
        self.turn = white

    def get_board(self):
        return self.board

    def create_board(self):
        board = np.zeros(self.rows * self.cols).astype(np.int32)
        board = board.reshape(self.rows, self.cols).tolist()
        board[3][3] = self.white
        board[3][4] = self.black
        board[4][3] = self.black
        board[4][4] = self.white
        self.board = board
        return board

    def update_board(self, row, column):
        # 入れ替えを行う
        self.flip(row, column)
        self.turn = self.opponent_turn()
        return self.board

    def flip(self, row, column):
        print(f"turn: {self.turn}")
        print(f"row: {row}, column: {column}")
        for flip_len, vector in self.check_flippable([row, column]):
            reference_row = row
            reference_column = column
            print(f"flip_len {flip_len}, vector: {vector}")
            while flip_len:
                self.board[reference_row][reference_column] = self.turn
                flip_len -= 1
                reference_row += vector[0]
                reference_column += vector[1]
        print("------------------------------------------")

    def get_piece(self, coord: List[int]):
        return self.board[coord[0]][coord[1]]

    def opponent_turn(self):
        return self.black if self.turn == self.white else self.white

    def get_coords_on_ray(self, reference: List[int], vector: List[int]):
        pieces = []
        while reference[0] < 8 and reference[0] >= 0 and reference[1] < 8 and reference[1] >= 0:
            pieces.append([reference[0], reference[1]])
            reference[0] += vector[0]
            reference[1] += vector[1]
        return pieces

    def check_flippable(self, reference: List[int]):
        vectors = [[round(math.cos(math.pi * n / 4)), round(math.sin(math.pi * n / 4))] for n in list(range(8))]
        flippable_list = []
        for coords, vector in [(self.get_coords_on_ray(reference[:], vector), vector) for vector in vectors]:
            pieces = [self.get_piece(coord) for coord in coords]
            flip_len = self.nflippable(pieces)
            if flip_len:
                flippable_list.append((flip_len, vector))
        if len(flippable_list) != 0:
            return flippable_list
        return None

    def nflippable(self, pieces):
        if len(pieces) < 3:
            return 0
        flip_len = 1
        if pieces[1] == self.opponent_turn():
            for piece in pieces[1:]:
                if piece == 0:
                    return 0
                elif piece == self.turn:
                    return flip_len
                else:
                    flip_len += 1
        return 0

    def get_flippable_coords(self):
        coords = []
        for r, columns in enumerate(self.board):
            for c, value in enumerate(columns):
                if value == 0:
                    if self.check_flippable([r, c]):
                        coords.append([r, c])
        return coords

    def pass_turn(self):
        self.turn = self.opponent_turn()
        flippable_coords = self.get_flippable_coords()
        if len(flippable_coords) == 0:
            return False
        return True

    def finish(self):
        white_pieces = 0
        black_pieces = 0
        for columns in self.board:
            for v in columns:
                if v == self.black:
                    black_pieces += 1
                if v == self.white:
                    white_pieces += 1
        if white_pieces == black_pieces:
            return "draw"
        elif white_pieces > black_pieces:
            return "white"
        else:
            return "black"


class Field:
    def __init__(self) -> None:
        pass

    def green_field(self, row, column, disabled):
        return self._set_color(row, column, "green", disabled)

    def black_field(self, row, column):
        return self._set_color(row, column, "black", True)

    def white_field(self, row, column):
        return self._set_color(row, column, "white", True)

    def _set_color(self, row, column, color, disabled=False):
        return sg.Button(
            "", key=(row, column), size=(4, 4), pad=(0, 0), button_color=("yellow", color), disabled=disabled
        )


class Reversi:
    ROWS = 8
    COLS = 8
    WHITE = 1
    BLACK = 2

    def __init__(self) -> None:
        self.field = Field()
        self.engine = Engine(self.WHITE, self.BLACK, self.ROWS, self.COLS)

    def create_layout(self):
        layout = []
        board = self.engine.create_board()
        flippable_coords = self.engine.get_flippable_coords()
        for r, columns in enumerate(board):
            layout_row = []
            for c, v in enumerate(columns):
                if v == 0:
                    disable = [r, c] not in flippable_coords
                    layout_row.append(self.field.green_field(r, c, disable))
                elif v == self.WHITE:
                    layout_row.append(self.field.white_field(r, c))
                else:
                    layout_row.append(self.field.black_field(r, c))
            layout.append(layout_row)
        return layout

    def update_layout(self, window, row=None, column=None):
        board = None
        if row is not None:
            board = self.engine.update_board(row, column)
        else:
            board = self.engine.get_board()
        flippable_coords = self.engine.get_flippable_coords()
        if len(flippable_coords) == 0:
            is_finish = self.engine.pass_turn()
            if not is_finish:
                return self.engine.finish()
            sg.popup("turn change")
            self.update_layout(window)
        for r, columns in enumerate(board):
            layout_row = []
            for c, v in enumerate(columns):
                window[(r, c)].update()
                if v == 0:
                    disable = [r, c] not in flippable_coords
                    window[(r, c)].update("", button_color=("yellow", "green"), disabled=disable)
                elif v == self.WHITE:
                    window[(r, c)].update("", button_color=("yellow", "white"), disabled=True)
                    layout_row.append(self.field.white_field(r, c))
                else:
                    window[(r, c)].update("", button_color=("yellow", "black"), disabled=True)
                    layout_row.append(self.field.black_field(r, c))

    def main_loop(self):
        layout = self.create_layout()
        window = sg.Window("simple reversi", layout)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            result = self.update_layout(window, event[0], event[1])
            if result:
                sg.popup(result)

        window.close()


reversi = Reversi()
reversi.main_loop()
