#code for switching tabs
import gradio as gr
from PIL import Image
import numpy as np

def add_border(image):
    (w,h) = image.size
    if w >= h:
        return image
    else:
        # make square if image is vertical aligned.
        new_image = Image.new("RGB", (h, h), "White")
        new_image.paste(image, ((h-w) // 2, 0))
        return new_image

# TODO load images from PATH
def dummy_image_loader(path):
    # ignore path and return random image
    return Image.fromarray(np.random.randint(0, 256, size=(512, 384, 3)).astype(np.uint8))

class StudyFramework:    
    def __init__(self) -> None:
        with gr.Blocks() as self.app:
            with gr.Tabs() as tabs:
                ###### FIRST TAB ###############
                with gr.Tab("First", id=0) as tab0:
                    gr.Markdown("""
                                # HEADING
                                some text
                                wow
                                """)
                    tab0_next = gr.Button("Next")
                    tab0.select(self.on_tab0_clicked) # TODO provide all components that should get an update when Tab0 is clicked
                    
                    
                ###### SECOND TAB ###############
                with gr.Tab("Second", interactive=True, id=1) as tab1:
                    with gr.Row():
                        img = gr.Image()
                        tab1_choices = gr.Radio(["A", "B", "C"])
                    with gr.Row():
                        tab1_prev = gr.Button("Prev")
                        tab1_next = gr.Button("Next", interactive=False)
                    tab1.select(self.on_tab1_clicked, outputs=[img]) # TODO provide all components that should get an update when Tab1 is clicked
                    
                    
                ###### THIRD TAB ###############
                with gr.Tab("Third", visible=False, interactive=False, id=2) as tab2:
                    with gr.Row():
                        img2 = gr.Image()
                        tab2_choices = gr.Radio(["A", "B", "C"])
                    with gr.Row():
                        tab2_prev = gr.Button("Prev")
                        tab2_submit = gr.Button("Submit", interactive=False)
                    tab2.select(self.on_tab2_clicked, outputs=[img2]) # TODO provide all components that should get an update when Tab2 is clicked
                
                
                ###### FOURTH TAB ###############  
                with gr.Tab("Fourth", interactive=False, visible=False, id=3) as tab3:
                    with gr.Row():
                        img3 = gr.Image()
                        tab3_choices = gr.Radio(["A", "B", "C"])
                    with gr.Row():
                        tab3_submit = gr.Button("Submit")
                    tab3.select(self.on_tab3_clicked, outputs=[img3, tab0, tab1, tab2]) # TODO provide all components that should get an update when Tab2 is clicked

                #### EVENT HANDLING ###############
                tab0_next.click(lambda :gr.Tabs(selected=1), outputs=tabs)
                tab1_next.click(lambda :gr.Tabs(selected=2), outputs=tabs)
                tab1_prev.click(lambda :gr.Tabs(selected=0), outputs=tabs)
                tab2_prev.click(lambda :gr.Tabs(selected=1), outputs=tabs)
                tab2_submit.click(lambda :gr.Tabs(selected=3), outputs=tabs)
                tab1_choices.select(self.on_choise, inputs=tab1_choices, outputs=[tab2, tab1_next])
                tab2_choices.select(self.on_choise, inputs=tab2_choices, outputs=[tab3, tab2_submit])
                tab3_choices.select(self.on_choise, inputs=tab3_choices, outputs=[tab3, tab3_submit])
    
    def on_choise(self, value, selection: gr.SelectData):
        # print(selection.target, selection.selected, selection.value)
        # TODO do something with selection
        return gr.Tab(interactive=True, visible=True), gr.Button(interactive=True)
    
    def on_tab0_clicked(self):
        print("tab0 clicked")
    
    def on_tab1_clicked(self):
        print("tab1 clicked")
        # TODO update all components in tab1
        image = dummy_image_loader("/path/to/image")
        image = add_border(image)
        return image
            
    def on_tab2_clicked(self):
        print("tab2 clicked")
        # TODO update all components in tab2
        image = dummy_image_loader("/path/to/image")
        image = add_border(image)
        return image
    
    def on_tab3_clicked(self):
        print("tab3 clicked")
        # TODO update all components in tab2
        image = dummy_image_loader("/path/to/image")
        image = add_border(image)
        return image, gr.Tab(visible=False), gr.Tab(visible=False), gr.Tab(visible=False)
    
    def launch(self):
        self.app.queue()
        #self.app.launch(server_name="0.0.0.0", server_port=7860) # expose 
        self.app.launch()
    
if __name__ == "__main__":
    framework = StudyFramework()
    framework.launch()