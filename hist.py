import cv2
import dearpygui.dearpygui as dpg
import numpy as np

# Replace with your image path
image_path = "lenna.png"

# Load image using OpenCV
image = cv2.imread(image_path)

if image is None:
    raise Exception("Failed to load image")

# Split color channels (OpenCV uses BGR format)
blue_channel = image[:, :, 0]
green_channel = image[:, :, 1]
red_channel = image[:, :, 2]

# Compute histograms for each channel
blue_hist = cv2.calcHist([blue_channel], [0], None, [256], [0, 256])
green_hist = cv2.calcHist([green_channel], [0], None, [256], [0, 256])
red_hist = cv2.calcHist([red_channel], [0], None, [256], [0, 256])


# Normalize histograms to [0, 1]
def normalize(hist):
    return hist / hist.max() if hist.max() != 0 else hist


blue_hist = normalize(blue_hist).flatten()
green_hist = normalize(green_hist).flatten()
red_hist = normalize(red_hist).flatten()

# Create Dear PyGui context
dpg.create_context()
dpg.create_viewport(title="Image Histogram", width=800, height=600)

with dpg.window(label="Histogram", width=800, height=600):
    # Create a plot
    with dpg.plot(label="Color Histogram", height=500, width=750):
        # X-axis
        dpg.add_plot_axis(dpg.mvXAxis, label="Pixel Value")
        # Y-axis
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Normalized Frequency")

        # Add histogram lines
        dpg.add_line_series(
            x=list(range(256)),
            y=blue_hist.tolist(),
            label="Blue",
            parent=y_axis,
        )
        dpg.add_line_series(
            x=list(range(256)),
            y=green_hist.tolist(),
            label="Green",
            parent=y_axis,
        )
        dpg.add_line_series(
            x=list(range(256)),
            y=red_hist.tolist(),
            label="Red",
            parent=y_axis,
        )

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
