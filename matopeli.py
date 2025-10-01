# 'pip install PySide6' tarvitaan 
import sys
import random
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMenu, QGraphicsPixmapItem
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QPixmap
from PySide6.QtCore import Qt, QTimer
import winsound

# vakiot
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 15

class SnakeGame(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setSceneRect(0, 0, CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.game_started = False
        self.init_screen()
        
    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            # päivitetään suunta vain jos se ei ole vastakkainen valitulle suunnalle
            if key == Qt.Key_Left and self.direction != Qt.Key_Right:
                self.direction = key
            elif key == Qt.Key_Right and self.direction != Qt.Key_Left:
                self.direction = key
            elif key == Qt.Key_Up and self.direction != Qt.Key_Down:
                self.direction = key
            elif key == Qt.Key_Down and self.direction != Qt.Key_Up:
                self.direction = key

            # starting game by button
        if not self.game_started:
            if key == event.key() and event.key() != Qt.Key_Left and event.key() != Qt.Key_Up and event.key() != Qt.Key_Right and event.key() != Qt.Key_Down:
                self.game_started = True
                self.scene().clear()
                self.start_game()


    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return x, y

    def update_game(self):
        head_x, head_y = self.snake[0]

        if self.direction == Qt.Key_Left:
            new_head = (head_x - 1, head_y)
        elif self.direction == Qt.Key_Right:
            new_head = (head_x + 1, head_y)
        elif self.direction == Qt.Key_Up:
            new_head = (head_x, head_y - 1)
        elif self.direction == Qt.Key_Down:
            new_head = (head_x, head_y + 1)

        #pelialueen rajat
        if new_head in self.snake or not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
            winsound.PlaySound("aanet\death.wav", winsound.SND_ASYNC | winsound.SND_ALIAS)
            self.timer.stop()
            # Game over text
            game_over_text = self.scene().addText("Game Over", QFont("Arial", 24))
            text_width = game_over_text.boundingRect().width()
            text_x = (self.width() - text_width) / 2
            game_over_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 3)
            self.game_started = False
            self.init_screen_game_over()
            return

        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            winsound.PlaySound("aanet\omnom.wav", winsound.SND_ASYNC | winsound.SND_ALIAS)
            self.food = self.spawn_food()
            self.score += 1
        else:
            self.snake.pop()

        self.print_game()

    def print_game(self):
        self.scene().clear()

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if (x + y) % 2 == 0:
                    color = QColor("#31A84B")  # vaaleampi sävy
                else:
                    color = QColor("#2A9144")  # tummempi sävy
                self.scene().addRect(
                    x * CELL_SIZE, y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE,
                    QPen(Qt.NoPen), QBrush(color)
                )

        fx, fy = self.food
        
        food_emoji = self.scene().addText("🍎", QFont("Segoe UI Emoji", CELL_SIZE/2))
        food_emoji.setPos(fx * CELL_SIZE, fy * CELL_SIZE - CELL_SIZE // 4)

        for i, segment in enumerate(self.snake):
            x, y = segment
            if i == 0:
                # Madon pää kuvalla
                pixmap = QPixmap("kuvat/emoji.webp")
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
                    item = QGraphicsPixmapItem(pixmap)
                    item.setPos(x * CELL_SIZE, y * CELL_SIZE)
                    self.scene().addItem(item)
                else:
                    # Jos kuvaa ei löydy, piirrä varablokki
                    self.scene().addRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, QPen(Qt.black), QBrush(Qt.darkGreen))
            else:
                # Muut segmentit
                self.scene().addRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, QPen(QColor("#FFFFFF")), QBrush(QColor('#5BCF78')))
        #self.scene().addText(f'Score: {self.score}', QFont("Arial", 12))
        
        self.setWindowTitle(f'Score: {self.score}')

    def init_screen_game_over(self):
        start_text = self.scene().addText("Press any key to start", QFont("Arial", 18))
        text_width = start_text.boundingRect().width()
        text_x = (self.width() - text_width)/2
        start_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 2)

    def init_screen(self):
        start_text = self.scene().addText("Press any key to start", QFont("Arial", 18))
        text_width = start_text.boundingRect().width()
        text_x = (self.width()/2 - text_width)
        start_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 2)


    def start_game(self):
        self.direction = Qt.Key_Right
        self.snake = [(5, 5), (5, 6), (5, 7)]
        self.food = self.spawn_food()
        self.timer.start(300)
        self.level_limit = 5
        self.timer_delay = 300

        self.timer.start(self.timer_delay)
        
        self.score = 0
        if self.score == self.level_limit:
            self.level_limit += 5
            self.timer_delay *= 0.9
            self.timer.setInterval(self.timer_delay)

def main():
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()