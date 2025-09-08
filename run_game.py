"""
Simple script to run the Tic Tac Toe UI.
Run this to see the game in action!
"""

from src.tictactoe.ui import GameUI
from src.tictactoe.consts.board_consts import Player


def main():
    """Run the Tic Tac Toe game UI."""
    print("🎮 Starting Tic Tac Toe Game!")
    print("=" * 50)
    print("HOW TO PLAY:")
    print("• Click on any empty cell to make your move")
    print("• X goes first (red pieces)")
    print("• O goes second (blue pieces)")
    print("• Get 3 in a row to win!")
    print("")
    print("CONTROLS:")
    print("• Mouse hover: Shows valid moves")
    print("• R key: Reset the game")
    print("• ESC key: Quit the game")
    print("• Close window: Quit the game")
    print("=" * 50)
    print("Starting game window...")

    # Create and run the game
    game = GameUI(width=600, height=700)

    # Optional: Add some logging callbacks
    def on_move(move, player):
        player_name = "X" if player == Player.X_PLAYER.value else "O"
        print(f"Move: {player_name} played at ({move[0]}, {move[1]})")

    def on_game_over(winner):
        if winner is None:
            print("🎯 Game Over: It's a draw!")
        else:
            winner_name = "X" if winner == Player.X_PLAYER.value else "O"
            print(f"🎉 Game Over: {winner_name} wins!")
        print("Press 'R' to play again or ESC to quit")

    game.set_move_callback(on_move)
    game.set_game_over_callback(on_game_over)

    try:
        # This will open a pygame window and run the game
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error running game: {e}")
    finally:
        print("Thanks for playing! 🎮")


if __name__ == "__main__":
    main()
