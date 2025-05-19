import chess
import torch
import torch.nn as nn
import torch.optim as optim
import random
import time
from typing import Tuple, List

# === 1. Neural Network ===
class ChessNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(14 * 8 * 8, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 1)  # Score output
        )

    def forward(self, x):
        return self.model(x)


# === 2. Board to Tensor ===
def board_to_tensor(board: chess.Board) -> torch.Tensor:
    tensor = torch.zeros(14, 8, 8)
    piece_map = board.piece_map()

    for square, piece in piece_map.items():
        row, col = divmod(square, 8)
        idx = (piece.piece_type - 1) + (0 if piece.color == chess.WHITE else 6)
        tensor[idx, row, col] = 1

    if board.has_kingside_castling_rights(chess.WHITE): tensor[12, 0, 7] = 1
    if board.has_queenside_castling_rights(chess.WHITE): tensor[12, 0, 0] = 1
    if board.has_kingside_castling_rights(chess.BLACK): tensor[12, 7, 7] = 1
    if board.has_queenside_castling_rights(chess.BLACK): tensor[12, 7, 0] = 1

    if board.ep_square:
        row, col = divmod(board.ep_square, 8)
        tensor[13, row, col] = 1

    return tensor.unsqueeze(0)  # Add batch dim


# === 3. Evaluation Wrapper ===
def evaluate(model: ChessNet, board: chess.Board) -> float:
    model.eval()
    with torch.no_grad():
        tensor = board_to_tensor(board)
        score = model(tensor).item()
        return score


# === 4. Minimax Search ===
def minimax(model: ChessNet, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> Tuple[chess.Move, float]:
    if depth == 0 or board.is_game_over():
        return None, evaluate(model, board)

    best_move = None
    legal_moves = list(board.legal_moves)

    if maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            _, eval = minimax(model, board, depth-1, alpha, beta, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return best_move, max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            _, eval = minimax(model, board, depth-1, alpha, beta, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return best_move, min_eval


# === 5. Training ===
def generate_selfplay_data(num_games=100) -> List[Tuple[torch.Tensor, float]]:
    data = []
    for _ in range(num_games):
        board = chess.Board()
        history = []

        while not board.is_game_over():
            tensor = board_to_tensor(board)
            history.append(tensor)
            move = random.choice(list(board.legal_moves))
            board.push(move)

        result = board.result()
        if result == '1-0': value = 1
        elif result == '0-1': value = -1
        else: value = 0

        for tensor in history:
            data.append((tensor, torch.tensor([value], dtype=torch.float32)))
    return data

def train(model: ChessNet, data: List[Tuple[torch.Tensor, float]], epochs=10):
    model.train()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        total_loss = 0
        for x, y in data:
            optimizer.zero_grad()
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {total_loss / len(data):.4f}")


# === 6. UCI Engine ===
def uci_loop(model: ChessNet):
    board = chess.Board()
    print("id name SimpleNNChess")
    print("id author OpenAI")
    print("uciok")

    while True:
        cmd = input().strip()
        if cmd == "uci":
            print("id name SimpleNNChess")
            print("id author OpenAI")
            print("uciok")
        elif cmd == "isready":
            print("readyok")
        elif cmd.startswith("position"):
            parts = cmd.split(" ")
            if "startpos" in parts:
                board.reset()
                moves_index = parts.index("moves") if "moves" in parts else len(parts)
                for move_str in parts[moves_index+1:]:
                    board.push_uci(move_str)
            elif "fen" in parts:
                fen = " ".join(parts[parts.index("fen") + 1:])
                board.set_fen(fen)
        elif cmd.startswith("go"):
            move, score = minimax(model, board, depth=2, alpha=-9999, beta=9999, maximizing=board.turn == chess.WHITE)
            if move:
                print(f"info score cp {int(score * 100)}")
                print(f"bestmove {move.uci()}")
            else:
                print("bestmove 0000")
        elif cmd == "quit":
            break
        elif cmd == "ucinewgame":
            board.reset()


# === 7. Main Entry ===
def main():
    model = ChessNet()

    print("Generating training data...")
    data = generate_selfplay_data(200)

    print("Training model...")
    train(model, data, epochs=5)

    torch.save(model.state_dict(), "chess_nn.pth")
    print("Starting UCI loop...")
    uci_loop(model)


if __name__ == "__main__":
    main()