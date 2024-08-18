import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from shapely.geometry import Point
from shapely.ops import unary_union

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Python Krugovi")
root.geometry("900x600")

canvas = ctk.CTkCanvas(root, bg="white")
canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

circles = []
highlight_ids = []
highlighted_shapes = []
previous_highlights = []
shapes_highlighted = False
calculated = False

dot_id = None
dot_visible = True
pixel_to_cm = 0.1

def draw_coordinate_system():
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    center_x = width // 2
    center_y = height // 2

    canvas.create_line(center_x, 0, center_x, height, fill="black")
    canvas.create_line(0, center_y, width, center_y, fill="black")

    for x in range(center_x, width, 50):
        canvas.create_text(x, center_y + 10, text=str(x - center_x), fill="black")
    for x in range(center_x, 0, -50):
        canvas.create_text(x, center_y + 10, text=str(x - center_x), fill="black")

    for y in range(center_y, height, 50):
        canvas.create_text(center_x + 10, y, text=str(center_y - y), fill="black")
    for y in range(center_y, 0, -50):
        canvas.create_text(center_x + 10, y, text=str(center_y - y), fill="black")

    update_dot_position()

    for circle in circles:
        draw_circle(circle[1], circle[2], circle[3])

def update_dot_position():
    global dot_id
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    center_x = width // 2
    center_y = height // 2

    try:
        x = int(entry_x.get())
        y = int(entry_y.get())
    except ValueError:
        x = y = 0

    if dot_id:
        canvas.delete(dot_id)
    
    if dot_visible:
        dot_id = canvas.create_oval(center_x + x - 5, center_y - y - 5, center_x + x + 5, center_y - y + 5, fill="dark red", outline="dark red")

def add_circle():
    global previous_highlights
    try:
        x = int(entry_x.get())
        y = int(entry_y.get())
        r = int(entry_radius.get())
        if r <= 0:
            raise ValueError("Prečnik mora biti pozitivan")
        circle = Point(x, y).buffer(r)
        circles.append((circle, x, y, r))
        draw_circle(x, y, r)
        previous_highlights = highlight_ids.copy()
    except ValueError as e:
        messagebox.showerror("Error", f"Neispravan unos: {e}")

def draw_circle(x, y, r, color="#1976d2"):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    center_x = width // 2
    center_y = height // 2
    canvas.create_oval(center_x + x - r, center_y - y - r, center_x + x + r, center_y - y + r, outline=color, width=2)

def highlight_shapes():
    global highlight_ids, highlighted_shapes
    if len(circles) < 2:
        return
    
    for item_id in highlight_ids:
        canvas.delete(item_id)
    highlight_ids.clear()
    highlighted_shapes.clear()
    
    try:
        union_circles = [c[0] for c in circles]
        intersection = union_circles[0]
        for circle in union_circles[1:]:
            intersection = intersection.intersection(circle)

        if not intersection.is_empty:
            union = unary_union(union_circles)
            regions = []
            for i, c1 in enumerate(circles):
                for j, c2 in enumerate(circles):
                    if i != j:
                        if not c1[0].disjoint(c2[0]):
                            regions.append(c1[0].difference(c2[0]))
                            regions.append(c2[0].difference(c1[0]))

            if not intersection.is_empty:
                regions.append(intersection)

            for region in regions:
                if not region.is_empty:
                    if region.equals(intersection):
                        color = "green"
                    else:
                        color = "#F08080"
                    polygon_id = draw_polygon(region, color, color)
                    highlight_ids.append(polygon_id)
                    highlighted_shapes.append((region, color, color))
        else:
            union = unary_union(union_circles)
            if not union.is_empty:
                for region in [c.buffer(0) for c in union_circles]:
                    if not region.is_empty:
                        color = "#F08080"
                        polygon_id = draw_polygon(region, color, color)
                        highlight_ids.append(polygon_id)
                        highlighted_shapes.append((region, color, color))

    except Exception as e:
        messagebox.showerror("Error", f"Došlo je do greške: {e}")

