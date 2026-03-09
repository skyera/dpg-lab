import json
import math
import os
import random
import shutil
import subprocess
import sys
import time

import dearpygui.dearpygui as dpg

CONFIG_FILE = "connection.json"
state = {"file_path": ""}
image_filename = "lenna.png"

# Particle system state for "life patterns"
particles = []
for _ in range(35):
    particles.append(
        {
            "pos": [random.uniform(0, 330), random.uniform(0, 120)],
            "vel": [random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)],
            "color": [
                random.randint(50, 150),
                random.randint(150, 255),
                random.randint(200, 255),
                150,
            ],
            "size": random.uniform(1.5, 4),
        }
    )


def update_life_patterns():
    if not dpg.does_item_exist("life_drawlist"):
        return

    dpg.delete_item("life_drawlist", children_only=True)
    t = time.time()

    # Updated center for 160x120
    center_x, center_y = 80, 60
    points = []
    num_points = 150
    turns = 8 + math.sin(t * 0.7) * 4
    max_radius = 40 + math.cos(t * 1.1) * 10

    for i in range(num_points):
        prog = i / num_points
        angle = prog * turns * 2 * math.pi + t * 0.5
        r = prog * max_radius
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        points.append([x, y])

    r_val = int(100 + 50 * math.sin(t))
    g_val = int(200 + 55 * math.cos(t * 0.5))
    dpg.draw_polyline(
        points, color=[r_val, g_val, 255, 180], thickness=2, parent="life_drawlist"
    )

    for p in particles:
        p["pos"][0] += p["vel"][0]
        p["pos"][1] += p["vel"][1]

        # Updated boundaries for 160x120
        if p["pos"][0] < 5 or p["pos"][0] > 155:
            p["vel"][0] *= -1
        if p["pos"][1] < 5 or p["pos"][1] > 115:
            p["vel"][1] *= -1

        dpg.draw_circle(
            p["pos"],
            p["size"] + 2,
            fill=[p["color"][0], p["color"][1], p["color"][2], 30],
            color=[0, 0, 0, 0],
            parent="life_drawlist",
        )
        dpg.draw_circle(
            p["pos"],
            p["size"],
            fill=p["color"],
            color=p["color"],
            parent="life_drawlist",
        )


def update_solar_system():
    if not dpg.does_item_exist("solar_drawlist"):
        return

    dpg.delete_item("solar_drawlist", children_only=True)
    t = time.time()
    # Updated center for 160x120
    cx, cy = 80, 60

    dpg.draw_circle(
        [cx, cy],
        10,
        fill=[255, 200, 0, 255],
        color=[255, 255, 100, 255],
        parent="solar_drawlist",
    )

    planets = [
        {"r": 22, "s": 1.8, "sz": 3, "c": [180, 180, 180, 255]},
        {"r": 35, "s": 1.2, "sz": 4, "c": [230, 190, 150, 255]},
        {"r": 48, "s": 0.8, "sz": 5, "c": [100, 150, 255, 255]},
    ]

    for p in planets:
        angle = t * p["s"]
        px = cx + p["r"] * math.cos(angle)
        py = cy + p["r"] * math.sin(angle)
        dpg.draw_circle(
            [cx, cy], p["r"], color=[60, 60, 60, 100], parent="solar_drawlist"
        )
        dpg.draw_circle(
            [px, py], p["sz"], fill=p["c"], color=p["c"], parent="solar_drawlist"
        )

        if p["c"] == [100, 150, 255, 255]:
            ma = t * 4
            mx = px + 8 * math.cos(ma)
            my = py + 8 * math.sin(ma)
            dpg.draw_circle(
                [mx, my], 1.5, fill=[200, 200, 200, 255], parent="solar_drawlist"
            )


def resource_path(exe_name):
    """
    Resolve executable path for:
    - PyInstaller bundle (_MEIPASS)
    - Normal script execution (PATH)
    """
    # 1. Running from PyInstaller bundle
    if hasattr(sys, "_MEIPASS"):
        candidate = os.path.join(sys._MEIPASS, exe_name)
        if os.path.exists(candidate):
            return candidate

    # 2. Running from source: find in PATH
    found = shutil.which(exe_name)
    if found:
        return found

    # 3. Optional: local directory fallback
    local = os.path.abspath(exe_name)
    if os.path.exists(local):
        return local

    raise FileNotFoundError(f"{exe_name} not found in bundle or PATH")


def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, shell=False)


def set_status(msg, ok=True):
    color = (100, 255, 100) if ok else (255, 100, 100)
    dpg.set_value("status", msg)
    dpg.configure_item("status", color=color)


