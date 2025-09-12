# 🎮 Tic Tac Toe

This is a Tic Tac Toe game that uses pygame for the user interface and features an AI opponent powered by the minimax algorithm with alpha-beta pruning. The game supports both local multiplayer (1v1) and single-player modes against an AI with adjustable difficulty levels.

A Python-based Tic Tac Toe game with a pygame UI, support for 1v1 and 1vAI modes, and a simple AI opponent powered by minimax with alpha–beta pruning.

## ✨ Features

- ✅ Play 1 vs 1 locally
- ✅ Play 1 vs AI at different difficulties (Easy, Medium, Hard)
- ✅ Interactive menu system built with pygame-menu
- ✅ Simple AI using minimax with alpha–beta pruning
- ✅ Leaderboard tracking and match history
- ✅ Persistent data storage with SQLite
- ✅ Lightweight, no install needed (run with uvx)

## 🚀 Quick Start (One-line Run with uvx)

No need to install! Run directly from GitHub:

```bash
uvx --from git+https://github.com/<your-username>/tictactoe tictactoe
```

👉 This will:
- Download the repo into an ephemeral environment
- Install dependencies from pyproject.toml
- Run the tictactoe entrypoint defined under [project.scripts]

You'll see a game window pop up immediately. 🎉

## 🔧 Development Setup

If you want to hack on the code:

```bash
# Clone the repository
git clone https://github.com/<your-username>/tictactoe
cd tictactoe

# Sync dependencies (including dev)
uv sync --group dev

# Run the game
uv run tictactoe

# Run tests
uv run pytest

# Lint & format
uv run ruff check .
uv run ruff format .
```

## 🗂️ Project Structure

```
src/tictactoe/
├── __main__.py           # Entry point for uvx / uv run
├── app/                  # Main application and scene management
│   ├── app.py           # Main game loop & state management
│   ├── scene_manager.py # Scene transitions and orchestration
│   └── scene.py         # Base scene class
├── consts/              # Constants & enums
│   ├── ai_consts.py     # AI difficulty levels and constants
│   ├── board_consts.py  # Board dimensions and player symbols
│   ├── scene_consts.py  # Scene transition types
│   └── theme_consts.py  # UI colors and styling
├── domain/              # Core game logic
│   ├── ai.py            # Minimax + alpha-beta pruning AI
│   ├── board.py         # Game board logic and validation
│   ├── models.py        # Data models and types
│   └── services/        # Business logic services
│       ├── history_service.py    # Match history management
│       └── leaderboard_service.py # Leaderboard calculations
├── infra/               # Infrastructure and utilities
│   ├── logger.py        # Logging configuration
│   └── storage.py       # SQLite database operations
├── screens/             # Game screens and UI scenes
│   ├── game_scene.py    # Main game board interface
│   ├── history_scene.py # Match history display
│   ├── leaderboard_scene.py # Leaderboard display
│   ├── main_menu_scene.py # Main menu interface
│   ├── reset_scene.py   # Data reset confirmation
│   └── window_manager.py # Window size management
└── ui/                  # UI components and layout
    ├── layout.py        # Screen layout calculations
    └── widgets.py       # Reusable UI widgets
```

## 🧑‍💻 Development Tools

- **Linting & formatting**: ruff
- **Testing**: pytest with coverage (pytest-cov)
- **Packaging**: hatchling (via [build-system] in pyproject.toml)
- **Dependency management**: uv

## 🎯 AI Difficulty Levels

The AI opponent offers three difficulty levels:

- **Easy**: Random moves for beginners
- **Medium**: Minimax with limited depth (3 levels) for intermediate players  
- **Hard**: Full minimax with alpha-beta pruning for advanced players

## 🧠 Minimax Algorithm Implementation

The AI uses the **minimax algorithm** with **alpha-beta pruning** to make optimal moves:

### How Minimax Works
- **Minimax** is a decision-making algorithm for turn-based games
- It assumes both players play optimally (AI maximizes its score, opponent minimizes it)
- The algorithm explores all possible future game states to find the best move
- It uses a scoring system where winning = +1, losing = -1, draw = 0

### Alpha-Beta Pruning Optimization
- **Alpha-beta pruning** dramatically reduces the number of positions evaluated
- It eliminates branches that won't affect the final decision
- This makes the algorithm much faster while maintaining optimal play
- Without pruning, minimax would evaluate every possible game state (up to 9! = 362,880 positions)

### Implementation Details
- **Easy Mode**: Completely random moves (no minimax)
- **Medium Mode**: Minimax with depth limit of 3 moves ahead
- **Hard Mode**: Full minimax with alpha-beta pruning (explores all possible moves)

The AI evaluates board positions by considering:
- Immediate wins/losses
- Future strategic positions
- Blocking opponent threats
- Creating winning opportunities

## 📦 Alternative Install Options

Install globally as a user-level app:

```bash
uv tool install --from git+https://github.com/<your-username>/tictactoe tictactoe
```

Then run anywhere with:

```bash
tictactoe
```

## 🎮 How to Play

1. **Main Menu**: Choose between Player vs Player or Player vs AI
2. **Player Setup**: Enter player names and select AI difficulty (if applicable)
3. **Gameplay**: Click on empty cells to make your move
4. **Game Over**: View results and return to main menu
5. **Statistics**: Check leaderboard and match history

## 🏆 Features in Detail

- **Persistent Storage**: Game data is saved to SQLite database
- **Window Management**: Remembers window size and supports fullscreen (F11)
- **Responsive UI**: Adapts to window resizing
- **Match History**: Track all games played
- **Leaderboard**: See top players and win statistics

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/tictactoe

# Run specific test file
uv run pytest tests/test_ai.py
```

## 📝 Requirements

- Python 3.10+
- pygame >= 2.5.0
- pygame-menu >= 4.3.0
- numpy >= 1.24.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is open source.
