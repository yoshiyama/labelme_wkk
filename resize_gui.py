import tkinter as tk
from tkinter import filedialog, Label, Entry, Button

def select_input_directory():
    global input_directory
    input_directory = filedialog.askdirectory()
    input_label.config(text=input_directory)

def select_output_directory():
    global output_directory
    output_directory = filedialog.askdirectory()
    output_label.config(text=output_directory)

def run_program():
    divisor = float(divisor_entry.get())
    main(input_directory, output_directory, divisor)

root = tk.Tk()
root.title("JSON and Image Resizer")

input_label = Label(root, text="Select Input Directory")
input_label.pack()
Button(root, text="Browse", command=select_input_directory).pack()

output_label = Label(root, text="Select Output Directory")
output_label.pack()
Button(root, text="Browse", command=select_output_directory).pack()

Label(root, text="Divisor:").pack()
divisor_entry = Entry(root)
divisor_entry.pack()

run_button = Button(root, text="Run", command=run_program)
run_button.pack()

root.mainloop()
