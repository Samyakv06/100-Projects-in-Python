import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -----------------------------
# Globals
# -----------------------------
current_expression = ""
memory_value = 0.0
calculation_history = []

# Modern color scheme
COLORS = {
    'bg_dark': '#0F1419',
    'bg_medium': '#1A1F29', 
    'bg_light': '#252B37',
    'accent': '#00D4AA',
    'accent_hover': '#00B89A',
    'text_primary': '#FFFFFF',
    'text_secondary': '#A0A6B8',
    'error': '#FF6B6B',
    'warning': '#FFD93D',
    'number': '#4ECDC4',
    'operator': '#45B7D1',
    'function': '#96CEB4',
    'special': '#FFEAA7'
}

# -----------------------------
# Fonts / Responsiveness helpers
# -----------------------------
def make_fonts(root, min_ref=32):
    """Return responsive fonts based on window size."""
    w = max(400, root.winfo_width())
    h = max(350, root.winfo_height())
    base = max(8, int(min(w, h) / min_ref))
    
    display_size = max(14, base + 6)
    btn_size = max(9, base + 2)
    small_size = max(8, base)
    
    # Use standard Windows fonts that definitely exist
    display_font = tkfont.Font(family="Consolas", size=display_size, weight="normal")
    btn_font = tkfont.Font(family="Segoe UI", size=btn_size, weight="normal")
    small_font = tkfont.Font(family="Segoe UI", size=small_size)
    return display_font, btn_font, small_font

# -----------------------------
# History management
# -----------------------------
def add_to_history(expression, result):
    """Add a calculation to history."""
    global calculation_history
    if expression and result != "Error":
        calculation_history.append((expression, result))
        if len(calculation_history) > 50:
            calculation_history = calculation_history[-50:]
        update_history_display()

def update_history_display():
    """Update the history listbox."""
    history_listbox.delete(0, tk.END)
    for i, (expr, result) in enumerate(reversed(calculation_history)):
        history_listbox.insert(tk.END, f"{expr} = {result}")

def on_history_select(event):
    """Handle selection from history."""
    global current_expression
    selection = history_listbox.curselection()
    if selection:
        history_text = history_listbox.get(selection[0])
        result = history_text.split(" = ")[-1]
        current_expression = result
        _update_entry()

def clear_history():
    """Clear calculation history."""
    global calculation_history
    calculation_history = []
    update_history_display()

# -----------------------------
# Calculator logic
# -----------------------------
def on_button_click(char):
    """Handle calculator button clicks."""
    global current_expression, memory_value
    original_expression = current_expression
    
    if char == "C":
        current_expression = ""
    elif char == "←":
        current_expression = current_expression[:-1]
    elif char == "=":
        try:
            safe_dict = {
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
                'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
                'sqrt': math.sqrt, 'ln': math.log, 'log': math.log10, 'log2': math.log2,
                'exp': math.exp, 'pow': pow,
                'abs': abs, 'factorial': math.factorial, 'gcd': math.gcd,
                'lcm': getattr(math, "lcm", lambda a, b: 0),
                'pi': math.pi, 'e': math.e, 'g': 9.81
            }
            expr = current_expression.replace("√", "sqrt(").replace("∛", "**(1/3)").replace("^", "**")
            expr = expr.replace("π", "pi")
            result = eval(expr, {"__builtins__": None}, safe_dict)
            
            # Format result nicely
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 8)
            
            add_to_history(original_expression, str(result))
            current_expression = str(result)
        except Exception:
            current_expression = "Error"
    elif char == "+/-":
        try:
            val = float(current_expression)
            current_expression = str(-val)
        except Exception:
            current_expression = "Error"
    elif char == "MC":
        memory_value = 0.0
    elif char == "MR":
        current_expression += str(memory_value)
    elif char == "MS":
        try:
            memory_value = float(eval(current_expression, {"__builtins__": None}, math.__dict__))
        except Exception:
            memory_value = 0.0
    elif char == "M+":
        try:
            memory_value += float(eval(current_expression, {"__builtins__": None}, math.__dict__))
        except Exception:
            pass
    else:
        if char in {"sin","cos","tan","asin","acos","atan","sinh","cosh","tanh","asinh","acosh","atanh",
                    "ln","log","log2","exp","sqrt","pow","factorial"}:
            current_expression += f"{char}("
        elif char == "%":
            current_expression += "*0.01"
        elif char == "π":
            current_expression += "pi"
        elif char == "∛":
            current_expression += "**(1/3)"
        elif char == "√":
            current_expression += "sqrt("
        elif char == "^":
            current_expression += "**"
        else:
            current_expression += str(char)

    _update_entry()

