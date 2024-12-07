import tkinter as tk
from tkinter import messagebox


class MazeProblem:
    def __init__(self, maze, initial, goal):
        self.maze = maze
        self.initial = initial
        self.goal = goal
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.facts = {}  # Facts store paths for backward chaining
        self.explored = set()  # Track explored positions
        self.rules = [
            ("move_up", lambda pos: (pos[0] - 1, pos[1]), lambda pos: pos[0] > 0),
            ("move_down", lambda pos: (pos[0] + 1, pos[1]), lambda pos: pos[0] < self.rows - 1),
            ("move_left", lambda pos: (pos[0], pos[1] - 1), lambda pos: pos[1] > 0),
            ("move_right", lambda pos: (pos[0], pos[1] + 1), lambda pos: pos[1] < self.cols - 1),
        ]

    def is_within_bounds(self, position):
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols and self.maze[row][col] == 0

    def add_fact(self, position, path):
        if position not in self.facts:
            self.facts[position] = path
            self.explored.add(position)

    def apply_rules(self):
        self.add_fact(self.goal, [self.goal])

        while self.facts:
            current_facts = list(self.facts.items())
            for position, path in current_facts:
                if position == self.initial:
                    return list(reversed(path)), len(self.explored)

                del self.facts[position]

                for _, transform, condition in self.rules:
                    if condition(position):
                        new_position = transform(position)
                        if new_position not in self.explored and self.is_within_bounds(new_position):
                            self.add_fact(new_position, path + [new_position])

        return None, len(self.explored)


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver (Backward Chaining with GMP)")

        self.rows = 0
        self.cols = 0
        self.blocked_cells = set()
        self.start = None
        self.end = None

        self.page1 = tk.Frame(root, padx=20, pady=20)
        self.page2 = tk.Frame(root, padx=20, pady=20)

        for page in (self.page1, self.page2):
            page.grid(row=0, column=0, sticky="nsew")

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.grid_frame = None
        self.result_grid_frame = None

        self.create_page1()
        self.create_page2()

        self.page1.tkraise()

    def create_page1(self):
        tk.Label(self.page1, text="Number of Rows:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.rows_entry = tk.Entry(self.page1, width=5)
        self.rows_entry.grid(row=0, column=1)

        tk.Label(self.page1, text="Number of Columns:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.cols_entry = tk.Entry(self.page1, width=5)
        self.cols_entry.grid(row=0, column=3)

        create_grid_button = tk.Button(self.page1, text="Create Grid", command=self.create_grid)
        create_grid_button.grid(row=1, column=0, columnspan=4, pady=10)

        next_page_button = tk.Button(self.page1, text="Next", command=self.show_page2, state="disabled")
        next_page_button.grid(row=2, column=0, columnspan=4, pady=10)
        self.next_page_button = next_page_button

    def create_grid(self):
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
        label = self.grid_frame.grid_slaves(row=row, column=col)[0]
        if (row, col) not in self.blocked_cells:
            label.config(bg="red")
            self.blocked_cells.add((row, col))
        else:
            label.config(bg="lightblue")
            self.blocked_cells.remove((row, col))

    def create_page2(self):
        tk.Label(self.page2, text="Start Position (x, y):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.start_x_entry = tk.Entry(self.page2, width=5)
        self.start_y_entry = tk.Entry(self.page2, width=5)
        self.start_x_entry.grid(row=0, column=1)
        self.start_y_entry.grid(row=0, column=2)

        tk.Label(self.page2, text="Goal Position (x, y):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.end_x_entry = tk.Entry(self.page2, width=5)
        self.end_y_entry = tk.Entry(self.page2, width=5)
        self.end_x_entry.grid(row=1, column=1)
        self.end_y_entry.grid(row=1, column=2)

        find_path_button = tk.Button(self.page2, text="Find Path", command=self.find_path)
        find_path_button.grid(row=2, column=0, columnspan=4, pady=10)

        self.result_text = tk.Text(self.page2, height=10, width=40)
        self.result_text.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.cost_label = tk.Label(self.page2, text="", font=("Arial", 12))
        self.cost_label.grid(row=4, column=0, columnspan=4, pady=5)

    def display_path_on_grid(self, path):
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
                    color = "yellow"
                    text = "End"
                elif (r, c) in self.blocked_cells:
                    color = "red"
                elif (r, c) in path:
                    color = "green"

                label = tk.Label(self.result_grid_frame, text=text, width=5, height=2, relief="solid", bg=color)
                label.grid(row=r, column=c, sticky="nsew")

    def show_page2(self):
        self.page2.tkraise()

    def generate_maze(self):
        maze = [[0] * self.cols for _ in range(self.rows)]
        for r, c in self.blocked_cells:
            maze[r][c] = 1
        return maze

    def calculate_manhattan_distance(self, path):
        start = self.start
        distance = 0
        for pos in path:
            distance += abs(pos[0] - start[0]) + abs(pos[1] - start[1])
            start = pos
        return distance

    def find_path(self):
        try:
            start_x = int(self.start_x_entry.get())
            start_y = int(self.start_y_entry.get())
            end_x = int(self.end_x_entry.get())
            end_y = int(self.end_y_entry.get())

            if (start_x, start_y) in self.blocked_cells or (end_x, end_y) in self.blocked_cells:
                messagebox.showerror("Invalid Positions", "Start or End position is blocked.")
                return

            self.start = (start_x, start_y)
            self.end = (end_x, end_y)

            maze = self.generate_maze()
            problem = MazeProblem(maze, self.start, self.end)

            solution_path, total_explored = problem.apply_rules()

            if solution_path:
                path_display = ['({},{})'.format(pos[0], pos[1]) for pos in solution_path]
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, '\n'.join(path_display))

                optimized_cost = len(solution_path) - 1
                manhattan_cost = self.calculate_manhattan_distance(solution_path)
                self.cost_label.config(text=f"Total explored cost: {total_explored}\nOptimized path cost: {optimized_cost}")

                self.display_path_on_grid(solution_path)
            else:
                messagebox.showinfo("No Solution", "No path found.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for the positions.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()