def draw_polygon(polygon, outline_color, fill_color):
    if not polygon.is_empty:
        coords = [(canvas.winfo_width()//2 + x, canvas.winfo_height()//2 - y) for x, y in polygon.exterior.coords]
        return canvas.create_polygon(coords, outline=outline_color, fill=fill_color, stipple="gray50")

def calculate():
    global calculated
    if len(circles) < 2:
        messagebox.showinfo("Rezultat", "Sistem mora imati minimum dva kruga")
        return

    highlight_shapes()
    
    try:
        intersection = circles[0][0]
        for circle in circles[1:]:
            intersection = intersection.intersection(circle[0])

        union = unary_union([c[0] for c in circles])
        intersection_area = intersection.area * (pixel_to_cm ** 2)
        union_area = union.area * (pixel_to_cm ** 2) if not union.is_empty else 0

        result_table.insert("", "end", values=(intersection_area, union_area))

        for item_id in highlight_ids:
            canvas.delete(item_id)
        highlight_ids.clear()
        highlighted_shapes.clear()
        calculated = True

    except Exception as e:
        messagebox.showerror("Error", f"Došlo je do greške: {e}")

def toggle_highlight():
    if not calculated:
        messagebox.showinfo("Upozorenje", "Prvo morate izračunati")
        return

    global shapes_highlighted
    if shapes_highlighted:
        for item_id in highlight_ids:
            canvas.delete(item_id)
        highlight_ids.clear()
        highlighted_shapes.clear()
    else:
        highlight_shapes()
    shapes_highlighted = not shapes_highlighted

def toggle_dot():
    global dot_visible
    dot_visible = not dot_visible
    update_dot_position()

def undo_last_circle():
    global previous_highlights, calculated
    if circles:
        circles.pop()
        canvas.delete("all")
        draw_coordinate_system()
        for circle in circles:
            draw_circle(circle[1], circle[2], circle[3])
        highlight_ids = previous_highlights.copy()
        for item_id in highlight_ids:
            canvas.itemconfig(item_id, outline="green")
        previous_highlights = []
        calculated = False  

def exit_app():
    root.destroy()

def handle_resize(event):
    draw_coordinate_system()
    if shapes_highlighted:
        highlight_shapes()

def on_coordinate_change(*args):
    draw_coordinate_system()

frame_input = ctk.CTkFrame(root)
frame_input.pack(side=ctk.LEFT, padx=20, pady=20, fill=ctk.Y)

label_radius = ctk.CTkLabel(frame_input, text="Prečnik (cm):")
label_radius.grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_radius = ctk.CTkEntry(frame_input)
entry_radius.grid(row=0, column=1, padx=10, pady=10)
entry_radius.insert(0, "100")  

label_x = ctk.CTkLabel(frame_input, text="X koordinata centra:")
label_x.grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_x = ctk.CTkEntry(frame_input)
entry_x.grid(row=1, column=1, padx=10, pady=10)
entry_x.insert(0, "0")  
entry_x.bind("<KeyRelease>", on_coordinate_change)

label_y = ctk.CTkLabel(frame_input, text="Y koordinata centra:")
label_y.grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_y = ctk.CTkEntry(frame_input)
entry_y.grid(row=2, column=1, padx=10, pady=10)
entry_y.insert(0, "0")  
entry_y.bind("<KeyRelease>", on_coordinate_change)

button_frame = ctk.CTkFrame(frame_input, fg_color=frame_input.cget("fg_color"))
button_frame.grid(row=3, column=0, columnspan=2, pady=10)

add_button = ctk.CTkButton(button_frame, text="Dodaj krug", command=add_circle, fg_color="#1976d2", text_color="white", corner_radius=10)
add_button.grid(row=0, column=0, padx=10)

calc_button = ctk.CTkButton(button_frame, text="Izračunaj", command=calculate, fg_color="#1976d2", text_color="white", corner_radius=10)
calc_button.grid(row=0, column=1, padx=10)

toggle_highlight_button = ctk.CTkButton(frame_input, text="Osenči rezultate", command=toggle_highlight, fg_color="#ed6c02", text_color="white", hover_color="#e65100", corner_radius=10)
toggle_highlight_button.grid(row=4, column=0, padx=10, sticky="s")

undo_button = ctk.CTkButton(frame_input, text="Undo", command=undo_last_circle, fg_color="#ed6c02", text_color="white", hover_color="#e65100", corner_radius=10)
undo_button.grid(row=4, column=1, padx=10, sticky="s")

btn_toggle_dot = ctk.CTkButton(frame_input, text="Prikaz tačke", command=toggle_dot, fg_color="#ed6c02", text_color="white", hover_color="#e65100", corner_radius=10)
btn_toggle_dot.grid(row=5, column=0, padx=10, pady=10)

exit_button = ctk.CTkButton(frame_input, text="Izlaz", command=exit_app, fg_color="#d32f2f", text_color="white", hover_color="#b71c1c", corner_radius=10)
exit_button.grid(row=5, column=1, padx=10, pady=10, sticky="s")

result_frame = ctk.CTkFrame(frame_input,)
result_frame.grid(row=6, column=0, columnspan=2, pady=10,)

result_table = ttk.Treeview(result_frame, columns=("intersect", "union"), show="headings", height=20)
result_table.heading("intersect", text="Površina preseka (cm²)")
result_table.heading("union", text="Površina unije (cm²)")
result_table.pack()

root.after(100, draw_coordinate_system)

canvas.bind("<Configure>", handle_resize)

root.mainloop()
