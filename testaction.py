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

def get_fake_markdown():
    return fake.post(size="medium")

def get_fake_text():
    return fake.text()

class ReportMemoryProcess(multiprocessing.Process):
    def __init__(self, queue, count, interval):
        super().__init__()
        self.queue = queue
        self.count = count
        self.interval = interval

    def run(self):
        for i in range(self.count):
            time.sleep(self.interval)
            # Simulated VSS value
            val = 50 + (random.random() * 20) + (i / self.count * 10)
            self.queue.put((i, val))
        self.queue.put("done")

class MainWindow:
    def __init__(self):
        self.queue = multiprocessing.Queue()
        self.tc_tags = [f"tc_{i}" for i in range(35)] # t1-t5 + 30 others

    def create(self):
        self.setup_theme()
        self.create_mainwindow()
        self.create_file_window()

    def setup_theme(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (50, 100, 200, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (45, 45, 45, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 120, 255, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (50, 50, 50, 255))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 0) # Primary window
        dpg.bind_theme(global_theme)

    def create_mainwindow(self):
        with dpg.window(label="Unit Test Dashboard", tag="main_window"):
            # 1. Menu Bar
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Show Demo", callback=demo.show_demo)
                    dpg.add_menu_item(label="Item Registry", callback=dpg.show_item_registry)
                    dpg.add_menu_item(label="Tool", callback=dpg.show_tool)
                    dpg.add_menu_item(label="ImPlot Demo", callback=dpg.show_implot_demo)
                    dpg.add_menu_item(label="Doc", callback=dpg.show_documentation)
                    dpg.add_menu_item(label="Debug", callback=dpg.show_debug)
                    dpg.add_menu_item(label="Metrics", callback=dpg.show_metrics)
                    dpg.add_menu_item(label="About", callback=dpg.show_about)

            # 2. Banner + Quote
            with dpg.group(horizontal=True):
                dpg.add_text(get_banner(), color=(100, 200, 255))
                dpg.add_separator()
                if platform.system() == "Linux":
                    dpg.add_text(get_quote(), tag="quote_text", color=(150, 150, 150))

            # 3. Build Type
            with dpg.group(horizontal=True):
                dpg.add_text("Build Configuration:")
                dpg.add_radio_button(["Debug", "Release"], horizontal=True, default_value="Debug")

            dpg.add_separator()

            # 4. Test Cases (Table)
            dpg.add_text("Test Case Selection", color=(255, 200, 100))
            with dpg.child_window(height=200, border=True):
                with dpg.table(header_row=False, policy=dpg.mvTable_SizingFixedFit):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    
                    for i in range(len(self.tc_tags)):
                        if i % 3 == 0:
                            row = dpg.add_table_row()
                        dpg.add_checkbox(label=f"case {i+1:02d}", tag=self.tc_tags[i], parent=row)
                        if i < 1: dpg.set_value(self.tc_tags[i], True)

            dpg.add_spacer(height=5)

            # 5. Selection Buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Select All", callback=self.select_all_callback, width=100)
                dpg.add_button(label="Select None", callback=self.select_none_callback, width=100)
                dpg.add_button(label="Registry", callback=dpg.show_item_registry, width=100)

            dpg.add_separator()

            # 6. Settings
            with dpg.group():
                dpg.add_drag_int(label="Data Count", default_value=100, max_value=1000, tag="count", width=200)
                with dpg.group(horizontal=True):
                    dpg.add_input_float(label="Interval", default_value=0.05, tag="interval", width=200)
                    dpg.add_text("(s)", color=(150, 150, 150))
                with dpg.tooltip("interval"):
                    dpg.add_text("Sleep time between data samples")

            dpg.add_spacer(height=10)

            # 7. Run Controls
            with dpg.group(horizontal=True):
                dpg.add_drag_int(label="Repeat", default_value=1, width=150, min_value=1)
                dpg.add_button(label="  RUN TESTS  ", width=120, height=30, tag="run_button", callback=self.run_callback)
                dpg.add_loading_indicator(tag="ind", show=False, radius=2, color=(100, 150, 255))
                dpg.add_button(label="Browse...", callback=self.browse_callback)

            # 8. Modal Error
            with dpg.window(label="Warning", modal=True, show=False, tag="modal_id", no_title_bar=False):
                dpg.add_spacer(height=5)
                dpg.add_text("No test cases selected! Please check at least one.")
                dpg.add_spacer(height=10)
                dpg.add_separator()
                dpg.add_button(label="Close", width=75, callback=lambda: dpg.configure_item("modal_id", show=False))

            dpg.add_spacer(height=10)
            dpg.add_progress_bar(label="Progress", width=-1, tag="progress")

            dpg.add_separator()

            # 9. Status
            with dpg.group(horizontal=True):
                dpg.add_text("Current Status:")
                dpg.add_text("IDLE", tag="run_status", color=(150, 150, 150))

            dpg.add_spacer(height=5)

            # 10. Results Tab Bar
            with dpg.tab_bar():
                with dpg.tab(label="Memory Plot"):
                    with dpg.plot(label="VSS Usage Over Time", height=-1, width=-1, tag="plot"):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="Sequence")
                        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="MB", tag="y_axis")
                        dpg.add_line_series([], [], label="VSS Metric", parent="y_axis", tag="mem")

                with dpg.tab(label="Test Summary"):
                    dpg.add_text("Analysis report will appear here after run.", tag="test_summary", wrap=800)

                with dpg.tab(label="Test XML"):
                    dpg.add_input_text(multiline=True, readonly=True, width=-1, height=-1, tag="test_xml")

                with dpg.tab(label="Valgrind Log"):
                    dpg.add_input_text(multiline=True, readonly=True, width=-1, height=-1, tag="test_valgrind")

    def run_callback(self, sender):
        selected = [dpg.get_value(tag) for tag in self.tc_tags]
        if not any(selected):
            dpg.configure_item("modal_id", show=True)
            return

        self.update_quote()
        self.prepare_ui_for_run()
        
        count = dpg.get_value("count")
        interval = dpg.get_value("interval")
        
        proc = ReportMemoryProcess(self.queue, count, interval)
        proc.start()
        
        monitor_thread = threading.Thread(target=self.monitor_logic, args=(count,), daemon=True)
        monitor_thread.start()

    def update_quote(self):
        if platform.system() == "Linux" and dpg.does_item_exist("quote_text"):
            dpg.set_value("quote_text", get_quote())

    def prepare_ui_for_run(self):
        dpg.configure_item("run_button", enabled=False)
        dpg.configure_item("ind", show=True)
        dpg.set_value("mem", [[], []])
        dpg.set_value("run_status", "RUNNING...")
        dpg.configure_item("run_status", color=(255, 255, 0))
        dpg.set_value("progress", 0.0)

    def monitor_logic(self, total_count):
        data_x, data_y = [], []
        while True:
            msg = self.queue.get()
            if msg == "done":
                break
            
            idx, val = msg
            data_x.append(idx)
            data_y.append(val)
            
            # Throttle UI updates for performance
            if idx % 5 == 0 or idx == total_count - 1:
                dpg.set_value("mem", [data_x, data_y])
                dpg.set_value("progress", (idx + 1) / total_count)
        
        self.finalize_run()

    def finalize_run(self):
        success = random.random() > 0.2
        color = (100, 255, 100) if success else (255, 100, 100)
        status = "SUCCESS" if success else "FAILED"
        
        dpg.set_value("run_status", status)
        dpg.configure_item("run_status", color=color)
        dpg.set_value("test_summary", get_fake_markdown())
        dpg.set_value("test_xml", f"<testsuite tests='{len(self.tc_tags)}'>\n  <testcase classname='Simulation' status='{status}'/>\n</testsuite>")
        dpg.set_value("test_valgrind", get_fake_text())
        
        dpg.configure_item("ind", show=False)
        dpg.configure_item("run_button", enabled=True)

    def select_all_callback(self, sender):
        for tag in self.tc_tags: dpg.set_value(tag, True)

    def select_none_callback(self, sender):
        for tag in self.tc_tags: dpg.set_value(tag, False)

    def create_file_window(self):
        with dpg.file_dialog(directory_selector=False, tag="file_window", show=False, callback=lambda s, a: print(f"File selected: {a}")):
            dpg.add_file_extension(".*")
            dpg.add_file_extension(".cpp", color=(255, 255, 0, 255))
            dpg.add_file_extension(".h", color=(255, 0, 255, 255))

    def browse_callback(self):
        dpg.show_item("file_window")

class App:
    def __init__(self):
        dpg.create_context()
        self.main_window = MainWindow()

    def run(self):
        self.main_window.create()
        dpg.create_viewport(title="Test Action Pro", width=800, height=900)
        dpg.set_primary_window("main_window", True)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()

    def __del__(self):
        dpg.destroy_context()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.run()
