import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import numpy as np
from PIL import Image

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
    width, height = img.size
    width, height, channels, data = dpg.load_image(file_path)

    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width, height, data, tag="texture")

    with dpg.window(label="Image Viewer", width=width, height=height):
        dpg.add_image("texture")


with dpg.file_dialog(
    directory_selector=False,
    show=False,
    callback=open_callback,
    id="file_dialog",
    width=600,
    height=400,
):
    dpg.add_file_extension(".*")
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension("*.png", color=(150, 150, 255, 255), custom_text="PNG")

with dpg.window(label="Main Window", tag="Primary Window"):
    dpg.add_text("Choose Image")
    dpg.add_button(label="Open", callback=lambda: dpg.show_item("file_dialog"))
    dpg.add_input_text(label="Input", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1.0)

dpg.create_viewport(title="Test", width=600, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
