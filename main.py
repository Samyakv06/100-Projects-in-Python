import tkinter as tk
from tkinter import messagebox

# -----------------------------
# Tic Tac Toe Game with Score
# -----------------------------

# Initialize main window
root = tk.Tk()
root.title("Tic Tac Toe")
root.configure(bg="#2b2b2b")  # Dark background

# Game variables
current_player = "X"
player1_score = 0
player2_score = 0

# -----------------------------
# Functions
# -----------------------------

def check_winner():
    """Check if someone has won or if it's a draw"""
    global player1_score, player2_score

    # All possible winning combinations (rows, cols, diagonals)
    wins = [
        [buttons[0][0], buttons[0][1], buttons[0][2]],
        [buttons[1][0], buttons[1][1], buttons[1][2]],
        [buttons[2][0], buttons[2][1], buttons[2][2]],
        [buttons[0][0], buttons[1][0], buttons[2][0]],
        [buttons[0][1], buttons[1][1], buttons[2][1]],
        [buttons[0][2], buttons[1][2], buttons[2][2]],
        [buttons[0][0], buttons[1][1], buttons[2][2]],
        [buttons[0][2], buttons[1][1], buttons[2][0]]
    ]

    # Check all win conditions
    for combo in wins:
        if combo[0]["text"] == combo[1]["text"] == combo[2]["text"] != "":
            winner = combo[0]["text"]
            if winner == "X":
                player1_score += 1
                messagebox.showinfo("Game Over", "Player 1 (X) Wins!")
            else:
                player2_score += 1
                messagebox.showinfo("Game Over", "Player 2 (O) Wins!")
            update_score()
            reset_board()
            return

    # Check for draw (all filled)
    if all(button["text"] != "" for row in buttons for button in row):
        messagebox.showinfo("Game Over", "It's a Draw!")
        reset_board()

def button_click(row, col):
    """Handle button click for the current player"""
    global current_player

    if buttons[row][col]["text"] == "":  # If empty
        buttons[row][col]["text"] = current_player
        buttons[row][col]["fg"] = "#ff4d4d" if current_player == "X" else "#4da6ff"
        check_winner()
        # Switch player
        current_player = "O" if current_player == "X" else "X"

def reset_board():
    """Clear the board for a new round"""
    global current_player
    for row in buttons:
        for button in row:
            button.config(text="")
    current_player = "X"  # Always start with Player 1

def update_score():
    """Update score labels"""
    player1_label.config(text=f"Player 1 (X): {player1_score}")
    player2_label.config(text=f"Player 2 (O): {player2_score}")

# -----------------------------
# UI Setup
# -----------------------------

# Frames (Left = game board, Right = score)
frame_board = tk.Frame(root, bg="#2b2b2b")
frame_board.grid(row=0, column=0, padx=20, pady=20)

frame_score = tk.Frame(root, bg="#2b2b2b")
frame_score.grid(row=0, column=1, padx=20, pady=20)

# Score labels
player1_label = tk.Label(frame_score, text=f"Player 1 (X): {player1_score}",
                         font=("Arial", 14), fg="white", bg="#2b2b2b")
player1_label.pack(pady=10)

player2_label = tk.Label(frame_score, text=f"Player 2 (O): {player2_score}",
                         font=("Arial", 14), fg="white", bg="#2b2b2b")
player2_label.pack(pady=10)

# Reset button
reset_btn = tk.Button(frame_score, text="Reset Board", font=("Arial", 12),
                      command=reset_board, bg="#444", fg="white")
reset_btn.pack(pady=20)

# Game board buttons (3x3 grid)
buttons = []
for r in range(3):
    row = []
    for c in range(3):
        btn = tk.Button(frame_board, text="", width=6, height=3,
                        font=("Arial", 24, "bold"),
                        bg="#333", fg="white",
                        command=lambda r=r, c=c: button_click(r, c))
        btn.grid(row=r, column=c, padx=5, pady=5)
        row.append(btn)
    buttons.append(row)

# Run the main loop
root.mainloop()