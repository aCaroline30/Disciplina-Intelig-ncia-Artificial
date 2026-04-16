import tkinter as tk
from tkinter import messagebox
import time
import heapq
import random

# --- Lógica do Jogo e Algoritmos ---

class State:
    def __init__(self, board, parent=None, move="", depth=0, cost=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.cost = cost # Usado para heurística

    def __lt__(self, other):
        return self.cost < other.cost

    def get_blank_pos(self):
        idx = self.board.index(0)
        return idx // 3, idx % 3

    def is_goal(self):
        return self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0]

    def expand(self):
        successors = []
        r, c = self.get_blank_pos()
        moves = {
            "Cima": (r - 1, c),
            "Baixo": (r + 1, c),
            "Esquerda": (r, c - 1),
            "Direita": (r, c + 1)
        }

        for move, (nr, nc) in moves.items():
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = list(self.board)
                idx1 = r * 3 + c
                idx2 = nr * 3 + nc
                new_board[idx1], new_board[idx2] = new_board[idx2], new_board[idx1]
                successors.append(State(new_board, self, move, self.depth + 1))
        return successors

def get_out_of_place(board):
    goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    count = 0
    for i in range(len(board)):
        if board[i] != 0 and board[i] != goal[i]:
            count += 1
    return count

def get_manhattan(board):
    distance = 0
    for i in range(len(board)):
        if board[i] != 0:
            # Posição atual
            r, c = i // 3, i % 3
            # Posição alvo
            target = board[i] - 1
            tr, tc = target // 3, target % 3
            distance += abs(r - tr) + abs(c - tc)
    return distance

def solve(initial_board, mode):
    start_time = time.time()
    initial_state = State(initial_board)
    
    # Configuração de custo inicial baseada no modo
    if mode == "bfs":
        queue = [initial_state]
    else:
        # A* ou Ganancioso (Heurística pura)
        if mode == "misplaced":
            initial_state.cost = get_out_of_place(initial_board)
        elif mode == "manhattan_plus":
            initial_state.cost = get_out_of_place(initial_board) + get_manhattan(initial_board)
        
        queue = [(initial_state.cost, initial_state)]
        heapq.heapify(queue)

    visited = set()
    visited.add(tuple(initial_board))
    expanded_count = 0

    while queue:
        if mode == "bfs":
            current = queue.pop(0)
        else:
            _, current = heapq.heappop(queue)

        expanded_count += 1

        if current.is_goal():
            end_time = time.time()
            path = []
            while current.parent:
                path.append(current.board)
                current = current.parent
            return path[::-1], expanded_count, end_time - start_time

        for succ in current.expand():
            board_tuple = tuple(succ.board)
            if board_tuple not in visited:
                visited.add(board_tuple)
                
                if mode == "misplaced":
                    succ.cost = get_out_of_place(succ.board)
                    heapq.heappush(queue, (succ.cost, succ))
                elif mode == "manhattan_plus":
                    # f(x) = g(x) + h(x) -> g=misplaced, h=manhattan
                    succ.cost = get_out_of_place(succ.board) + get_manhattan(succ.board)
                    heapq.heappush(queue, (succ.cost, succ))
                else: # bfs
                    queue.append(succ)
    return None

# --- Interface Gráfica ---

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver")
        self.board = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        self.buttons = []
        self.create_widgets()

    def create_widgets(self):
        # Frame do Tabuleiro
        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=20)

        for i in range(9):
            btn = tk.Button(board_frame, text="", font=('Helvetica', 20, 'bold'), 
                            width=4, height=2, bg="lightgrey")
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)
        self.update_board()

        # Controles
        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(pady=10)

        tk.Button(ctrl_frame, text="Embaralhar", command=self.shuffle_board).grid(row=0, column=0, columnspan=3, sticky="we", pady=5)
        
        tk.Button(ctrl_frame, text="Busca Horizontal (BFS)", command=lambda: self.run_solve("bfs")).grid(row=1, column=0, padx=5)
        tk.Button(ctrl_frame, text="Heurística: g(x)", command=lambda: self.run_solve("misplaced")).grid(row=1, column=1, padx=5)
        tk.Button(ctrl_frame, text="Heurística: g(x) + h(x)", command=lambda: self.run_solve("manhattan_plus")).grid(row=1, column=2, padx=5)

        # Labels de Status
        self.status_label = tk.Label(self.root, text="Pronto para iniciar", fg="blue")
        self.status_label.pack(pady=10)

    def update_board(self, board=None):
        if board: self.board = board
        for i, val in enumerate(self.board):
            self.buttons[i].config(text=str(val) if val != 0 else "", 
                                   bg="white" if val != 0 else "darkgrey")

    def shuffle_board(self):
        # Gera um estado resolvível fazendo movimentos aleatórios
        for _ in range(100):
            r, c = self.board.index(0)//3, self.board.index(0)%3
            possible_moves = []
            if r > 0: possible_moves.append(-3)
            if r < 2: possible_moves.append(3)
            if c > 0: possible_moves.append(-1)
            if c < 2: possible_moves.append(1)
            
            move = random.choice(possible_moves)
            idx = self.board.index(0)
            self.board[idx], self.board[idx+move] = self.board[idx+move], self.board[idx]
        self.update_board()
        self.status_label.config(text="Tabuleiro Embaralhado!", fg="black")

    def run_solve(self, mode):
        result = solve(self.board, mode)
        if result:
            path, expanded, duration = result
            self.animate_solution(path)
            stats = f"Tempo: {duration:.4f}s | Expansões: {expanded} | Movimentos: {len(path)}"
            self.status_label.config(text=stats, fg="green")
        else:
            messagebox.showerror("Erro", "Solução não encontrada.")

    def animate_solution(self, path):
        if path:
            next_step = path.pop(0)
            self.update_board(next_step)
            self.root.after(300, lambda: self.animate_solution(path))

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()