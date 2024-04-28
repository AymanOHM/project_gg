from PIL import Image
import os


output_directory = "data/images/entities/player/run_"
input_directory = "data/images/entities/player/run"
for i in range(len(input_directory) - 1):
    # Open the image
    image = Image.open(f'{input_directory}/{i}.png')

    # Convert the image to RGBA mode (if not already)
    image = image.convert("RGBA")

    # Get the pixel data
    pixels = image.load()

    # Iterate over each pixel
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            # If the pixel is black, make it transparent
            if pixels[x, y] == (0, 0, 0, 255):
                pixels[x, y] = (0, 0, 0, 0)  # Make it transparent

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Save the modified image
    output_path = os.path.join(output_directory, f"{i}.png")
    image.save(output_path)
