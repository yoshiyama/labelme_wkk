import tkinter as tk
from tkinter import filedialog, messagebox, Checkbutton, IntVar
import collections
import datetime
import glob
import json
import os
import os.path as osp
import sys
import uuid

import imgviz
import numpy as np

import labelme
try:
    import pycocotools.mask
except ImportError:
    print("Please install pycocotools:\n\n    pip install pycocotools\n")
    sys.exit(1)

def select_input_directory():
    global input_directory
    input_directory = filedialog.askdirectory()
    input_dir_label.config(text=input_directory)

def select_output_directory():
    global output_directory
    output_directory = filedialog.askdirectory()
    output_dir_label.config(text=output_directory)

def select_labels_file():
    global labels_file
    labels_file = filedialog.askopenfilename()
    labels_file_label.config(text=labels_file)

def run_conversion():
    noviz = noviz_var.get()
    main(input_directory, output_directory, labels_file, noviz)



def main(input_dir, output_dir, labels, noviz):
    if not input_dir or not output_dir or not labels:
        messagebox.showerror("Error", "Please select all required fields")
        return

    if osp.exists(output_dir):
        print("Output directory already exists:", output_dir)
        print("The program will write into this existing directory.")
    else:
        os.makedirs(output_dir)
    os.makedirs(osp.join(output_dir, "JPEGImages"), exist_ok=True)
    if not noviz:
        os.makedirs(osp.join(output_dir, "Visualization"), exist_ok=True)
    print("Creating dataset:", output_dir)

    now = datetime.datetime.now()

    data = dict(
        info=dict(
            description=None,
            url=None,
            version=None,
            year=now.year,
            contributor=None,
            date_created=now.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),
        licenses=[
            dict(
                url=None,
                id=0,
                name=None,
            )
        ],
        images=[],
        type="instances",
        annotations=[],
        categories=[],
    )

    class_name_to_id = {}
    for i, line in enumerate(open(labels).readlines()):
        class_id = i - 1
        class_name = line.strip()
        if class_id == -1:
            assert class_name == "__ignore__"
            continue
        class_name_to_id[class_name] = class_id
        data["categories"].append(
            dict(
                supercategory=None,
                id=class_id,
                name=class_name,
            )
        )

    out_ann_file = osp.join(output_dir, "annotations.json")
    label_files = glob.glob(osp.join(input_dir, "*.json"))
    # masks = {}  # Initialize masks here
    for image_id, filename in enumerate(label_files):
        print("Generating dataset from:", filename)
        masks  ={}
        label_file = labelme.LabelFile(filename=filename)

        base = osp.splitext(osp.basename(filename))[0]
        out_img_file = osp.join(output_dir, "JPEGImages", base + ".jpg")

        img = labelme.utils.img_data_to_arr(label_file.imageData)
        imgviz.io.imsave(out_img_file, img)
        data["images"].append(
            dict(
                license=0,
                url=None,
                file_name=osp.relpath(out_img_file, osp.dirname(out_ann_file)),
                height=img.shape[0],
                width=img.shape[1],
                date_captured=None,
                id=image_id,
            )
        )
        masks.clear()
        # Further processing...
        # (include the rest of your script logic here, following the same pattern)
        if not noviz:
            viz = img
            mask_data = [
                (class_name_to_id[cnm], cnm, msk)
                for (cnm, gid), msk in masks.items()
                if cnm in class_name_to_id
            ]
            if mask_data:
                labels, captions, masks = zip(*mask_data)
                viz = imgviz.instances2rgb(
                    image=img,
                    labels=labels,
                    masks=masks,
                    captions=captions,
                    font_size=15,
                    line_width=2,
                )
                out_viz_file = osp.join(
                    output_dir, "Visualization", base + ".jpg"
                )
                imgviz.io.imsave(out_viz_file, viz)
            else:
                print(f"No valid annotations found for image {base}, skipping visualization.")
        else:
            print(f"Visualization skipped for image {base} due to 'noviz' setting.")

    with open(out_ann_file, "w") as f:
        json.dump(data, f)

    messagebox.showinfo("Success", "Processing completed successfully")


root = tk.Tk()
root.title("Labelme to COCO Converter")

# Input directory
input_dir_label = tk.Label(root, text="Select Input Directory")
input_dir_label.pack()
tk.Button(root, text="Browse", command=select_input_directory).pack()

# Output directory
output_dir_label = tk.Label(root, text="Select Output Directory")
output_dir_label.pack()
tk.Button(root, text="Browse", command=select_output_directory).pack()

# Labels file
labels_file_label = tk.Label(root, text="Select Labels File")
labels_file_label.pack()
tk.Button(root, text="Browse", command=select_labels_file).pack()

# No visualization checkbox
noviz_var = IntVar()
Checkbutton(root, text="No visualization", variable=noviz_var).pack()

# Run button
run_button = tk.Button(root, text="Run", command=run_conversion)
run_button.pack()

root.mainloop()
