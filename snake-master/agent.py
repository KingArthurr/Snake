from gameobjects import GameObject
from move import Direction, Move


class Agent:

    score = 0
    totalscore = 0
    gameamount = 0

    snake = {}

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
        self.score = score

        board_width, board_height, snake_head, snake_tail, snake_body, food, walls = self.scan_board(board)

        path = []
        move = False

        """"SEARCH FOR FOOD"""
        for unit in food:
            new_path = self.a_search_shortest(snake_head, unit, board_width, board_height, snake_head, snake_body,
                                              walls)
            if new_path != False and (path == [] or len(path) > len(new_path) and (len(new_path) < turns_to_starve or turns_to_starve == -1)):
                foods = food.copy()
                foods.remove(unit)

                for foodsels in foods:
                    next_path = self.a_search_shortest(unit, foodsels, board_width, board_height, snake_head, snake_body + new_path,
                                              walls)
                    if next_path != False:
                        path = new_path

        if path:
            move = self.get_next_move(path, direction)

        """"Go random"""
        if not move:
            path = []
            new_h = 0
            old_h = 0
            for adj in self.get_adj(snake_head,board_width,board_height,snake_head,snake_body,walls):
                if 0 < adj[0] < board_width and 0 < adj[1] < board_width:
                    for unit in food:
                        new_h += self.heuristic_cost_estimate(adj,unit)
                    if new_h > old_h:
                        path = [snake_head, adj]
            if path:
                move = self.get_next_move(path,direction)

        if not move:
            adjs = self.get_adj(snake_head,board_width,board_height,snake_head,snake_body,walls)
            if adjs:
                move = self.get_next_move([snake_head, adjs[0]], direction)
        return move

    def on_die(self):
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.
        """
        self.gameamount += 1
        self.totalscore += self.score
        print('------TOTALSCORE =', self.totalscore/self.gameamount,self.gameamount,'------')
        pass

    def scan_board(self, board):
        board_width = len(board)-1
        board_height = len(board[0])-1
        snake_head = ()
        snake_tail = ()
        snake_body = []
        food = []
        walls = []
        for x in range(board_width+1):
            for y in range(board_height+1):
                if board[x][y] == GameObject.SNAKE_HEAD:
                    snake_head = (x, y)
                if board[x][y] == GameObject.SNAKE_BODY:
                    snake_body.append((x, y))
                if board[x][y] == GameObject.FOOD:
                    food.append((x, y))
                if board[x][y] == GameObject.WALL:
                    walls.append((x, y))
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


    def a_search_shortest(self, start, goal, board_width, board_height, snake_head, snake_body, walls):
        closedSet = []
        openSet = [start]
        cameFrom = {}

        gScore = {}
        gScore[start] = 0

        fScore = {}
        fScore[start] = self.heuristic_cost_estimate(start, goal)

        while openSet:
            current = self.lowest_fscore(fScore, openSet)
            if current == goal:
                return self.reconstruct_path(cameFrom, start, goal)

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

        return False

    def heuristic_cost_estimate(self, start, goal):
        return abs((start[0] - goal[0]) + (start[1] - goal[1]))

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

    def get_next_move(self, path, direction):
        move = False
        move_coord = (path[1][0] - path[0][0], path[1][1] - path[0][1])

        moves_coord = {(0, 1): Direction.SOUTH, (0, -1): Direction.NORTH, (1, 0): Direction.EAST,
                       (-1, 0): Direction.WEST}
        move_direction = moves_coord.get(move_coord)

        direction_right = {Direction.NORTH: Direction.EAST, Direction.EAST: Direction.SOUTH,
                           Direction.SOUTH: Direction.WEST, Direction.WEST: Direction.NORTH}
        direction_left = {Direction.NORTH: Direction.WEST, Direction.WEST: Direction.SOUTH,
                          Direction.SOUTH: Direction.EAST, Direction.EAST: Direction.NORTH}

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

    def get_adj(self, current, board_width, board_height, snake_head, snake_body, walls):
        adj_tiles = []
        adj_coord = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for coord in adj_coord:
            tile = (current[0] + coord[0], current[1] + coord[1])
            if (0 <= tile[0] <= board_width) and (0 <= tile[1] <= board_height) and \
                            tile != snake_head and tile not in snake_body and tile not in walls:
                adj_tiles.append(tile)
        return adj_tiles