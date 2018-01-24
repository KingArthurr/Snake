from gameobjects import GameObject
from move import Direction, Move

import time


class Agent:
    # just for the measurements how many food on average per trial
    score = 0  # score at the moment of the turn, gives final score of each trial
    totalscore = 0  # total score of allgames combined
    gameamount = 0  # used to get average by dividing totalscore / gameamount

    # initilazie snake full body (head, body, tail. Its a map containing all body arts with head = 1 and tail = 1 of
    # the snake. Its to track all parts.
    snake = {}


    # Used to calc run time of A* search funtion
    total_runs_time = 0
    total_runs = 0

    # Done by the teacher
    def get_move(self, board, score, turns_alive, turns_to_starve, direction):
        """This function behaves as the 'brain' of the snake. You only need to change the code in this function for
        the project. Every turn the agent needs to return a move. This move will be executed by the snake. If this
        functions fails to return a valid return (see return), the snake will die (as this confuses its tiny brain
        that much that it will explode). The starting direction of the snake will be North.

        :param board: A two dimensional array representing the current state of the board. The upper left most
        coordinate is equal to (0,0) and each coordinate (x,y) can be accessed by executing board[x][y]. At each
        coordinate a GameObject is present. This can be either GameObject.EMPTY (meaning there is nothing at the
        given coordinate), GameObject.FOOD (meaning there is food at the given coordinate), GameObject.WALL (meaning
        there is a wall at the given coordinate. TIP: do not run into them), GameObject.SNAKE_HEAD (meaning the head
        of the snake is located there) and GameObject.SNAKE_BODY (meaning there is a body part of the snake there.
        TIP: also, do not run into these). The snake will also die when it tries to escape the board (moving out of
        the boundaries of the array)

        :param score: The current score as an integer. Whenever the snake eats, the score will be increased by one.
        When the snake tragically dies (i.e. by running its head into a wall) the score will be reset. In ohter
        words, the score describes the score of the current (alive) worm.

        :param turns_alive: The number of turns (as integer) the current snake is alive.

        :param turns_to_starve: The number of turns left alive (as integer) if the snake does not eat. If this number
        reaches 1 and there is not eaten the next turn, the snake dies. If the value is equal to -1, then the option
        is not enabled and the snake can not starve.

        :param direction: The direction the snake is currently facing. This can be either Direction.NORTH,
        Direction.SOUTH, Direction.WEST, Direction.EAST. For instance, when the snake is facing east and a move
        straight is returned, the snake wil move one cell to the right.

        :return: The move of the snake. This can be either Move.LEFT (meaning going left), Move.STRAIGHT (meaning
        going straight ahead) and Move.RIGHT (meaning going right). The moves are made from the viewpoint of the
        snake. This means the snake keeps track of the direction it is facing (North, South, West and East).
        Move.LEFT and Move.RIGHT changes the direction of the snake. In example, if the snake is facing north and the
        move left is made, the snake will go one block to the left and change its direction to west.
        """

        self.score = score  # self.score is score in the begnning, it will increase during the game through score

        # scans the board for width, height, head, tail, body, food, walls. slef.scan(board) returns the values for
        # all those variable
        board_width, board_height, snake_head, snake_tail, snake_body, food, walls = self.scan_board(board)

        # no move yet, and no path yet, path is empty list
        path = []
        move = False

        "SEARCH FOR FOOD"
        """"agent has a list with all coordinates of the food because of previous scan/function self.scan(board) it 
        enters the for-loop. For each food within food-list it checks with A* which is the best path this is the 
        final selection og finding a path !!searchs for shortest move by calling the A* function!! 1) checks is path 
        exists and your not dead before your reach that food unit (nothing is in thte way) it will take it always (
        new_path) for one specific unit in the food list (first one in the food list) 1.2) checks if from that path 
        that was just found (food unit) there exists a way to one of the (two) other food units 2) checks the ath for 
        the second and third  in the lsit and checks if path exists and if thispath is shorter that the other and in 
        case it will take that path 3) if finds a part or DOES NOT: than it will select GO RANDOM -> see go dandom 

        """
        for unit in food:
            new_path = self.a_search_shortest(snake_head, unit, board_width, board_height, snake_head, snake_body,
                                              # returns a full path to the food if it exists
                                              walls)
            if new_path != False and (path == [] or len(path) > len(new_path) and (
                    len(new_path) < turns_to_starve or turns_to_starve == -1)):
                foods = food.copy()
                foods.remove(unit)

                for foodsels in foods:
                    next_path = self.a_search_shortest(unit, foodsels, board_width, board_height, snake_head,
                                                       snake_body + new_path,
                                                       walls)
                    if next_path != False:
                        path = new_path
        # get the move for the get.move function and get.more returns move or False.
        if path:
            move = self.get_next_move(path, direction)

            # if move is still false after searching for move it will call the Go random function
        """"Go random"""
        """" Looks at the neighbores (4) of the snake head and picks the one with the biggest heuristic values: sums 
        the values from all three food units up. Which is the farest away in total.    
        """
        if not move:
            path = []
            new_h = 0
            old_h = 0
            for adj in self.get_adj(snake_head, board_width, board_height, snake_head, snake_body,
                                    walls):  # returns all neighbores of coordiante
                if 0 < adj[0] < board_width and 0 < adj[1] < board_width:  # try to keep bourder free
                    for unit in food:  # calculates the heuristic value of the neighbore
                        new_h += self.heuristic_cost_estimate(adj, unit)
                    if new_h > old_h:  # checks on all and selects the one woth the highest
                        path = [snake_head, adj]
            # chekc if there is a move to from that highest neighbore, and if this is still not the case it selects a
            #  rondom existing one
            if path:
                move = self.get_next_move(path, direction)
        if not move:
            for adj in self.get_adj(snake_head, board_width, board_height, snake_head, snake_body, walls):
                random = self.get_next_move([snake_head, adj], direction)
                if random != False:
                    move = random
        return move

        # Done by the teacher

    def on_die(self):
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.
        """

        # gets the average  for A2 b), c)
        self.gameamount += 1
        print('------TOTALSCORE =', self.total_runs_time / self.total_runs,self.total_runs, self.gameamount, '------')
        pass

    # check sposition of each object on the board: board is a list fild with a map and its coordiantes and the
    # objects which are connected with a cooridnate list is the width and the maps is the height of the board
    def scan_board(self, board):
        board_width = len(board) - 1
        board_height = len(board[0]) - 1
        snake_head = ()
        snake_tail = ()
        snake_body = []
        food = []
        walls = []
        # search through the whole lsit like in the the 4 in a row game. if it is equal food, add it to the food list
        #  etc.
        for x in range(board_width + 1):
            for y in range(board_height + 1):
                if board[x][y] == GameObject.SNAKE_HEAD:
                    snake_head = (x, y)
                if board[x][y] == GameObject.SNAKE_BODY:
                    snake_body.append((x, y))
                if board[x][y] == GameObject.FOOD:
                    food.append((x, y))
                if board[x][y] == GameObject.WALL:
                    walls.append((x, y))
                    # checks for every part in the snake lst, except the head which is in its own tuple (x,
                    # y). you check how long a part of the snake has been in the coordinate while the snake did one
                    # move furtehr
        for part in snake_body:
            if part in self.snake:
                self.snake[part] += 1
            else:
                self.snake[part] = 1
        for part in self.snake.copy().keys():
            if part not in snake_body:
                del self.snake[part]
        if snake_tail:
            snake_tail = max(self.snake, key=lambda k: self.snake[k])
        else:
            snake_tail = snake_head

        return board_width, board_height, snake_head, snake_tail, snake_body, food, walls

    #
    def a_search_shortest(self, start, goal, board_width, board_height, snake_head, snake_body, walls):
        start_time = time.time()

        closedSet = []
        openSet = [start]  # first positon from which you wanne go next (head or food to next food)
        cameFrom = {}

        gScore = {}
        gScore[start] = 0

        fScore = {}
        fScore[start] = self.heuristic_cost_estimate(start, goal)  # from start to goal

        while openSet:
            current = self.lowest_fscore(fScore, openSet)
            if current == goal:
                self.total_runs_time += time.time() - start_time
                self.total_runs += 1
                return self.reconstruct_path(cameFrom, start, goal)  # if you have found the goal

            # remove open set to the closed set
            openSet.remove(current)
            closedSet.append(current)

            for neighbour in self.get_adj(current, board_width, board_height, snake_head, snake_body, walls):
                if neighbour in closedSet:
                    continue

                tentative_gScore = gScore[current] + 1
                if neighbour not in openSet:
                    openSet.append(neighbour)
                elif tentative_gScore >= gScore[neighbour]:
                    continue

                cameFrom[neighbour] = current
                gScore[neighbour] = tentative_gScore
                fScore[neighbour] = gScore[neighbour] + self.heuristic_cost_estimate(neighbour, goal)

        self.total_runs_time += time.time() - start_time
        self.total_runs += 1
        return False

    # reutn the absolut value  of the heuristic value of x ad y to get a final result to calculate with, every step
    # is +1
    def heuristic_cost_estimate(self, start, goal):
        return abs((start[0] - goal[0]) + (start[1] - goal[1]))

    #
    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)  # optional
        path.reverse()  # optional
        if path:
            return path
        return False

    # gets the path, but just does the first move within the calucalted path. Calculate snext coordinate minus
    # current coordinate translate your move to the given variables which are festgelegt in other .py
    #
    def get_next_move(self, path, direction):
        move = False
        move_coord = (path[1][0] - path[0][0], path[1][1] - path[0][1])

        # direction to go
        moves_coord = {(0, 1): Direction.SOUTH, (0, -1): Direction.NORTH, (1, 0): Direction.EAST,
                       (-1, 0): Direction.WEST}
        move_direction = moves_coord.get(move_coord)

        # what does the direction mean from were snake is right now
        direction_right = {Direction.NORTH: Direction.EAST, Direction.EAST: Direction.SOUTH,
                           Direction.SOUTH: Direction.WEST, Direction.WEST: Direction.NORTH}
        direction_left = {Direction.NORTH: Direction.WEST, Direction.WEST: Direction.SOUTH,
                          Direction.SOUTH: Direction.EAST, Direction.EAST: Direction.NORTH}

        # final more to ceratin direction
        if move_direction == direction:
            move = Move.STRAIGHT
        elif direction_right.get(direction) == move_direction:
            move = Move.RIGHT
        elif direction_left.get(direction) == move_direction:
            move = Move.LEFT

        return move

    def lowest_fscore(self, fScore, openSet):
        next = openSet[0]
        for node in openSet:
            if fScore[next] > fScore[node]:
                next = node
        return next

    # get all neighboures of the current state which are availibe and do not lead into the body, wall (units in the
    # way) , head or border
    def get_adj(self, current, board_width, board_height, snake_head, snake_body, walls):
        adj_tiles = []
        adj_coord = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for coord in adj_coord:
            tile = (current[0] + coord[0], current[1] + coord[1])
            if (0 <= tile[0] <= board_width) and (0 <= tile[1] <= board_height) and \
                            tile != snake_head and tile not in snake_body and tile not in walls:
                adj_tiles.append(tile)
        return adj_tiles
