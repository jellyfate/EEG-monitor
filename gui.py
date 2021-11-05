import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo


def save_callback():
    print("Save Clicked")


class GUI:

    def __init__(self, timeloop, database):
        self.timeloop = timeloop
        self.database = database
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()

    def _construct(self):
        with dpg.window(label="Example Window"):
            dpg.add_text("Hello world")
            dpg.add_button(label="Save", callback=save_callback)
            dpg.add_input_text(label="string")
            dpg.add_slider_float(label="float")

    def show(self):
        self._construct()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
