import chess
import math
import random
import time
import tkinter as tk
from tkinter import messagebox
from stockfish import Stockfish # Import the stockfish library

class ChessAI:
    def __init__(self, color, search_depth=3, initial_elo=1200):
        """
        Initializes a Chess AI player.
        Args:
            color (chess.WHITE or chess.BLACK): The color of the AI.
            search_depth (int): How many moves deep the AI will look.
                                Higher depth means smarter AI but slower performance.
            initial_elo (int): The starting ELO rating for this AI.
        """
        self.color = color
        self.search_depth = search_depth
        
        # Initial piece values (will be adjusted by learning from Stockfish)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0 # King value is handled by checkmate, not material
        }
        
        # Initial positional bonuses for central squares (will be adjusted by learning from Stockfish)
        self.positional_bonuses = {
            chess.D4: 10, chess.E4: 10, chess.D5: 10, chess.E5: 10,
            # Add more squares to positional bonuses if desired
            chess.C3: 5, chess.F3: 5, chess.C6: 5, chess.F6: 5,
            chess.G2: 2, chess.B2: 2, chess.A7: 2, chess.H7: 2
        }
        
        self.elo = initial_elo # Current ELO rating
        # Metrics for ACPL tracking per game
        self.current_game_cp_loss = 0
        self.current_game_moves_made = 0

    def evaluate_board(self, board):
        """
        Evaluates the current state of the board using the AI's current piece values
        and positional bonuses. A positive score favors White, a negative score favors Black.
        This score is *from White's perspective* inside this function for consistency.
        The final return handles the AI's actual color.
        """
        if board.is_checkmate():
            # If it's the opponent's turn and checkmated, the current player (White) won
            if board.turn == chess.BLACK: # Black was just checkmated by White
                return math.inf
            # If it's White's turn and checkmated, White lost
            else: # White was just checkmated by Black
                return -math.inf
        if board.is_stalemate() or board.is_insufficient_material() or \
           board.is_seventyfive_moves() or board.is_fivefold_repetition():
            return 0

        score = 0
        
        # Sum material based on AI's current piece values (always White's perspective for score accumulation)
        for piece_type in self.piece_values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]

        # Apply positional bonuses (always White's perspective)
        for square in self.positional_bonuses:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += self.positional_bonuses[square]
                else: # Black piece
                    score -= self.positional_bonuses[square]

        # Return score from the current AI's perspective
        return score if self.color == chess.WHITE else -score

    def minimax(self, board, depth, alpha, beta, is_maximizing_player):
        """
        Minimax algorithm with Alpha-Beta Pruning.
        This function uses the *calling AI's* evaluation function.
        Args:
            board (chess.Board): The current chess board.
            depth (int): Current depth in the search tree.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
            is_maximizing_player (bool): True if it's the AI's turn to maximize score, False otherwise.
        Returns:
            float: The best score found for the current board state.
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board) # Use this AI's evaluation

        legal_moves = list(board.legal_moves)
        
        # Simple move ordering heuristic: prioritize captures
        def move_heuristic(move):
            if board.is_capture(move):
                return 1 # Higher priority for captures
            # Consider promoting pawns higher too
            if move.promotion is not None:
                return 2
            return 0
        
        # Sort moves by heuristic in descending order
        legal_moves.sort(key=move_heuristic, reverse=True)

        if is_maximizing_player:
            max_eval = -math.inf
            for move in legal_moves:
                board.push(move)
                # Recursively call minimax, switching maximizing player
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break # Beta cut-off
            return max_eval
        else: # Minimizing player
            min_eval = math.inf
            for move in legal_moves:
                board.push(move)
                # Recursively call minimax, switching maximizing player
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break # Alpha cut-off
            return min_eval

    def choose_move(self, board):
        """
        Chooses the best move for the AI using the minimax algorithm.
        """
        start_time = time.time()
        best_move = None
        # Initialize best_eval based on the AI's color (maximizing white, minimizing black)
        best_eval = -math.inf if self.color == chess.WHITE else math.inf

        legal_moves = list(board.legal_moves)
        
        # Initial move ordering before search: prioritize captures for the root node too
        def root_move_heuristic(move):
            if board.is_capture(move):
                return 1
            if move.promotion is not None:
                return 2
            return 0
        legal_moves.sort(key=root_move_heuristic, reverse=True)


        # Iterate through all legal moves to find the best one
        for move in legal_moves:
            board.push(move) # Make the move temporarily
            # Evaluate from the perspective of the *other* player next turn
            # The 'is_maximizing_player' for the recursive call is True if the current AI is Black, False if White.
            # This is because the minimax function evaluates from the perspective of the player whose turn it is
            # at the current depth of the recursive call.
            eval = self.minimax(board, self.search_depth - 1, -math.inf, math.inf, not (self.color == chess.WHITE))
            board.pop() # Undo the move

            # Update best_move and best_eval based on AI's color
            if self.color == chess.WHITE: # White AI wants to maximize score
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
            else: # Black AI wants to minimize score (or maximize negative score from its perspective)
                if eval < best_eval:
                    best_eval = eval
                    best_move = move
        
        end_time = time.time()
        print(f"AI ({'White' if self.color == chess.WHITE else 'Black'}) (ELO: {self.elo:.0f}) thought for {end_time - start_time:.2f} seconds. Score: {best_eval}")
        return best_move

    def learn_from_stockfish_evaluation(self, final_board, stockfish_engine):
        """
        Adjusts AI's internal evaluation parameters (piece values, positional bonuses)
        based on the difference between its evaluation and Stockfish's evaluation of the final board.
        Args:
            final_board (chess.Board): The board state at the end of the game.
            stockfish_engine (Stockfish): The Stockfish engine instance for evaluation.
        """
        if not stockfish_engine:
            print("Stockfish engine not available for learning.")
            return

        stockfish_engine.set_fen_position(final_board.fen())
        sf_eval_dict = stockfish_engine.get_evaluation()

        sf_eval_cp = 0
        if sf_eval_dict['type'] == 'cp':
            sf_eval_cp = sf_eval_dict['value']
        elif sf_eval_dict['type'] == 'mate':
            # Assign a very large (but capped) value for mate to represent strong advantage/disadvantage
            # This prevents parameter values from exploding to infinity/negative infinity
            sf_eval_cp = 100000 if sf_eval_dict['value'] > 0 else -100000

        # Now, `sf_eval_cp` is from White's perspective (positive for White advantage).

        # Get AI's evaluation, also from White's perspective for consistent comparison.
        # Temporarily change AI's color to WHITE for evaluation if it's BLACK, then revert.
        original_ai_color = self.color
        temp_original_color = self.color # Store to restore later if necessary
        self.color = chess.WHITE # Temporarily set to WHITE to get evaluation from White's perspective
        ai_eval_for_comparison = self.evaluate_board(final_board)
        self.color = temp_original_color # Restore original color immediately

        # Calculate the error: Stockfish's evaluation - AI's evaluation (both from White's perspective)
        # This error indicates how much the AI needs to shift its values to match Stockfish.
        error = sf_eval_cp - ai_eval_for_comparison

        learning_rate = 0.00005 # A very small learning rate for stability and fine adjustments

        # Adjust piece values
        for piece_type in self.piece_values:
            # The 'feature value' for a piece type is its count for White minus its count for Black.
            # This reflects its contribution to the score (from White's perspective).
            white_pieces_count = len(final_board.pieces(piece_type, chess.WHITE))
            black_pieces_count = len(final_board.pieces(piece_type, chess.BLACK))
            
            piece_type_feature = white_pieces_count - black_pieces_count
            
            # Update the piece value based on the error and the feature's contribution.
            # A positive error means Stockfish sees more White advantage. If this feature
            # increases White's score, we want to increase its value.
            self.piece_values[piece_type] += learning_rate * error * piece_type_feature

            # Clamp values to prevent them from becoming too small or negative (except king)
            if piece_type != chess.KING:
                self.piece_values[piece_type] = max(1, self.piece_values[piece_type])
            else: # King value is 0, keep it that way for material evaluation
                self.piece_values[chess.KING] = 0

        # Adjust positional bonuses
        for square in self.positional_bonuses:
            piece_on_square = final_board.piece_at(square)
            
            # The 'feature value' for a positional bonus is +1 if a White piece is there, -1 if Black, 0 otherwise.
            positional_feature = 0
            if piece_on_square:
                if piece_on_square.color == chess.WHITE:
                    positional_feature = 1
                else: # Black piece
                    positional_feature = -1

            # Update the positional bonus based on the error and the feature's contribution.
            self.positional_bonuses[square] += learning_rate * error * positional_feature
            
            # Clamp values to prevent them from becoming negative
            self.positional_bonuses[square] = max(0, self.positional_bonuses[square])
            
        print(f"AI ({'White' if original_ai_color == chess.WHITE else 'Black'}): Learning from Stockfish. White's Error: {error:.2f}")
        # print(f"  New Piece Values: {self.piece_values}")
        # print(f"  New Positional Bonuses: {self.positional_bonuses}")

    def reset_game_metrics(self):
        """Resets ACPL tracking metrics for a new game."""
        self.current_game_cp_loss = 0
        self.current_game_moves_made = 0


def calculate_elo_change(rating_a, rating_b, score_a, K_factor=32):
    """
    Calculates ELO rating changes for two players.
    Args:
        rating_a (float): Current ELO rating of player A.
        rating_b (float): Current ELO rating of player B.
        score_a (float): Actual score of player A (1.0 for win, 0.5 for draw, 0.0 for loss).
        K_factor (int): Maximum possible rating change in a single game.
    Returns:
        tuple: (change_a, change_b) - ELO changes for player A and B.
    """
    expected_score_a = 1 / (1 + 10**((rating_b - rating_a) / 400))
    change_a = K_factor * (score_a - expected_score_a)
    change_b = -change_a # Player B's change is opposite of A's
    return change_a, change_b

class ChessGUI:
    def __init__(self, master, white_ai, black_ai, stockfish_path="stockfish"):
        self.master = master
        master.title("Chess AI vs AI Learning")
        master.resizable(False, False) # Make window non-resizable

        self.board = chess.Board()
        self.white_ai = white_ai
        self.black_ai = black_ai
        self.square_size = 60 # Size of each square in pixels
        self.board_width = 8 * self.square_size
        self.board_height = 8 * self.square_size
        self.move_delay_ms = 500 # Delay between AI moves in milliseconds

        self.game_count = 0
        self.max_games_to_play = 10 # Default to 10 games
        self.game_results = [] # To store results of each game
        self.white_acpl_history = [] # Store ACPL for each game for overall average
        self.black_acpl_history = [] # Store ACPL for each game for overall average

        self.stockfish_path = stockfish_path
        self.stockfish_engine = None
        self._initialize_stockfish() # Initialize Stockfish here


        # Canvas for drawing the chess board and pieces
        self.canvas = tk.Canvas(master, width=self.board_width, height=self.board_height, bg="lightgray")
        self.canvas.pack(pady=10)

        # Status label
        self.status_label = tk.Label(master, text="Initializing game...", font=("Arial", 14))
        self.status_label.pack(pady=5)

        # ELO display labels
        self.elo_frame = tk.Frame(master)
        self.elo_frame.pack(pady=5)
        self.white_elo_label = tk.Label(self.elo_frame, text=f"White AI ELO: {self.white_ai.elo:.0f}", font=("Arial", 12))
        self.white_elo_label.pack(side=tk.LEFT, padx=10)
        self.black_elo_label = tk.Label(self.elo_frame, text=f"Black AI ELO: {self.black_ai.elo:.0f}", font=("Arial", 12))
        self.black_elo_label.pack(side=tk.RIGHT, padx=10)

        # ACPL display labels
        self.acpl_frame = tk.Frame(master)
        self.acpl_frame.pack(pady=5)
        self.white_acpl_label = tk.Label(self.acpl_frame, text="White ACPL: N/A", font=("Arial", 10))
        self.white_acpl_label.pack(side=tk.LEFT, padx=10)
        self.black_acpl_label = tk.Label(self.acpl_frame, text="Black ACPL: N/A", font=("Arial", 10))
        self.black_acpl_label.pack(side=tk.RIGHT, padx=10)


        # Controls frame
        self.controls_frame = tk.Frame(master)
        self.controls_frame.pack(pady=10)

        self.games_label = tk.Label(self.controls_frame, text="Games to Play:", font=("Arial", 12))
        self.games_label.pack(side=tk.LEFT, padx=5)
        self.games_entry = tk.Entry(self.controls_frame, width=5, font=("Arial", 12))
        self.games_entry.insert(0, str(self.max_games_to_play))
        self.games_entry.pack(side=tk.LEFT, padx=5)

        self.play_button = tk.Button(self.controls_frame, text="Start Simulation", command=self.start_simulation, font=("Arial", 12))
        self.play_button.pack(side=tk.LEFT, padx=10)

        self.restart_button = tk.Button(self.controls_frame, text="Reset Simulation", command=self.reset_simulation, font=("Arial", 12))
        self.restart_button.pack(side=tk.LEFT, padx=10)
        
        self._load_piece_symbols()
        self.draw_board()
        self.update_board_display()

        # Initial status update
        self.status_label.config(text=f"Ready to play {self.max_games_to_play} games.")

        # Bind the close event to a cleanup function
        master.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _initialize_stockfish(self):
        """Initializes the Stockfish engine."""
        try:
            # Set a timeout for Stockfish initialization
            self.stockfish_engine = Stockfish(path=self.stockfish_path, depth=10, parameters={"Contempt": 0, "Threads": 1, "Hash": 128})
            print(f"Stockfish engine initialized from: {self.stockfish_path}")
            # Set a reasonable skill level for analysis (optional)
            self.stockfish_engine.set_skill_level(10) # 0-20, 20 is strongest
        except Exception as e:
            messagebox.showerror("Stockfish Error", f"Could not initialize Stockfish engine. Make sure 'stockfish' executable is in the same directory as the script or provide the full path.\nError: {e}")
            self.stockfish_engine = None # Set to None if initialization fails
            print(f"Failed to initialize Stockfish: {e}")

    def _on_closing(self):
        """Handles window closing, ensuring Stockfish process is terminated."""
        if self.stockfish_engine:
            self.stockfish_engine.quit()
            print("Stockfish engine quit.")
        self.master.destroy()

    def _load_piece_symbols(self):
        """Maps chess.Piece objects to Unicode chess symbols."""
        self.piece_symbols = {
            chess.Piece(chess.PAWN, chess.WHITE): '♙',
            chess.Piece(chess.KNIGHT, chess.WHITE): '♘',
            chess.Piece(chess.BISHOP, chess.WHITE): '♗',
            chess.Piece(chess.ROOK, chess.WHITE): '♖',
            chess.Piece(chess.QUEEN, chess.WHITE): '♕',
            chess.Piece(chess.KING, chess.WHITE): '♔',
            chess.Piece(chess.PAWN, chess.BLACK): '♟',
            chess.Piece(chess.KNIGHT, chess.BLACK): '♞',
            chess.Piece(chess.BISHOP, chess.BLACK): '♝',
            chess.Piece(chess.ROOK, chess.BLACK): '♜',
            chess.Piece(chess.QUEEN, chess.BLACK): '♛',
            chess.Piece(chess.KING, chess.BLACK): '♚',
        }

    def draw_board(self):
        """Draws the chess board squares on the canvas."""
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E" # Light and dark squares
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def update_board_display(self):
        """Clears existing pieces and draws new ones based on the current board state."""
        self.canvas.delete("pieces") # Delete all items with the "pieces" tag

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Convert square index to (col, row)
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square) # Tkinter y-axis is inverted for chess board

                x = col * self.square_size + self.square_size // 2
                y = row * self.square_size + self.square_size // 2
                
                symbol = self.piece_symbols.get(piece, '?') # Get Unicode symbol for the piece
                self.canvas.create_text(x, y, text=symbol, font=("Arial", 36, "bold"), tags="pieces")

        self.status_label.config(text=self._get_status_message())
        self.white_elo_label.config(text=f"White AI ELO: {self.white_ai.elo:.0f}")
        self.black_elo_label.config(text=f"Black AI ELO: {self.black_ai.elo:.0f}")

        # Update ACPL display
        white_acpl_text = f"White ACPL: {self.white_ai.current_game_cp_loss / self.white_ai.current_game_moves_made:.2f}" if self.white_ai.current_game_moves_made > 0 else "White ACPL: N/A"
        black_acpl_text = f"Black ACPL: {self.black_ai.current_game_cp_loss / self.black_ai.current_game_moves_made:.2f}" if self.black_ai.current_game_moves_made > 0 else "Black ACPL: N/A"
        self.white_acpl_label.config(text=white_acpl_text)
        self.black_acpl_label.config(text=black_acpl_text)


    def _get_status_message(self):
        """Generates the current status message for the game."""
        if self.board.is_checkmate():
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            return f"Checkmate! {winner} wins! (Game {self.game_count}/{self.max_games_to_play})"
        elif self.board.is_stalemate():
            return f"Stalemate! It's a draw. (Game {self.game_count}/{self.max_games_to_play})"
        elif self.board.is_insufficient_material():
            return f"Draw by insufficient material. (Game {self.game_count}/{self.max_games_to_play})"
        elif self.board.is_seventyfive_moves():
            return f"Draw by 75-move rule. (Game {self.game_count}/{self.max_games_to_play})"
        elif self.board.is_fivefold_repetition():
            return f"Draw by fivefold repetition. (Game {self.game_count}/{self.max_games_to_play})"
        elif self.board.is_game_over():
            return f"Game Over. (Game {self.game_count}/{self.max_games_to_play})"
        else:
            current_player_name = "White" if self.board.turn == chess.WHITE else "Black"
            return f"{current_player_name}'s turn. AI thinking... (Game {self.game_count}/{self.max_games_to_play})"

    def start_simulation(self):
        """Starts a batch of games."""
        try:
            self.max_games_to_play = int(self.games_entry.get())
            if self.max_games_to_play <= 0:
                messagebox.showerror("Invalid Input", "Number of games must be positive.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for games.")
            return

        self.game_count = 0
        self.game_results = []
        self.white_acpl_history = []
        self.black_acpl_history = []
        self.reset_game_board() # Reset board for the first game
        self.make_ai_move() # Start the first move

    def reset_game_board(self):
        """Resets the chess board for a new game."""
        self.board = chess.Board()
        self.white_ai.reset_game_metrics() # Reset ACPL for new game
        self.black_ai.reset_game_metrics() # Reset ACPL for new game
        self.update_board_display()
        self.status_label.config(text=f"Game {self.game_count + 1}/{self.max_games_to_play}: White's turn. AI thinking...")

    def end_current_game(self):
        """Processes the end of a single game, updates ELOs and learning."""
        result = self.board.result() # e.g., "1-0", "0-1", "1/2-1/2"
        
        # Determine scores for ELO calculation
        white_score = 0.5 # Default to draw
        if result == "1-0":
            white_score = 1.0
        elif result == "0-1":
            white_score = 0.0
        
        black_score = 1.0 - white_score # Black's score is opposite of White's

        # Calculate ELO changes
        change_white, change_black = calculate_elo_change(
            self.white_ai.elo, self.black_ai.elo, white_score
        )
        self.white_ai.elo += change_white
        self.black_ai.elo += change_black

        # Apply learning from Stockfish's evaluation
        if self.stockfish_engine:
            self.white_ai.learn_from_stockfish_evaluation(self.board, self.stockfish_engine)
            self.black_ai.learn_from_stockfish_evaluation(self.board, self.stockfish_engine)
        else:
            print("Stockfish not initialized, skipping Stockfish-guided learning.")

        # Store ACPL for this game
        if self.white_ai.current_game_moves_made > 0:
            self.white_acpl_history.append(self.white_ai.current_game_cp_loss / self.white_ai.current_game_moves_made)
        if self.black_ai.current_game_moves_made > 0:
            self.black_acpl_history.append(self.black_ai.current_game_cp_loss / self.black_ai.current_game_moves_made)

        self.game_results.append(f"Game {self.game_count + 1}: Result: {result}, White ELO: {self.white_ai.elo:.0f}, Black ELO: {self.black_ai.elo:.0f}")
        print(self.game_results[-1]) # Print to console for detailed log

        # Stockfish analysis of the final board (for observation)
        if self.stockfish_engine:
            self.stockfish_engine.set_fen_position(self.board.fen())
            stockfish_eval = self.stockfish_engine.get_evaluation()
            eval_type = stockfish_eval['type']
            eval_value = stockfish_eval['value']
            print(f"Stockfish final board evaluation: Type: {eval_type}, Value: {eval_value} ({'cp' if eval_type == 'cp' else 'mate'})")
            # Convert centipawn to human readable
            if eval_type == 'cp':
                print(f"  (Stockfish thinks White is {'+' if eval_value >= 0 else ''}{eval_value/100:.2f} pawns ahead)")
            elif eval_type == 'mate':
                print(f"  (Stockfish predicts mate in {eval_value} moves)")


        self.update_board_display() # Update ELO labels

        self.game_count += 1
        if self.game_count < self.max_games_to_play:
            self.master.after(1500, self.reset_game_board) # Pause then start next game
            self.master.after(2000, self.make_ai_move) # Start AI move for new game
        else:
            final_message = f"Simulation complete! Played {self.max_games_to_play} games.\n"
            if self.white_acpl_history:
                avg_white_acpl = sum(self.white_acpl_history) / len(self.white_acpl_history)
                final_message += f"Average White ACPL over {len(self.white_acpl_history)} games: {avg_white_acpl:.2f}\n"
            if self.black_acpl_history:
                avg_black_acpl = sum(self.black_acpl_history) / len(self.black_acpl_history)
                final_message += f"Average Black ACPL over {len(self.black_acpl_history)} games: {avg_black_acpl:.2f}\n"
            
            final_message += "\n" + "\n".join(self.game_results)

            self.status_label.config(text=final_message.split('\n')[0]) # Show first line in status
            messagebox.showinfo("Simulation Complete", final_message)


    def make_ai_move(self):
        """Handles an AI player's move."""
        if self.board.is_game_over():
            self.end_current_game()
            return

        current_ai = self.white_ai if self.board.turn == chess.WHITE else self.black_ai
        
        # Update status to show whose turn it is and that AI is thinking
        player_name = "White" if self.board.turn == chess.WHITE else "Black"
        self.status_label.config(text=f"Game {self.game_count + 1}/{self.max_games_to_play}: {player_name}'s turn. AI thinking...")
        self.master.update_idletasks() # Update GUI immediately

        # Use a try-except block for robustness
        try:
            # Get Stockfish's evaluation of the current position BEFORE our AI makes a move
            stockfish_eval_before_move = None
            if self.stockfish_engine:
                self.stockfish_engine.set_fen_position(self.board.fen())
                sf_eval_dict = self.stockfish_engine.get_evaluation()
                if sf_eval_dict['type'] == 'cp':
                    stockfish_eval_before_move = sf_eval_dict['value']
                elif sf_eval_dict['type'] == 'mate':
                    stockfish_eval_before_move = 100000 if sf_eval_dict['value'] > 0 else -100000
                
                stockfish_best_move = self.stockfish_engine.get_best_move()
                if stockfish_best_move:
                    print(f"  Stockfish best move for {player_name}: {stockfish_best_move}")


            ai_move = current_ai.choose_move(self.board)
            if ai_move:
                # Compare AI's chosen move to Stockfish's best move (for observation)
                if self.stockfish_engine and stockfish_best_move:
                    if ai_move.uci() != stockfish_best_move:
                        print(f"  *** Our AI chose {ai_move.uci()} while Stockfish suggests {stockfish_best_move} ***")
                    else:
                        print(f"  Our AI's move {ai_move.uci()} matches Stockfish's best move!")

                self.board.push(ai_move)
                print(f"Game {self.game_count + 1}: {player_name} AI played: {ai_move.uci()}")
                
                # Calculate ACPL for this move
                if self.stockfish_engine and stockfish_eval_before_move is not None:
                    self.stockfish_engine.set_fen_position(self.board.fen()) # Set board to state AFTER AI's move
                    sf_eval_after_move_dict = self.stockfish_engine.get_evaluation()
                    sf_eval_after_move = 0
                    if sf_eval_after_move_dict['type'] == 'cp':
                        sf_eval_after_move = sf_eval_after_move_dict['value']
                    elif sf_eval_after_move_dict['type'] == 'mate':
                        sf_eval_after_move = 100000 if sf_eval_after_move_dict['value'] > 0 else -100000

                    # ACPL is the difference between best possible (Stockfish before move) and actual (Stockfish after AI's move)
                    # Ensure evaluation is from the current player's perspective for ACPL calculation
                    if current_ai.color == chess.BLACK: # If Black AI, invert Stockfish scores for comparison
                        cp_loss = abs(stockfish_eval_before_move - (-sf_eval_after_move)) # (Best for Black) - (Actual for Black)
                    else: # White AI
                        cp_loss = abs(stockfish_eval_before_move - sf_eval_after_move) # (Best for White) - (Actual for White)
                    
                    # A simpler way to calculate CP loss:
                    # The ideal score after a move is the score before the move (assuming best play).
                    # So, if White is playing, and Stockfish thought +100 before, and after White's move it's +80,
                    # White lost 20 cp. If Black is playing, and Stockfish thought -100 before, and after Black's move it's -80,
                    # Black gained 20 cp (meaning White lost 20 cp).
                    
                    # Convert Stockfish eval to current player's perspective for ACPL calculation
                    sf_eval_before_move_player_perspective = stockfish_eval_before_move if current_ai.color == chess.WHITE else -stockfish_eval_before_move
                    sf_eval_after_move_player_perspective = sf_eval_after_move if current_ai.color == chess.WHITE else -sf_eval_after_move
                    
                    # Centipawn loss is how much worse the position became for the current player
                    # compared to what Stockfish thought was possible before the move.
                    # A positive value means the AI made a suboptimal move.
                    cp_loss = sf_eval_before_move_player_perspective - sf_eval_after_move_player_perspective
                    
                    current_ai.current_game_cp_loss += max(0, cp_loss) # Only accumulate positive loss
                    current_ai.current_game_moves_made += 1
                    print(f"  Current game ACPL for {player_name}: {current_ai.current_game_cp_loss / current_ai.current_game_moves_made:.2f}")


                self.update_board_display()
            else:
                self.status_label.config(text=f"Game {self.game_count + 1}: AI ({player_name}) could not find a move. Game ends.")
                self.end_current_game() # End game if AI can't move
                return
        except Exception as e:
            self.status_label.config(text=f"Game {self.game_count + 1}: An error occurred: {e}")
            print(f"Error during AI move: {e}")
            self.end_current_game() # End game on error
            return

        # Schedule the next AI move if the game is not over
        if not self.board.is_game_over():
            self.master.after(self.move_delay_ms, self.make_ai_move)
        else:
            self.end_current_game() # Game is over, process results

    def reset_simulation(self):
        """Resets the entire simulation, including ELOs, AI parameters, and ACPL history."""
        self.game_count = 0
        self.game_results = []
        self.white_acpl_history = []
        self.black_acpl_history = []
        # Re-initialize AIs to reset their learned parameters and ELOs
        self.white_ai = ChessAI(chess.WHITE, search_depth=self.white_ai.search_depth, initial_elo=1200)
        self.black_ai = ChessAI(chess.BLACK, search_depth=self.black_ai.search_depth, initial_elo=1200)
        self.board = chess.Board()
        self.update_board_display()
        self.status_label.config(text="Simulation reset. Ready to play.")
        # Cancel any pending 'after' calls to prevent old moves from executing
        try:
            self.master.after_cancel(self.master.after_idle(lambda: None)) 
        except Exception:
            pass # Ignore if no pending calls
        
# Main game execution
if __name__ == "__main__":
    root = tk.Tk()
    # IMPORTANT: Set the correct path to your Stockfish executable here!
    # If stockfish.exe (Windows) or stockfish (Linux/macOS) is in the same directory as this script,
    # you can just use "stockfish" or "stockfish.exe".
    # Otherwise, provide the full path, e.g., r"C:\Users\YourUser\Downloads\stockfish_15\stockfish_15_x64.exe"
    # or "/usr/local/bin/stockfish"
    STOCKFISH_EXECUTABLE_PATH = "TIK-TAK-TOES\stockfish.exe" 

    # Create AI instances with initial ELOs
    white_ai = ChessAI(chess.WHITE, search_depth=3, initial_elo=1200) # Adjust depth as needed
    black_ai = ChessAI(chess.BLACK, search_depth=3, initial_elo=1200) # Adjust depth as needed

    # Initialize and run the GUI, passing the Stockfish path
    game_gui = ChessGUI(root, white_ai, black_ai, stockfish_path=STOCKFISH_EXECUTABLE_PATH)
    root.mainloop()

