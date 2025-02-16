import dearpygui.dearpygui as dpg

def save_callback():
    print("Save clicked")

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="Main Window"):
    dpg.add_text("Hello")
    dpg.add_button(label="Save", callback=save_callback)
    dpg.add_input_text(label="Input")
    dpg.add_slider_float(label="float")

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
