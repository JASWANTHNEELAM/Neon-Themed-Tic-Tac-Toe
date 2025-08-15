import tkinter as tk
from tkinter import messagebox
import random
import itertools

# =========================
# Neon Radium Colors
# =========================
BG_COLOR = "#0a0f1b"       # deep black-blue
PANEL_COLOR = "#0f172a"    # dark panel
CELL_COLOR = "#1e293b"     # default cell
CELL_HOVER = "#334155"     # hover cell
TEXT_COLOR = "#a5f3fc"     # neon cyan
ACCENT = "#0ff"             # bright cyan accent
ACCENT_2 = "#38bdf8"        # lighter cyan
WIN_COLOR = "#ff0"          # yellow highlight for win
BORDER_COLOR = "#0ea5e9"    # panel border

SYMBOLS = ["❌", "⭕", "⭐", "❤️", "🐱", "⚡", "🍀", "🌀", "🔥", "🌙"]

WINS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

# =========================
# AI Helpers
# =========================
def get_available_moves(board):
    return [i for i, v in enumerate(board) if v is None]

def check_winner(board):
    for a,b,c in WINS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return "Draw" if all(board) else None

def minimax(board, is_max, ai_symbol, human_symbol):
    winner = check_winner(board)
    if winner == ai_symbol:
        return {"score": 10}
    if winner == human_symbol:
        return {"score": -10}
    if winner == "Draw":
        return {"score": 0}

    if is_max:
        best = {"score": -float("inf")}
        for m in get_available_moves(board):
            board[m] = ai_symbol
            res = minimax(board, False, ai_symbol, human_symbol)
            board[m] = None
            if res["score"] > best["score"]:
                best = {"score": res["score"], "index": m}
        return best
    else:
        best = {"score": float("inf")}
        for m in get_available_moves(board):
            board[m] = human_symbol
            res = minimax(board, True, ai_symbol, human_symbol)
            board[m] = None
            if res["score"] < best["score"]:
                best = {"score": res["score"], "index": m}
        return best

def ai_pick_move(board, level, ai_symbol, human_symbol):
    moves = get_available_moves(board)
    if not moves:
        return None
    if level == "easy":
        return random.choice(moves)
    elif level == "normal":
        for m in moves:
            board[m] = ai_symbol
            if check_winner(board) == ai_symbol:
                board[m] = None
                return m
            board[m] = None
        for m in moves:
            board[m] = human_symbol
            if check_winner(board) == human_symbol:
                board[m] = None
                return m
            board[m] = None
        return random.choice(moves)
    else:  # hard
        return minimax(board[:], True, ai_symbol, human_symbol)["index"]

# =========================
# App Class
# =========================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe — Neon Radium")
        self.configure(bg=BG_COLOR)
        self.state("zoomed")  # fullscreen
        self.resizable(True, True)

        # Game state
        self.mode = tk.StringVar(value="PvP")
        self.ai_level = tk.StringVar(value="easy")
        self.p1_symbol = tk.StringVar(value="❌")
        self.p2_symbol = tk.StringVar(value="⭕")
        self.turn = "p1"
        self.board = [None]*9

        # Glow iterator
        self.glow_iter = itertools.cycle([ACCENT, ACCENT_2, "#ff0", "#ff00ff"])
        
        # Container
        container = tk.Frame(self, bg=BG_COLOR)
        container.pack(fill="both", expand=True,anchor="center")
        self.frames = {}
        for F in (PageMode, PageSetup, PageGame):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PageMode")
        self.after(500, self.animate_glow)

    def animate_glow(self):
        color = next(self.glow_iter)
        for frame in self.frames.values():
            if hasattr(frame, "pulse"):
                frame.pulse(color)
        self.after(500, self.animate_glow)

    def show_frame(self, name):
        self.frames[name].tkraise()

    def reset_board(self):
        self.board = [None]*9
        self.turn = "p1"

    def start_game(self):
        if self.p1_symbol.get() == self.p2_symbol.get():
            messagebox.showwarning("Symbols", "Choose different symbols.")
            return
        self.reset_board()
        game_page = self.frames["PageGame"]
        game_page.refresh_board()
        self.show_frame("PageGame")

