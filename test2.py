import cv2
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import numpy as np
from PIL import Image


def calculate_histogram(img):
    img_data = np.array(img)
    r, g, b = (
        img_data[:, :, 0],
        img_data[:, :, 1],
        img_data[:, :, 2],
    )

    hist_r = np.histogram(r, bins=256, range=(0, 256))[0]
    hist_g = np.histogram(g, bins=256, range=(0, 256))[0]
    hist_b = np.histogram(b, bins=256, range=(0, 256))[0]

    return hist_r, hist_g, hist_b


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
    hist_r, hist_g, hist_b = calculate_histogram(img)

    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width, height, data, tag="texture")

    with dpg.window(label="Image Viewer", width=width, height=height):
        dpg.add_image("texture")

        with dpg.plot(label="Histogram"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Pixel Intensity")
            dpg.add_plot_axis(dpg.mvYAxis, label="Frequency")
            # dpg.add_line_series([i for i in range(256)], hist_r, label="R")
            # dpg.add_line_series([i for i in range(256)], hist_g, label="G")
            # dpg.add_line_series([i for i in range(256)], hist_b, label="B")


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
