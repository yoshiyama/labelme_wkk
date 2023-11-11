'''
This Python program takes three command-line arguments: the input directory, output directory, and divisor. The program then processes all JSON files in the input directory, updates the coordinates by dividing them by the given divisor, and saves the updated JSON files in the output directory. In addition to updating the JSON files, the program also looks for corresponding image files (with the same base name as the JSON file and either a `.jpg` or `.png` extension) in the input directory. If an image file is found, the program resizes the image by dividing its width and height by the divisor and then saves the resized image in the output directory. If no corresponding image file is found for a JSON file, a warning message is printed.

To run the program, use the following command in your terminal:

```bash
python resize.py input_directory output_directory divisor
```

Where:
- `input_directory` is the path to the directory containing the JSON files and image files.
- `output_directory` is the path to the directory where the updated JSON files and resized images will be saved.
- `divisor` is the number by which the coordinates and image dimensions will be divided.
'''

import json
import os
import sys
from PIL import Image
from io import BytesIO
import base64

def update_coordinates_and_resize_image(json_file, image_file, output_directory, divisor):
    # Check if output files already exist
    output_image_file = os.path.join(output_directory, os.path.basename(image_file))
    output_json_file = os.path.join(output_directory, os.path.basename(json_file))

    if os.path.exists(output_image_file) or os.path.exists(output_json_file):
        print(f"Warning: Output files already exist for {json_file}. Skipping.")
        return

    # Load the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Divide the coordinates by the specified divisor
    for shape in data['shapes']:
        for point in shape['points']:
            point[0] /= divisor
            point[1] /= divisor

    # Create the output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load and resize the image
    img = Image.open(image_file)
    width, height = img.size
    img = img.resize((int(width / divisor), int(height / divisor)), Image.BICUBIC)

    # Save the resized image file
    img.save(output_image_file)
    print(f"Resized image saved at {output_image_file}")

    # Convert the resized image to base64
    buffered = BytesIO()
    image_format = "JPEG" if image_file.lower().endswith(".jpg") else "PNG"
    img.save(buffered, format=image_format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Update the JSON data
    data['imageData'] = img_str
    data['imageHeight'] = img.height
    data['imageWidth'] = img.width

    # Save the updated JSON file
    with open(output_json_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Updated JSON file saved at {output_json_file}")

def main(input_directory, output_directory, divisor):
    json_files = [f for f in os.listdir(input_directory) if f.endswith('.json')]
    for json_file in json_files:
        json_path = os.path.join(input_directory, json_file)
        base_name = os.path.splitext(json_file)[0]
        image_file_jpg = os.path.join(input_directory, base_name + '.jpg')
        image_file_png = os.path.join(input_directory, base_name + '.png')

        if os.path.exists(image_file_jpg):
            update_coordinates_and_resize_image(json_path, image_file_jpg, output_directory, divisor)
        elif os.path.exists(image_file_png):
            update_coordinates_and_resize_image(json_path, image_file_png, output_directory, divisor)
        else:
            print(f"Image file not found for {json_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python script.py <input_directory> <output_directory> <divisor>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    divisor = float(sys.argv[3])

    main(input_directory, output_directory, divisor)