def test_connection():
    ip = dpg.get_value("ip")
    port = dpg.get_value("port")
    user = dpg.get_value("user")
    password = dpg.get_value("password")

    if not ip or not user:
        set_status("IP or username missing!", ok=False)
        return

    plink = resource_path("plink.exe")
    print(plink)
    if not os.path.exists(plink):
        set_status("plink.exe not found!", ok=False)
        return

    cmd = [
        plink,
        "-batch",
        "-P",
        str(port),
        "-pw",
        password,
        f"{user}@{ip}",
        "echo connected",
    ]
    result = run_cmd(cmd)

    if result.returncode == 0:
        set_status("SSH connection successful")
    else:
        set_status(f"SSH failed: {result.stderr.strip()}", ok=False)


def upload_file():
    ip = dpg.get_value("ip")
    port = dpg.get_value("port")
    user = dpg.get_value("user")
    password = dpg.get_value("password")
    version = dpg.get_value("version")
    print(version)
    if not version:
        set_status("Version missing!", ok=False)
        return

    file_path = dpg.get_value("file_label")
    # file_path = state["file_path"]

    if not file_path or not os.path.exists(file_path):
        set_status("Invalid file selected", ok=False)
        return

    base, ext = os.path.splitext(os.path.basename(file_path))
    remote_path = f"/tmp/{base}_{version}{ext}"
    print(remote_path)
    pscp = resource_path("pscp.exe")
    print(pscp)

    if not os.path.exists(pscp):
        set_status("pscp.exe not found!", ok=False)
        return
    cmd = [
        pscp,
        "-batch",
        "-P",
        str(port),
        "-pw",
        password,
        file_path,
        f"{user}@{ip}:{remote_path}",
    ]
    result = run_cmd(cmd)

    if result.returncode == 0:
        set_status(f"Uploaded to {remote_path}")
        save_config()
    else:
        set_status(f"Upload failed: {result.stderr.strip()}", ok=False)


