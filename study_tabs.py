import gradio as gr
from PIL import Image
import numpy as np
import pandas as pd
import os
import random
import math
import json
from pathlib import Path

def add_border(image):
    (w,h) = image.size
    if w >= h:
        return image
    else:
        # make square if image is vertical aligned.
        new_image = Image.new("RGB", (h, h), "White")
        new_image.paste(image, ((h-w) // 2, 0))
        return new_image
        
user = ""
default_image_path = './images_training/2.jpg'
default_explain="Correct Image :\n\nThis image is classified as a correct image since it does not have any of the other five problems we are looking at in a generated face. The image accurately reflects the prompt that we have provided and the facial structure of the man looks realistic."
default_level="No mistakes"
default_cat_exp="Generated faces do not suffer from any kind of structural or feature-related problem. Realistic human faces."

# Load the CSV file
df = pd.read_csv('./training_images_log.csv')

# Grouping image paths by category
category_to_images = df.groupby('category_name')['image_path'].apply(list).to_dict()

#Grouping category_name to category
category_to_names = df.groupby('category')['category_name'].apply(list).to_dict()
#dictionary mapping image paths to explanations
image_to_explanation = dict(zip(df['image_path'], df['explanation']))

#dict mapping of image path to prompt
image_to_prompt = dict(zip(df['image_path'], df['prompt']))

#dictionary mapping image paths to levels of mistake
image_to_mistake = dict(zip(df['image_path'], df['level_of_mistake']))

#dict mapping of image path to category explanation
image_to_cat_exp = dict(zip(df['image_path'], df['category_explanation']))

# Function to load an image
def image_load(image_path):
    img = Image.open(image_path)
    #img_resized=img.resize((300,300))
    return img
    #return gr.ImageEditor(value=img)

# Function to display an image for the selected category
def show_image(category):
    if category in category_to_images:
        # Get the list of image paths for this category
        image_path = category_to_images[category][0]
    
        explanation= image_to_explanation.get(image_path,"No explanation available for this image")
        prompt=image_to_prompt.get(image_path,"No prompt available")
        category_explain=image_to_cat_exp.get(image_path, "No explanation of category")
        level_msk=image_to_mistake.get(image_path,"No levels specified")
        return prompt,image_load(image_path),category_explain,explanation,level_msk
    
    else:
        return None  # Or return a default image if the category is not found

# Unique categories for dropdown
categories = df['category'].unique().tolist()
category_name = df['category_name'].unique().tolist()


def next_page(username):
    global nxt_page
    global user
    user = username
    if (len(username)>0) & (len(username)<12):
        nxt_page = True
        return gr.Button(interactive=True)
    return gr.Button(interactive=False)

def get_pictures(username):
    df = pd.read_csv("batches.csv")
    first_empty_index = (df['username'].isna() | (df['username'] == '')).idxmax()
    df.at[first_empty_index, 'username'] = username
    df.to_csv("batches.csv", index=False)
    return df.at[first_empty_index, 'batch']

def link_user_to_pics(username):
    df_users = pd.DataFrame()
    pics = get_pictures(username)
    df_users['pictures'] = json.loads(pics.replace('\'', '"'))
    df_users['username'] = username
    df_users['Category'] = None
    df_users['Level'] = None
    global default_image
    default_image = gr.Image(df_users['username'][0])
    print(df_users)
    global image_path
    image_path=df_users['pictures']
    df_users.to_csv(f"ratings_{username}.csv", index=False)
    global data_array
    data_array = df_users
    return True

def display_categories():

    categories_radio = gr.Radio(["Alignment Problem", "Incorrect Proportion", "Number of Features", "Wrong Aspect", "Unrealistic"], interactive=True, visible=True) 
    slider = gr.Slider(minimum=0, maximum=5, step=1, interactive=True, visible=True)
    
    return categories_radio, slider
current_pre_study_index = 0
def update_prestudy_data():
    
    data_array = pd.read_csv("prestudy_log.csv")
    global current_pre_study_index
    
    all_images_done = current_pre_study_index >= 5
    current_pre_study_index = (current_pre_study_index + 1) % len(data_array)
    img_path = data_array['image_path'][current_pre_study_index]#, data_array[current_index]["category"]
    img = Image.open(img_path)
    

    current_picture_label = f"{current_pre_study_index}/6"

    img = gr.ImageEditor(img,height=576,width=416, label=current_picture_label)
    
    if all_images_done:
        return img, gr.Radio(visible=False, value=None), gr.Slider(visible=False,value=None), gr.Text(visible=False,value=None), gr.Button(visible=False),gr.Button(interactive=True), gr.Button(interactive=False),gr.Button(interactive=False), gr.Button(interactive=False)
    return img, gr.Radio(visible=False,value=None), gr.Slider(visible=False,value=None), gr.Text(visible=False,value=None), gr.Button(visible=False),gr.Button(interactive=False), gr.Button(interactive=False),gr.Button(), gr.Button()

def show_solution(category, slider):
    
    data_array = pd.read_csv("prestudy_log.csv")

    print(category)

    if category == data_array['category_name'][current_pre_study_index]:
        answer_text = f"Your selection is correct. Level of mistake: {data_array['level_of_mistake'][current_pre_study_index]}"

        return gr.Text(answer_text, visible=True), gr.Button(visible=True)
    else:
        answer_text = f"Your selection was wrong. Category: {data_array['category_name'][current_pre_study_index]}, level of mistake: {data_array['level_of_mistake'][current_pre_study_index]}"
        return gr.Text(answer_text, visible=True), gr.Button(visible=True)

def show_solution_no_button():
    
    data_array = pd.read_csv("prestudy_log.csv")

    if  (data_array['category_name'][current_pre_study_index] == "Correct Image"):
        answer_text = f"Your selection is correct. Level of mistake: {data_array['level_of_mistake'][current_pre_study_index]}"

        return gr.Text(answer_text, visible=True), gr.Button(visible=True)
    else:
        answer_text = f"Your selection was wrong. Category: {data_array['category_name'][current_pre_study_index]}, level of mistake: {data_array['level_of_mistake'][current_pre_study_index]}"
        return gr.Text(answer_text, visible=True), gr.Button(visible=True)

# Initial index for displaying the first image
current_index = 0
# Boolean which indicates if all pictures were displayed
reached_end = False
# Function to update the displayed image and category

def update_data():

        
    data_array = pd.read_csv("ratings_" + user + ".csv")
    global current_index
    current_index = current_index + 1
    img_path = data_array['pictures'][current_index]
    img = Image.open(img_path)

    batch_size = len(data_array)
    current_picture_label = gr.Label(str(current_index +1) + "/" + str(batch_size))
    
    global reached_end

    print(reached_end)
        
    if (current_index+1) == batch_size:
        reached_end = True
    
    img = gr.ImageEditor(img,height=576,width=416, label=str(current_index+1) + "/" + str(batch_size))
    return img


def save_rating(radio, slider):

    path = "ratings_" + user + ".csv"
    df = pd.read_csv(path)

    df.loc[df['pictures']==image_path[current_index],['Category']] = radio
    df.loc[df['pictures']==image_path[current_index],['Level']] = slider

    categories_radio = gr.Radio(visible=False,value=None)
    slider =  gr.Slider(visible=False,value=None)

    df.to_csv(path, header=True, index=False)

    return update_data(), categories_radio, slider, gr.Button(interactive=False)

def save_no_mistake():
    path = "ratings_" + user + ".csv"
    df = pd.read_csv(path)
    
    df.loc[df['pictures']==image_path[current_index],['Category']] = "Correct Image"
    df.loc[df['pictures']==image_path[current_index],['Level']] = 0

    df.to_csv(path, header=True, index=False)

    return update_data()

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
                    with gr.Blocks() as introduction:
    
                        gr.Markdown(
                        """
                        # Introduction
                        Enter a username and press continue to see some examples of images and their categories.
                        """)
                        username = gr.Textbox(placeholder="Username", label="Enter any username", max_lines=1)
                        tab0_next = gr.Button(interactive=False, value="Continue")
                        username.change(next_page, username, tab0_next)
                        tab0.select(self.on_tab0_clicked) # TODO provide all components that should get an update when Tab0 is clicked
                        
                    
                ###### SECOND TAB ###############
                with gr.Tab("Second", interactive=False, id=1) as tab1:
                    gr.Markdown(
                    """
                    # Training phase
                    
                    On the left, we have the text prompt along with the generated image. 
                    On the right, we have the 6 radio buttons with categories and respective explanations. 
                    
                    Currently we can see first radio button 'Correct Image' is selected and an example image with respective text prompt, category explanation and reason for choice of category displayed.
                    
                    Please select other radio buttons to see respective examples. 
                    Thank you.
                
                    """
                    )
                    with gr.Row(): 
                     with gr.Column():
                            output_text1=gr.Text(label="Prompt", info="Select a category from the 6 radio buttons", value="sleeping face, man, realistic")
                            output_image=gr.ImageEditor(height=576,width=416,value=default_image_path)
                     with gr.Column():
                            radio=gr.Radio(choices=category_name,value="Correct Image", label="Category of Mistake",info="Please choose 1 category from the 6 options below")
                            output_text2=gr.Text(label="Short Explanation of Category",value=default_cat_exp)
                            output_text3=gr.Text(label="Reason for Category Choice",info="Why this image belongs to the above selected category",value =default_explain)
                            output_text4=gr.Text(label="Level of Mistake",value=default_level)
                    radio.change(fn=show_image, inputs=radio, outputs=[output_text1,output_image,output_text2,output_text3,output_text4])
                    with gr.Row():
                        tab1_next = gr.Button("Pre-Study", interactive=True)
                    tab1.select(self.on_tab1_clicked, outputs=[tab1,tabs]) # TODO provide all components that should get an update when Tab1 is clicked
                    
                    
                    
                ###### THIRD TAB ###############
                with gr.Tab("Third", visible=True, interactive=False, id=2) as tab2:
                    data_array = pd.read_csv("prestudy_log.csv")
                    first_image = Image.open(data_array['image_path'][0])
                    gr.Markdown(
                        """
                        # Pre-Study
                        Now it is your turn. We have 6 images for you to try before moving to Main study.
                         
                        If you spot a mistake, then click "YES" and say which category the mistake has and also which degree the mistake has in your opinion.
                        Then click on "Submit" to view if your answer was correct or wrong. Click on "Next Image" to see the next image. 
                        
                        If you don't spot any mistake, click "NO", and the next image apppears.
                    
                        """)
                    

                    with gr.Row():
                        current_pre_study_index = 0
                        with gr.Column():
                            gr.Textbox(label="Prompt", value="this is the prompt")
                            image = gr.ImageEditor(first_image, height=576,width=416, label=str(current_pre_study_index+1) + "/" + "6")

                        with gr.Column():
                            gr.Markdown(
                                """
                                # Do you spot any Mistake in this picture?
                                """
                            )
                            yes_button = gr.Button("YES")
                            # yes_button.click(display_categories, inputs=[], outputs=[gr.Radio(), gr.Slider()])
                            no_button  = gr.Button("NO")
                            #radio = gr.Radio(["YES", "NO"], label="Select")   
                            
                            
                            
                            categories_radio = gr.Radio(visible=False, label="Mistake Category")
                            
                            slider = gr.Slider(visible=False, label="Level of Mistake")

                            submit_button = gr.Button("Submit", interactive=False)
                            
                            yes_button.click(display_categories, 
                                 inputs=[],
                                 outputs=[categories_radio, slider]
                            )

                            categories_radio.select(fn=self.on_choice, inputs=[], outputs=[submit_button])
                            
                            
                            answer_text=""
                            
                            answer = gr.Text(value=answer_text, label="Correct Answer", visible=False)
                            next_image_button = gr.Button("Next Image",visible=False)

                            
                            no_button.click(fn=show_solution_no_button, inputs=[], outputs=[answer, next_image_button])
                    
                
                            submit_button.click(
                                fn=show_solution,
                                inputs=[categories_radio, slider],
                                outputs=[answer, next_image_button]
                            )
                    with gr.Row():
                        tab2_prev = gr.Button("Back to Training")
                        tab2_submit = gr.Button("Main Study", interactive=False)
                            
                        next_image_button.click(
                            fn=update_prestudy_data,
                            inputs=[],
                            outputs=[image,categories_radio,slider,answer,next_image_button,tab2_submit, submit_button,yes_button,no_button]
                        )

                        tab2.select(self.on_tab2_clicked, outputs=[tab2, tabs]) # TODO provide all components that should get an update when Tab2 is clicked
                            
            
                    
                ###### FOURTH TAB ###############  
                with gr.Tab("Fourth", interactive=False, visible=False, id=3) as tab3:
                        gr.Markdown(
                        """
                        # Main study
                        Hello! 
                        We will now look for mistakes in the pictures and categorize them into 5 categories of mistake.
                        
                        If you spot a mistake, then click "YES" and say which category the mistake has and also which degree the mistake has in your opinion.
                        Then submit your rating, and the next image appears. 
                        
                        If you don't spot any mistake, click "NO", and the next image apppears.
                        
                        Have Fun.
                        """)

                        

                        with gr.Row():
                            
                            
                            with gr.Column():
                                
                                gr.Textbox(label="prompt", value="this is the prompt")
                               #image = gr.ImageEditor(height=576,width=416, label=str(current_index+1) + "/" + str(batch_size))
                                image = gr.ImageEditor(height=576, width=416)
                        
                            with gr.Column():
                                gr.Markdown(
                                """
                                # Do you spot any Mistake in this picture?
                                """
                                )
                                yes_button = gr.Button("YES")
                                # yes_button.click(display_categories, inputs=[], outputs=[gr.Radio(), gr.Slider()])
                                no_button  = gr.Button("NO")
                                #radio = gr.Radio(["YES", "NO"], label="Select")   
                            
                                categories_radio = gr.Radio(visible=False)
                            
                                slider = gr.Slider(visible=False)
                        
                                yes_button.click(display_categories, 
                                inputs=[],
                                outputs=[categories_radio, slider]
                                )
                        
                                
                                
                                submit_button = gr.Button("Submit", interactive=False)
                                
                                categories_radio.select(fn=self.on_choice, inputs=[], outputs=[submit_button])
        
                                no_button.click(fn=save_no_mistake, inputs=[], outputs=[image])
                        
                                submit_button.click(
                                    fn=save_rating,
                                    inputs=[categories_radio, slider],
                                    outputs=[image, categories_radio, slider, submit_button]
                                )
                        
                            
                        with gr.Row():
                            tab3_finish_study = gr.Button("Finish Study")
                        
                        tab3.select(self.on_tab3_clicked, outputs=[image, tab0, tab1, tab2, tab3]) # TODO provide all components that should get an update when Tab2 is clicked

                ###### FIFTH TAB ###############  
                with gr.Tab("Fifth", interactive=False, visible=False, id=4) as tab4:
                    gr.Markdown(
                                """
                              # Thank you for Participating!!!
                                You can now close the study
                                 """
                                )
                    tab4.select(self.on_tab4_clicked, outputs=[tab3, tab4]) # TODO provide all components that should get an update when Tab2 is clicked

                #### EVENT HANDLING ###############
                tab0_next.click(lambda :gr.Tabs(selected=1), outputs=tabs)
                tab1_next.click(lambda :gr.Tabs(selected=2), outputs=tabs)
                # tab1_prev.click(lambda :gr.Tabs(selected=0), outputs=tabs)
                tab2_prev.click(lambda :gr.Tabs(selected=1), outputs=tabs)
                tab2_submit.click(lambda :gr.Tabs(selected=3), outputs=tabs)

                tab3_finish_study.click(lambda :gr.Tabs(selected=4), outputs=tabs)
                # tab1_choices.select(self.on_choise, inputs=tab1_choices, outputs=[tab2, tab1_next])
                # tab2_choices.select(self.on_choise, inputs=tab2_choices, outputs=[tab3, tab2_submit])
                # tab3_choices.select(self.on_choise, inputs=tab3_choices, outputs=[tab3, tab3_submit])


    
    
    def on_choice(self):
        # print(selection.target, selection.selected, selection.value)
        # TODO do something with selection
        return gr.Button(interactive=True)
    
    def on_tab0_clicked(self):
        print("tab0 clicked")
        return gr.Tab("First", interactive=True, id=0)
    
    def on_tab1_clicked(self):
        print("tab1 clicked")
        link_user_to_pics(user)
        # TODO update all components in tab1
        image = dummy_image_loader("/path/to/image")
        image = add_border(image)
        return gr.Tab(interactive=True,visible=True, id=1)
            
    def on_tab2_clicked(self):
        print("tab2 clicked")
        # TODO update all components in tab2
        image = dummy_image_loader("/path/to/image")
        image = add_border(image)
        return gr.Tab(interactive=True, visible=True, id=2)
    
    def on_tab3_clicked(self):
        print("tab3 clicked")
        # TODO update all components in tab2
        path = f"ratings_" + str(user) + ".csv"
        data_array = pd.read_csv(path)
        img_path = data_array['pictures'][0]
        #image = add_border(image)
        image = Image.open(img_path)
        return image, gr.Tab(interactive=False, visible=False, id=0), gr.Tab(interactive=False, visible=False, id=1), gr.Tab(interactive=False, visible=False, id=2), gr.Tab(interactive=True, visible=True, id=3)
    
    def on_tab4_clicked(self):
        print("Tab 5")
        #return gr.Tab("First", interactive=False, visible=False, id=0), gr.Tab("Second", interactive=False, visible=False, id=1), gr.Tab("Third", interactive=False, visible=False, id=2), gr.Tab("Fourth", interactive=False, visible=False, id=3), gr.Tab("Fith", interactive=True, visible=True, id=4)
        return gr.Tab("Fourth", interactive=False, visible=False, id=3), gr.Tab("Fith", interactive=True, visible=True, id=4)
        
    
    def launch(self):
        self.app.queue()
        #self.app.launch(server_name="0.0.0.0", server_port=7860) # expose 
        self.app.launch()
    
if __name__ == "__main__":
    framework = StudyFramework()
    framework.launch()