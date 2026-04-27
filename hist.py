import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import os

def calculate_histogram(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None, None
    
    # Calculate histograms for B, G, R channels
    channels = cv2.split(image)
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

def update_metadata(image_path, width, height):
    # filename
    filename = os.path.basename(image_path)
    dpg.set_value("meta_filename", f"File: {filename}")
    dpg.set_value("meta_resolution", f"Resolution: {width} x {height}")
    # size in mb
    try:
        size_kb = os.path.getsize(image_path) / 1024
        dpg.set_value("meta_size", f"Size: {size_kb:.1f} KB")
    except:
        dpg.set_value("meta_size", "Size: Unknown")

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
    
    # Update Shade data
    dpg.set_value("blue_shade", [list(range(256)), hists[0]])
    dpg.set_value("green_shade", [list(range(256)), hists[1]])
    dpg.set_value("red_shade", [list(range(256)), hists[2]])
    dpg.set_value("gray_shade", [list(range(256)), hists[3]])
    
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
        
        update_metadata(image_path, width, height)

    except Exception as e:
        print(f"Error updating texture: {e}")

def toggle_series(sender, app_data, user_data):
    # user_data is a tuple of (line_series, shade_series)
    line_s, shade_s = user_data
    if app_data:
        dpg.show_item(line_s)
        dpg.show_item(shade_s)
    else:
        dpg.hide_item(line_s)
        dpg.hide_item(shade_s)

dpg.create_context()
dpg.create_viewport(title="Advanced Image Histogram", width=1280, height=800)

# Global Theme
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 107, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (71, 127, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (31, 87, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 45, 45, 255))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (55, 55, 55, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 230, 230, 255))
        
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8)
dpg.bind_theme(global_theme)

with dpg.texture_registry(tag="main_texture_registry"):
    try:
        width, height, channels, data = dpg.load_image("lenna.png")
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="image_texture")
    except:
        width, height = 1, 1
        dpg.add_static_texture(width=1, height=1, default_value=[0,0,0,1], tag="image_texture")

with dpg.file_dialog(directory_selector=False, show=False, callback=load_image_callback, id="file_dialog_id", width=700, height=500):
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".png", color=(0, 255, 255, 255))
    dpg.add_file_extension(".jpg", color=(255, 255, 0, 255))
    dpg.add_file_extension(".jpeg", color=(255, 255, 0, 255))
    dpg.add_file_extension(".bmp", color=(255, 0, 255, 255))

