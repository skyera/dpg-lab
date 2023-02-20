import dearpygui.dearpygui as dpg
from math import sin
import pyfiglet
import subprocess


datax = []
datay = []


def get_quote():
    result = subprocess.run(["fortune|cowsay"], shell=True, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


for i in range(500):
    datax.append(i)
    datay.append(sin(i))


def run_callback():
    quote = get_quote()
    dpg.set_value('quote_text', quote)


def get_banner():
    ascii_banner = pyfiglet.figlet_format('Unit Testing', width=80)
    return ascii_banner


dpg.create_context()

with dpg.window(label='Test', tag='main_window'):
    with dpg.group(horizontal=True):
        banner = get_banner()
        print(banner)
        dpg.add_text(banner)
        dpg.add_separator()
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
                dpg.add_line_series(datax, datay, label='VSS', parent='y_axis' )

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
