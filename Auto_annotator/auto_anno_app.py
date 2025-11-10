import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ultralytics import YOLO
from PIL import Image

def annotate_images(model_path, img_dir):
    model = YOLO(model_path)
    names = model.names
    vehicle_classes = {"car", "truck", "bus", "auto rickshaw"}
    bike_classes = {"bicycle", "motorcycle"}
    class_map = {name: 0 for name in vehicle_classes}
    class_map.update({name: 1 for name in bike_classes})
    for img_file in os.listdir(img_dir):
        if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        img_path = os.path.join(img_dir, img_file)
        results = model(img_path)[0]
        h, w = Image.open(img_path).size
        annotations = set()
        for box in results.boxes:
            cls = int(box.cls.item())
            name = names[cls]
            if name not in class_map:
                continue
            custom_id = class_map[name]
            xywh = box.xywh[0].tolist()
            x_center = xywh[0] / w
            y_center = xywh[1] / h
            bw = xywh[2] / w
            bh = xywh[3] / h
            key = (custom_id, round(x_center, 5), round(y_center, 5), round(bw, 5), round(bh, 5))
            annotations.add(key)
        label_path = os.path.splitext(img_path)[0] + ".txt"
        with open(label_path, "w") as f:
            for anno in annotations:
                f.write(f"{anno[0]} {anno[1]} {anno[2]} {anno[3]} {anno[4]}\n")

def select_model():
    path = filedialog.askopenfilename(filetypes=[("YOLOv8 .pt", "*.pt")])
    if path:
        model_entry.delete(0, tk.END)
        model_entry.insert(0, path)

def select_folder():
    path = filedialog.askdirectory()
    if path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, path)

def run():
    model_path = model_entry.get().strip()
    folder_path = folder_entry.get().strip()
    if not os.path.exists(model_path) or not os.path.exists(folder_path):
        messagebox.showerror("Error", "Invalid model or image folder path")
        return
    try:
        annotate_images(model_path, folder_path)
        messagebox.showinfo("Success", "Annotations complete!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

app = tk.Tk()
app.title("Auto Annotator")
app.geometry("500x200")

tk.Label(app, text="Model Path").pack()
model_entry = tk.Entry(app, width=60)
model_entry.pack()
tk.Button(app, text="Browse Model", command=select_model).pack()

tk.Label(app, text="Image Folder").pack()
folder_entry = tk.Entry(app, width=60)
folder_entry.pack()
tk.Button(app, text="Browse Folder", command=select_folder).pack()

tk.Button(app, text="Run Annotation", command=run).pack(pady=10)

app.mainloop()