def _update_entry():
    entry_var.set(current_expression)

# -----------------------------
# Graph suggestions & plotting
# -----------------------------
graph_suggestions = [
    "x**2", "-x**2", "(x-2)**2 + 3", "x**3", "x**4",
    "sin(x)", "cos(x)", "tan(x)", "abs(sin(x))",
    "log(x)", "ln(x)", "exp(x)", "log2(x)",
    "sin(2*x)*exp(-0.5*x)", "sin(5*x)/x",
    "sin(x)+cos(x)", "x*sin(x)", "2*abs(x)", "2*x**2 - 5*x + 3",
    "x**2 + sin(x)", "cos(x)*exp(-x/5)", "x**3 - 3*x"
]

def update_suggestions(event=None):
    text = graph_entry_var.get().strip().lower()
    if not text:
        suggestions_listbox.pack_forget()
        return
    filtered = [s for s in graph_suggestions if text in s.lower()]
    if filtered:
        suggestions_listbox.delete(0, tk.END)
        for s in filtered:
            suggestions_listbox.insert(tk.END, s)
        suggestions_listbox.pack(fill="x", padx=20, pady=(0,10))
    else:
        suggestions_listbox.pack_forget()

def select_suggestion(event):
    sel = suggestions_listbox.curselection()
    if sel:
        s = suggestions_listbox.get(sel)
        graph_entry_var.set(s)
        suggestions_listbox.pack_forget()

def plot_graph(event=None):
    expr = graph_entry_var.get().strip()
    scope = {
        'x': np.linspace(-10, 10, 1000),
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
        'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
        'sqrt': np.sqrt, 'log': np.log10, 'ln': np.log, 'log2': np.log2,
        'exp': np.exp, 'pi': np.pi, 'e': np.e, 'abs': np.abs
    }
    ax.clear()
    try:
        if not expr:
            ax.text(0.5, 0.5, "Enter a function above to visualize", 
                   ha="center", va="center", color=COLORS['text_secondary'], 
                   fontsize=title_font['size'], style='italic')
            canvas.draw()
            return
        
        expr = expr.replace("^", "**").replace("π", "pi")
        y = eval(expr, {"__builtins__": None}, scope)
        y = np.where(np.isfinite(y), y, np.nan)
        
        # Modern plot styling
        ax.plot(scope['x'], y, linewidth=3, color=COLORS['accent'], alpha=0.9)
        ax.set_title(f"f(x) = {expr}", fontsize=title_font['size'], color=COLORS['text_primary'], pad=20)
        ax.set_xlabel("x", fontsize=axis_font['size'], color=COLORS['text_primary'])
        ax.set_ylabel("y", fontsize=axis_font['size'], color=COLORS['text_primary'])
        
        # Modern grid and styling
        ax.grid(True, linestyle='-', alpha=0.1, color=COLORS['text_secondary'])
        ax.set_facecolor(COLORS['bg_dark'])
        fig.patch.set_facecolor(COLORS['bg_medium'])
        
        # Subtle axis lines
        ax.axhline(y=0, color=COLORS['text_secondary'], linewidth=1, alpha=0.5)
        ax.axvline(x=0, color=COLORS['text_secondary'], linewidth=1, alpha=0.5)
        
        # Modern spines
        for spine in ax.spines.values():
            spine.set_color(COLORS['text_secondary'])
            spine.set_linewidth(0.5)
        
        ax.tick_params(colors=COLORS['text_secondary'], size=4)
        
    except Exception as e:
        ax.text(0.5, 0.5, f"Invalid function", 
               ha="center", va="center", color=COLORS['error'], 
               fontsize=axis_font['size'])
    finally:
        canvas.draw_idle()

