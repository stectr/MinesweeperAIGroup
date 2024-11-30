from AI import AI
from Action import Action
import random


class MyAI(AI):

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.boardY = rowDimension
        self.boardX = colDimension
        self.totalM = totalMines
        self.startX = startX
        self.startY = startY
        self.board = [[' ' for _ in range(colDimension)]
                      for _ in range(rowDimension)]
        # print(f'INITIALIZED - startx{startX} starty{startY} mines{totalMines}')

        # VARIABLES TO TRACK GAME STATE
        self.actions = -1
        self.currentx = startX
        self.currenty = startY

        # SETS TO TRACK GAME ELEMENTS
        self.safe = set()  # known safe cells
        self.dangerous = set()  # set to hold possible danger coordinates

    def getAction(self, number: int) -> "Action Object":
        self.actions += 1  # increment action count (purely for starting off)

        # START BY UNCOVERING THE STARTING POSITION
        if self.actions == 0:
            # mark the starting position as '0'
            self.board[self.startY][self.startX] = '0'
            self.currentx = self.startX
            self.currenty = self.startY

            # add neighboring safe
            self.addsafeneighbors(self.startX, self.startY)
            # self.printboard()
            return Action(AI.Action.UNCOVER, self.startX, self.startY)

        # UPDATE THE BOARD WITH THE CURRENT NUMBER
        if self.board[self.currenty][self.currentx] != f'{number}':
            self.board[self.currenty][self.currentx] = f'{number}'
            self.printboard()  # Print the current board state

        # CHECK FOR SPECIFIC NUMBERS AND ADD TO RESPECTIVE SETS
        if number == 0:
            # handle safe neighbors
            self.addsafeneighbors(self.currentx, self.currenty)
        elif number == 1:
            self.adddangerousneighbors(self.currentx, self.currenty)

        while self.safe:  # CONTINUE TO UNCOVER
            if self.safe:
                x, y = self.safe.pop()  # UNCOVER THE FIRST SAFE COORDINATE FOUND
                # print(f'\t\t\t\t\t\tpop {x},{y} from safe and uncover')
                self.currentx, self.currenty = x, y
                return Action(AI.Action.UNCOVER, x, y)

        # CHECK DANGEROUS CELLS
        stillempty = set()
        for y, v in enumerate(self.board):
            for x, i in enumerate(v):
                if self.board[y][x] == ' ':
                    stillempty.add((x, y))
        # print(f'stillempty {stillempty}')

        mostdangerous = [(0, 0), 0]
        for coord in stillempty:
            x, y = coord
            numsurround = self.countSurroundingOnes(x, y)
            if numsurround >= mostdangerous[1]:
                mostdangerous[0] = coord
                mostdangerous[1] = numsurround

        while stillempty:
            x, y = stillempty.pop()
            if (x, y) != mostdangerous[0]:
                self.board[y][x] = '1'
                return Action(AI.Action.UNCOVER, x, y)
            else:
                continue

        mineX, mineY = mostdangerous[0]
        self.board[mineY][mineX] = 'F'
        return Action(AI.Action.FLAG, x, y)

        # uhhhhhhhh lol
        return Action(AI.Action.LEAVE, 0, 0)

    def countSurroundingOnes(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:  # iterate through neighboring cells
            for dy in [-1, 0, 1]:
                if (dx == 0 and dy == 0) or not (0 <= x + dx < self.boardX and 0 <= y + dy < self.boardY):
                    continue
                if self.board[y + dy][x + dx] == '1':
                    count += 1  # increment count for each '1' found
        return count

    def printboard(self):  # FOR MY OWN DEBUGGING PURPOSES CAUSE IM TOO LAZY TO USE DEBUGGER AND FLAGS
        print(
            f'\tcurrentx {self.currentx} currenty {self.currenty} actions {self.actions}')
        print(f'\tsafe {str(self.safe).replace(" ", "")}')
        print(f'\tdangerous {str(self.dangerous).replace(" ", "")}')
        bottom = len(self.board) - 1  # start from the last row
        while bottom >= 0:
            print(f'{bottom} {self.board[bottom]}')  # print each row
            bottom -= 1
        for i in range(len(self.board[0])):  # print column in bottom
            print(f'    {i}', end="")
        print('')

    def addsafeneighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx == 0 and dy == 0):
                    continue  # Skip the cell itself
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.boardX and 0 <= ny < self.boardY:
                    if self.board[ny][nx] == ' ':
                        self.safe.add((nx, ny))  # add to safe set

    def adddangerousneighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx == 0 and dy == 0):
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.boardX and 0 <= ny < self.boardY:
                    if self.board[ny][nx] == ' ' and (nx, ny) not in self.safe:
                        self.dangerous.add((nx, ny))  # add to dangerous set
