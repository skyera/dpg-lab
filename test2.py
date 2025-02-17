import dearpygui.dearpygui as dpg
import dearpygui.demo as demo


def save_callback():
    print("Save clicked")


dpg.create_context()

with dpg.window(label="Main Window", tag="Primary Window"):
    dpg.add_text("Hello")
    dpg.add_button(label="Save", callback=save_callback)
    dpg.add_input_text(label="Input", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1.0)

dpg.create_viewport(title="Test", width=600, height=300)
demo.show_demo()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