# -----------------------------
# Build Modern UI
# -----------------------------
root = tk.Tk()
root.title("CalcPro - Scientific Calculator & Grapher")
root.geometry("1300x750")
root.minsize(800, 500)
root.configure(bg=COLORS['bg_dark'])

# Configure ttk style
style = ttk.Style()
style.theme_use("clam")

# Override some ttk styles for modern look
style.configure('Modern.TButton',
                background=COLORS['bg_light'],
                foreground=COLORS['text_primary'],
                borderwidth=0,
                focuscolor='none')

style.map('Modern.TButton',
          background=[('active', COLORS['accent_hover'])])

# Main container
main_container = tk.Frame(root, bg=COLORS['bg_dark'])
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# Header
header_frame = tk.Frame(main_container, bg=COLORS['bg_dark'])
header_frame.pack(fill="x", pady=(0, 20))

title_label = tk.Label(
    header_frame, 
    text="CalcPro", 
    font=("Segoe UI", 24, "bold"),
    bg=COLORS['bg_dark'], 
    fg=COLORS['accent']
)
title_label.pack(side="left")

subtitle_label = tk.Label(
    header_frame,
    text="Scientific Calculator & Function Plotter",
    font=("Segoe UI", 11),
    bg=COLORS['bg_dark'],
    fg=COLORS['text_secondary']
)
subtitle_label.pack(side="left", padx=(15, 0), pady=(5, 0))

# Content area
content_frame = tk.Frame(main_container, bg=COLORS['bg_dark'])
content_frame.pack(fill="both", expand=True)

# Left panel: Calculator + History
left_panel = tk.Frame(content_frame, bg=COLORS['bg_medium'], relief='raised', bd=1)
left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

# Calculator section
calc_section = tk.Frame(left_panel, bg=COLORS['bg_medium'])
calc_section.pack(fill="both", expand=True, padx=20, pady=20)

# Display
display_frame = tk.Frame(calc_section, bg=COLORS['bg_dark'], relief='sunken', bd=2)
display_frame.pack(fill="x", pady=(0, 20))

entry_var = tk.StringVar(value=current_expression)
entry = tk.Entry(
    display_frame,
    textvariable=entry_var,
    justify="right",
    bg=COLORS['bg_dark'],
    fg=COLORS['text_primary'],
    insertbackground=COLORS['accent'],
    bd=0,
    relief='flat',
    font=("Consolas", 16)
)
entry.pack(fill="x", padx=15, pady=15)

# Button definitions with color categories
button_config = [
    # Row 1: Memory and Clear
    [("MC","#8B5CF6"),("MR","#8B5CF6"),("MS","#8B5CF6"),("M+","#8B5CF6"),("C","#EF4444"),("←","#EF4444")],
    # Row 2: Trig functions
    [("sin","#10B981"),("cos","#10B981"),("tan","#10B981"),("^","#3B82F6"),("!","#10B981"),("%","#3B82F6")],
    # Row 3: Inverse trig
    [("asin","#10B981"),("acos","#10B981"),("atan","#10B981"),("√","#10B981"),("∛","#10B981"),("pow","#10B981")],
    # Row 4: Hyperbolic and brackets
    [("sinh","#10B981"),("cosh","#10B981"),("tanh","#10B981"),("(","#3B82F6"),(")","#3B82F6"),("mod","#3B82F6")],
    # Row 5: Numbers and operators
    [("7","#6B7280"),("8","#6B7280"),("9","#6B7280"),("/","#3B82F6"),("*","#3B82F6"),("π","#F59E0B")],
    [("4","#6B7280"),("5","#6B7280"),("6","#6B7280"),("-","#3B82F6"),("ln","#10B981"),("log","#10B981")],
    [("1","#6B7280"),("2","#6B7280"),("3","#6B7280"),("+","#3B82F6"),("log2","#10B981"),("exp","#10B981")],
    [("0","#6B7280"),(".","#6B7280"),("±","#3B82F6"),("g","#F59E0B"),("deg","#F59E0B"),("rad","#F59E0B")],
    # Row 9: Final row
    [("lcm","#10B981"),("gcd","#10B981"),("=","#00D4AA"),("=","#00D4AA"),("=","#00D4AA"),("=","#00D4AA")]
]

