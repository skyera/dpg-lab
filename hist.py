import cv2
import dearpygui.dearpygui as dpg
import numpy as np

def calculate_histogram(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None, None
    
    # Calculate histograms for B, G, R channels
    channels = cv2.split(image)
    colors = ("b", "g", "r")
    hists = []
    
    for channel in channels:
        hist = cv2.calcHist([channel], [0], None, [256], [0, 256])
        # Normalize
        hist = hist / hist.max() if hist.max() != 0 else hist
        hists.append(hist.flatten().tolist())
        
    # Also calculate grayscale for convenience
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    gray_hist = gray_hist / gray_hist.max() if gray_hist.max() != 0 else gray_hist
    hists.append(gray_hist.flatten().tolist())
    
    return hists, image

def load_image_callback(sender, app_data):
    image_path = app_data['file_path_name']
    hists, image = calculate_histogram(image_path)
    
    if hists is None:
        print(f"Failed to load image: {image_path}")
        return

    # Update plot data
    dpg.set_value("blue_series", [list(range(256)), hists[0]])
    dpg.set_value("green_series", [list(range(256)), hists[1]])
    dpg.set_value("red_series", [list(range(256)), hists[2]])
    dpg.set_value("gray_series", [list(range(256)), hists[3]])
    
    # Update Image Texture
    try:
        width, height, channels, data = dpg.load_image(image_path)
        if data is None:
            raise Exception("DPG failed to load image data")
            
        if dpg.does_item_exist("image_texture"):
            dpg.delete_item("image_texture")
        
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="image_texture", parent="main_texture_registry")
        dpg.set_item_configuration("image_display", texture_tag="image_texture")
        
        # Scale image to fit within 400x400 while maintaining aspect ratio
        scale = min(400 / width, 400 / height, 1.0)
        dpg.set_item_configuration("image_display", width=int(width * scale), height=int(height * scale))
    except Exception as e:
        print(f"Error updating texture: {e}")

def toggle_series(sender, app_data, user_data):
    if app_data:
        dpg.show_item(user_data)
    else:
        dpg.hide_item(user_data)

dpg.create_context()
dpg.create_viewport(title="Advanced Image Histogram", width=1200, height=800)

with dpg.texture_registry(tag="main_texture_registry"):
    # Initial image
    try:
        width, height, channels, data = dpg.load_image("lenna.png")
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="image_texture")
    except:
        # Create a blank texture if lenna.png is missing
        dpg.add_static_texture(width=1, height=1, default_value=[0,0,0,1], tag="image_texture")

with dpg.file_dialog(directory_selector=False, show=False, callback=load_image_callback, id="file_dialog_id", width=600, height=400):
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".png", color=(255, 255, 0, 255))
    dpg.add_file_extension(".jpg", color=(255, 0, 255, 255))

with dpg.window(label="Histogram Dashboard", width=1180, height=780, no_close=True):
    with dpg.group(horizontal=True):
        with dpg.group(width=400):
            dpg.add_button(label="Open Image", callback=lambda: dpg.show_item("file_dialog_id"))
            dpg.add_image("image_texture", tag="image_display", width=400, height=400)
            
            dpg.add_spacer(height=10)
            dpg.add_text("Visibility Controls")
            dpg.add_checkbox(label="Red Channel", default_value=True, callback=toggle_series, user_data="red_series")
            dpg.add_checkbox(label="Green Channel", default_value=True, callback=toggle_series, user_data="green_series")
            dpg.add_checkbox(label="Blue Channel", default_value=True, callback=toggle_series, user_data="blue_series")
            dpg.add_checkbox(label="Grayscale", default_value=False, callback=toggle_series, user_data="gray_series")
            
        with dpg.plot(label="Normalized Histogram", height=-1, width=-1):
            dpg.add_plot_legend()
            x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Pixel Value")
            y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Frequency (Normalized)")
            
            # Initial data calculation for lenna.png
            hists, _ = calculate_histogram("lenna.png")
            
            dpg.add_line_series(list(range(256)), hists[2], label="Red", parent=y_axis, tag="red_series")
            dpg.add_line_series(list(range(256)), hists[1], label="Green", parent=y_axis, tag="green_series")
            dpg.add_line_series(list(range(256)), hists[0], label="Blue", parent=y_axis, tag="blue_series")
            dpg.add_line_series(list(range(256)), hists[3], label="Grayscale", parent=y_axis, tag="gray_series")
            
            # Set colors for the series
            with dpg.theme() as red_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots)
            with dpg.theme() as green_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 255, 0), category=dpg.mvThemeCat_Plots)
            with dpg.theme() as blue_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 0, 255), category=dpg.mvThemeCat_Plots)
            with dpg.theme() as gray_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (200, 200, 200), category=dpg.mvThemeCat_Plots)

            dpg.bind_item_theme("red_series", red_theme)
            dpg.bind_item_theme("green_series", green_theme)
            dpg.bind_item_theme("blue_series", blue_theme)
            dpg.bind_item_theme("gray_series", gray_theme)
            
            dpg.hide_item("gray_series")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
