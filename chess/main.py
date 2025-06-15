import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import chess
import chess.engine
import json
import os
import threading
import time
import datetime
import random
import copy # To deep copy board for prev gen evaluation

class ChessRLGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess RL Learning AI (vs Stockfish)")
        self.master.geometry("1000x700") # Larger window for evaluation info
        self.master.resizable(True, True)

        # --- Initialize ALL attributes at the very beginning ---
        # Core game and display attributes
        self.board = chess.Board()
        self.square_colors = {"light": "#DCCBA6", "dark": "#8A6D4B"}
        self.current_display_color = chess.WHITE # Initial board display perspective

        # File paths for persistence
        self.q_table_file = "q_table.json"
        self.cumulative_score_file = "cumulative_score.json"
        self.game_history_file = "game_history.json"
        self.stockfish_path_file = "stockfish_path.txt"
        self.previous_gen_q_table_file = "q_table_prev_gen.json"

        # RL related parameters and state
        self.q_table = {} # Initialize empty, then load
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon_start = 0.5
        self.epsilon_end = 0.05
        self.epsilon_decay_rate = 0.999 # Applied per game, not per move
        self.epsilon = self.epsilon_start # Current epsilon value
        self.reward_per_cp = 0.01

        # Cumulative Score (for RL AI vs Stockfish)
        self.cumulative_rl_score = 0 # Initialize to 0, then load

        # Training phase control
        self.training_phase = 'stockfish_training'
        self.stockfish_training_games_per_phase = 10
        self.self_play_games_per_phase = 5
        self.games_in_current_phase = 0
        self.game_counter = 0 # Total games played across all phases
        self.save_interval = 5 # Save Q-table/score every X games
        self.save_counter = 0 # To track games played since last save (Crucial for the error fix)

        # Self-play specific tracking
        self.rl_ai_prev_gen_q_table = {} # Initialize empty, then load if needed
        self.current_gen_wins = 0
        self.prev_gen_wins = 0
        self.self_play_draws = 0

        # Store evaluations during the game for learning (for RL AI)
        self.game_states_evaluations = []
        self.game_history = [] # Initialize empty, then load

        # For displaying average evaluation during the current game (always White's POV)
        self.display_eval_history = [] 

        # AI player colors
        self.rl_ai_color = chess.WHITE # RL AI (current generation) plays as White
        self.stockfish_color = chess.BLACK # Stockfish plays as Black

        # Stockfish engine instance (initialized to None)
        self.engine = None

        # Piece display map using Unicode characters
        self.images = {}
        self.piece_display_map = {
            'P': '\u2659', 'N': '\u2658', 'B': '\u2657', 'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
            'p': '\u265f', 'n': '\u265e', 'b': '\u265d', 'r': '\u265c', 'q': '\u265b', 'k': '\u265a',
        }

        # --- Load persistent data AFTER all attributes are initialized ---
        self.q_table = self.load_q_table()
        self.cumulative_rl_score = self.load_cumulative_score()
        self.game_history = self.load_game_history()
        # Initialize games_in_current_phase and game_counter based on loaded history length if needed.
        # For simplicity in this demo, they reset on app start to clearly show phase transitions.
        # If you need continuity of games_in_current_phase, it would need to be saved/loaded too.


        # --- GUI Layout ---
        self.main_frame = tk.Frame(self.master, bg="#2c3e50", padx=10, pady=10, relief=tk.RAISED, bd=3)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.canvas_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.sidebar_frame = tk.Frame(self.main_frame, bg="#34495e", width=250, relief=tk.GROOVE, bd=2)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.sidebar_frame.pack_propagate(False)

        self.canvas = tk.Canvas(self.canvas_frame, width=640, height=640, bg="white", highlightbackground="#5b7b9b", highlightthickness=2)
        self.canvas.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        self.canvas.bind("<Configure>", self.on_resize)

        # Sidebar elements
        self.phase_label = tk.Label(self.sidebar_frame, text=f"Phase: {self.training_phase.replace('_', ' ').title()}", font=("Inter", 12, "bold"), fg="#ADD8E6", bg="#34495e", pady=5)
        self.phase_label.pack(fill=tk.X, pady=(10, 2))

        self.games_in_phase_label = tk.Label(self.sidebar_frame, text=f"Games in phase: {self.games_in_current_phase}", font=("Inter", 10), fg="#ADD8E6", bg="#34495e", pady=2)
        self.games_in_phase_label.pack(fill=tk.X, pady=(0, 5))

        self.eval_label = tk.Label(self.sidebar_frame, text="Evaluation: N/A\nAvg: N/A\nDiff: N/A", font=("Inter", 12, "bold"), fg="#ffe0b2", bg="#34495e", pady=10)
        self.eval_label.pack(fill=tk.X, pady=(10, 5))

        self.status_label = tk.Label(self.sidebar_frame, text="Initializing...", font=("Inter", 10, "bold"), fg="white", bg="#34495e", wraplength=230)
        self.status_label.pack(fill=tk.X, pady=(5, 5))

        self.outcome_label = tk.Label(self.sidebar_frame, text="", font=("Inter", 10), fg="lightgray", bg="#34495e")
        self.outcome_label.pack(fill=tk.X, pady=(2, 10))

        self.epsilon_label = tk.Label(self.sidebar_frame, text=f"Epsilon: {self.epsilon:.2f}", font=("Inter", 10), fg="#b0e0e6", bg="#34495e")
        self.epsilon_label.pack(fill=tk.X, pady=5)

        self.game_count_label = tk.Label(self.sidebar_frame, text=f"Total Games: {len(self.game_history)}", font=("Inter", 10), fg="#b0e0e6", bg="#34495e")
        self.game_count_label.pack(fill=tk.X, pady=5)

        self.cumulative_score_label = tk.Label(self.sidebar_frame, text=f"RL AI vs Stockfish Score: {self.cumulative_rl_score}", font=("Inter", 10, "bold"), fg="#8aff8a", bg="#34495e")
        self.cumulative_score_label.pack(fill=tk.X, pady=(10, 5))

        self.self_play_score_label = tk.Label(self.sidebar_frame, text=f"Self-Play (Current Gen vs Prev Gen):\nW: {self.current_gen_wins} | L: {self.prev_gen_wins} | D: {self.self_play_draws}",
                                                font=("Inter", 10), fg="#DAF7A6", bg="#34495e", wraplength=230)
        self.self_play_score_label.pack(fill=tk.X, pady=(5, 10))


        # Control buttons in sidebar
        self.new_game_button = tk.Button(self.sidebar_frame, text="New Game", command=self.new_game,
                                        font=("Inter", 10, "bold"), bg="#28a745", fg="white",
                                        activebackground="#218838", activeforeground="white",
                                        relief=tk.RAISED, bd=2, padx=10, pady=5, borderwidth=3,
                                        cursor="hand2", width=20)
        self.new_game_button.pack(pady=10)

        self.set_stockfish_button = tk.Button(self.sidebar_frame, text="Set Stockfish Path", command=self.prompt_stockfish_path,
                                              font=("Inter", 10, "bold"), bg="#007bff", fg="white",
                                              activebackground="#0056b3", activeforeground="white",
                                              relief=tk.RAISED, bd=2, padx=10, pady=5, borderwidth=3,
                                              cursor="hand2", width=20)
        self.set_stockfish_button.pack(pady=5)

        self.flip_board_button = tk.Button(self.sidebar_frame, text="Flip Board View", command=self.flip_board_view,
                                            font=("Inter", 10, "bold"), bg="#17a2b8", fg="white",
                                            activebackground="#138496", activeforeground="white",
                                            relief=tk.RAISED, bd=2, padx=10, pady=5, borderwidth=3,
                                            cursor="hand2", width=20)
        self.flip_board_button.pack(pady=5)

        self.show_history_button = tk.Button(self.sidebar_frame, text="Show Game History", command=self.show_history,
                                            font=("Inter", 10, "bold"), bg="#ffc107", fg="black",
                                            activebackground="#e0a800", activeforeground="black",
                                            relief=tk.RAISED, bd=2, padx=10, pady=5, borderwidth=3,
                                            cursor="hand2", width=20)
        self.show_history_button.pack(pady=5)

        # --- Initial Setup for Engine ---
        self.stockfish_path = self.load_stockfish_path()
        if not self.stockfish_path:
            default_stockfish_exec_name = "stockfish-windows-x86-64.exe"
            potential_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chess", default_stockfish_exec_name)
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                self.stockfish_path = potential_path
                self.save_stockfish_path(self.stockfish_path)
                self.status_label.config(text=f"Default Stockfish path found:\n{self.stockfish_path}. Initializing...")

        if not self.stockfish_path or not os.path.exists(self.stockfish_path):
            self.status_label.config(text="Stockfish executable not found. Please set the path.", fg="red")
            self.master.after(100, self.prompt_stockfish_path)
        else:
            self.start_engine()
            if self.engine:
                self.status_label.config(text="Stockfish engine ready.")
                self.draw_board() # This ensures the board is drawn
                self.update_board() # This updates status and evaluation display
                self.new_game() # This starts the first game in the appropriate phase
            else:
                self.status_label.config(text="Failed to start Stockfish. Check path.", fg="red")

    def on_resize(self, event):
        self.draw_board()
        self.update_board()

    def draw_board(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.square_size = min(canvas_width, canvas_height) // 8

        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = self.square_colors["light"] if (row + col) % 2 == 0 else self.square_colors["dark"]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=f"square_{chr(97 + col)}{8 - row}")

                if col == 0:
                    self.canvas.create_text(x1 + 5, y1 + 5, text=str(8 - row), anchor="nw",
                                            fill="#555555" if (row + col) % 2 == 0 else "#aaaaaa",
                                            font=("Inter", 8))
                if row == 7:
                    self.canvas.create_text(x2 - 5, y2 - 5, text=chr(97 + col), anchor="se",
                                            fill="#555555" if (row + col) % 2 == 0 else "#aaaaaa",
                                            font=("Inter", 8))
        self.update_board()

    def update_board(self):
        self.canvas.delete("pieces")

        display_rows = range(8) if self.current_display_color == chess.WHITE else range(7, -1, -1)
        display_cols = range(8) if self.current_display_color == chess.WHITE else range(7, -1, -1)

        for r_idx, row in enumerate(display_rows):
            for c_idx, col in enumerate(display_cols):
                square = chess.square(col, row)
                piece = self.board.piece_at(square)

                x = c_idx * self.square_size
                y = r_idx * self.square_size

                if piece:
                    piece_char = piece.symbol()
                    display_char = self.piece_display_map.get(piece_char, piece_char)

                    color = "white" if piece.color == chess.WHITE else "black"
                    self.canvas.create_text(x + self.square_size / 2, y + self.square_size / 2,
                                            text=display_char,
                                            font=("Inter", int(self.square_size * 0.7), "bold"),
                                            fill=color,
                                            tags="pieces")

        self.update_status()
        self.update_evaluation_display()

    def update_status(self):
        status_text = ""
        outcome_text = ""
        game_over_reward = 0 # Reward for RL AI (current generation) at game end for scoring

        if self.board.is_checkmate():
            status_text = "Checkmate!"
            winner_color = self.board.turn # This is the color that was checkmated
            if winner_color == self.rl_ai_color: # RL AI (current gen) was checkmated
                outcome_text = f"RL AI (Prev Gen) wins!" if self.training_phase == 'self_play_evaluation' else f"Stockfish wins!"
                game_over_reward = -1 # RL AI (current gen) loss
                if self.training_phase == 'self_play_evaluation':
                    self.prev_gen_wins += 1
            else: # Opponent was checkmated (Stockfish or Prev Gen)
                outcome_text = f"RL AI (Current Gen) wins!"
                game_over_reward = 1 # RL AI (current gen) win
                if self.training_phase == 'self_play_evaluation':
                    self.current_gen_wins += 1
            self.status_label.config(fg="red")
            
        elif self.board.is_stalemate() or \
             self.board.is_insufficient_material() or \
             self.board.is_fivefold_repetition() or \
             self.board.is_seventyfive_moves() or \
             self.board.is_variant_draw():
            status_text = "Draw!"
            outcome_text = "Game Drawn."
            self.status_label.config(fg="yellow")
            game_over_reward = 0 # Draw
            if self.training_phase == 'self_play_evaluation':
                self.self_play_draws += 1
        elif self.board.is_check():
            status_text = f"Check! {'White' if self.board.turn == chess.WHITE else 'Black'}'s turn."
            self.status_label.config(fg="red")
        else:
            status_text = f"{'White' if self.board.turn == chess.WHITE else 'Black'}'s turn."
            self.status_label.config(fg="white")

        self.status_label.config(text=status_text)
        self.outcome_label.config(text=outcome_text)
        
        # Update scores only at the end of a game
        if self.board.is_game_over():
            self.learn_from_game_outcome(game_over_reward)
            # Update cumulative score only for Stockfish games
            if self.training_phase == 'stockfish_training':
                self.cumulative_rl_score += game_over_reward
                self.cumulative_score_label.config(text=f"RL AI vs Stockfish Score: {self.cumulative_rl_score}")
            self.self_play_score_label.config(text=f"Self-Play (Current Gen vs Prev Gen):\nW: {self.current_gen_wins} | L: {self.prev_gen_wins} | D: {self.self_play_draws}")

    def update_evaluation_display(self):
        if self.engine and not self.board.is_game_over():
            try:
                info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
                current_cp_eval = info["score"].white().score() # Always White's POV for display consistency

                self.display_eval_history.append(current_cp_eval)

                average_cp_eval = sum(self.display_eval_history) / len(self.display_eval_history)
                diff_from_average = current_cp_eval - average_cp_eval

                eval_text_parts = []
                if info["score"].is_mate():
                    eval_text_parts.append(f"Current: Mate in {info['score'].mate()}")
                else:
                    eval_text_parts.append(f"Current: {current_cp_eval / 100.0:.2f} P")
                
                eval_text_parts.append(f"Avg: {average_cp_eval / 100.0:.2f} P")

                if diff_from_average > 0:
                    eval_text_parts.append(f"Diff: +{diff_from_average / 100.0:.2f} P")
                    self.eval_label.config(fg="#28a745")
                elif diff_from_average < 0:
                    eval_text_parts.append(f"Diff: {diff_from_average / 100.0:.2f} P")
                    self.eval_label.config(fg="#dc3545")
                else:
                    eval_text_parts.append(f"Diff: 0.00 P")
                    self.eval_label.config(fg="#ffe0b2")

                self.eval_label.config(text="\n".join(eval_text_parts))

            except chess.engine.EngineError:
                self.eval_label.config(text="Eval: Engine Error\nAvg: N/A\nDiff: N/A", fg="red")
            except Exception as e:
                self.eval_label.config(text=f"Eval Error: {e}\nAvg: N/A\nDiff: N/A", fg="red")
        else:
            self.eval_label.config(text="Evaluation: N/A\nAvg: N/A\nDiff: N/A", fg="#ffe0b2")

    def play_next_move(self):
        if self.board.is_game_over():
            self.check_game_over()
            return

        self.master.config(cursor="wait")
        self.status_label.config(text="AI is thinking...", fg="orange")

        def make_move_thread():
            try:
                current_board_fen = self.board.board_fen()
                current_eval_info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
                current_cp_eval_for_learning = current_eval_info["score"].pov(self.board.turn).score()

                move_to_make = None
                mover_type = ""

                if self.board.turn == self.rl_ai_color:
                    mover_type = "RL AI (Current Gen)"
                    chosen_move_rl = self.get_rl_move_from_q_table(self.board, self.q_table, self.epsilon)
                    
                    if chosen_move_rl and chosen_move_rl in self.board.legal_moves:
                        move_to_make = chosen_move_rl
                    else:
                        if chosen_move_rl:
                            q_key_to_penalize = f"{current_board_fen}-{chosen_move_rl.uci()}"
                            self.q_table[q_key_to_penalize] = self.q_table.get(q_key_to_penalize, 0.0) - 1000 
                            self.save_q_table()
                            self.master.after(0, lambda: self.status_label.config(text=f"RL AI attempted illegal move! Penalized.", fg="red"))
                        
                        legal_moves = list(self.board.legal_moves)
                        if legal_moves:
                            move_to_make = random.choice(legal_moves)
                        else:
                            move_to_make = None
                else: # Opponent's turn
                    if self.training_phase == 'stockfish_training':
                        mover_type = "Stockfish"
                        info = self.engine.play(self.board, chess.engine.Limit(time=0.5))
                        move_to_make = info.move
                    elif self.training_phase == 'self_play_evaluation':
                        mover_type = "RL AI (Prev Gen)"
                        move_to_make = self.get_rl_move_from_q_table(self.board, self.rl_ai_prev_gen_q_table, 0.01)
                        if not move_to_make and list(self.board.legal_moves):
                             move_to_make = random.choice(list(self.board.legal_moves))

                if move_to_make is None:
                    self.master.after(0, lambda: self.status_label.config(text=f"{mover_type} has no legal moves!", fg="red"))
                    self.master.after(0, lambda: self.master.config(cursor=""))
                    return

                self.board.push(move_to_make)
                self.game_states_evaluations.append((current_board_fen, move_to_make.uci(), current_cp_eval_for_learning, self.board.turn)) 

                self.master.after(0, self.update_board)
                self.master.after(0, lambda: self.master.config(cursor=""))

                if not self.board.is_game_over():
                    self.master.after(100, self.play_next_move) # Changed from 500 to 100
                else:
                    self.master.after(0, self.check_game_over)

            except chess.engine.EngineError as e:
                self.master.after(0, lambda: self.status_label.config(text=f"Engine Error: {e}", fg="red"))
                self.master.after(0, lambda: self.master.config(cursor=""))
            except Exception as e:
                self.master.after(0, lambda: self.status_label.config(text=f"An error occurred during move: {e}", fg="red"))
                self.master.after(0, lambda: self.master.config(cursor=""))

        threading.Thread(target=make_move_thread).start()

    def get_rl_move_from_q_table(self, board_obj, q_table_instance, epsilon_val):
        legal_moves = list(board_obj.legal_moves)
        if not legal_moves:
            return None

        current_fen = board_obj.board_fen()

        if random.uniform(0, 1) < epsilon_val:
            return random.choice(legal_moves)

        best_move = None
        max_q_value = -float('inf')
        candidate_moves = []

        for move in legal_moves:
            q_key = f"{current_fen}-{move.uci()}"
            q_value = q_table_instance.get(q_key, 0.0)
            if q_value > max_q_value:
                max_q_value = q_value
                candidate_moves = [move]
            elif q_value == max_q_value:
                candidate_moves.append(move)

        if candidate_moves:
            return random.choice(candidate_moves)
        else:
            return random.choice(legal_moves)

    def learn_from_game_outcome(self, final_game_reward):
        for i in reversed(range(len(self.game_states_evaluations))):
            current_fen, move_uci, eval_before_move, mover_color_after_move = self.game_states_evaluations[i]

            if mover_color_after_move == self.rl_ai_color:
                q_key = f"{current_fen}-{move_uci}"

                temp_board = chess.Board(current_fen)
                try:
                    temp_board.push_uci(move_uci)
                except ValueError:
                    continue

                if temp_board.is_game_over():
                    reward = final_game_reward
                    max_q_next_state = 0
                else:
                    next_eval_info = self.engine.analyse(temp_board, chess.engine.Limit(time=0.1))
                    next_cp_eval = next_eval_info["score"].pov(self.rl_ai_color).score()

                    reward = (next_cp_eval - eval_before_move) * self.reward_per_cp

                    next_state_fen = temp_board.board_fen()
                    max_q_next_state = 0.0
                    
                    for key in self.q_table.keys():
                        if key.startswith(next_state_fen):
                            max_q_next_state = max(max_q_next_state, self.q_table[key])


                old_q_value = self.q_table.get(q_key, 0.0)
                new_q_value = old_q_value + self.learning_rate * (reward + self.discount_factor * max_q_next_state - old_q_value)
                self.q_table[q_key] = new_q_value
        
        self.save_counter += 1
        if self.save_counter >= self.save_interval:
            self.save_q_table()
            self.save_cumulative_score()
            self.save_counter = 0

        self.game_states_evaluations = []
        self.display_eval_history = []

    def load_game_history(self):
        if os.path.exists(self.game_history_file):
            try:
                with open(self.game_history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_game_history(self):
        with open(self.game_history_file, 'w') as f:
            json.dump(self.game_history, f, indent=4)

    def load_q_table(self):
        if os.path.exists(self.q_table_file):
            try:
                with open(self.q_table_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_q_table(self):
        with open(self.q_table_file, 'w') as f:
            json.dump(self.q_table, f, indent=4)

    def load_prev_gen_q_table(self):
        if os.path.exists(self.previous_gen_q_table_file):
            try:
                with open(self.previous_gen_q_table_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_prev_gen_q_table(self):
        with open(self.previous_gen_q_table_file, 'w') as f:
            json.dump(self.q_table, f, indent=4)

    def load_cumulative_score(self):
        if os.path.exists(self.cumulative_score_file):
            try:
                with open(self.cumulative_score_file, 'r') as f:
                    return json.load(f).get("score", 0)
            except json.JSONDecodeError:
                return 0
        return 0

    def save_cumulative_score(self):
        with open(self.cumulative_score_file, 'w') as f:
            json.dump({"score": self.cumulative_rl_score}, f, indent=4)

    def load_stockfish_path(self):
        if os.path.exists(self.stockfish_path_file):
            with open(self.stockfish_path_file, 'r') as f:
                return f.read().strip()
        return ""

    def save_stockfish_path(self, path):
        with open(self.stockfish_path_file, 'w') as f:
            f.write(path)

    def prompt_stockfish_path(self):
        new_path = filedialog.askopenfilename(
            title="Select Stockfish Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if new_path:
            if os.path.exists(new_path) and os.path.isfile(new_path):
                self.stockfish_path = new_path
                self.save_stockfish_path(self.stockfish_path)
                self.status_label.config(text="Stockfish path set. Initializing engine...")
                self.start_engine()
                if self.engine:
                    self.status_label.config(text="Stockfish engine ready.")
                    self.new_game()
                else:
                    self.status_label.config(text="Failed to start Stockfish. Check path.", fg="red")
            else:
                messagebox.showerror("Invalid Path", "The selected path is not a valid file.")
                self.status_label.config(text="Invalid Stockfish path.", fg="red")
        else:
            self.status_label.config(text="Stockfish path not set.", fg="red")

    def start_engine(self):
        if self.engine:
            try:
                self.engine.quit()
            except Exception as e:
                print(f"Error quitting old engine: {e}")
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
        except Exception as e:
            self.engine = None
            self.status_label.config(text=f"Could not start Stockfish: {e}. Check path.", fg="red")
            messagebox.showerror("Engine Error", f"Could not start Stockfish engine. Please ensure the path is correct and Stockfish is executable.\nError: {e}")

    def new_game(self):
        if self.engine is None:
            messagebox.showerror("Engine Not Ready", "Stockfish engine is not initialized. Please set its path first.")
            return

        is_phase_complete = False
        if self.training_phase == 'stockfish_training' and self.games_in_current_phase >= self.stockfish_training_games_per_phase:
            is_phase_complete = True
            self.training_phase = 'self_play_evaluation'
            self.games_in_current_phase = 0
            self.save_prev_gen_q_table()
            self.rl_ai_prev_gen_q_table = self.load_prev_gen_q_table()
            self.current_gen_wins = 0
            self.prev_gen_wins = 0
            self.self_play_draws = 0
            self.status_label.config(text="Entering Self-Play Evaluation Phase!")
            
        elif self.training_phase == 'self_play_evaluation' and self.games_in_current_phase >= self.self_play_games_per_phase:
            is_phase_complete = True
            self.training_phase = 'stockfish_training'
            self.games_in_current_phase = 0
            self.status_label.config(text="Entering Stockfish Training Phase!")

        self.games_in_current_phase += 1
        self.game_counter += 1
        self.game_count_label.config(text=f"Total Games: {self.game_counter}")
        self.games_in_phase_label.config(text=f"Games in phase: {self.games_in_current_phase} / " + 
                                            (f"{self.stockfish_training_games_per_phase}" if self.training_phase == 'stockfish_training' else f"{self.self_play_games_per_phase}"))
        self.phase_label.config(text=f"Phase: {self.training_phase.replace('_', ' ').title()}")
        self.self_play_score_label.config(text=f"Self-Play (Current Gen vs Prev Gen):\nW: {self.current_gen_wins} | L: {self.prev_gen_wins} | D: {self.self_play_draws}")

        self.board = chess.Board()
        self.game_states_evaluations = []
        self.display_eval_history = []
        self.outcome_label.config(text="")
        
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay_rate) 
        self.epsilon_label.config(text=f"Epsilon: {self.epsilon:.2f}")

        self.update_board()
        self.master.update_idletasks()

        self.master.after(100, self.play_next_move) # Changed from 500 to 100

    def check_game_over(self):
        if self.board.is_game_over():
            self.update_status()
            self.master.after(100, self.new_game) # Changed from 1000 to 100

    def flip_board_view(self):
        self.current_display_color = not self.current_display_color
        self.draw_board()
        self.update_board()

    def show_history(self):
        history_window = tk.Toplevel(self.master)
        history_window.title("Game History")
        history_window.geometry("500x400")
        history_window.configure(bg="#2c3e50")

        history_text = tk.Text(history_window, wrap="word", bg="#34495e", fg="white", font=("Inter", 10))
        history_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        if not self.game_history:
            history_text.insert(tk.END, "No games played yet.")
        else:
            for i, game in enumerate(self.game_history):
                history_text.insert(tk.END, f"--- Game {i + 1} ---\n")
                history_text.insert(tk.END, f"Date: {game.get('date', 'N/A')}\n")
                history_text.insert(tk.END, f"Outcome: {game.get('outcome', 'N/A')}\n")
                history_text.insert(tk.END, f"Moves: {', '.join(game.get('moves', []))}\n")
                history_text.insert(tk.END, f"FEN (start): {game.get('fen_start', 'N/A')}\n\n")
        history_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessRLGUI(root)
    root.mainloop()

    if app.engine:
        try:
            app.engine.quit()
        except Exception as e:
            print(f"Error shutting down engine: {e}")
    
    app.save_q_table()
    app.save_cumulative_score()
    app.save_prev_gen_q_table()