# Create button grid with modern styling
buttons_frame = tk.Frame(calc_section, bg=COLORS['bg_medium'])
buttons_frame.pack(fill="both", expand=True)

btn_widgets = []
for row_idx, row in enumerate(button_config):
    for col_idx, (text, color) in enumerate(row):
        # Map button text for better display
        display_text = text
        actual_command = text
        if text == "!":
            display_text = "x!"
            actual_command = "factorial"
        elif text == "±":
            actual_command = "+/-"
        
        btn = tk.Button(
            buttons_frame,
            text=display_text,
            command=lambda t=actual_command: on_button_click(t),
            bg=color,
            fg='white',
            activebackground=color,
            activeforeground='white',
            bd=0,
            relief='flat',
            cursor='hand2',
            font=("Segoe UI", 10, "bold")
        )
        
        # Special handling for equals button
        if text == "=" and col_idx == 2:
            btn.grid(row=row_idx, column=col_idx, columnspan=4, padx=3, pady=3, sticky="nsew")
            btn_widgets.append(btn)
            break
        elif text == "=" and col_idx > 2:
            continue
        else:
            btn.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nsew")
            btn_widgets.append(btn)

# Configure grid weights
for i in range(len(button_config)):
    buttons_frame.grid_rowconfigure(i, weight=1)
for j in range(6):
    buttons_frame.grid_columnconfigure(j, weight=1)

# History section
history_section = tk.Frame(left_panel, bg=COLORS['bg_medium'])
history_section.pack(side="bottom", fill="x", padx=20, pady=(0, 20))

history_header = tk.Frame(history_section, bg=COLORS['bg_medium'])
history_header.pack(fill="x", pady=(0, 10))

history_title = tk.Label(
    history_header,
    text="History",
    font=("Segoe UI", 12, "bold"),
    bg=COLORS['bg_medium'],
    fg=COLORS['text_primary']
)
history_title.pack(side="left")

clear_btn = tk.Button(
    history_header,
    text="Clear",
    command=clear_history,
    bg=COLORS['error'],
    fg='white',
    bd=0,
    relief='flat',
    cursor='hand2',
    font=("Segoe UI", 9)
)
clear_btn.pack(side="right", padx=(0, 0), ipadx=10)

# History listbox
history_list_frame = tk.Frame(history_section, bg=COLORS['bg_dark'], relief='sunken', bd=1)
history_list_frame.pack(fill="x")

history_scrollbar = ttk.Scrollbar(history_list_frame)
history_scrollbar.pack(side="right", fill="y")

history_listbox = tk.Listbox(
    history_list_frame,
    height=6,
    bg=COLORS['bg_dark'],
    fg=COLORS['text_primary'],
    selectbackground=COLORS['accent'],
    selectforeground=COLORS['bg_dark'],
    bd=0,
    relief='flat',
    yscrollcommand=history_scrollbar.set,
    font=("Consolas", 9)
)
history_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
history_scrollbar.config(command=history_listbox.yview)
history_listbox.bind("<Double-Button-1>", on_history_select)

# Right panel: Graph plotter
right_panel = tk.Frame(content_frame, bg=COLORS['bg_medium'], relief='raised', bd=1)
right_panel.pack(side="right", fill="both", expand=True)

