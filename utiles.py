from voice_assistant import VoiceAssistant
import ipywidgets as widgets
from IPython.display import display

class Utiles:

    def button ():
        button = widgets.Button(description="Click me!")
        output = widgets.Output()
        display(button, output)
        def on_button_clicked(b):
            with output:
                object = VoiceAssistant()
                object.voice_to_action()
        button.on_click(on_button_clicked)