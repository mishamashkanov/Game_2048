from PySide6.QtCore import Qt, QRect, QRectF, QSize, QTimer
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QTextOption
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
import random
import os

class Tile:
    def __init__(self, value):
        self.value = value

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2048 Main Menu")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()

        title = QLabel("2048 Game")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_start_light = QPushButton("Start Light Theme")
        btn_start_dark = QPushButton("Start Dark Theme")

        btn_start_light.clicked.connect(lambda: self.start_game(dark=False))
        btn_start_dark.clicked.connect(lambda: self.start_game(dark=True))

        layout.addWidget(btn_start_light)
        layout.addWidget(btn_start_dark)

        self.setLayout(layout)

    def start_game(self, dark):
        self.game = Game2048(darkMode=dark)
        self.game.show()
        self.close()

class Game2048(QWidget):
    def __init__(self, parent=None, boardWidth=340, gridSize=4, darkMode=False):
        super().__init__(parent)
        self.boardWidth = boardWidth
        self.gridSize = gridSize
        self.panelHeight = 80
        self.tileMargin = 16
        self.gridOffsetX = self.tileMargin
        self.gridOffsetY = self.panelHeight + self.tileMargin
        self.gameRunning = False
        self.darkMode = darkMode
        self.setTheme()
        self.setWindowTitle("2048 Game")
        self.scoreRect = QRect(10, 10, 80, self.panelHeight - 20)
        self.hiScoreRect = QRect(100, 10, 80, self.panelHeight - 20)
        self.resetRect = QRectF(190, 10, 80, self.panelHeight - 20)
        self.scoreLabel = QRectF(10, 25, 80, self.panelHeight - 30)
        self.hiScoreLabel = QRectF(100, 25, 80, self.panelHeight - 30)
        self.hiScore = self.loadHiScore()
        self.lastPoint = None
        self.resize(QSize(self.boardWidth, self.boardWidth + self.panelHeight))
        self.reset_game()

    def setTheme(self):
        if self.darkMode:
            self.backgroundBrush = QBrush(QColor(30, 30, 30))
            self.brushes = {
                0: QBrush(QColor(60, 60, 60)),
                1: QBrush(QColor(100, 100, 100)),
                2: QBrush(QColor(70, 130, 180)),
                4: QBrush(QColor(60, 179, 113)),
                8: QBrush(QColor(218, 112, 214)),
                16: QBrush(QColor(255, 140, 0)),
                32: QBrush(QColor(255, 99, 71)),
                64: QBrush(QColor(255, 69, 0)),
                128: QBrush(QColor(255, 215, 0)),
                256: QBrush(QColor(255, 255, 0)),
                512: QBrush(QColor(255, 255, 102)),
                1024: QBrush(QColor(255, 255, 153)),
                2048: QBrush(QColor(255, 255, 204)),
            }
            self.lightPen = QPen(QColor(230, 230, 230))
            self.darkPen = QPen(QColor(200, 200, 200))
        else:
            self.backgroundBrush = QBrush(QColor(0xbbada0))
            self.brushes = {
                0: QBrush(QColor(0xcdc1b4)),
                1: QBrush(QColor(0x999999)),
                2: QBrush(QColor(0xeee4da)),
                4: QBrush(QColor(0xede0c8)),
                8: QBrush(QColor(0xf2b179)),
                16: QBrush(QColor(0xf59563)),
                32: QBrush(QColor(0xf67c5f)),
                64: QBrush(QColor(0xf65e3b)),
                128: QBrush(QColor(0xedcf72)),
                256: QBrush(QColor(0xedcc61)),
                512: QBrush(QColor(0xedc850)),
                1024: QBrush(QColor(0xedc53f)),
                2048: QBrush(QColor(0xedc22e)),
            }
            self.lightPen = QPen(QColor(0xf9f6f2))
            self.darkPen = QPen(QColor(0x776e65))

    def resizeEvent(self, e):
        width = min(e.size().width(), e.size().height() - self.panelHeight)
        self.tileSize = (width - self.tileMargin * (self.gridSize + 1)) / self.gridSize
        self.font = QFont('Arial', int(self.tileSize / 4))

    def reset_game(self):
        self.tiles = [[None for _ in range(self.gridSize)] for _ in range(self.gridSize)]
        self.availableSpots = list(range(self.gridSize * self.gridSize))
        self.score = 0
        self.addTile()
        self.addTile()
        self.update()
        self.gameRunning = True

    def addTile(self):
        if self.availableSpots:
            v = 2 if random.random() < 0.9 else 4
            i = self.availableSpots.pop(int(random.random() * len(self.availableSpots)))
            gridX = i % self.gridSize
            gridY = i // self.gridSize
            self.tiles[gridX][gridY] = Tile(v)

    def updateTiles(self):
        self.availableSpots = []
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                if self.tiles[i][j] is None:
                    self.availableSpots.append(i + j * self.gridSize)
        self.addTile()
        if self.score > self.hiScore:
            self.hiScore = self.score
            self.saveHiScore()
        self.update()
        if not self.movesAvailable():
            QMessageBox.information(self, '', 'Game Over')
            self.gameRunning = False

    def saveHiScore(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.hiScore))
        except:
            pass

    def loadHiScore(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read())
        except:
            pass
        return 0

    def movesAvailable(self):
        if self.availableSpots:
            return True
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                if i < self.gridSize - 1 and self.tiles[i][j].value == self.tiles[i + 1][j].value:
                    return True
                if j < self.gridSize - 1 and self.tiles[i][j].value == self.tiles[i][j + 1].value:
                    return True
        return False

    def move_tiles(self, direction_func):
        moved = direction_func()
        if moved:
            self.updateTiles()

    def up(self):
        moved = False
        for x in range(self.gridSize):
            for y in range(1, self.gridSize):
                if self.tiles[x][y]:
                    i = y
                    while i > 0 and not self.tiles[x][i - 1]:
                        i -= 1
                    if i > 0 and self.tiles[x][i - 1].value == self.tiles[x][y].value:
                        self.score += self.tiles[x][y].value * 2
                        self.tiles[x][i - 1].value *= 2
                        self.tiles[x][y] = None
                        moved = True
                    elif i < y:
                        self.tiles[x][i] = self.tiles[x][y]
                        self.tiles[x][y] = None
                        moved = True
        return moved

    def down(self):
        moved = False
        for x in range(self.gridSize):
            for y in range(self.gridSize - 2, -1, -1):
                if self.tiles[x][y]:
                    i = y
                    while i + 1 < self.gridSize and not self.tiles[x][i + 1]:
                        i += 1
                    if i + 1 < self.gridSize and self.tiles[x][i + 1].value == self.tiles[x][y].value:
                        self.score += self.tiles[x][y].value * 2
                        self.tiles[x][i + 1].value *= 2
                        self.tiles[x][y] = None
                        moved = True
                    elif i > y:
                        self.tiles[x][i] = self.tiles[x][y]
                        self.tiles[x][y] = None
                        moved = True
        return moved

    def left(self):
        moved = False
        for x in range(1, self.gridSize):
            for y in range(self.gridSize):
                if self.tiles[x][y]:
                    i = x
                    while i > 0 and not self.tiles[i - 1][y]:
                        i -= 1
                    if i > 0 and self.tiles[i - 1][y].value == self.tiles[x][y].value:
                        self.score += self.tiles[x][y].value * 2
                        self.tiles[i - 1][y].value *= 2
                        self.tiles[x][y] = None
                        moved = True
                    elif i < x:
                        self.tiles[i][y] = self.tiles[x][y]
                        self.tiles[x][y] = None
                        moved = True
        return moved

    def right(self):
        moved = False
        for x in range(self.gridSize - 2, -1, -1):
            for y in range(self.gridSize):
                if self.tiles[x][y]:
                    i = x
                    while i + 1 < self.gridSize and not self.tiles[i + 1][y]:
                        i += 1
                    if i + 1 < self.gridSize and self.tiles[i + 1][y].value == self.tiles[x][y].value:
                        self.score += self.tiles[x][y].value * 2
                        self.tiles[i + 1][y].value *= 2
                        self.tiles[x][y] = None
                        moved = True
                    elif i > x:
                        self.tiles[i][y] = self.tiles[x][y]
                        self.tiles[x][y] = None
                        moved = True
        return moved

    def keyPressEvent(self, e):
        if not self.gameRunning:
            return
        if e.key() == Qt.Key_Escape:
            self.reset_game()
        elif e.key() == Qt.Key_Up:
            self.move_tiles(self.up)
        elif e.key() == Qt.Key_Down:
            self.move_tiles(self.down)
        elif e.key() == Qt.Key_Left:
            self.move_tiles(self.left)
        elif e.key() == Qt.Key_Right:
            self.move_tiles(self.right)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.backgroundBrush)
        painter.drawRect(self.rect())

        painter.setBrush(self.brushes[1])
        painter.drawRoundedRect(self.scoreRect, 10.0, 10.0)
        painter.drawRoundedRect(self.hiScoreRect, 10.0, 10.0)
        painter.drawRoundedRect(self.resetRect, 10.0, 10.0)

        painter.setFont(QFont('Arial', 9))
        painter.setPen(self.darkPen)
        painter.drawText(QRectF(10, 15, 80, 20), 'SCORE', QTextOption(Qt.AlignHCenter | Qt.AlignVCenter))
        painter.drawText(QRectF(100, 15, 80, 20), 'HIGHSCORE', QTextOption(Qt.AlignHCenter | Qt.AlignVCenter))

        painter.setFont(QFont('Arial', 15))
        painter.setPen(self.lightPen)
        painter.drawText(self.resetRect, 'RESET', QTextOption(Qt.AlignHCenter | Qt.AlignVCenter))
        painter.drawText(self.scoreLabel, str(self.score), QTextOption(Qt.AlignHCenter | Qt.AlignVCenter))
        painter.drawText(self.hiScoreLabel, str(self.hiScore), QTextOption(Qt.AlignHCenter | Qt.AlignVCenter))

        painter.setFont(self.font)
        for x in range(self.gridSize):
            for y in range(self.gridSize):
                tile = self.tiles[x][y]
                rect = QRectF(
                    self.gridOffsetX + x * (self.tileSize + self.tileMargin),
                    self.gridOffsetY + y * (self.tileSize + self.tileMargin),
                    self.tileSize,
                    self.tileSize
                )
                painter.setBrush(self.brushes[0] if tile is None else self.brushes.get(tile.value, self.brushes[2048]))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect, 10.0, 10.0)
                if tile:
                    painter.setPen(self.darkPen if tile.value < 16 else self.lightPen)
                    painter.drawText(rect, str(tile.value), QTextOption(Qt.AlignHCenter | Qt.AlignVCenter))

if __name__ == '__main__':
    app = QApplication([])
    menu = MainMenu()
    menu.show()
    app.exec()
