import multiprocessing
import platform
import random
import subprocess
import threading
import time
import os

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import psutil
import pyfiglet
from faker import Faker
from mdgen import MarkdownPostProvider

# Initialize Faker
fake = Faker()
fake.add_provider(MarkdownPostProvider)

def get_quote():
    if platform.system() == "Linux":
        try:
            result = subprocess.run("fortune | cowsay", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if result.returncode == 0:
                return result.stdout
        except:
            pass
    return "The only way to do great work is to love what you do. - Steve Jobs"

def get_banner():
    return pyfiglet.figlet_format("Test Action", font="slant")

class ReportMemoryProcess(multiprocessing.Process):
    def __init__(self, queue, count, interval, stop_event):
        super().__init__()
        self.queue = queue
        self.count = count
        self.interval = interval
        self.stop_event = stop_event

    def run(self):
        for i in range(self.count):
            if self.stop_event.is_set():
                break
            time.sleep(self.interval)
            # Simulate memory usage
            val = 50 + (random.random() - 0.5) * 20 + (i / self.count) * 30
            self.queue.put((i, val))
        self.queue.put("done")

class MainWindow:
    def __init__(self):
        self.queue = multiprocessing.Queue()
        self.stop_event = multiprocessing.Event()
        self.test_cases = [] # List of tags
        self.is_running = False
        self.monitor_thread = None

    def create(self):
        self.setup_theme()
        self.create_mainwindow()
        self.create_file_window()

    def setup_theme(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (50, 50, 200, 255))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (100, 150, 255, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 80, 200, 255))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
        dpg.bind_theme(global_theme)

    def create_mainwindow(self):
        with dpg.window(label="Test Action Dashboard", tag="main_window"):
            with dpg.menu_bar():
                with dpg.menu(label="Tools"):
                    dpg.add_menu_item(label="Show Demo", callback=demo.show_demo)
                    dpg.add_menu_item(label="Item Registry", callback=dpg.show_item_registry)
                    dpg.add_menu_item(label="Metrics", callback=dpg.show_metrics)
                with dpg.menu(label="Help"):
                    dpg.add_menu_item(label="About", callback=dpg.show_about)

            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text(get_banner(), color=(100, 200, 255))
                    self.quote_text = dpg.add_text(get_quote(), wrap=600)
                
            dpg.add_spacer(height=10)
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=450, label="Configuration", border=True):
                    dpg.add_text("Build Configuration", color=(255, 200, 100))
                    dpg.add_radio_button(["Debug", "Release"], horizontal=True, default_value="Debug", tag="build_type")
                    
                    dpg.add_spacer(height=10)
                    dpg.add_text("Execution Settings", color=(255, 200, 100))
                    dpg.add_drag_int(label="Data Points", default_value=100, min_value=10, max_value=1000, tag="count", width=150)
                    dpg.add_input_float(label="Interval (s)", default_value=0.05, min_value=0.01, tag="interval", width=150)
                    dpg.add_drag_int(label="Repeat Count", default_value=1, min_value=1, max_value=10, tag="repeat", width=150)
                    
                    dpg.add_spacer(height=20)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="RUN TESTS", width=120, height=40, tag="run_button", callback=self.run_callback)
                        dpg.add_button(label="STOP", width=80, height=40, tag="stop_button", callback=self.stop_callback, enabled=False)
                    
                    dpg.add_spacer(height=10)
                    dpg.add_loading_indicator(tag="ind", show=False, radius=2, color=(100, 150, 255))
                    dpg.add_text("Status: Idle", tag="run_status")
                    dpg.add_progress_bar(label="Progress", width=-1, tag="progress")

                with dpg.child_window(label="Test Case Selection", border=True):
                    dpg.add_text("Available Test Cases", color=(255, 200, 100))
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Select All", callback=self.select_all_callback, small=True)
                        dpg.add_button(label="Deselect All", callback=self.select_none_callback, small=True)
                    
                    dpg.add_spacer(height=5)
                    with dpg.child_window(height=300, border=False):
                        with dpg.table(header_row=False, policy=dpg.mvTable_SizingFixedFit):
                            dpg.add_table_column()
                            dpg.add_table_column()
                            dpg.add_table_column()
                            
                            for i in range(24):
                                if i % 3 == 0:
                                    row = dpg.add_table_row()
                                tag = f"tc_{i+1}"
                                self.test_cases.append(tag)
                                dpg.add_checkbox(label=f"TC-{i+1:02d}", tag=tag, parent=row)

                    dpg.add_spacer(height=10)
                    dpg.add_button(label="Browse Workspace...", callback=self.browse_callback)

            dpg.add_spacer(height=10)
            
            with dpg.tab_bar():
                with dpg.tab(label="System Monitor"):
                    with dpg.plot(label="Resource Usage Simulation", height=-1, width=-1, tag="plot"):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="Sequence")
                        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Value", tag="y_axis")
                        dpg.add_line_series([], [], label="Metric Alpha", parent="y_axis", tag="mem_series")
                
                with dpg.tab(label="Analysis"):
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Generate Fake Report", callback=self.update_analysis_tabs)
                    dpg.add_separator()
                    with dpg.tab_bar():
                        with dpg.tab(label="Summary"):
                            dpg.add_text("", tag="test_summary", wrap=800)
                        with dpg.tab(label="XML Output"):
                            dpg.add_input_text(multiline=True, readonly=True, width=-1, height=-1, tag="test_xml")
                        with dpg.tab(label="Logs"):
                            dpg.add_input_text(multiline=True, readonly=True, width=-1, height=-1, tag="test_logs")

    def run_callback(self, sender):
        selected_count = sum([dpg.get_value(tc) for tc in self.test_cases])
        if selected_count == 0:
            self.show_error("Please select at least one test case.")
            return

        self.is_running = True
        self.stop_event.clear()
        
        # UI Updates
        dpg.configure_item("run_button", enabled=False)
        dpg.configure_item("stop_button", enabled=True)
        dpg.configure_item("ind", show=True)
        dpg.set_value("run_status", "Running...")
        dpg.configure_item("run_status", color=(255, 255, 0))
        dpg.set_value("mem_series", [[], []])
        dpg.set_value("progress", 0.0)

        # Start process
        count = dpg.get_value("count")
        interval = dpg.get_value("interval")
        proc = ReportMemoryProcess(self.queue, count, interval, self.stop_event)
        proc.start()

        # Start monitor
        self.monitor_thread = threading.Thread(target=self.monitor_logic, args=(count,), daemon=True)
        self.monitor_thread.start()

    def stop_callback(self, sender):
        self.stop_event.set()
        dpg.set_value("run_status", "Stopping...")

    def monitor_logic(self, total_count):
        data_x, data_y = [], []
        while True:
            try:
                msg = self.queue.get(timeout=0.1)
                if msg == "done":
                    break
                
                idx, val = msg
                data_x.append(idx)
                data_y.append(val)
                
                # Update UI periodically to save overhead
                if len(data_x) % 5 == 0 or idx == total_count - 1:
                    dpg.set_value("mem_series", [data_x, data_y])
                    dpg.set_value("progress", (idx + 1) / total_count)
            except:
                if self.stop_event.is_set() and self.queue.empty():
                    break
                continue

        self.finalize_run()

    def finalize_run(self):
        self.is_running = False
        dpg.configure_item("run_button", enabled=True)
        dpg.configure_item("stop_button", enabled=False)
        dpg.configure_item("ind", show=False)
        
        if self.stop_event.is_set():
            dpg.set_value("run_status", "Cancelled")
            dpg.configure_item("run_status", color=(255, 100, 100))
        else:
            success = random.random() > 0.2
            status_text = "Success" if success else "Failed"
            status_color = (100, 255, 100) if success else (255, 100, 100)
            dpg.set_value("run_status", status_text)
            dpg.configure_item("run_status", color=status_color)
            self.update_analysis_tabs()

    def update_analysis_tabs(self):
        dpg.set_value("test_summary", fake.post(size="medium"))
        dpg.set_value("test_xml", f"<testsuite name='TestAction' tests='{len(self.test_cases)}'>\n  <testcase name='Simulation' time='1.2'/>\n</testsuite>")
        dpg.set_value("test_logs", f"[INFO] Starting simulation...\n[DEBUG] Interval: {dpg.get_value('interval')}\n[INFO] Data points: {len(self.test_cases)}\n[SUCCESS] Completed.")

    def select_all_callback(self):
        for tc in self.test_cases:
            dpg.set_value(tc, True)

    def select_none_callback(self):
        for tc in self.test_cases:
            dpg.set_value(tc, False)

    def show_error(self, message):
        with dpg.window(label="Error", modal=True, tag="error_modal"):
            dpg.add_text(message)
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item("error_modal"))

    def create_file_window(self):
        with dpg.file_dialog(directory_selector=True, tag="file_window", show=False, callback=lambda s, a: print(f"Selected: {a}")):
            dpg.add_file_extension(".*")

    def browse_callback(self):
        dpg.show_item("file_window")

class App:
    def __init__(self):
        dpg.create_context()
        self.main_window = MainWindow()

    def run(self):
        self.main_window.create()
        dpg.create_viewport(title="Test Action Pro", width=1000, height=800)
        dpg.set_primary_window("main_window", True)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()

    def __del__(self):
        dpg.destroy_context()

if __name__ == "__main__":
    # On Windows, multiprocessing needs this
    multiprocessing.freeze_support()
    app = App()
    app.run()
