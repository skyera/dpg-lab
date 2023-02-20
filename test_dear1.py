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


def run_callback():
    if platform.system() == 'Linux':
        quote = get_quote()
        dpg.set_value('quote_text', quote)
    
    global datax, datay
    datax = []
    datay = []
    dpg.set_value('mem', [datax, datay])
    mq = multiprocessing.Queue()
    
    p2 = multiprocessing.Process(target=report_mem, args=(mq,))
    p2.daemon = True
    p2.start()

    t = threading.Thread(target=monitor_mem, args=(mq,))
    t.start()
    t.join()
    x = random.random() % 2
    if x == 0:
        color = (0, 255, 0)
        text = 'Sucess'
    else:
        color = (255, 0, 0)
        text = 'Failed'
    dpg.configure_item('run_status', **{"color": color})
    dpg.set_value('run_status', text)
    dpg.set_value('test_summary', get_fake_markdown())
    dpg.set_value('test_xml', get_fake_text())
    dpg.set_value('test_valgrind', get_fake_text())


def get_banner():
    ascii_banner = pyfiglet.figlet_format('Unit Testing', width=80)
    return ascii_banner


def report_mem(mq):
    for i in range(100):
        time.sleep(0.1)
        x = random.random() * 100
        print(x)
        mq.put((i, x))
    mq.put('done')
    print('report_mem: done')


def monitor_mem(mq):
    global datax, datay
    while True:
        x = mq.get()
        if x == 'done':
            print('done')
            break
        print('recv', x)
        datax.append(x[0])
        datay.append(x[1])
        print(len(datax), len(datay))
        dpg.set_value('mem', [datax, datay])


def main():
    global datax, datay
    datax = []
    datay = []
    for i in range(20):
        x = random.random() * 100
        datax.append(i)
        datay.append(x)
    dpg.create_context()

    with dpg.window(label='Test', tag='main_window'):
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
            dpg.add_checkbox(label='case 1')
            dpg.add_checkbox(label='case 2')
            dpg.add_checkbox(label='case 3')
            dpg.add_checkbox(label='case 4')
            dpg.add_checkbox(label='case 5')

        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label='Select All')
            dpg.add_button(label='Select None')
            dpg.add_button(label='Refresh')
        
        dpg.add_separator()
        with dpg.group():
            dpg.add_drag_int(label='Repeat', min_value=0)
            dpg.add_button(label='Run', callback=run_callback)

        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_text('Status')
            dpg.add_text('Success', tag='run_status')

        with dpg.tab_bar():
            with dpg.tab(label='Test summary'):
                dpg.add_text('Test Summary', tag='test_summary')
            with dpg.tab(label='Plot'):
                with dpg.plot(label='Memory', height=-1, width=-1):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label='Time(seconds)')
                    dpg.add_plot_axis(dpg.mvYAxis, label='vss', tag='y_axis')
                    dpg.add_line_series(datax, datay, label='VSS', parent='y_axis',
                            tag='mem')

            with dpg.tab(label='Test XML'):
                dpg.add_text("This is test xml report", tag='test_xml')

            with dpg.tab(label='Valgrind log'):
                dpg.add_text("This is valgrind log", tag='test_valgrind')

    dpg.configure_item('run_status', **{"color": (0, 255, 0)})
    dpg.create_viewport(title='Test Radio', width=600, height=600)
    dpg.set_primary_window('main_window', True)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()
