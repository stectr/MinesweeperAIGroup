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
        self.actions = -1
        self.currentx = startX
        self.currenty = startY
        self.safe = set()
        self.dangerous = set()
        self.flags = set()
        self.numdict = dict()
        for i in range(1, 9):
            self.numdict[i] = set()
        self.done = set()
        self.numtriple = list()
        self.toflag = set()

    def getAction(self, number: int) -> "Action Object":
        if len(self.flags) == self.totalM:
            return Action(AI.Action.LEAVE, 0, 0)

        self.actions += 1

        if self.actions == 0:
            self.currentx = self.startX
            self.currenty = self.startY
            self.board[self.currenty][self.currentx] = '0'
            self.addsafeneighbors(self.startX, self.startY)
            return Action(AI.Action.UNCOVER, self.startX, self.startY)

        if (self.board[self.currenty][self.currentx] != f'{number}') and (self.board[self.currenty][self.currentx] != f'-1'):
            self.board[self.currenty][self.currentx] = f'{number}'

        if number != 0:
            if number == -1:
                self.flags.add((self.currentx, self.currenty))
            elif (self.currentx, self.currenty) not in self.done:
                self.numtriple.append((number, self.currentx, self.currenty))
                self.numtriple = sorted(self.numtriple, key=lambda x: x[0])

        if number == 0:
            self.addsafeneighbors(self.currentx, self.currenty)
        elif number >= 1:
            self.adddangerousneighbors(self.currentx, self.currenty)

        # Uncover safe cells
        while self.safe:
            x, y = self.safe.pop()
            # Ensure the cell is not flagged or uncovered already
            if self.board[y][x] == ' ':
                self.currentx, self.currenty = x, y
                return Action(AI.Action.UNCOVER, x, y)

        # Flag the dangerous cells
        while self.toflag:
            x, y = self.toflag.pop()
            # Ensure the cell is not flagged or uncovered already
            if self.board[y][x] == ' ':
                self.currentx, self.currenty = x, y
                self.flags.add((x, y))
                return Action(AI.Action.FLAG, x, y)

        loop_count = 0
        while self.numtriple:
            i, x, y = self.numtriple.pop(0)
            empty, emptyset, flags, flagset = self.countflagsempty(x, y)
            self.done.add((x, y))
            if (empty == i) and (flags == 0):
                while emptyset:
                    qx, qy = emptyset.pop()
                    if self.board[qy][qx] == ' ':
                        self.toflag.add((qx, qy))
                fx, fy = self.toflag.pop()
                self.currentx = fx
                self.currenty = fy
                self.flags.add((fx, fy))
                return Action(AI.Action.FLAG, fx, fy)
            elif (empty > 0) and (flags == i):
                while emptyset:
                    qx, qy = emptyset.pop()
                    if self.board[qy][qx] == ' ':
                        self.safe.add((qx, qy))
                fx, fy = self.safe.pop()
                self.currentx = fx
                self.currenty = fy
                return Action(AI.Action.UNCOVER, fx, fy)
            elif (flags + empty == i) and empty > 0:
                while emptyset:
                    qx, qy = emptyset.pop()
                    if self.board[qy][qx] == ' ':
                        self.toflag.add((qx, qy))
                fx, fy = self.toflag.pop()
                self.currentx = fx
                self.currenty = fy
                self.flags.add((fx, fy))
                return Action(AI.Action.FLAG, fx, fy)
            elif loop_count == 64:
                probabilities = self.calculateprobabilities()
                min_prob_cell = min(probabilities, key=probabilities.get)
                self.currentx, self.currenty = min_prob_cell
                return Action(AI.Action.UNCOVER, self.currentx, self.currenty)
            else:
                self.numtriple.append((i, x, y))
                self.numtriple = sorted(self.numtriple, key=lambda x: x[0])
                loop_count += 1
        return Action(AI.Action.LEAVE, 0, 0)

    def printboard(self):
        bottom = len(self.board) - 1
        while bottom >= 0:
            print(f'{bottom} {self.board[bottom]}'.replace('-1', '?').replace('\'', ''))
            bottom -= 1
        for i in range(len(self.board[0])):
            print(f'  {i}', end="")
        print('')

    def addsafeneighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx == 0 and dy == 0):
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.boardX and 0 <= ny < self.boardY:
                    if self.board[ny][nx] == ' ':
                        self.safe.add((nx, ny))

    def adddangerousneighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.boardX and 0 <= ny < self.boardY:
                    if self.board[ny][nx] == ' ':
                        if self.board[y][x] != ' ' and self.board[y][x] != '-1' and int(self.board[y][x]) > 0:
                            self.dangerous.add((nx, ny))
                    elif (nx, ny) in self.dangerous and self.board[ny][nx] != ' ':
                        self.dangerous.remove((nx, ny))

    def countflagsempty(self, x, y):
        empty = 0
        flags = 0
        emptyset = set()
        flagset = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx == 0 and dy == 0) or not (0 <= x + dx < self.boardX and 0 <= y + dy < self.boardY):
                    continue
                elif self.board[y + dy][x + dx] == ' ':
                    empty += 1
                    emptyset.add((x+dx, y+dy))
                elif self.board[y + dy][x + dx] == '-1':
                    flags += 1
                    flagset.add((x+dx, y+dy))
        return empty, emptyset, flags, flagset

    def calculateprobabilities(self):
        probabilities = {}
        flagsleft = self.totalM - len(self.flags)
        for y in range(self.boardY):
            for x in range(self.boardX):
                if self.board[y][x] == ' ':
                    probabilities[(x, y)] = self.calculateprobabilitycell(x, y, flagsleft)
        return probabilities

    def calculateprobabilitycell(self, x, y, flagsleft):
        surroundingnumbers = 0
        clues = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx == 0 and dy == 0) or not (0 <= x + dx < self.boardX and 0 <= y + dy < self.boardY):
                    continue
                if self.board[y + dy][x + dx].isdigit():
                    num = int(self.board[y + dy][x + dx])
                    surroundingnumbers += 1
                    clues.append((num, x + dx, y + dy))
        if surroundingnumbers == 0:
            return 1.0  # maximum probability if there are no neighboring clues
        probsum = 0
        for num, cx, cy in clues:
            empty, emptyset, flags, flagset = self.countflagsempty(cx, cy)
            remainingmines = num - flags
            if empty > 0:
                probsum += remainingmines / empty
        return probsum / len(clues) if clues else 1.0

