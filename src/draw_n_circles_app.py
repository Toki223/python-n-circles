import customtkinter as ctk
from tkinter import messagebox
from shapely.geometry import Point
from shapely.ops import unary_union


ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

root = ctk.CTk()  
root.title("Python Circles")

root.geometry("800x600")  

canvas = ctk.CTkCanvas(root, bg="white")
canvas.pack(fill=ctk.BOTH, expand=True)

circles = []

def add_circle():
    try:
        x = int(entry_x.get())
        y = int(entry_y.get())
        r = int(entry_radius.get())
        if r <= 0:
            raise ValueError("Radius must be positive")
        circle = Point(x, y).buffer(r)
        circles.append(circle)
        draw_circle(x, y, r)
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

def draw_circle(x, y, r):
    canvas.create_oval(x-r, y-r, x+r, y+r, outline="#1976d2", width=2)

def calculate():
    if not circles:
        messagebox.showinfo("Result", "No circles added")
        return

    try:
        intersection = circles[0]
        for circle in circles[1:]:
            intersection = intersection.intersection(circle)

        union = unary_union(circles)
        intersection_area = intersection.area
        union_area = union.area

        messagebox.showinfo("Result", f"Intersection Area: {intersection_area}\nUnion Area: {union_area}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def exit_app():
    root.destroy()

frame_input = ctk.CTkFrame(root)
frame_input.pack(side=ctk.LEFT, padx=20, pady=20, fill=ctk.Y)

label_x = ctk.CTkLabel(frame_input, text="Center X:")
label_x.pack(pady=5)
entry_x = ctk.CTkEntry(frame_input)
entry_x.pack(pady=5)

label_y = ctk.CTkLabel(frame_input, text="Center Y:")
label_y.pack(pady=5)
entry_y = ctk.CTkEntry(frame_input)
entry_y.pack(pady=5)

label_radius = ctk.CTkLabel(frame_input, text="Radius:")
label_radius.pack(pady=5)
entry_radius = ctk.CTkEntry(frame_input)
entry_radius.pack(pady=5)

add_button = ctk.CTkButton(frame_input, text="Add Circle", command=add_circle)
add_button.pack(pady=5)

calc_button = ctk.CTkButton(frame_input, text="Calculate", command=calculate)
calc_button.pack(pady=5)

exit_button = ctk.CTkButton(frame_input, text="Exit", command=exit_app, fg_color="red", hover_color="darkred")
exit_button.pack(pady=5)

root.mainloop()