def save_config():
    data = {
        "ip": dpg.get_value("ip"),
        "port": dpg.get_value("port"),
        "user": dpg.get_value("user"),
        "file": state["file_path"],
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        dpg.set_value("ip", data.get("ip", ""))
        dpg.set_value("port", data.get("port", 22))
        dpg.set_value("user", data.get("user", ""))
        state["file_path"] = data.get("file", "")
        dpg.set_value("file_label", state["file_path"])


def save_json_to(path):
    data = {
        "ip": dpg.get_value("ip"),
        "port": dpg.get_value("port"),
        "user": dpg.get_value("user"),
        "file": state["file_path"],
    }
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        set_status(f"JSON saved to {path}")
    except Exception as e:
        set_status(f"Failed to save JSON: {e}", ok=False)


def file_selected(sender, app_data):
    selections = app_data.get("selections", {})
    if selections:
        file_name, full_path = next(iter(selections.items()))
        state["file_path"] = full_path
        dpg.set_value("file_label", full_path)


dpg.create_context()
w, h, c, data = dpg.load_image(resource_path(image_filename))
desired_width = 120
aspect_ratio = h / w
desired_height = int(desired_width * aspect_ratio)

with dpg.texture_registry(show=False):
    dpg.add_static_texture(w, h, data, tag="image_texture")

with dpg.file_dialog(show=False, callback=file_selected, tag="file_dialog"):
    dpg.add_file_extension(".*")

with dpg.file_dialog(
    show=False,
    callback=lambda s, a: save_json_to(a["file_path_name"]),
    directory_selector=False,
    default_filename="connection.json",
    modal=True,
    tag="save_json_dialog",
):
    dpg.add_file_extension(".json")


def create_about_dialog():
    with dpg.window(
        label="About - USA Flag",
        modal=True,
        show=False,
        tag="about_dialog",
        width=240,
        height=250,
        no_resize=True,
    ):
        dpg.add_text("Linux File Transfer 1.0.0", color=(150, 200, 255))
        dpg.add_spacer(height=10)

        with dpg.drawlist(width=200, height=110):
            # Flag dimensions
            fw, fh = 190, 100
            ox, oy = 5, 0

            # Draw 13 stripes
            stripe_h = fh / 13
            for i in range(13):
                color = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
                dpg.draw_rectangle(
                    [ox, oy + i * stripe_h],
                    [ox + fw, oy + (i + 1) * stripe_h],
                    fill=color,
                    color=color,
                )

            # Draw Union (blue box)
            uw = fw * 0.4
            uh = stripe_h * 7
            dpg.draw_rectangle(
                [ox, oy], [ox + uw, oy + uh], fill=(60, 59, 110), color=(60, 59, 110)
            )

            # Draw simplified stars (white dots)
            for row in range(9):
                for col in range(11):
                    if (row % 2 == 0 and col % 2 == 0) or (
                        row % 2 != 0 and col % 2 != 0
                    ):
                        sx = ox + (col + 1) * (uw / 12)
                        sy = oy + (row + 1) * (uh / 10)
                        dpg.draw_circle(
                            [sx, sy], 1, fill=(255, 255, 255), color=(255, 255, 255)
                        )

        dpg.add_spacer(height=10)
        dpg.add_button(
            label="Close",
            width=100,
            callback=lambda: dpg.configure_item("about_dialog", show=False),
        )


create_about_dialog()

# with dpg.theme() as dark_theme:
#     with dpg.theme_component(dpg.mvAll):
#         dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25))
#         dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (35, 35, 35))
#         dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 70, 70))
#         dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (90, 90, 90))
#         dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (110, 110, 110))
#         dpg.add_theme_color(dpg.mvThemeCol_Text, (200, 200, 200))
#         dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
#         dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
# dpg.bind_theme(dark_theme)


# Main Window
with dpg.window(
    label="Linux File Transfer Tool",
    tag="Primary Window",
    width=1050,
    height=500,
    no_resize=True,
    no_collapse=True,
):
    with dpg.menu_bar():
        with dpg.menu(label="Help"):
            dpg.add_menu_item(
                label="About", callback=lambda: dpg.show_item("about_dialog")
            )

    dpg.add_text("Linux File Transfer", color=(150, 200, 255))
    dpg.add_separator()

    with dpg.group(horizontal=True):
        # Instruction Section (Matches the height of a single row)
        with dpg.child_window(width=450, height=120, border=True):
            dpg.add_text("Instructions", color=(200, 200, 100))
            dpg.add_separator()
            dpg.add_text(
                "Before uploading, you can test SSH manually:\nRun the following command in a terminal to verify connectivity:",
                color=(180, 180, 180),
            )
            dpg.add_text("plink -P <port> user@ip", color=(100, 255, 255))

        dpg.add_spacer(width=20)

        # Single row: Image, LifePatterns, and SolarSystem
        with dpg.group(horizontal=True):
            with dpg.child_window(width=120, height=120, border=True):
                dpg.add_image(
                    "image_texture", width=desired_width, height=desired_height
                )

            dpg.add_spacer(width=10)

            with dpg.child_window(
                label="LifePatterns", width=160, height=120, border=True
            ):
                with dpg.drawlist(width=160, height=120, tag="life_drawlist"):
                    pass

            dpg.add_spacer(width=10)

            with dpg.child_window(
                label="SolarSystem", width=160, height=120, border=True
            ):
                with dpg.drawlist(width=160, height=120, tag="solar_drawlist"):
                    pass

    # Connection and File Panels
    with dpg.group(horizontal=True):
        # Connection Panel
        with dpg.child_window(width=450, height=250, border=True):
            dpg.add_text("Connection", color=(200, 200, 200))
            dpg.add_separator()
            dpg.add_input_text(label="IP Address", tag="ip")
            dpg.add_input_int(label="Port", tag="port", default_value=22)
            dpg.add_input_text(label="Username", tag="user")
            dpg.add_input_text(label="Password", password=True, tag="password")
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="Test Connection",
                width=-1,
                height=35,
                callback=test_connection,
            )
            dpg.add_spacer(height=8)
            dpg.add_button(
                label="Save JSON",
                width=-1,
                height=35,
                callback=lambda: dpg.show_item("save_json_dialog"),
            )

        dpg.add_spacer(width=20)

        # File Transfer Panel
        with dpg.child_window(width=450, height=250, border=True):
            dpg.add_text("File Transfer", color=(200, 200, 200))
            dpg.add_separator()
            dpg.add_input_text(label="Selected File", tag="file_label")
            dpg.add_input_text(label="Version", tag="version")
            dpg.add_spacer(height=50)
            dpg.add_button(
                label="Select File",
                width=-1,
                height=35,
                callback=lambda: dpg.show_item("file_dialog"),
            )
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="Upload to Server", width=-1, height=40, callback=upload_file
            )

    dpg.add_spacer(height=15)
    dpg.add_separator()

    with dpg.group(horizontal=True):
        dpg.add_text("Status:", color=(180, 180, 180))
        dpg.add_text("", tag="status", color=(100, 255, 100))

# Setup viewport with a large fixed size (compatible with older DPG versions)
dpg.create_viewport(title="Linux File Transfer Tool", width=1000, height=550)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)

load_config()

# Manual render loop for animation
while dpg.is_dearpygui_running():
    update_life_patterns()
    update_solar_system()
    dpg.render_dearpygui_frame()

dpg.destroy_context()
