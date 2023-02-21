import dearpygui.dearpygui as dpg
from faker import Faker
from mdgen import MarkdownPostProvider
import multiprocessing
import platform
import pyfiglet
import random
import subprocess
import threading
import time


def get_quote():
    result = subprocess.run(["fortune|cowsay"], shell=True, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def get_fake_markdown():
    fake = Faker()
    fake.add_provider(MarkdownPostProvider)
    fake_post = fake.post(size='medium')
    return fake_post


def get_fake_text():
    fake = Faker()
    return fake.text()


def get_checked_tc_count():
    ts_tags = ('t1', 't2', 't3', 't4', 't5')
    count = 0
    for ts in ts_tags:
        if dpg.get_value(ts):
            count += 1
    return count


def get_banner():
    ascii_banner = pyfiglet.figlet_format('Unit Testing', width=80)
    return ascii_banner


def report_mem(mq):
    for i in range(100):
        time.sleep(0.1)
        x = random.random() * 100
        mq.put((i, x))
    mq.put('done')
    print('report_mem: done')


def monitor_mem(mq):
    datax = []
    datay = []
    p  = 0
    dpg.set_value('progress', p)
    while True:
        x = mq.get()
        if x == 'done':
            print('done')
            break
        datax.append(x[0])
        datay.append(x[1])
        dpg.set_value('mem', [datax, datay])
        p += 0.1
        dpg.set_value('progress', p)

    x = random.random()
    print(x)
    if x > 0.5 :
        color = (0, 255, 0)
        text = 'Sucess'
    else:
        color = (255, 0, 0)
        text = 'Failed'
    dpg.configure_item('run_status', color=color)
    dpg.set_value('run_status', text)
    dpg.set_value('test_summary', get_fake_markdown())
    dpg.set_value('test_xml', get_fake_text())
    dpg.set_value('test_valgrind', get_fake_text())
    dpg.configure_item('ind', show=False)
    dpg.configure_item('run_button', enabled=True)


def main():
    app = App()
    app.run()


class MainWindow:
    def __init__(self):
        pass

    def create(self):
        datax = []
        datay = []
        for i in range(20):
            x = random.random() * 100
            datax.append(i)
            datay.append(x)
        
        with dpg.window(label='Unit Test', tag='main_window'):
            with dpg.group(horizontal=True):
                banner = get_banner()
                dpg.add_text(banner)
                dpg.add_separator()
                
                if platform.system() == 'Linux':
                    quote = get_quote()
                    dpg.add_text(quote, tag='quote_text')
            
            with dpg.group(horizontal=True):
                dpg.add_text("Build Type:")
                dpg.add_radio_button(label='Build', items=['Debug', 'Release'],
                        horizontal=True)
            
            dpg.add_separator()
            with dpg.group(xoffset=100):
                dpg.add_text('Test cases')
                dpg.add_checkbox(label='case 1', tag='t1')
                dpg.add_checkbox(label='case 2', tag='t2')
                dpg.add_checkbox(label='case 3', tag='t3')
                dpg.add_checkbox(label='case 4', tag='t4')
                dpg.add_checkbox(label='case 5', tag='t5')

            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Select All', callback=self.select_all_callback)
                dpg.add_button(label='Select None', callback=self.select_none_callback)
                dpg.add_button(label='Refresh')
            
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_drag_int(label='Repeat', default_value=1, width=200, min_value=1)
                dpg.add_button(label='Run', width=100, tag='run_button',
                        callback=self.run_callback)
                dpg.add_loading_indicator(tag='ind', show=False)

            with dpg.window(label='Test cases', modal=True, show=False, tag='modal_id'):
                dpg.add_text('No test cases selected')
                dpg.add_separator()
                dpg.add_button(label='Close', 
                        callback=lambda: dpg.configure_item('modal_id', show=False))

            dpg.add_progress_bar(label='Progress', width=-1, tag='progress')

            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_text('Status')
                dpg.add_text('Success', tag='run_status')

            with dpg.tab_bar():
                with dpg.tab(label='Memory Plot'):
                    with dpg.plot(label='Memory', height=-1, width=-1):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label='Time(seconds)')
                        dpg.add_plot_axis(dpg.mvYAxis, label='vss', tag='y_axis')
                        dpg.add_line_series(datax, datay, label='VSS', parent='y_axis',
                                tag='mem')

                with dpg.tab(label='Test summary'):
                    dpg.add_text('Test Summary', tag='test_summary')
                
                with dpg.tab(label='Test XML'):
                    dpg.add_text("This is test xml report", tag='test_xml')

                with dpg.tab(label='Valgrind log'):
                    dpg.add_text("This is valgrind log", tag='test_valgrind')

    def run_callback(self, sender):
        if get_checked_tc_count() == 0:
            dpg.configure_item('modal_id', show=True)
            return

        if platform.system() == 'Linux':
            quote = get_quote()
            dpg.set_value('quote_text', quote)

        dpg.configure_item(sender, enabled=False)
        dpg.configure_item('ind', show=True)
        dpg.set_value('mem', [[], []])
        mq = multiprocessing.Queue()
        
        proc = multiprocessing.Process(target=report_mem, args=(mq,))
        proc.daemon = True
        proc.start()

        monitor_thread = threading.Thread(target=monitor_mem, args=(mq,))
        monitor_thread.start()

    def select_all_callback(self, sender):
        ts_tags = ('t1', 't2', 't3', 't4', 't5')
        for ts in ts_tags:
            dpg.set_value(ts, True)

    def select_none_callback(self, sender):
        ts_tags = ('t1', 't2', 't3', 't4', 't5')
        for ts in ts_tags:
            dpg.set_value(ts, False)


class App:
    def __init__(self):
        dpg.create_context()
        self.main_window = MainWindow()

    def run(self):
        self.main_window.create()
        dpg.configure_item('run_status', **{"color": (0, 255, 0)})
        dpg.create_viewport(title='Test Radio', width=600, height=600)
        dpg.set_primary_window('main_window', True)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()

    def __del__(self):
        dpg.destroy_context()


if __name__ == '__main__':
    main()
