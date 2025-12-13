import json
import os
import subprocess

import dearpygui.dearpygui as dpg

CONFIG_FILE = "connection.json"
state = {"file_path": ""}


# ---------------- Helper Functions ----------------
def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, shell=False)


def set_status(msg, ok=True):
    color = (100, 255, 100) if ok else (255, 100, 100)
    dpg.set_value("status", msg)
    dpg.configure_item("status", color=color)


# ---------------- SSH Test ----------------
def test_connection():
    ip = dpg.get_value("ip")
    port = dpg.get_value("port")
    user = dpg.get_value("user")
    password = dpg.get_value("password")

    if not ip or not user:
        set_status("IP or username missing!", ok=False)
        return

    cmd = [
        "plink",
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


# ---------------- File Upload ----------------
def upload_file():
    ip = dpg.get_value("ip")
    port = dpg.get_value("port")
    user = dpg.get_value("user")
    password = dpg.get_value("password")
    file_path = state["file_path"]

    if not file_path or not os.path.exists(file_path):
        set_status("Invalid file selected", ok=False)
        return

    remote_path = f"/tmp/{os.path.basename(file_path)}"
    cmd = [
        "pscp",
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


# ---------------- JSON Config ----------------
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


# ---------------- Save JSON to chosen location ----------------
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


# ---------------- File Dialog ----------------
def file_selected(sender, app_data):
    selections = app_data.get("selections", {})
    if selections:
        file_name, full_path = next(iter(selections.items()))
        state["file_path"] = full_path
        dpg.set_value("file_label", full_path)


# ---------------- UI ----------------
dpg.create_context()

# File Dialogs
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

# Dark Theme
with dpg.theme() as dark_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25))
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (35, 35, 35))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 70, 70))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (90, 90, 90))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (110, 110, 110))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (200, 200, 200))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
dpg.bind_theme(dark_theme)


# Main Window
with dpg.window(
    label="🚀 Linux File Transfer Tool",
    width=1400,
    height=900,
    no_resize=True,
    no_collapse=True,
):
    dpg.add_text("Linux File Transfer", color=(150, 200, 255))
    dpg.add_separator()

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
            dpg.add_text("Selected File:")
            dpg.add_text("", tag="file_label", wrap=600)
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

    # Instruction Section
    with dpg.child_window(width=920, height=120, border=True):
        dpg.add_text("Instructions", color=(200, 200, 100))
        dpg.add_separator()
        dpg.add_text(
            "Before uploading, you can test SSH manually:\nRun the following command in a terminal to verify connectivity:",
            color=(180, 180, 180),
        )
        dpg.add_text("plink -P <port> user@ip", color=(100, 255, 255))
        dpg.add_text(
            "Replace <port>, user, and ip with your server information.",
            color=(180, 180, 180),
        )

    dpg.add_spacer(height=15)
    dpg.add_separator()

    # Status Bar
    with dpg.group(horizontal=True):
        dpg.add_text("Status:", color=(180, 180, 180))
        dpg.add_text("", tag="status", color=(100, 255, 100))

# Setup viewport with a large fixed size (compatible with older DPG versions)
dpg.create_viewport(title="Linux File Transfer Tool", width=1000, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()

load_config()
dpg.start_dearpygui()
dpg.destroy_context()
