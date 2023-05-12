import board
import neopixel 

pixels = neopixel.NeoPixel(board.D18, 128, auto_write=False)

# Define the start and end RGB values as tuples
start_rgb = (255, 0, 0)  # Red
end_rgb = (100, 0, 255)    # Green

# Calculate the maximum difference in any one color channel
max_diff = max(abs(end_rgb[i] - start_rgb[i]) for i in range(3))

# Define the number of steps in the transition based on the maximum difference
num_steps = max_diff + 1

# Calculate the step size for each color channel
r_step = (end_rgb[0] - start_rgb[0]) / num_steps
g_step = (end_rgb[1] - start_rgb[1]) / num_steps
b_step = (end_rgb[2] - start_rgb[2]) / num_steps

# Loop through each step and calculate the new RGB value
for i in range(num_steps):
    r = round(start_rgb[0] + (i * r_step))
    g = round(start_rgb[1] + (i * g_step))
    b = round(start_rgb[2] + (i * b_step))
    print(f"Step {i+1}: RGB({r}, {g}, {b})")
    for i in range(64):
        pixels[i*2] = (r,g,b)
        pixels[i*2 +1] = (r,g,b)
    pixels.show()
    start_rgb = 