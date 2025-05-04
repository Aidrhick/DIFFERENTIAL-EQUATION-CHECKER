import customtkinter as ctk
from tkinter import messagebox
import math
import re
import time


class ExactCheckerApp:
    def __init__(self):
        # Initialize the window
        self.root = ctk.CTk()
        self.root.title("CheckXACT: Exact Equation Examiner")
        self.root.geometry("600x700")

        self.active_input = None  # To track which input is active

        # Title Label
        self.titlepane = ctk.CTkLabel(
            self.root, text="CheckXACT\nThe Exact Equation Examiner", font=("Times New Roman", 16)
        )
        self.titlepane.pack(pady=15)

        # Input for M(x, y)
        self.label_M = ctk.CTkLabel(self.root, text="M(x, y):", font=("Times New Roman", 14))
        self.label_M.pack(pady=10)
        self.variable_M = ctk.CTkEntry(self.root, font=("Times New Roman", 12), width=300)
        self.variable_M.pack(pady=10)
        self.variable_M.bind("<FocusIn>", lambda e: self.set_active_input("M"))

        # Input for N(x, y)
        self.label_N = ctk.CTkLabel(self.root, text="N(x, y):", font=("Times New Roman", 14))
        self.label_N.pack(pady=5)
        self.variable_N = ctk.CTkEntry(self.root, font=("Times New Roman", 12), width=300)
        self.variable_N.pack(pady=5)
        self.variable_N.bind("<FocusIn>", lambda e: self.set_active_input("N"))

        # Scientific Buttons
        self.create_scientific_buttons()

        # Check Button
        self.check_button = ctk.CTkButton(
            self.root,
            text="Check the Equation",
            font=("Times New Roman", 12),
            command=self.check_equation,
        )
        self.check_button.pack(pady=20)

        # Loading bar
        self.loading_label = ctk.CTkLabel(self.root, text="Processing...", font=("Times New Roman", 12))
        self.progress_bar = ctk.CTkProgressBar(self.root, width=300)
        self.progress_bar.set(0)

    def create_scientific_buttons(self):
        """Create buttons for scientific functions."""
        self.button_panel = ctk.CTkFrame(self.root)
        self.button_panel.pack(pady=10)

        buttons = [
            ('1', '2', '3', '+'),
            ('4', '5', '6', '-'),
            ('7', '8', '9', '*'),
            ('x', 'y', '0', '/'),
            ('sin', 'cos', 'tan', 'log'),
            ('(', ')', ',', 'exp'),
            ('clear', 'delete'),
        ]

        for row in buttons:
            button_row = ctk.CTkFrame(self.button_panel)
            button_row.pack(pady=5)
            for button_text in row:
                button = ctk.CTkButton(
                    button_row,
                    text=button_text,
                    width=80,
                    command=lambda b=button_text: self.append_to_input(b)
                )
                button.pack(side="left", padx=5)

    def set_active_input(self, field):
        """Set the active input field."""
        self.active_input = field

    def append_to_input(self, value):
        """Append value to the active input field."""
        target_field = self.variable_M if self.active_input == "M" else self.variable_N if self.active_input == "N" else None
        if target_field:
            if value == "clear":
                target_field.delete(0, "end")
            elif value == "delete":
                target_field.delete(len(target_field.get()) - 1, "end")
            else:
                target_field.insert("end", value)

    def check_equation(self):
        """Validate and check the entered equation for exactness and homogeneity."""
        m_input = self.variable_M.get()
        n_input = self.variable_N.get()

        try:
            # Parse the inputs as mathematical expressions
            M = self.parse_expression(m_input)
            N = self.parse_expression(n_input)

            # Show the loading bar
            self.show_loading_bar()

            # Check if the equation is exact
            exact = self.is_exact(M, N)
            exact_result = "exact" if exact else "not exact"

            # Check if the equation is homogeneous
            homogeneous, degree = self.is_homogeneous(M, N)
            homogeneous_result = (
                f"homogeneous of degree {degree}" if homogeneous else "non-homogeneous"
            )

            # Show the result in a messagebox
            result = f"The equation is {exact_result}.\nThe equation is {homogeneous_result}."
            messagebox.showinfo("Result", result)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Clear the input fields after checking
            self.variable_M.delete(0, ctk.END)
            self.variable_N.delete(0, ctk.END)

            # Reset the progress bar and label
            self.progress_bar.set(0)
            self.loading_label.pack_forget()

    def show_loading_bar(self):
        """Show and update the loading bar during processing."""
        self.loading_label.pack(pady=10)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        # Simulate some calculation progress (replace this with actual calculation logic)
        steps = 10
        for i in range(steps):
            time.sleep(0.5)  # Simulate delay for processing
            self.progress_bar.set((i + 1) / steps)  # Update the progress bar
            self.loading_label.configure(text="Processing...")  # Keep the "Processing..." label
            self.root.update_idletasks()

        # After process is complete
        self.loading_label.configure(text="Process Completed")  # Change label to "Process Completed"
        self.root.update_idletasks()

    def parse_expression(self, func_str):
        """Convert user input string to a valid Python function."""
        func_str = func_str.replace("^", "**")
        replacements = {
            "sin": "math.sin",
            "cos": "math.cos",
            "tan": "math.tan",
            "log": "math.log",
            "ln": "math.log",
            "exp": "math.exp",
            "e": "math.e"
        }

        for key, val in replacements.items():
            func_str = self.replace_word(func_str, key, val)

        try:
            return lambda x, y: self.safe_eval(func_str, x, y)
        except Exception as e:
            raise ValueError(f"Invalid function: {e}")

    def replace_word(self, expression, word, replacement):
        """Replace all instances of a word in the expression."""
        return re.sub(rf'\b{word}\b', replacement, expression)

    def safe_eval(self, expr, x, y):
        """Evaluate the mathematical expression safely."""
        allowed_names = {"x": x, "y": y, "math": math}
        try:
            return eval(expr, {"_builtins_": None}, allowed_names)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expr}': {e}")

    def numerical_partial_derivative(self, func, var, x, y, delta=1e-5):
        """Compute the numerical partial derivative."""
        try:
            if var == "x":
                return (func(x + delta, y) - func(x - delta, y)) / (2 * delta)
            elif var == "y":
                return (func(x, y + delta) - func(x, y - delta)) / (2 * delta)
        except Exception as e:
            raise ValueError(f"Error computing partial derivative: {e}")

    def is_exact(self, M, N):
        """Check if the equation is exact."""
        points = [(i, j) for i in range(1, 6) for j in range(1, 6)]
        tolerance = 1e-6
        for x, y in points:
            dM_dy = self.numerical_partial_derivative(M, "y", x, y)
            dN_dx = self.numerical_partial_derivative(N, "x", x, y)
            if abs(dM_dy - dN_dx) > tolerance:
                return False
        return True

    def is_homogeneous(self, M, N):
        """Check if the equation is homogeneous."""
        def check_homogeneity(func):
            original_value = func(1.0, 1.0)
            if original_value is None:
                return False, None

            for degree in range(1, 11):
                scaled_value = func(2.0, 2.0)
                expected_value = 2**degree * original_value

                if abs(scaled_value - expected_value) < 1e-6:
                    return True, degree
            return False, None

        m_homogeneous, m_degree = check_homogeneity(M)
        n_homogeneous, n_degree = check_homogeneity(N)

        if m_homogeneous and n_homogeneous and m_degree == n_degree:
            return True, m_degree
        return False, None


# Running the application
exact_checker = ExactCheckerApp()
exact_checker.root.mainloop()