# =========================
# Page Classes
# =========================
class RadiumPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=PANEL_COLOR, highlightthickness=4, highlightbackground=BORDER_COLOR)
    def pulse(self, color):
        self.configure(highlightbackground=color)

class PageMode(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        center_frame = tk.Frame(self, bg=BG_COLOR)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.title = tk.Label(self, text="Tic Tac Toe — Neon Radium",
                              bg=BG_COLOR, fg=ACCENT, font=("Segoe UI", 30, "bold"))
        self.title.pack(pady=40)

        panel = RadiumPanel(self)
        panel.pack(padx=40, pady=20)
        inner = tk.Frame(panel, bg=PANEL_COLOR)
        inner.pack(padx=20, pady=20)

        tk.Label(inner, text="Choose Mode", bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 16, "bold"))\
            .pack(pady=10)
        for label, val in [("Player vs Player", "PvP"), ("Player vs Computer", "PvC")]:
            rb = tk.Radiobutton(inner, text=label, value=val, variable=controller.mode,
                                indicatoron=False, width=20, pady=10,
                                bg=CELL_COLOR, fg="black", selectcolor=ACCENT,
                                activebackground=CELL_HOVER, relief="flat", font=("Segoe UI", 12, "bold"))
            rb.pack(pady=8)

        tk.Button(inner, text="Next →", command=lambda: controller.show_frame("PageSetup"),
                  bg=ACCENT, fg="black", font=("Segoe UI", 12, "bold"), width=16, pady=10)\
            .pack(pady=20)
        self.panel = panel
    def pulse(self, color):
        self.panel.pulse(color)

class PageSetup(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        center_frame = tk.Frame(self, bg=BG_COLOR)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self, text="Setup Game", bg=BG_COLOR, fg=ACCENT, font=("Segoe UI", 26, "bold"))\
            .pack(pady=30)
        self.panel = RadiumPanel(self)
        self.panel.pack(padx=40, pady=20)
        inner = tk.Frame(self.panel, bg=PANEL_COLOR)
        inner.pack(padx=20, pady=20)

        self.mode_label = tk.Label(inner, text="", bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 12))
        self.mode_label.pack(pady=8)
        self.ai_label = tk.Label(inner, text="AI Level", bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 12, "bold"))
        self.ai_label.pack(pady=6)
        self.ai_menu = tk.OptionMenu(inner, controller.ai_level, "easy","normal","hard")
        self.ai_menu.pack(pady=6)

        tk.Label(inner, text="Player 1 Symbol", bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 12, "bold")).pack(pady=6)
        self.p1_menu = tk.OptionMenu(inner, controller.p1_symbol, *SYMBOLS)
        self.p1_menu.pack(pady=4)
        tk.Label(inner, text="Player 2 Symbol", bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 12, "bold")).pack(pady=6)
        self.p2_menu = tk.OptionMenu(inner, controller.p2_symbol, *SYMBOLS)
        self.p2_menu.pack(pady=4)

        btn_frame = tk.Frame(inner, bg=PANEL_COLOR)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="← Back", command=lambda: controller.show_frame("PageMode"),
                  bg=CELL_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 12, "bold"), width=12, pady=8).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Start Game", command=controller.start_game,
                  bg=ACCENT, fg="black", font=("Segoe UI", 12, "bold"), width=16, pady=8).pack(side="left", padx=8)

        self.panel = self.panel

    def pulse(self, color):
        self.panel.pulse(color)

