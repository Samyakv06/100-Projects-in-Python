import tkinter as tk
from tkinter import messagebox, ttk
import random
from wordfreq import top_n_list
from datetime import datetime

# Try to import NLTK for word validation
try:
    import nltk
    from nltk.corpus import words
    NLTK_AVAILABLE = True
    
    # Download required data if not present
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        print("Downloading NLTK words corpus...")
        nltk.download('words', quiet=True)
        
    english_words = set(word.lower() for word in words.words() if 5 <= len(word) <= 10)
    print(f"Loaded {len(english_words)} valid words from NLTK")
    
except ImportError:
    NLTK_AVAILABLE = False
    english_words = set()
    print("Warning: NLTK not installed. Install with: pip install nltk")

# Load word lists for different lengths (5-7 letters only)
word_lists = {}
for length in range(5, 8):  # 5, 6, 7 letters only
    word_lists[length] = {
        'answers': [w.lower() for w in top_n_list("en", 3000) if len(w) == length and w.isalpha()],
        'valid': set([w.lower() for w in top_n_list("en", 15000) if len(w) == length and w.isalpha()])
    }

# Combine with NLTK words if available
if NLTK_AVAILABLE:
    for length in range(5, 8):
        nltk_words = set(word.lower() for word in english_words if len(word) == length)
        word_lists[length]['valid'] = word_lists[length]['valid'].union(nltk_words)

def is_valid_word(word, word_length):
    """Check if a word is valid for the given length"""
    word = word.lower()
    return word in word_lists[word_length]['valid']

class WordleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Wordle")
        
        # Wordle Dark Mode Color Palette
        self.COLORS = {
            "background": "#121213",
            "tile_bg": "#1e1e1e",
            "text": "#EFEFEF",
            "green": "#6aaa64",
            "yellow": "#c9b458",
            "grey": "#3a3a3c",
            "key_bg": "#818384",
            "tile_border": "#3a3a3c"
        }
        
        self.root.configure(bg=self.COLORS["background"])
        
        # Increased window size for side-by-side layout
        self.root.geometry("850x650")
        self.root.minsize(850, 650)
        
        self.word_length = 5
        self.max_attempts = 6
        self.score = 0
        self.game_history = []
        
        # Font preference: Poppins, with Arial as fallback
        self.font = ("Poppins", 10)
        
        # Setup modern ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TCombobox", fieldbackground=self.COLORS["key_bg"], 
                             background=self.COLORS["key_bg"], 
                             foreground=self.COLORS["text"],
                             selectbackground=self.COLORS["green"],
                             selectforeground=self.COLORS["text"],
                             font=self.font)
        self.style.map("TCombobox", fieldbackground=[('readonly', self.COLORS["key_bg"])])

        self.setup_ui()
        self.reset_game()
        
        self.root.bind("<Key>", self.handle_key)
        self.root.focus_set()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg=self.COLORS["background"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.create_header()
        
        self.controls_frame = tk.Frame(self.main_frame, bg=self.COLORS["background"])
        self.controls_frame.pack(pady=(0, 10))
        
        self.create_controls()
        
        # Main container for side-by-side layout
        self.game_content_frame = tk.Frame(self.main_frame, bg=self.COLORS["background"])
        self.game_content_frame.pack(fill="both", expand=True, pady=10)

        # Left side for the game grid
        self.game_grid_frame = tk.Frame(self.game_content_frame, bg=self.COLORS["background"])
        self.game_grid_frame.pack(side="left", padx=(0, 20), expand=True)
        
        # Right side for history and keyboard
        self.right_panel_frame = tk.Frame(self.game_content_frame, bg=self.COLORS["background"])
        self.right_panel_frame.pack(side="right", padx=(20, 0), expand=True, fill="y")
        
        self.create_history()
        self.create_keyboard()
        self.create_game_grid()
        self.update_window_size()

    def create_header(self):
        header_frame = tk.Frame(self.main_frame, bg=self.COLORS["background"])
        header_frame.pack(pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="ENHANCED WORDLE", 
                               font=(self.font[0], 28, "bold"), fg=self.COLORS["text"], 
                               bg=self.COLORS["background"])
        title_label.pack()
        
        self.score_label = tk.Label(header_frame, text=f"Score: {self.score}", 
                                    font=(self.font[0], 14), fg="#878a8c", 
                                    bg=self.COLORS["background"])
        self.score_label.pack(pady=(5, 0))
    
    def create_controls(self):
        length_frame = tk.Frame(self.controls_frame, bg=self.COLORS["background"])
        length_frame.pack(side="left", padx=(0, 10))
        
        tk.Label(length_frame, text="Length:", font=(self.font[0], 12), fg=self.COLORS["text"], 
                 bg=self.COLORS["background"]).pack(side="left", padx=(0, 5))
        
        self.length_var = tk.StringVar(value="5")
        length_combo = ttk.Combobox(length_frame, textvariable=self.length_var,
                                    values=["5", "6", "7"], width=3, state="readonly")
        length_combo.pack(side="left")
        length_combo.bind("<<ComboboxSelected>>", self.change_word_length)
        
        self.history_btn = tk.Button(self.controls_frame, text="Show History", 
                                     font=(self.font[0], 10, "bold"),
                                     bg=self.COLORS["key_bg"], fg=self.COLORS["text"], relief="flat",
                                     command=self.toggle_history, padx=10, pady=5)
        self.history_btn.pack(side="right", padx=(10, 0))

        new_game_btn = tk.Button(self.controls_frame, text="New Game", 
                                 font=(self.font[0], 10, "bold"),
                                 bg=self.COLORS["green"], fg=self.COLORS["text"], relief="flat",
                                 command=self.start_new_game, padx=10, pady=5)
        new_game_btn.pack(side="right")

    def create_game_grid(self):
        for widget in self.game_grid_frame.winfo_children():
            widget.destroy()
        
        self.grid_labels = []
        for r in range(self.max_attempts):
            row_labels = []
            for c in range(self.word_length):
                lbl = tk.Label(self.game_grid_frame, text="", width=3, height=2, 
                               font=(self.font[0], 24, "bold"),
                               bg=self.COLORS["background"], 
                               fg=self.COLORS["text"],
                               highlightbackground=self.COLORS["tile_border"],
                               highlightthickness=2)
                lbl.grid(row=r, column=c, padx=3, pady=3)
                row_labels.append(lbl)
            self.grid_labels.append(row_labels)

    def create_keyboard(self):
        self.keyboard_container = tk.Frame(self.right_panel_frame, bg=self.COLORS["background"])
        self.keyboard_container.pack(side="bottom", fill="x", pady=(20, 0))
            
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        self.key_buttons = {}
        
        for row_idx, keys in enumerate(rows):
            frame = tk.Frame(self.keyboard_container, bg=self.COLORS["background"])
            frame.pack(pady=4)
            
            if row_idx == 2:
                enter_btn = tk.Button(frame, text="ENTER", width=6, height=2,
                                       font=(self.font[0], 10, "bold"),
                                       bg=self.COLORS["key_bg"], fg=self.COLORS["text"],
                                       relief="flat", borderwidth=0,
                                       command=self.submit_guess)
                enter_btn.pack(side="left", padx=2)
            
            for ch in keys:
                btn = tk.Button(frame, text=ch, width=3, height=2,
                                font=(self.font[0], 11, "bold"),
                                bg=self.COLORS["key_bg"], fg=self.COLORS["text"],
                                relief="flat", borderwidth=0,
                                command=lambda c=ch: self.add_letter(c.lower()))
                btn.pack(side="left", padx=2)
                self.key_buttons[ch] = btn
            
            if row_idx == 2:
                back_btn = tk.Button(frame, text="⌫", width=6, height=2,
                                      font=(self.font[0], 11, "bold"),
                                      bg=self.COLORS["key_bg"], fg=self.COLORS["text"],
                                      relief="flat", borderwidth=0,
                                      command=self.remove_letter)
                back_btn.pack(side="left", padx=2)

    def create_history(self):
        self.history_frame = tk.Frame(self.right_panel_frame, bg=self.COLORS["background"])
        self.history_frame.pack(side="top", fill="both", expand=True)
        self.history_visible = False
        self.history_frame.pack_forget() # Initially hidden
        
        history_label = tk.Label(self.history_frame, text="Game History", 
                                 font=(self.font[0], 16, "bold"), fg=self.COLORS["text"], 
                                 bg=self.COLORS["background"])
        history_label.pack(pady=(0, 10))
        
        history_container = tk.Frame(self.history_frame, bg=self.COLORS["background"])
        history_container.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(history_container)
        scrollbar.pack(side="right", fill="y")
        
        self.history_text = tk.Text(history_container, height=10, 
                                     bg=self.COLORS["key_bg"], fg=self.COLORS["text"], 
                                     font=("Courier New", 10),
                                     yscrollcommand=scrollbar.set,
                                     relief="flat", borderwidth=0)
        self.history_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_text.yview)

    def change_word_length(self, event=None):
        new_length = int(self.length_var.get())
        if new_length != self.word_length:
            self.word_length = new_length
            self.max_attempts = self.word_length + 1
            
            self.update_window_size()
            self.create_game_grid()
            self.reset_keyboard_colors()
            self.reset_game()
            
            if self.history_visible:
                self.toggle_history()

    def update_window_size(self):
        base_width = 850
        self.root.geometry(f"{base_width}x650")

    def toggle_history(self):
        if self.history_visible:
            self.history_frame.pack_forget()
            self.history_btn.config(text="Show History")
            self.history_visible = False
        else:
            self.history_frame.pack(side="top", fill="both", expand=True)
            self.history_btn.config(text="Hide History")
            self.history_visible = True
            self.update_history_display()

    def update_history_display(self):
        self.history_text.delete(1.0, tk.END)
        if not self.game_history:
            self.history_text.insert(tk.END, "No games played yet.")
            return

        for i, game in enumerate(reversed(self.game_history[-10:])):
            self.history_text.insert(tk.END, f"Game {len(self.game_history) - i}: ")
            self.history_text.insert(tk.END, f"{game['word'].upper()} ({game['length']} letters) - ")
            if game['won']:
                self.history_text.insert(tk.END, f"Won in {game['attempts']} {'try' if game['attempts'] == 1 else 'tries'}\n")
            else:
                self.history_text.insert(tk.END, "Lost\n")
            
            for j, guess in enumerate(game['guesses']):
                self.history_text.insert(tk.END, f"  {j+1}. {guess.upper()}\n")
            self.history_text.insert(tk.END, "\n")

    def reset_game(self):
        if not word_lists[self.word_length]['answers']:
            messagebox.showerror("Error", f"No {self.word_length}-letter words available!", parent=self.root)
            return
            
        self.secret_word = random.choice(word_lists[self.word_length]['answers'])
        self.current_row = 0
        self.current_col = 0
        self.guess = ""
        self.current_game_guesses = []
        print(f"New {self.word_length}-letter word selected: {self.secret_word}")

    def add_letter(self, letter):
        if self.current_col < self.word_length and self.current_row < self.max_attempts:
            lbl = self.grid_labels[self.current_row][self.current_col]
            lbl.config(
                text=letter.upper(),
                bg=self.COLORS["tile_bg"],
                highlightbackground=self.COLORS["tile_bg"]
            )
            self.guess += letter
            self.current_col += 1

    def remove_letter(self):
        if self.current_col > 0:
            self.current_col -= 1
            lbl = self.grid_labels[self.current_row][self.current_col]
            lbl.config(
                text="", 
                bg=self.COLORS["background"],
                highlightbackground=self.COLORS["tile_border"]
            )
            self.guess = self.guess[:-1]

    def handle_key(self, event):
        if event.keysym == "BackSpace":
            self.remove_letter()
        elif event.keysym == "Return":
            self.submit_guess()
        elif event.char.isalpha() and len(event.char) == 1:
            self.add_letter(event.char.lower())

    def submit_guess(self):
        if len(self.guess) != self.word_length:
            messagebox.showwarning("Invalid", f"Word must be {self.word_length} letters!", parent=self.root)
            return
        
        if not is_valid_word(self.guess, self.word_length):
            messagebox.showwarning("Invalid Word", 
                                   f"'{self.guess.upper()}' is not a valid English word!", 
                                   parent=self.root)
            return
        
        self.current_game_guesses.append(self.guess)
        self.animate_guess_reveal()

    def animate_guess_reveal(self):
        secret_copy = list(self.secret_word)
        guess_copy = list(self.guess)
        colors = [""] * self.word_length
        
        for i in range(self.word_length):
            if guess_copy[i] == secret_copy[i]:
                colors[i] = self.COLORS["green"]
                secret_copy[i] = None
                guess_copy[i] = None
        
        for i in range(self.word_length):
            if guess_copy[i] is None:
                continue
            if guess_copy[i] in secret_copy:
                colors[i] = self.COLORS["yellow"]
                secret_copy[secret_copy.index(guess_copy[i])] = None
            else:
                colors[i] = self.COLORS["grey"]

        def flip_tile(index):
            if index < self.word_length:
                lbl = self.grid_labels[self.current_row][index]
                lbl.config(bg=colors[index], highlightbackground=colors[index])
                self.update_keyboard_color(self.guess[index].upper(), colors[index])
                self.root.after(200, lambda: flip_tile(index + 1))
            else:
                self.check_end_game()

        flip_tile(0)

    def check_end_game(self):
        if self.guess == self.secret_word:
            self.show_win_message()
            return

        self.current_row += 1
        self.current_col = 0
        self.guess = ""

        if self.current_row == self.max_attempts:
            self.show_lose_message()

    def show_win_message(self):
        self.score += 1
        self.score_label.config(text=f"Score: {self.score}")
        
        self.game_history.append({
            'word': self.secret_word,
            'length': self.word_length,
            'won': True,
            'attempts': self.current_row + 1,
            'guesses': self.current_game_guesses.copy(),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        messagebox.showinfo("Congratulations!", 
                            f"You got it in {self.current_row + 1} {'try' if self.current_row == 0 else 'tries'}!\n\n"
                            f"The word was: {self.secret_word.upper()}", 
                            parent=self.root)
        self.start_new_game()

    def show_lose_message(self):
        self.game_history.append({
            'word': self.secret_word,
            'length': self.word_length,
            'won': False,
            'attempts': self.max_attempts,
            'guesses': self.current_game_guesses.copy(),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        messagebox.showinfo("Better luck next time!", 
                            f"The word was: {self.secret_word.upper()}", 
                            parent=self.root)
        self.start_new_game()

    def update_keyboard_color(self, letter, color):
        btn = self.key_buttons.get(letter)
        if btn:
            current_bg = btn.cget("bg")
            if current_bg == self.COLORS["green"]:
                return
            if current_bg == self.COLORS["yellow"] and color == self.COLORS["grey"]:
                return
                
            btn.config(bg=color, fg=self.COLORS["text"])

    def reset_keyboard_colors(self):
        for btn in self.key_buttons.values():
            btn.config(bg=self.COLORS["key_bg"], fg=self.COLORS["text"])

    def start_new_game(self):
        for r in range(self.max_attempts):
            for c in range(self.word_length):
                if r < len(self.grid_labels) and c < len(self.grid_labels[r]):
                    self.grid_labels[r][c].config(
                        text="", 
                        bg=self.COLORS["background"], 
                        highlightbackground=self.COLORS["tile_border"]
                    )
        
        self.reset_keyboard_colors()
        self.reset_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = WordleGame(root)
    root.mainloop()