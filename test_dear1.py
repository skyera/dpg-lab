import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label='Test', tag='main_window'):
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
        dpg.add_button(label='Run')

    dpg.add_separator()
    with dpg.group(horizontal=True):
        dpg.add_text('Status')
        dpg.add_text('Success', tag='run_status')

dpg.configure_item('run_status', **{"color": (0, 255, 0)})
dpg.create_viewport(title='Test Radio', width=600, height=600)
dpg.set_primary_window('main_window', True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