with dpg.window(label="Histogram Dashboard", tag="main_window"):
    with dpg.group(horizontal=True):
        
        # LEFT PANEL (Controls & Image)
        with dpg.child_window(width=450, border=False):
            dpg.add_spacer(height=5)
            
            dpg.add_text("IMAGE ANALYSIS TOOL", color=(51, 153, 255))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Button nicely padded
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=2)
                dpg.add_button(label="  Open Image File  ", height=35, callback=lambda: dpg.show_item("file_dialog_id"))
            dpg.add_spacer(height=10)
            
            # Image Container with a background
            with dpg.child_window(width=430, height=430, border=True):
                dpg.add_image("image_texture", tag="image_display", width=400, height=400)
                
            dpg.add_spacer(height=10)
            
            # Metadata section
            dpg.add_text("Metadata", color=(150, 150, 150))
            dpg.add_separator()
            dpg.add_text("File: lenna.png", tag="meta_filename")
            try:
                dpg.add_text(f"Resolution: {width} x {height}", tag="meta_resolution")
            except:
                dpg.add_text("Resolution: Unknown", tag="meta_resolution")
            dpg.add_text("Size: Unknown KB", tag="meta_size")
            
            dpg.add_spacer(height=15)
            
            # Visibility Controls
            dpg.add_text("Channels Visualization", color=(150, 150, 150))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            dpg.add_checkbox(label="Red Channel", default_value=True, callback=toggle_series, user_data=("red_series", "red_shade"))
            dpg.add_checkbox(label="Green Channel", default_value=True, callback=toggle_series, user_data=("green_series", "green_shade"))
            dpg.add_checkbox(label="Blue Channel", default_value=True, callback=toggle_series, user_data=("blue_series", "blue_shade"))
            dpg.add_checkbox(label="Grayscale", default_value=False, callback=toggle_series, user_data=("gray_series", "gray_shade"))
            
        # RIGHT PANEL (Plot)
        with dpg.child_window(border=False):
            with dpg.plot(label="Color Intensity Distribution", height=-1, width=-1):
                dpg.add_plot_legend()
                
                # Setup axes
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Pixel Intensity (0-255)")
                dpg.set_axis_limits(x_axis, 0, 255)
                
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Normalized Frequency")
                dpg.set_axis_limits(y_axis, 0, 1.05)
                
                # Initial data calculation for lenna.png
                hists, _ = calculate_histogram("lenna.png")
                
                if hists is not None:
                    # Shade Series (Fill)
                    dpg.add_shade_series(list(range(256)), hists[2], parent=y_axis, tag="red_shade")
                    dpg.add_shade_series(list(range(256)), hists[1], parent=y_axis, tag="green_shade")
                    dpg.add_shade_series(list(range(256)), hists[0], parent=y_axis, tag="blue_shade")
                    dpg.add_shade_series(list(range(256)), hists[3], parent=y_axis, tag="gray_shade")
                    
                    # Line Series (Outlines)
                    dpg.add_line_series(list(range(256)), hists[2], label="Red", parent=y_axis, tag="red_series")
                    dpg.add_line_series(list(range(256)), hists[1], label="Green", parent=y_axis, tag="green_series")
                    dpg.add_line_series(list(range(256)), hists[0], label="Blue", parent=y_axis, tag="blue_series")
                    dpg.add_line_series(list(range(256)), hists[3], label="Grayscale", parent=y_axis, tag="gray_series")
                else:
                    # Empty placeholders if lenna not found
                    empty = [0]*256
                    dpg.add_shade_series(list(range(256)), empty, parent=y_axis, tag="red_shade")
                    dpg.add_shade_series(list(range(256)), empty, parent=y_axis, tag="green_shade")
                    dpg.add_shade_series(list(range(256)), empty, parent=y_axis, tag="blue_shade")
                    dpg.add_shade_series(list(range(256)), empty, parent=y_axis, tag="gray_shade")
                    
                    dpg.add_line_series(list(range(256)), empty, label="Red", parent=y_axis, tag="red_series")
                    dpg.add_line_series(list(range(256)), empty, label="Green", parent=y_axis, tag="green_series")
                    dpg.add_line_series(list(range(256)), empty, label="Blue", parent=y_axis, tag="blue_series")
                    dpg.add_line_series(list(range(256)), empty, label="Grayscale", parent=y_axis, tag="gray_series")
                
                # Themes for plotting
                def create_series_theme(line_color, fill_color):
                    with dpg.theme() as t:
                        with dpg.theme_component(dpg.mvLineSeries):
                            dpg.add_theme_color(dpg.mvPlotCol_Line, line_color, category=dpg.mvThemeCat_Plots)
                        with dpg.theme_component(dpg.mvShadeSeries):
                            dpg.add_theme_color(dpg.mvPlotCol_Fill, fill_color, category=dpg.mvThemeCat_Plots)
                    return t
                
                t_red = create_series_theme((255, 50, 50, 255), (255, 50, 50, 60))
                t_green = create_series_theme((50, 255, 50, 255), (50, 255, 50, 60))
                t_blue = create_series_theme((50, 150, 255, 255), (50, 150, 255, 60))
                t_gray = create_series_theme((200, 200, 200, 255), (200, 200, 200, 60))

                dpg.bind_item_theme("red_series", t_red)
                dpg.bind_item_theme("red_shade", t_red)
                dpg.bind_item_theme("green_series", t_green)
                dpg.bind_item_theme("green_shade", t_green)
                dpg.bind_item_theme("blue_series", t_blue)
                dpg.bind_item_theme("blue_shade", t_blue)
                dpg.bind_item_theme("gray_series", t_gray)
                dpg.bind_item_theme("gray_shade", t_gray)
                
                dpg.hide_item("gray_series")
                dpg.hide_item("gray_shade")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
