import cv2
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import numpy as np
from PIL import Image


def normalize(hist):
    return hist / hist.max() if hist.max() != 0 else hist


dpg.create_context()


def open_callback(sender, app_dat, user_data):
    print("Sender: ", sender)
    print("App Data: ", app_dat)
    print("User Data: ", user_data)
    file_path = next(iter(app_dat["selections"].values()))
    print(file_path)

    img = Image.open(file_path)
    print("Format: ", img.format)
    print("Size: ", img.size)
    print("Mode: ", img.mode)
    if img.mode != "RGB":
        img = img.convert("RGB")
    width, height = img.size
    width, height, channels, data = dpg.load_image(file_path)

    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width, height, data, tag="texture")

    with dpg.window(label="Image Viewer", width=width, height=height):
        dpg.add_image("texture")

        image = cv2.imread(file_path)
        blue_channel = image[:, :, 0]
        green_channel = image[:, :, 1]
        red_channel = image[:, :, 2]

        blue_hist = cv2.calcHist([blue_channel], [0], None, [256], [0, 256])
        green_hist = cv2.calcHist([green_channel], [0], None, [256], [0, 256])
        red_hist = cv2.calcHist([red_channel], [0], None, [256], [0, 256])
        blue_hist = normalize(blue_hist).flatten()
        green_hist = normalize(green_hist).flatten()
        red_hist = normalize(red_hist).flatten()

        with dpg.plot(label="Histogram", width=width, height=height):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Pixel Intensity")
            y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Frequency")
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


with dpg.file_dialog(
    directory_selector=False,
    show=False,
    callback=open_callback,
    id="file_dialog",
    width=600,
    height=300,
):
    dpg.add_file_extension(".*")
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension("*.png", color=(150, 150, 255, 255), custom_text="PNG")

with dpg.window(label="Main Window", tag="Primary Window"):
    dpg.add_text("Choose Image")
    dpg.add_button(label="Open", callback=lambda: dpg.show_item("file_dialog"))
    dpg.add_input_text(label="Input", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1.0)

dpg.create_viewport(title="Test", width=600, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
