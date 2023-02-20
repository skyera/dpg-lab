import dearpygui.dearpygui as dpg
from math import sin
import multiprocessing
import platform
import pyfiglet
import random
import subprocess
import threading
import time


datax = []
datay = []


def get_quote():
    result = subprocess.run(["fortune|cowsay"], shell=True, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


for i in range(20):
    x = random.random() * 100
    datax.append(i)
    datay.append(x)
#     datax.append(i)
#     datay.append(sin(i))


def run_callback():
    if platform.system() == 'Linux':
        quote = get_quote()
        dpg.set_value('quote_text', quote)
    
    global datax, datay
    datax = []
    datay = []
    dpg.set_value('mem', [datax, datay])
    
    p2 = multiprocessing.Process(target=report_mem)
    p2.daemon = True
    p2.start()

    t = threading.Thread(target=monitor_mem)
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


def get_banner():
    ascii_banner = pyfiglet.figlet_format('Unit Testing', width=80)
    return ascii_banner


mq = multiprocessing.Queue()

def report_mem():
    for i in range(100):
        time.sleep(0.2)
        x = random.random() * 100
        print(x)
        mq.put((i, x))
    mq.put('done')
    print('report_mem: done')


def monitor_mem():
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
            dpg.add_text('Test Summary')
        with dpg.tab(label='Plot'):
            with dpg.plot(label='Memory', height=-1, width=-1):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label='Time(seconds)')
                dpg.add_plot_axis(dpg.mvYAxis, label='vss', tag='y_axis')
                dpg.add_line_series(datax, datay, label='VSS', parent='y_axis',
                        tag='mem')

        with dpg.tab(label='Test XML'):
            dpg.add_text("This is test xml report")

        with dpg.tab(label='Valgrind log'):
            dpg.add_text("This is valgrind log")

dpg.configure_item('run_status', **{"color": (0, 255, 0)})
dpg.create_viewport(title='Test Radio', width=600, height=600)
dpg.set_primary_window('main_window', True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
