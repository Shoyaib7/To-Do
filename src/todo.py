import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Initialize main application window
root = tk.Tk()
root.title("To-Do")
root.geometry("1000x600")  
root.resizable(False, False)  
root.configure(bg="black")  

# Create a frame for scrolling
scrollable_frame = tk.Frame(root, bg="black")

# Create a canvas and scrollbar for the scrollable area
canvas = tk.Canvas(scrollable_frame, bg="black", highlightthickness=0)
scrollbar = tk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview, bg="#555555", troughcolor="black")
canvas.configure(yscrollcommand=scrollbar.set)

# Layout the canvas and scrollbar
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas
content_frame = tk.Frame(canvas, bg="black")
canvas.create_window((0, 0), window=content_frame, anchor='nw')

# Function to update scroll region
def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

content_frame.bind("<Configure>", update_scroll_region)

# Mouse wheel scrolling
def on_mouse_wheel(event):
    if canvas.yview()[0] > 0 or (event.delta < 0 and canvas.yview()[1] < 1):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

root.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows and MacOS

# Task input field with watermark effect
task_entry = tk.Entry(content_frame, width=45, font=("Open Sans", 15), bg="#3a3a3a", fg="gray", borderwidth=0)
task_entry.insert(0, "Enter a new task...")
task_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky="ew")

# Function to handle focus in
def on_entry_click(event):
    if task_entry.get() == "Enter a new task...":
        task_entry.delete(0, tk.END)  
        task_entry.config(fg="white")  

# Function to handle focus out
def on_focus_out(event):
    if task_entry.get() == "":
        task_entry.insert(0, "Enter a new task...") 
        task_entry.config(fg="gray")  

# Bind events to the entry
task_entry.bind("<FocusIn>", on_entry_click)
task_entry.bind("<FocusOut>", on_focus_out)
task_entry.bind("<Return>", lambda event: add_task())  

# Task list with extra features
tasks = []

# Function to load and resize icons
def load_resized_icon(image_path, size):
    icon = Image.open(image_path)
    icon = icon.resize(size, Image.LANCZOS)  
    return ImageTk.PhotoImage(icon)

# Load icons for buttons
icon_size = (20, 20)
delete_icon = load_resized_icon("assets/delete_icon.png", icon_size)
check_icon = load_resized_icon("assets/check_icon.png", icon_size)

# Function to add a task
def add_task():
    task = task_entry.get().strip()
    if task and task != "Enter a new task...":
        if any(existing_task["name"].lower() == task.lower() for existing_task in tasks):  # Check for duplicates
            messagebox.showwarning("Input Error", "This task already exists.")
        else:
            task_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            task_details = {
                "name": task,
                "time": task_time,
                "done": tk.BooleanVar()
            }
            tasks.append(task_details)
            update_task_list()
            task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter a valid task.")

# Function to update the displayed task list
def update_task_list():
    for widget in task_listbox.winfo_children():
        widget.destroy()
    for index, task in enumerate(tasks):
        task_frame = tk.Frame(task_listbox, bg="black")
        
        # Use a white color for the done button (check button)
        done_button = tk.Checkbutton(task_frame, variable=task["done"], image=check_icon, bg="black", 
                                      activebackground="black", selectcolor="black", fg="white", borderwidth=0)
        task_label = tk.Label(task_frame, text=f"{task['name']} - {task['time']}", bg="black", fg="white", font=("Open Sans", 14), wraplength=400, justify="left")
        
        # Use an icon for the delete button
        delete_button = tk.Button(task_frame, image=delete_icon, command=lambda idx=index: delete_task(idx), 
                                  bg="black", bd=0, activebackground="black")
        
        done_button.grid(row=0, column=0, padx=5)
        task_label.grid(row=0, column=1, padx=5, sticky="w")
        delete_button.grid(row=0, column=2, padx=5)
        
        task_frame.pack(fill="x", pady=2)

# Function to delete a task
def delete_task(index):
    tasks.pop(index)
    update_task_list()

# Function to show task statistics
def show_statistics():
    done_count = sum(1 for task in tasks if task["done"].get())
    not_done_count = len(tasks) - done_count
    labels = ['Completed', 'Pending']
    sizes = [done_count, not_done_count]
    
    # Create a new figure for the pie chart
    fig = Figure(figsize=(4, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=["#4CAF50", "#FFC107"])
    ax.set_facecolor("black")  
    ax.set_title("Task Completion Statistics", color='black')
    
    # Clear previous chart if any
    for widget in stats_frame.winfo_children():
        widget.destroy()
    chart = FigureCanvasTkAgg(fig, stats_frame)
    chart.get_tk_widget().grid(row=0, column=0, sticky="nsew")

# Create a frame for the task list with a scrollbar
task_frame = tk.Frame(content_frame, bg="black")
task_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# Create a Frame to hold the task list
task_listbox = tk.Frame(task_frame, bg="black")
task_listbox.pack(fill="both", expand=True)

# Add buttons in the same row as the task entry
button_frame = tk.Frame(content_frame, bg="black")
button_frame.grid(row=0, column=3, sticky="ns", padx=(0, 10))

add_task_button = tk.Button(button_frame, text="Add Task", command=add_task, bg="#4CAF50", fg="white", font=("Roboto", 13), bd=0)
add_task_button.grid(row=0, column=0, pady=5)

stats_button = tk.Button(button_frame, text="Show Stats", command=show_statistics, bg="#FFC107", fg="black", font=("Roboto", 13), bd=0)
stats_button.grid(row=1, column=0, pady=5)

# Add a frame for the stats
stats_frame = tk.Frame(content_frame, bg="black")
stats_frame.grid(row=1, column=3, sticky="nsew", padx=(10, 10), pady=(10, 0))

# Update layout weights for resizing
root.columnconfigure(0, weight=1)
content_frame.rowconfigure(1, weight=1)  
content_frame.columnconfigure(0, weight=1)  

# Update the layout to allow resizing
task_frame.columnconfigure(0, weight=1)  
stats_frame.columnconfigure(0, weight=1)

update_task_list()

# Finalize the layout of the main scrollable frame
scrollable_frame.pack(fill="both", expand=True)

root.mainloop()