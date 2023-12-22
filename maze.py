from tkinter import Tk, BOTH, Canvas
import time, random

class Window:
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("TITLE")
        self.__root.protocol("WM_DELETE_WINDOW", self.close())
        self.canvas = Canvas(width=width, height=height)
        self.canvas.configure(background="white")
        self.canvas.pack()
        self.__running = False

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line, fill_color):
        line.draw(self.canvas, fill_color)

    def draw_cell(self, cell, fill_color):
        cell.draw(fill_color)

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def draw(self, canvas, fill_color):
        canvas.create_line(
            self.p1.x,
            self.p1.y,
            self.p2.x,
            self.p2.y,
            fill=fill_color,
            width = 2
            )

class Cell:
    def __init__(self, p1, p2, win):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall= True
        self.has_bottom_wall = True
        self.p1 = p1
        self.p2 = p2
        self.win = win
        self.visited = False


    def draw(self, fill_color):
        p1, p2 = self.p1, self.p2

        fc = "white" if not self.has_left_wall else fill_color
        line = Line(Point(p1.x, p1.y), Point(p1.x, p2.y))
        line.draw(self.win.canvas, fc)

        fc = "white" if not self.has_right_wall else fill_color
        line = Line(Point(p2.x, p1.y), Point(p2.x, p2.y))
        line.draw(self.win.canvas, fc)

        fc = "white" if not self.has_top_wall else fill_color
        line = Line(Point(p1.x, p1.y), Point(p2.x, p1.y))
        line.draw(self.win.canvas, fc)

        fc = "white" if not self.has_bottom_wall else fill_color
        line = Line(Point(p1.x, p2.y), Point(p2.x, p2.y))
        line.draw(self.win.canvas, fc)

    def draw_move(self, to_cell, undo=False):
        fill_color = "red"
        if undo:
            fill_color = "gray"

        p1 = Point((self.p1.x + self.p2.x)/2, (self.p1.y + self.p2.y)/2)
        p2 = Point((to_cell.p1.x + to_cell.p2.x)/2, (to_cell.p1.y + to_cell.p2.y)/2)

        line = Line(p1, p2)
        line.draw(self.win.canvas, fill_color)


        

class Maze:
    def __init__(
            self,
            p,
            num_rows,
            num_cols,
            cell_size_x,
            cell_size_y,
            win,
            seed=None,
        ):
        self.p = p 
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        self.__cells = [[True] * num_rows for x in range(num_cols)]
        if seed is not None:
            self.seed = random.seed(self.seed)
        else:
            self.seed = seed

        self._create_cells()
        self._break_entrance_and_exit()
        self._break_walls_r(0,0)
        self._reset_cells_visited()

    def _create_cells(self):
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                p = self.p
                cell_size_x, cell_size_y = self.cell_size_x, self.cell_size_y
                self.__cells[col][row] = Cell(
                    Point(p.x + (col * p.x), p.y + (row * p.y)),
                    Point(p.x + (col * p.x) + cell_size_x, p.y + (row * p.y) + cell_size_y),
                    self.win,
                )
                self.__cells[col][row].draw("black")
                self._animate()

    def _draw_cell(self, i, j):
        self.__cells[i][j].draw("black")

    def _animate(self):
        self.win.redraw()
        time.sleep(0.05)

    def _break_entrance_and_exit(self):
        self.__cells[0][0].has_top_wall = False
        self.__cells[self.num_cols-1][self.num_rows-1].has_bottom_wall = False
        
        self._draw_cell(0,0)
        self._draw_cell(self.num_cols-1,self.num_rows-1)

    def _break_walls_r(self, i, j):
        self.__cells[i][j].visited = True
        while True:
            to_visit = []

            if i + 1 < len(self.__cells) and self.__cells[i+1][j] is not None and not self.__cells[i+1][j].visited:
                to_visit.append([i+1, j, 'r'])

            if j + 1 < len(self.__cells[0]) and self.__cells[i][j+1] is not None and not self.__cells[i][j+1].visited:
                to_visit.append([i, j+1, 'd'])

            if i - 1 >= 0 and self.__cells[i-1][j] is not None and not self.__cells[i-1][j].visited:
                to_visit.append([i-1, j, 'l'])

            if j - 1 >= 0 and self.__cells[i][j-1] is not None and not self.__cells[i][j-1].visited:
                to_visit.append([i, j-1, 'u'])
            
            if not to_visit:
                return

            
            direction = random.choice(to_visit)

            if direction[2] == "r":
                self.__cells[i][j].has_right_wall = False
                self.__cells[direction[0]][direction[1]].has_left_wall = False

            elif direction[2] == "d":
                self.__cells[i][j].has_bottom_wall = False
                self.__cells[direction[0]][direction[1]].has_top_wall = False

            elif direction[2] == "l":
                self.__cells[i][j].has_left_wall = False
                self.__cells[direction[0]][direction[1]].has_right_wall = False

            elif direction[2] == "u":
                self.__cells[i][j].has_top_wall = False
                self.__cells[direction[0]][direction[1]].has_bottom_wall = False

            self._draw_cell(i, j)
            self._draw_cell(direction[0],direction[1])
        
            self._break_walls_r(direction[0], direction[1])

    def _reset_cells_visited(self):
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                self.__cells[col][row].visited = False

    def solve(self):
        return self._solve_r(0,0)


    def _solve_r(self, i, j):
        print("SOLVE_R")
        self._animate()
        self.__cells[i][j].visited = True

        if i == self.num_cols-1 and j == self.num_rows-1:
            return True

        to_visit = []
        while True:
            if i + 1 < len(self.__cells) and self.__cells[i+1][j] is not None and not self.__cells[i+1][j].visited and self.__cells[i][j].has_right_wall is False:
                to_visit.append([i+1, j, 'r'])

            if j + 1 < len(self.__cells[0]) and self.__cells[i][j+1] is not None and not self.__cells[i][j+1].visited and self.__cells[i][j].has_bottom_wall is False:
                to_visit.append([i, j+1, 'd'])

            if i - 1 >= 0 and self.__cells[i-1][j] is not None and not self.__cells[i-1][j].visited and self.__cells[i][j].has_left_wall is False:
                to_visit.append([i-1, j, 'l'])

            if j - 1 >= 0 and self.__cells[i][j-1] is not None and not self.__cells[i][j-1].visited and self.__cells[i][j].has_top_wall is False:
                to_visit.append([i, j-1, 'u'])


            direction = to_visit.pop(0)
            self.__cells[i][j].draw_move(self.__cells[direction[0]][direction[1]])

            rec = self._solve_r(direction[0], direction[1])
            if rec:
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[direction[0]][direction[1]], undo=True)

            if not to_visit:
                break
        return False

def main():
    win = Window(800,600)

    maze = Maze(Point(50,50),5,5,50,50,win)
    res = maze.solve()
    print(res)
    # win.draw_line(Line(Point(100,100), Point(200,200)), "black")

    # cell1 = Cell(Point(100,100), Point(200,200), win)
    # cell2 = Cell(Point(200,100), Point(300,200), win)
    # win.draw_cell(cell1, "black")
    # win.draw_cell(cell2, "black")

    # cell2.draw_move(cell1)

    win.wait_for_close()

main()
