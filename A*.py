import tkinter as tk
from tkinter import messagebox
from heapq import heappush, heappop


class MazeSolver:
    def __init__(self, maze, initial, goal):
        self.maze = maze
        self.start = initial
        self.goal = goal
        self.rows = len(maze)
        self.cols = len(maze[0])

    def heuristic(self, position):
        """Calculate Manhattan distance heuristic."""
        return abs(position[0] - self.goal[0]) + abs(position[1] - self.goal[1])

    def solve_a_star(self):
        """Solve the maze using the A* algorithm."""
        open_set = []
        heappush(open_set, (0, self.start))
        came_from = {}
        g_score = {self.start: 0}
        explored = set()

        while open_set:
            _, current = heappop(open_set)

            if current == self.goal:
                path = self.reconstruct_path(came_from, current)
                return path, len(explored)

            explored.add(current)

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)

                if (0 <= neighbor[0] < self.rows and 0 <= neighbor[1] < self.cols and
                        self.maze[neighbor[0]][neighbor[1]] == 0 and neighbor not in explored):
                    tentative_g_score = g_score[current] + 1

                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + self.heuristic(neighbor)
                        heappush(open_set, (f_score, neighbor))

        return None, len(explored)

    def reconstruct_path(self, came_from, current):
        """Reconstruct the path from the goal to the start."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver (A*)")

        self.rows = 0
        self.cols = 0
        self.blocked_cells = set()
        self.start = None
        self.end = None

        # Create two pages
        self.page1 = tk.Frame(root, padx=20, pady=20)
        self.page2 = tk.Frame(root, padx=20, pady=20)

        # Configure layout
        for page in (self.page1, self.page2):
            page.grid(row=0, column=0, sticky="nsew")

        self.grid_frame = None
        self.result_grid_frame = None

        # Configure the root window for resizing
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Initialize pages
        self.create_page1()
        self.create_page2()

        # Show the first page initially
        self.page1.tkraise()

    def create_page1(self):
        """Page 1: Input rows, columns, and define blocked cells"""
        tk.Label(self.page1, text="Number of Rows:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.rows_entry = tk.Entry(self.page1, width=5)
        self.rows_entry.grid(row=0, column=1, sticky="w")

        tk.Label(self.page1, text="Number of Columns:", anchor="w").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.cols_entry = tk.Entry(self.page1, width=5)
        self.cols_entry.grid(row=0, column=3, sticky="w")

        create_grid_button = tk.Button(self.page1, text="Create Grid", command=self.create_grid)
        create_grid_button.grid(row=1, column=0, columnspan=4, pady=10)

        next_page_button = tk.Button(self.page1, text="Next", command=self.show_page2, state="disabled")
        next_page_button.grid(row=2, column=0, columnspan=4, pady=10)
        self.next_page_button = next_page_button

    def create_grid(self):
        """Create a grid of labels to mark blocked cells."""
        try:
            self.rows = int(self.rows_entry.get())
            self.cols = int(self.cols_entry.get())

            if self.grid_frame:
                self.grid_frame.destroy()
            self.grid_frame = tk.Frame(self.page1, padx=10, pady=10)
            self.grid_frame.grid(row=3, column=0, columnspan=4, pady=(10, 0), sticky="nsew")

            self.page1.grid_rowconfigure(3, weight=1)
            self.page1.grid_columnconfigure(0, weight=1)

            self.blocked_cells = set()
            for r in range(self.rows):
                for c in range(self.cols):
                    label_text = f"({r},{c})"
                    label = tk.Label(self.grid_frame, text=label_text, width=5, height=2, relief="solid", bg="lightblue")
                    label.grid(row=r, column=c, sticky="nsew")
                    label.bind("<Button-1>", lambda e, r=r, c=c: self.toggle_block(r, c))

            self.next_page_button.config(state="normal")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for rows and columns.")

    def toggle_block(self, row, col):
        """Toggle blocked cells by changing the label color."""
        label = self.grid_frame.grid_slaves(row=row, column=col)[0]
        if (row, col) not in self.blocked_cells:
            label.config(bg="red")
            self.blocked_cells.add((row, col))
        else:
            label.config(bg="lightblue")
            self.blocked_cells.remove((row, col))

    def create_page2(self):
        """Page 2: Input start/goal positions and show the path."""
        tk.Label(self.page2, text="Start Position (x, y):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.start_x_entry = tk.Entry(self.page2, width=5)
        self.start_y_entry = tk.Entry(self.page2, width=5)
        self.start_x_entry.grid(row=0, column=1, sticky="w")
        self.start_y_entry.grid(row=0, column=2, sticky="w")

        tk.Label(self.page2, text="Goal Position (x, y):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.end_x_entry = tk.Entry(self.page2, width=5)
        self.end_y_entry = tk.Entry(self.page2, width=5)
        self.end_x_entry.grid(row=1, column=1, sticky="w")
        self.end_y_entry.grid(row=1, column=2, sticky="w")

        find_path_button = tk.Button(self.page2, text="Find Path", command=self.find_path)
        find_path_button.grid(row=2, column=0, columnspan=4, pady=10)

        self.result_text = tk.Text(self.page2, height=10, width=40)
        self.result_text.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.cost_label = tk.Label(self.page2, text="", font=("Arial", 12))
        self.cost_label.grid(row=4, column=0, columnspan=4, pady=5)

        # Configure dynamic resizing
        self.page2.grid_rowconfigure(3, weight=1)
        self.page2.grid_columnconfigure(0, weight=1)

    def display_path_on_grid(self, path):
        """Display the maze grid and highlight the solution path."""
        if self.result_grid_frame:
            self.result_grid_frame.destroy()

        self.result_grid_frame = tk.Frame(self.page2, padx=10, pady=10)
        self.result_grid_frame.grid(row=5, column=0, columnspan=4, pady=10, sticky="nsew")

        self.page2.grid_rowconfigure(5, weight=1)
        self.page2.grid_columnconfigure(0, weight=1)

        for r in range(self.rows):
            for c in range(self.cols):
                color = "lightblue"
                text = f"({r},{c})"

                if (r, c) == self.start:
                    color = "lightgreen"
                    text = "Start"
                elif (r, c) == self.end:
                    color = "lightblue"
                    text = "End"
                elif (r, c) in self.blocked_cells:
                    color = "red"
                elif (r, c) in path:
                    color = "green"

                label = tk.Label(self.result_grid_frame, text=text, width=5, height=2, relief="solid", bg=color)
                label.grid(row=r, column=c, sticky="nsew")

    def show_page2(self):
        """Switch to Page 2."""
        self.page2.tkraise()

    def generate_maze(self):
        """Generate a maze array based on blocked cells."""
        maze = [[0] * self.cols for _ in range(self.rows)]
        for r, c in self.blocked_cells:
            maze[r][c] = 1
        return maze

    def find_path(self):
        """Find and display the solution path."""
        try:
            start_x = int(self.start_x_entry.get())
            start_y = int(self.start_y_entry.get())
            end_x = int(self.end_x_entry.get())
            end_y = int(self.end_y_entry.get())

            self.start = (start_x, start_y)
            self.end = (end_x, end_y)

            # Validate if start or end position is blocked
            if self.start in self.blocked_cells:
                messagebox.showerror("Invalid Start Position", "The start position is in a blocked cell.")
                return
            if self.end in self.blocked_cells:
                messagebox.showerror("Invalid Goal Position", "The goal position is in a blocked cell.")
                return

            maze = self.generate_maze()
            solver = MazeSolver(maze, self.start, self.end)

            solution_path, total_cost = solver.solve_a_star()

            self.result_text.delete(1.0, tk.END)
            if solution_path:
                path_display = ['({},{})'.format(pos[0], pos[1]) for pos in solution_path]
                self.result_text.insert(tk.END, '\n'.join(path_display))

                # Calculate optimized cost (steps in the path minus 1)
                optimized_cost = len(solution_path) - 1
                self.cost_label.config(text=f"Total explored cost: {total_cost}\nOptimized path cost: {optimized_cost}")
                self.display_path_on_grid(solution_path)
            else:
                messagebox.showinfo("No Path", "No valid path found!")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for start and goal positions.")


# Initialize the Tkinter root and application
root = tk.Tk()
app = MazeApp(root)
root.mainloop()
