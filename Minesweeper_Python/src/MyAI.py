# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
# agent in this file. You will write the 'getAction' function,
# the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
# - DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

import random
from AI import AI
from Action import Action


class MyAI(AI):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        ########################################################################
        # YOUR CODE BEGINS						   #
        ########################################################################
        # basic setting up board stuff
        self.rows = colDimension
        self.cols = rowDimension
        self.mineCount = totalMines
        self.x = startX
        self.y = startY
        # have a set for all the flagged mines and a set of all tiles already unconvered. The board is none for all tiles in the beginning using a 2d array.
        self.flagged = set()
        self.board = [[None for y in range(self.cols)]
                      for x in range(self.rows)]
        self.prob = [[(self.mineCount / self.rows * self.cols)
                      for y in range(self.cols)] for x in range(self.rows)]
        self.uncovered = set()
        # create a list of the x,y coordinates for all tiles that have not been explored. So essentially, self.next_moves is all the tiles that have not yet been uncovered.
        self.next_moves = [(x, y) for y in range(self.cols)
                           for x in range(self.rows)]

        # initializing the starting spot so i set the tile to be 0 for the board and remove it from next_moves and add it to the uncovered array as a tuple of it's (x,y)
        if (0 <= self.x < self.rows and 0 <= self.y < self.cols):
            self.board[self.x][self.y] = 0
            self.uncovered.add((self.x, self.y))
            self.next_moves.remove((self.x, self.y))

        # queue for all the next actions
        self.actions_queue = []
        self.flags_queue = []
    ########################################################################
    # YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        # YOUR CODE BEGINS						   #
        ########################################################################

        # maing sure that it is not already explored.
        if (self.x, self.y) not in self.uncovered:
            if 0 <= self.x < self.rows and 0 <= self.y < self.cols:
                # removing from queue so u don't explore again.
                if ((self.x, self.y) in self.actions_queue):
                    self.actions_queue.remove((self.x, self.y))
                # setting the board, removing it from the list of remaining tiles, and adding it to the explored tiles.
                self.board[self.x][self.y] = number
                self.next_moves.remove((self.x, self.y))
                self.uncovered.add((self.x, self.y))

        if number > -1:
            self.prob[self.x][self.y] = 0

        # base case
        if number == 0:
            # sets all of the tiles that have not been set as safe as safe tiles and adding them into queue to uncover.
            self.mark_safe(self.x, self.y)
            # if tiles were added, then explore them to get all of the 0 tiles out of the way. Essentially, I explore all safe tiles first
            if self.actions_queue:
                nx, ny = self.actions_queue.pop(0)
                if (0 <= nx < self.rows and 0 <= ny < self.cols):
                    self.x, self.y = nx, ny
                    return Action(AI.Action.UNCOVER, nx, ny)
            else:
                # check if we have completed board.
                if len(self.next_moves) + len(self.flagged) == self.mineCount:
                    return Action(AI.Action.LEAVE)

        # check for flag if so, then go to next action in queue
        if number == -1:
            # add to flag.
            self.prob[self.x][self.y] = 1
            self.flagged.add((self.x, self.y))
            if self.actions_queue:
                x1, y1 = self.actions_queue.pop(0)
                if (0 <= self.x < self.rows and 0 <= self.y < self.cols):
                    self.x, self.y = x1, y1
                    return Action(AI.Action.UNCOVER, x1, y1)
            else:
                # check if leave
                if len(self.next_moves) + len(self.flagged) == self.mineCount:
                    return Action(AI.Action.LEAVE)
                # might be redundant but i still check.
                if self.actions_queue:
                    x1, y1 = self.actions_queue.pop(0)
                    if (0 <= self.x < self.rows and 0 <= self.y < self.cols):
                        self.x, self.y = x1, y1
                        return Action(AI.Action.UNCOVER, x1, y1)

                # here is a basic checking for when you know a tile is safe and a tile is a mine. This doesn't implement patterns yet. It does basic checking for each of the unexplored tiles.
                # essentially, it checks if the flagged count and the amount of tiles that are unexplored is equal to the hint count, then it is a potential mine but if the flag count is equal to the hint
                # then it is a safe tile.
                for (x, y) in self.next_moves:
                    safe = False
                    potential_mine = False
                    for (x1, y1) in self.neighbors(x, y):
                        if isinstance(self.board[x1][y1], int):
                            hint = self.board[x1][y1]
                            neighbors = self.neighbors(x1, y1)

                            flagged_count = sum(
                                1 for (x2, y2) in neighbors if self.board[x2][y2] == -1)
                            covered_count = sum(
                                1 for (x2, y2) in neighbors if self.board[x2][y2] == None)

                            if flagged_count + covered_count == hint:
                                potential_mine = True
                            elif flagged_count == hint:
                                safe = True

                    if safe:
                        self.actions_queue.insert(0, (x, y))
                    elif potential_mine:
                        if ((x, y) not in self.actions_queue):
                            self.x, self.y = x, y
                            return Action(AI.Action.FLAG, x, y)

        if (number == 2 or number == 3): # hard-coded pattern test
            self.checkhardcoded(self.x, self.y)

        # checking for if there is a number other than 0 or -1, this code is kind of redundant. Can put into separate function but i just never did. Also checking for if i found a safe tile from the
        # code above
        if self.flags_queue:
            nx, ny = self.flags_queue.pop(0)
            self.x, self.y = nx, ny
            return Action(AI.Action.FLAG, nx, ny)

        if self.actions_queue:
            nx, ny = self.actions_queue.pop(0)
            if (0 <= nx < self.rows and 0 <= ny < self.cols):
                self.x, self.y = nx, ny
                return Action(AI.Action.UNCOVER, nx, ny)

        # check if can leave.
        if len(self.next_moves) + len(self.flagged) == self.mineCount:
            return Action(AI.Action.LEAVE)

        # here is a basic checking for when you know a tile is safe and a tile is a mine. This doesn't implement patterns yet. It does basic checking for each of the unexplored tiles.
        # essentially, it checks if the flagged count and the amount of tiles that are unexplored is equal to the hint count, then it is a potential mine but if the flag count is equal to the hint
        # then it is a safe tile. also redundant code
        for (x, y) in self.next_moves:
            safe = False
            potential_mine = False
            for (x1, y1) in self.neighbors(x, y):
                if isinstance(self.board[x1][y1], int):
                    hint = self.board[x1][y1]
                    neighbors = self.neighbors(x1, y1)

                    flagged_count = sum(
                        1 for (x2, y2) in neighbors if self.board[x2][y2] == -1)
                    covered_count = sum(
                        1 for (x2, y2) in neighbors if self.board[x2][y2] == None)

                    if flagged_count + covered_count == hint:
                        potential_mine = True
                    elif flagged_count == hint:
                        safe = True
            if safe:
                self.actions_queue.insert(0, (x, y))
            elif potential_mine:
                if ((x, y) not in self.actions_queue):
                    self.x, self.y = x, y
                    return Action(AI.Action.FLAG, x, y)

        # checking for after i did the code above to see if any other tile was potentially safe
        if self.actions_queue:
            nx, ny = self.actions_queue.pop(0)
            if (0 <= nx < self.rows and 0 <= ny < self.cols):
                self.x, self.y = nx, ny
                return Action(AI.Action.UNCOVER, nx, ny)

        # THE PART BELOW IS THE MAIN PART WE NEED TO CHANGE. I BELIEVE THE REST ABOVE SHOULD BE ALRIGHT FROM WHEN I RAN THE BOARDS AS THEY ONLY FAIL ONCE ALL ELSE ABOVE HAS BEEN RAN THROUGH AND IT
        # NEEDS TO SOMEHOW PICK A TILE RANDOMLY.
        # if all else fails, that is when we want to implement patterns in the self.score function. So far, i have just used some random heuristic i made up by running a couple of boards but
        # probably going to change that function to just be patterns first.

        # 1-1 implemented
        for (x, y) in self.next_moves:
            for (x1, y1) in self.explored_neighbors(x, y):
                una = {(i, j) for (i, j) in self.neighbors(
                    x1, y1) if self.board[i][j] == None}
                unaf = sum(1 for (i, j) in self.neighbors(
                    x1, y1) if self.board[i][j] == -1)
                if self.board[x1][y1] > 0:
                    for (x2, y2) in self.explored_neighbors(x1, y1):
                        if self.board[x2][y2] > 0:
                            unb = {(i, j) for (i, j) in self.neighbors(
                                x2, y2) if self.board[i][j] == None}
                            unbf = sum(1 for (i, j) in self.neighbors(
                                x2, y2) if self.board[i][j] == -1)
                            unab = una - unb
                            if unab:
                                if unb.issubset(una):
                                    if self.board[x1][y1] - unaf == self.board[x2][y2] - unbf:
                                        for (i, j) in unab:
                                            self.actions_queue.insert(
                                                0, (i, j))
                                    elif self.board[x1][y1] - unaf == self.board[x2][y2] - unbf + len(unab):
                                        for (i, j) in unab:
                                            self.flags_queue.insert(0, (i, j))

        if self.flags_queue:
            nx, ny = self.flags_queue.pop(0)
            self.x, self.y = nx, ny
            return Action(AI.Action.FLAG, nx, ny)

        if self.actions_queue:
            nx, ny = self.actions_queue.pop(0)
            if (0 <= nx < self.rows and 0 <= ny < self.cols):
                self.x, self.y = nx, ny
                return Action(AI.Action.UNCOVER, nx, ny)
        if self.next_moves:
            # so far i know that if it is 1 2 x, then that x will always have a mine either above or below.
            self.update_prob()
            min_value = min(self.prob[x][y] for x, y in self.next_moves)
            if min_value == 1:
                return Action(AI.Action.LEAVE)

            min_indices = [
                (x, y) for x, y in self.next_moves if self.prob[x][y] == min_value]
            next_x, next_y = random.choice(min_indices)
            if (0 <= self.x < self.rows and 0 <= self.y < self.cols):
                self.x, self.y = next_x, next_y
                return Action(AI.Action.UNCOVER, next_x, next_y)

        # if no more action, then leave.
        return Action(AI.Action.LEAVE)

    # gets all neighbors to a coordinate
    def neighbors(self, x, y):
        neighbors = []
        for x1 in range(-1, 2):
            for y1 in range(-1, 2):
                x2, y2 = x + x1, y + y1
                if 0 <= x2 < self.rows and 0 <= y2 < self.cols:
                    if (x1 == 0 and y1 == 0):
                        continue
                    neighbors.append((x2, y2))
        return neighbors

    # gets all uncovered neighbors
    def explored_neighbors(self, x, y):
        neighbors = []
        for x1 in range(-1, 2):
            for y1 in range(-1, 2):
                x2, y2 = x + x1, y + y1
                if 0 <= x2 < self.rows and 0 <= y2 < self.cols:
                    if (x1 == 0 and y1 == 0):
                        continue
                    if (x2, y2) in self.uncovered:
                        neighbors.append((x2, y2))
        return neighbors

    def covered_neighbors(self, x, y):
        neighbors = []
        for x1 in range(-1, 2):
            for y1 in range(-1, 2):
                x2, y2 = x + x1, y + y1
                if 0 <= x2 < self.rows and 0 <= y2 < self.cols:
                    if (x1 == 0 and y1 == 0):
                        continue
                    if (x2, y2) not in self.uncovered:
                        neighbors.append((x2, y2))
        return neighbors

    def flagged_neighbors(self, x, y):
        neighbors = []
        for x1 in range(-1, 2):
            for y1 in range(-1, 2):
                x2, y2 = x + x1, y + y1
                if 0 <= x2 < self.rows and 0 <= y2 < self.cols:
                    if (x1 == 0 and y1 == 0):
                        continue
                    if (x2, y2) in self.flagged:
                        neighbors.append((x2, y2))
        return neighbors

    # change this function.
    def score(self, list):
        # uses a random heuristic but doesn't get too far, should do patterns instead. We should start off with 1 2 C, essentially, for 1 2 C, the one above or below the C will be the mine.
        # from what i know we can get pretty far off that.
        moves_count = {}
        for i in list:
            neighbors = self.neighbors(i[0], i[1])
            moves_count[(i[0], i[1])] = (sum([self.board[z[0]][z[1]] for z in neighbors if self.board[z[0]][z[1]] is not None and self.board[z[0]][z[1]] > 0]), len(
                [z for z in neighbors if self.board[z[0]][z[1]] is None or self.board[z[0]][z[1]] == 0]))
        minimum = None
        for key, value in moves_count.items():
            if minimum == None:
                minimum = key
            if value[0] == moves_count[minimum][0]:
                if value[1] > moves_count[minimum][1]:
                    minimum = key
            if value[0] < moves_count[minimum][0]:
                minimum = key
        return minimum

    def mark_safe(self, x, y):
        # marks all the surrounding mines to that coordinate as safe. If one of the surrounding coordinates was flagged already, but we know that it is safe because one of it's neighbors is 0, then
        # we can now set remove a flag from it and add it back into the queue.
        for (x1, y1) in self.neighbors(x, y):
            self.prob[self.x][self.y] = 0
            if self.board[x1][y1] is None and (x1, y1) not in self.actions_queue:
                self.actions_queue.insert(0, (x1, y1))
            elif self.board[x1][y1] == -1:
                self.flagged.remove((x1, y1))
                self.next_moves.append((x1, y1))
                self.uncovered.remove((x1, y1))
                self.board[x1][y1] = None
                self.actions_queue.insert(0, (x1, y1))

    def calc_prob(self, x, y):
        if self.prob[x][y] == 0 or self.prob[x][y] == 1:
            return self.prob[x][y]

        non_flagged_neighbors = [(nx, ny) for (nx, ny) in self.neighbors(x, y) if (
            nx, ny) not in self.uncovered and (nx, ny) not in self.flagged]

        if not non_flagged_neighbors:
            return (self.mineCount - len(self.flagged)) / (self.rows * self.cols - len(self.uncovered))

        probabilities = []
        for (nx, ny) in self.explored_neighbors(x, y):
            hint = self.board[nx][ny]
            if hint > 0:
                total_neighbors = self.neighbors(nx, ny)
                flagged_count = sum(
                    1 for (tx, ty) in total_neighbors if (tx, ty) in self.flagged)
                covered_count = sum(1 for (tx, ty) in total_neighbors if (
                    tx, ty) not in self.uncovered and (tx, ty) not in self.flagged)

                if covered_count == 0:
                    continue

                prob = (hint - flagged_count) / covered_count
                probabilities.append(max(0, min(prob, 1)))

        return max(probabilities) if probabilities else (self.mineCount - len(self.flagged)) / (self.rows * self.cols - len(self.uncovered))

    def update_prob(self):
        for (x1, y1) in self.next_moves:
            self.prob[x1][y1] = self.calc_prob(x1, y1)

    def checkhardcoded(self, x, y):
        # HARD CODED PATTERNS THAT BARELY SEEM TO IMPROVE BUT PUTTING HERE REGARDLESS (maybe runtime improvement)
        # 1 2 1 or 1 2 2 1
        if self.board[x][y] == 2 and (0 < x < self.rows-1) and (0 < y < self.cols-1):
            # 1 [2] 1
            if self.board[x-1][y] == 1 and self.board[x+1][y] == 1:  # 1-2-1
                if self.board[x-1][y+1] == 0 and self.board[x][y+1] == 0 and self.board[x+1][y+1] == 0:
                    self.flags_queue.insert(0, (x-1, y-1))
                    self.actions_queue.insert(0, (x, y-1))
                    self.flags_queue.insert(0, (x+1, y-1))
                elif self.board[x-1][y-1] == 0 and self.board[x][y-1] == 0 and self.board[x+1][y-1] == 0:
                    self.flags_queue.insert(0, (x-1, y+1))
                    self.actions_queue.insert(0, (x, y+1))
                    self.flags_queue.insert(0, (x+1, y+1))
            elif self.board[x][y+1] == 1 and self.board[x][y-1] == 1:
                if self.board[x-1][y+1] == 0 and self.board[x-1][y] == 0 and self.board[x-1][y-1] == 0:
                    self.flags_queue.insert(0, (x+1, y+1))
                    self.actions_queue.insert(0, (x+1, y))
                    self.flags_queue.insert(0, (x+1, y-1))
                elif self.board[x+1][y+1] == 0 and self.board[x+1][y] == 0 and self.board[x+1][y-1] == 0:
                    self.flags_queue.insert(0, (x-1, y+1))
                    self.actions_queue.insert(0, (x-1, y))
                    self.flags_queue.insert(0, (x-1, y-1))
             # 1 [2] 2 1
            elif (0 < x < self.rows-2):
                if self.board[x-1][y] == 1 and self.board[x+1][y] == 2 and self.board[x+2][y] == 1:
                    if self.board[x-1][y+1] == 0 and self.board[x][y+1] == 0 and self.board[x+1][y+1] == 0 and self.board[x+2][y+1] == 0:
                        self.actions_queue.insert(0, (x-1, y-1))
                        self.flags_queue.insert(0, (x, y-1))
                        self.flags_queue.insert(0, (x+1, y-1))
                        self.actions_queue.insert(0, (x+2, y-1))
                    elif self.board[x-1][y-1] == 0 and self.board[x][y-1] == 0 and self.board[x+1][y-1] == 0 and self.board[x+2][y-1] == 0:
                        self.actions_queue.insert(0, (x-1, y+1))
                        self.flags_queue.insert(0, (x, y+1))
                        self.flags_queue.insert(0, (x+1, y+1))
                        self.actions_queue.insert(0, (x+2, y+1))
            # 1 2 [2] 1
            elif (1 < x < self.rows-1):
                if self.board[x-2][y] == 1 and self.board[x-1][y] == 2 and self.board[x+1][y] == 1:
                    if self.board[x-2][y+1] == 0 and self.board[x-1][y+1] == 0 and self.board[x][y+1] == 0 and self.board[x+1][y+1] == 0:
                        self.actions_queue.insert(0, (x-2, y-1))
                        self.flags_queue.insert(0, (x-1, y-1))
                        self.flags_queue.insert(0, (x, y-1))
                        self.actions_queue.insert(0, (x+1, y-1))
                    elif self.board[x-2][y-1] == 0 and self.board[x-1][y-1] == 0 and self.board[x][y-1] == 0 and self.board[x+1][y-1] == 0:
                        self.actions_queue.insert(0, (x-2, y+1))
                        self.flags_queue.insert(0, (x-1, y+1))
                        self.flags_queue.insert(0, (x, y+1))
                        self.actions_queue.insert(0, (x+1, y+1))
            #  1
            # [2]
            #  2
            #  1
            elif (0 < y < self.cols-2):
                if self.board[x][y-1] == 1 and self.board[x][y+1] == 2 and self.board[x][y+2] == 1:
                    if self.board[x-1][y-1] == 0 and self.board[x-1][y] == 0 and self.board[x-1][y+1] == 0 and self.board[x-1][y+2] == 0:
                        self.actions_queue.insert(0, (x+1, y-1))
                        self.flags_queue.insert(0, (x+1, y))
                        self.flags_queue.insert(0, (x+1, y+1))
                        self.actions_queue.insert(0, (x+1, y+2))
                    elif self.board[x+1][y-1] == 0 and self.board[x+1][y] == 0 and self.board[x+1][y+1] == 0 and self.board[x+1][y+2] == 0:
                        self.actions_queue.insert(0, (x-1, y-1))
                        self.flags_queue.insert(0, (x-1, y))
                        self.flags_queue.insert(0, (x-1, y+1))
                        self.actions_queue.insert(0, (x-1, y+2))
            #  1
            #  2
            # [2]
            #  1
            elif (1 < y < self.cols-1):
                if self.board[x][y-2] == 1 and self.board[x][y-1] == 2 and self.board[x][y+1] == 1:
                    if self.board[x-1][y-2] == 0 and self.board[x-1][y-1] == 0 and self.board[x-1][y] == 0 and self.board[x-1][y+1] == 0:
                        self.actions_queue.insert(0, (x+1, y-2))
                        self.flags_queue.insert(0, (x+1, y-1))
                        self.flags_queue.insert(0, (x+1, y))
                        self.actions_queue.insert(0, (x+1, y+1))
                    elif self.board[x+1][y-2] == 0 and self.board[x+1][y-1] == 0 and self.board[x+1][y] == 0 and self.board[x+1][y+1] == 0:
                        self.actions_queue.insert(0, (x-1, y-2))
                        self.flags_queue.insert(0, (x-1, y-1))
                        self.flags_queue.insert(0, (x-1, y))
                        self.actions_queue.insert(0, (x-1, y+1))
        # 2 [3] 2
        elif self.board[x][y] == 3 and (1 < x < self.rows-2) and (1 < y < self.cols-2):
            if self.board[x-1][y] == 2 and self.board[x+1][y] == 2:  # 2-3-2
                if self.board[x-1][y+1] == 0 and self.board[x][y+1] == 0 and self.board[x+1][y+1] == 0:
                    self.actions_queue.insert(0, (x-2, y-1))
                    self.flags_queue.insert(0, (x-1, y-1))
                    self.flags_queue.insert(0, (x, y-1))
                    self.flags_queue.insert(0, (x+1, y-1))
                    self.actions_queue.insert(0, (x+2, y-1))
                elif self.board[x-1][y-1] == 0 and self.board[x][y-1] == 0 and self.board[x+1][y-1] == 0:
                    self.actions_queue.insert(0, (x-2, y+1))
                    self.flags_queue.insert(0, (x-1, y+1))
                    self.flags_queue.insert(0, (x, y+1))
                    self.flags_queue.insert(0, (x+1, y+1))
                    self.actions_queue.insert(0, (x-2, y+1))
            elif self.board[x][y+1] == 2 and self.board[x][y-1] == 2:
                if self.board[x-1][y+1] == 0 and self.board[x-1][y] == 0 and self.board[x-1][y-1] == 0:
                    self.actions_queue.insert(0, (x+1, y+2))
                    self.flags_queue.insert(0, (x+1, y+1))
                    self.flags_queue.insert(0, (x+1, y))
                    self.flags_queue.insert(0, (x+1, y-1))
                    self.actions_queue.insert(0, (x+1, y-2))
                elif self.board[x+1][y+1] == 0 and self.board[x+1][y] == 0 and self.board[x+1][y-1] == 0:
                    self.actions_queue.insert(0, (x-1, y+2))
                    self.flags_queue.insert(0, (x-1, y+1))
                    self.flags_queue.insert(0, (x-1, y))
                    self.flags_queue.insert(0, (x-1, y-1))
                    self.actions_queue.insert(0, (x-1, y-2))
        # 1 [2] C and C [2] 1 last resort
        elif self.board[x][y] == 2 and (0 < x < self.rows-1) and (0 < y < self.cols-1):
            if self.board[x-1][y] == 1:  # 1-2-C
                if self.board[x-1][y-1] == 0 and self.board[x][y-1] == 0:
                    self.flags_queue.insert(0, (x+1, y+1))
                elif self.board[x-1][y+1] == 0 and self.board[x][y+1] == 0:
                    self.flags_queue.insert(0, (x+1, y-1))
            elif self.board[x+1][y] == 1:  # C-2-1
                if self.board[x+1][y-1] == 0 and self.board[x][y-1] == 0:
                    self.flags_queue.insert(0, (x-1, y+1))
                elif self.board[x+1][y+1] == 0 and self.board[x][y+1] == 0:
                    self.flags_queue.insert(0, (x-1, y-1))
            elif self.board[x][y+1] == 1:
                if self.board[x+1][y+1] == 0 and self.board[x+1][y] == 0:
                    self.flags_queue.insert(0, (x-1, y-1))
                elif self.board[x-1][y+1] == 0 and self.board[x-1][y] == 0:
                    self.flags_queue.insert(0, (x+1, y-1))
            elif self.board[x][y-1] == 1:
                if self.board[x+1][y-1] == 0 and self.board[x+1][y] == 0:
                    self.flags_queue.insert(0, (x-1, y+1))
                elif self.board[x-1][y-1] == 0 and self.board[x-1][y] == 0:
                    self.flags_queue.insert(0, (x+1, y+1))