# Graph header
graph_header = tk.Frame(right_panel, bg=COLORS['bg_medium'])
graph_header.pack(fill="x", padx=20, pady=(20, 15))

graph_title = tk.Label(
    graph_header,
    text="Function Plotter",
    font=("Segoe UI", 14, "bold"),
    bg=COLORS['bg_medium'],
    fg=COLORS['text_primary']
)
graph_title.pack(side="left")

# Graph input
graph_input_frame = tk.Frame(right_panel, bg=COLORS['bg_medium'])
graph_input_frame.pack(fill="x", padx=20, pady=(0, 15))

graph_label = tk.Label(
    graph_input_frame,
    text="f(x) =",
    font=("Segoe UI", 12, "bold"),
    bg=COLORS['bg_medium'],
    fg=COLORS['accent']
)
graph_label.pack(side="left", padx=(0, 10))

graph_entry_var = tk.StringVar()
graph_entry = tk.Entry(
    graph_input_frame,
    textvariable=graph_entry_var,
    bg=COLORS['bg_dark'],
    fg=COLORS['text_primary'],
    insertbackground=COLORS['accent'],
    bd=0,
    relief='flat',
    font=("Consolas", 12)
)
graph_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)
graph_entry.bind("<KeyRelease>", update_suggestions)
graph_entry.bind("<Return>", plot_graph)

plot_button = tk.Button(
    graph_input_frame,
    text="Plot",
    command=plot_graph,
    bg=COLORS['accent'],
    fg='white',
    activebackground=COLORS['accent_hover'],
    bd=0,
    relief='flat',
    cursor='hand2',
    font=("Segoe UI", 10, "bold")
)
plot_button.pack(side="right", ipadx=20, ipady=5)

# Suggestions
suggestions_listbox = tk.Listbox(
    right_panel,
    height=4,
    bg=COLORS['bg_dark'],
    fg=COLORS['text_secondary'],
    selectbackground=COLORS['accent'],
    bd=0,
    relief='flat',
    font=("Consolas", 9)
)
suggestions_listbox.bind("<<ListboxSelect>>", select_suggestion)

# Matplotlib with modern styling
fig, ax = plt.subplots(figsize=(7, 5), facecolor=COLORS['bg_medium'])
ax.set_facecolor(COLORS['bg_dark'])
canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill="both", expand=True, padx=20, pady=(0, 20))

# Font references for matplotlib
title_font = {'size': 14}
axis_font = {'size': 11}

# Initial empty plot
ax.text(0.5, 0.5, "Enter a function above to visualize", 
       ha="center", va="center", color=COLORS['text_secondary'], 
       fontsize=14, style='italic')
ax.set_facecolor(COLORS['bg_dark'])
fig.patch.set_facecolor(COLORS['bg_medium'])
canvas.draw()

# -----------------------------
# Responsiveness: resize handler
# -----------------------------
def on_root_resize(event):
    if event.widget != root:
        return
        
    try:
        display_font, btn_font, small_font = make_fonts(root, min_ref=35)
        
        # Update fonts safely
        entry.configure(font=display_font)
        graph_entry.configure(font=display_font)
        history_listbox.configure(font=small_font)
        suggestions_listbox.configure(font=small_font)
        
        # Update button fonts
        for btn in btn_widgets:
            btn.configure(font=btn_font)
        
        # Update matplotlib fonts
        title_font['size'] = max(12, int(display_font['size'] * 0.8))
        axis_font['size'] = max(10, int(display_font['size'] * 0.6))
        
    except Exception as e:
        # Fallback to default fonts if there's an issue
        pass

root.bind("<Configure>", on_root_resize)

# Apply initial styling
root.update_idletasks()

# Create a dummy event for initial resize
class DummyEvent:
    def __init__(self):
        self.widget = root

on_root_resize(DummyEvent())

# Start the application
root.mainloop()