class PageGame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        center_frame = tk.Frame(self, bg=BG_COLOR)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        top = tk.Frame(self, bg=BG_COLOR)
        top.pack(pady=20)
        
        self.info = tk.Label(top, text="", bg=BG_COLOR, fg=ACCENT_2, font=("Segoe UI", 14, "bold"))
        self.info.pack()

        # Back button
        back_btn = tk.Button(top, text="← Back to Menu", bg=CELL_COLOR, fg=TEXT_COLOR,
                             font=("Segoe UI", 12, "bold"), width=16, pady=5,
                             command=self.back_to_menu)
        back_btn.pack(pady=10)

        self.panel = RadiumPanel(self)
        self.panel.pack(padx=50, pady=20)
        
        self.grid_frame = tk.Frame(self.panel, bg=PANEL_COLOR)
        self.grid_frame.pack(padx=20, pady=20)
        
        self.cells = []
        for i in range(9):
            btn = tk.Button(self.grid_frame, text="", font=("Segoe UI Emoji", 32, "bold"),
                            width=4, height=2, bg=CELL_COLOR, fg=TEXT_COLOR, relief="flat",
                            activebackground=CELL_HOVER, command=lambda i=i: self.on_cell(i))
            btn.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=ACCENT_2))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=CELL_COLOR if b["text"]=="" else CELL_COLOR))
            self.cells.append(btn)
        for i in range(3):
            self.grid_frame.grid_columnconfigure(i, weight=1)
            self.grid_frame.grid_rowconfigure(i, weight=1)

    # pulse(), refresh_board(), status_text(), on_cell(), ai_move(), end_game() remain the same

    def back_to_menu(self):
        self.controller.reset_board()
        self.refresh_board()
        self.controller.show_frame("PageMode")

    def pulse(self, color):
        self.panel.pulse(color)
    def refresh_board(self):
        self.info.config(text=self.status_text())
        for i,v in enumerate(self.controller.board):
            self.cells[i].config(text=v if v else "", bg=CELL_COLOR)
        if self.controller.mode.get()=="PvC" and self.controller.turn=="p2":
            self.after(300, self.ai_move)
    def status_text(self):
        p1 = self.controller.p1_symbol.get()
        p2 = self.controller.p2_symbol.get()
        turn = "P1" if self.controller.turn=="p1" else ("CPU" if self.controller.mode.get()=="PvC" else "P2")
        return f"P1:{p1}  P2:{p2}   Turn: {turn}   Mode:{self.controller.mode.get()}  AI:{self.controller.ai_level.get() if self.controller.mode.get()=='PvC' else '-'}"
    def on_cell(self, idx):
        board = self.controller.board
        if board[idx] or check_winner(board): return
        sym = self.controller.p1_symbol.get() if self.controller.turn=="p1" else self.controller.p2_symbol.get()
        board[idx]=sym
        self.cells[idx].config(text=sym)
        self.controller.turn = "p2" if self.controller.turn=="p1" else "p1"
        winner=check_winner(board)
        if winner: self.end_game(winner); return
        if self.controller.mode.get()=="PvC" and self.controller.turn=="p2":
            self.after(300, self.ai_move)
        self.info.config(text=self.status_text())
    def ai_move(self):
        board=self.controller.board
        if check_winner(board): return
        ai_symbol = self.controller.p2_symbol.get()
        human_symbol = self.controller.p1_symbol.get()
        level=self.controller.ai_level.get()
        move = ai_pick_move(board, level, ai_symbol, human_symbol)
        if move is None: return
        board[move]=ai_symbol
        self.cells[move].config(text=ai_symbol)
        self.controller.turn="p1"
        winner=check_winner(board)
        if winner: self.end_game(winner)
        self.info.config(text=self.status_text())
    def end_game(self,result):
        if result=="Draw":
            messagebox.showinfo("Game Over","It's a Draw!")
        else:
            messagebox.showinfo("Game Over",f"{result} wins!")
        self.controller.reset_board()
        self.refresh_board()

# =========================
# Run App
# =========================
if __name__=="__main__":
    App().mainloop()
