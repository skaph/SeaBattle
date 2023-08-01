from random import random, randint, choice


# import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы стеляете мимо доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли по этой клетке"


class BoardWrongShipException(BoardException):
    pass


# Класс всех точек на поле. Принимает две координаты - X, Y

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Переопределяем методы eq и print для экземпляров класса

    def __eq__(self, _):
        return self.x == _.x and self.y == _.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


# Ship - Класс кораблей: length - длина, bow - точка носа корабля,
# direction - направление корабля, lives - жизни

class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    # Свойство dots возвращает список ship_dots - всех точек корабля

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            _x = self.bow.x
            _y = self.bow.y
            if self.direction == 0:
                _x += i
            elif self.direction == 1:
                _y += i
            ship_dots.append(Dot(_x, _y))
        return ship_dots

    # Проверяем наличие координат выстрела shot в списке ship_dots

    def shooten(self, shot):
        return shot in self.dots


# Класс игровой доски.
# hid - татус отображения кораблей соперника
# size - Размер игровой доски
# wrecked_ship - Число подбитых кораблей у игрока
# ships - Список координат всех точек кораблей пользователя
# occupy - Список координат занятых точек

class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.wrecked_ship = 0

        self.field = [['0'] * size for _ in range(size)]
        # self.radar = [['0'] * size for _ in range(size)]
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]
        self.weights = {}

        self.ships = []
        self.occupy = []
        self.damaged_ships = []
        self.destroyed_ships = []
        # self.weight = [(i, j) for i in range(size) for j in range(size)]

    # Переопределяем функцию str для более удобного отображения доски
    # Hid - Скрыть/отобразить корабли соперника
    def __str__(self):
        disp = ""
        disp += "  | 1 | 2 | 3 | 4 | 5 | 6 |"

        for i, row in enumerate(self.field):
            disp += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            disp = disp.replace("■", "0")
        return disp

    # Проверка соответствия координат точки размерам поля
    def out(self, point):
        return not ((0 <= point.x < self.size) and (0 <= point.y < self.size))

    # Определение точек вокруг корабля.
    # ship - экземпляр класса кораблей,
    # verb - bool для обведения пораженного корабля
    # around - Список изменений координат точек, окружающих корабль
    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for point in ship.dots:
            for point_x, point_y in around:
                tmp = Dot(point.x + point_x, point.y + point_y)
                if not (self.out(tmp)) and tmp not in self.occupy:
                    if verb:
                        self.field[tmp.x][tmp.y] = "."
                    self.occupy.append(tmp)

    # Добавление корабля на поле
    # Проверяем, не выходят ли точки корабля за поле и не заняты ли они, иначе - исключение
    # Помечаем занятую кораблем клетку на поле
    # Добавляем точку в список занятых
    # Добавляем корабль в список кораблей пользователя
    # Обводим контур корабля
    def add_ship(self, ship):
        for point in ship.dots:
            if self.out(point) or point in self.occupy:
                raise BoardWrongShipException()
        for point in ship.dots:
            self.field[point.x][point.y] = "■"
            self.occupy.append(point)

        self.ships.append(ship)
        self.contour(ship)

    # Выстрел по доске
    def shot(self, point):
        if self.out(point):
            raise BoardOutException()

        if point in self.occupy:
            raise BoardUsedException()

        self.occupy.append(point)
        # print(self.occupy)

        for ship in self.ships:
            if ship.shooten(point):
                ship.lives -= 1
                self.field[point.x][point.y] = "X"
                self.damaged_ships.append(point)
                # отладка
                # print(self.damaged_ships)
                if ship.lives == 0:
                    self.wrecked_ship += 1
                    self.destroyed_ships.append(ship.dots)
                    # print(destroyed_ships)
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен, капитан!")
                    return False
                else:
                    print("Корабль подбит, капитан!")
                    return True

        self.field[point.x][point.y] = "."
        print("Промах!")
        return False

    # # Считаем вес клеток для выстрелов AI
    def calc_weight(self):
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]
        for x in range(self.size):
            for y in range(self.size):
                tmp = Dot(x, y)
                if tmp in self.damaged_ships:
                    self.weight[x][y] = 0

                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.weight[x - 1][y - 1] = 0
                        self.weight[x - 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x - 1][y + 1] = 0

                    if y - 1 >= 0:
                        self.weight[x][y - 1] *= 50
                    if y + 1 < self.size:
                        self.weight[x][y + 1] *= 50

                    if x + 1 < self.size:
                        if y - 1 >= 0:
                            self.weight[x + 1][y - 1] = 0
                        self.weight[x + 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x + 1][y + 1] = 0

                if tmp in self.occupy:
                    self.weight[x][y] = 0

    def get_max_weights(self):
        max_weight = 0
        weights = {}
        for x in range(self.size):
            for y in range(self.size):
                if self.weight[x][y] > max_weight:
                    max_weight = self.weight[x][y]
                weights.setdefault(self.weight[x][y], []).append((x, y))
        max_point = choice(weights[max_weight])
        max_point = Dot(max_point[0], max_point[1])
        return max_point

    # Обнуляем список занятых точек
    def begin(self):
        self.occupy = []

    # Проверяем, не пора ли заканчивать игру
    def losing(self):
        return self.wrecked_ship == len(self.ships)


# Общий класс описания игрока (и человека, и компьютера)
# имеет доску игрока и доску противника
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    # Делаем ход и перерасчет веса клеток для стрельбы
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                self.enemy.calc_weight()
                #print(self.enemy.weight)
                return repeat
            except BoardException as e:
                print(e)


# Класс игрока - копмьютера
class AI(Player):

    def ask(self):
        # point = Dot(randint(0, 5), randint(0, 5))
        point = self.enemy.get_max_weights()
        print(f"Ход компьютера: {point.x + 1} {point.y + 1}")
        return point


# Класс игрока - человека
class User(Player):

    def ask(self):
        while True:
            coordinates = input("Ваш ход, капитан: ").split()

            if len(coordinates) != 2:
                print("Введите две координаты, капитан!")
                continue

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа, капитан!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Класс игры
class Game:
    def __init__(self, size=6):
        self.size = size
        man = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, man)
        self.us = User(man, comp)

    # Расположение кораблей на поле
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        decks = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for ship_decks in decks:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), ship_decks, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # Приветствие в игре
    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    # Игровой цикл
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.wrecked_ship == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.wrecked_ship == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g1 = Game()
g1.start()
