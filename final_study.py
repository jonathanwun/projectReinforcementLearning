import pandas as pd
import gradio as gr
import os
import random
import math
import json
from PIL import Image
from pathlib import Path

def generate_batches_from_folder(folder_path, batch_size):
    # Get a list of all files in the folder
    all_files = os.listdir(folder_path)
    
    # Filter out non-image files (you can customize this based on your file extensions)
    image_files = [file for file in all_files if file.lower().endswith(('.jpg'))]
 
    random.shuffle(image_files)
    
    # Split the triplicated image files into batches
    batches1 = [image_files[i:i + batch_size] for i in 
               range(0, len(image_files), batch_size)]
    random.shuffle(image_files)
    
    # Split the triplicated image files into batches
    batches2 = [image_files[i:i + batch_size] for i in 
               range(0, len(image_files), batch_size)]
    random.shuffle(image_files)
    
    # Split the triplicated image files into batches
    batches3 = [image_files[i:i + batch_size] for i in 
               range(0, len(image_files), batch_size)]
    batches = batches1 + batches2 + batches3
    
    # Generate full paths for each batch
    batch_paths = [[os.path.join(folder_path, image) for image in batch] for batch in batches]
    return batch_paths

# Example usage:
folder_path = 'sample_images'
batch_size = 5
result = generate_batches_from_folder(folder_path, batch_size)

image_path = []
nxt_page = False
user = ""


def link_user_to_pics(username):
    df_users = pd.DataFrame()
    pics = get_pictures(username)
    df_users['pictures'] = json.loads(pics.replace('\'', '"'))
    df_users['username'] = username
    df_users['Category'] = None
    df_users['Level'] = None
    print(df_users)
    global image_path
    image_path=df_users['pictures']
    df_users.to_csv(f"ratings_{username}.csv", index=False)
    return True

def get_pictures(username):
    df = pd.read_csv("batches.csv")
    first_empty_index = (df['username'].isna() | (df['username'] == '')).idxmax()
    df.at[first_empty_index, 'username'] = username
    df.to_csv("batches.csv", index=False)
    return df.at[first_empty_index, 'batch']
    # for index, row in df.iterrows():
    #     if any(row):
    #         df.at[index, 'username'] = username
    #         df.to_csv("batches.csv", index=False)
    #         print(row['batch'])
    #         return row['batch']



def next_page(username):
    global nxt_page
    global user
    user = username
    if (len(username)>0) & (len(username)<12):
        nxt_page = True
        return gr.Button(interactive=True, value="Continue")
    return gr.Button(interactive=False, value="Continue")
    
    


with gr.Blocks() as introduction:
    gr.Markdown(
    """
    # Introduction
    Hello and welcome to our study! Our goal is to create a dataset of realistic images of faces 
    generated by artificial intelligence. Most AI-generated images contain at least small mistakes.
    We want to assign a category and a level of mistake to each image. In this study you will be presented 
    with different images with varying degrees of mistakes. For some mistakes you may need to zoom in on 
    the picture. There are five different mistake categories:
    * Alignment Problem
    * Incorrect Proportions
    * Number of features
    * Wrong Aspects
    * Unrealistic
    
    Enter a username and press continue to see some examples of images and their categories.
    """)
    username = gr.Textbox(placeholder="Username", label="Enter any username", max_lines=1)
    nxt_page = gr.Button(interactive=False, value="Continue")
    username.change(next_page, username, nxt_page)
    nxt_page.click(link_user_to_pics, inputs=username)


"""
Here starts the part for training/examples section
"""


# Load the CSV file
df = pd.read_csv('./training_images_log.csv')

# Grouping image paths by category
category_to_images = df.groupby('category')['image_path'].apply(list).to_dict()

#dictionary mapping image paths to explanations
image_to_explanation = dict(zip(df['image_path'], df['explanation']))

#dict mapping of image path to prompt
image_to_prompt = dict(zip(df['image_path'], df['prompt']))

#slider for level of mistake (needs to be put as an image)

# Dictionary to keep track of the last shown image index for each category
last_shown = {category: 0 for category in category_to_images}

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
        image_paths = category_to_images[category]
        # Check if there are images in the category
        if not image_paths:
            return None  # Or return a default image if there are no images
        # Get the index of the next image to show
        next_index = (last_shown[category] + 1) % len(image_paths)
        last_shown[category] = next_index  # Update the last shown index
        #explain_text=f"Displaying image {next_index + 1} of {len(image_paths)} for category '{category}'"
        # Get the image path and display the image
        image_path = image_paths[next_index]
        explanation= image_to_explanation.get(image_path,"No explanation available")
        prompt=image_to_prompt.get(image_path,"No prompt available")
        return image_load(image_path),prompt,explanation

    else:
        return None  # Or return a default image if the category is not found

# Unique categories for dropdown
categories = df['category'].unique().tolist()


with gr.Blocks() as training:
    gr.Markdown(
    """
    # Training phase
    In this phase we look at 2 examples from each of the 6 categories. You need to select one of the below radio buttons to see the examples.  
    1 - Alignment Problem  
    2 - Correct Image  
    3 - Incorrect Proportion  
    4 - Number of Features  
    5 - Wrong Aspects  
    6 - Unrealistic
    """
    )
   # choices=["Aligmment Problem", "Correct Image","Incorrect Proportion","Number of Features","Wrong Aspects","Unrealistic"]
    radio=gr.Radio(choices=categories,label="Category of Mistake",info="Please choose 1 category from the 6 options below")
    #radio=gr.Radio(choices=categories,label="Category of Mistake",info="Choose an option from 1-6 to look at a category example")
    with gr.Row(): 
     output_image=gr.ImageEditor(height=576,width=416)
     output_text1=gr.Text(label="Prompt")
     output_text2=gr.Text(label="Explanation about Category Choice")
    radio.change(fn=show_image, inputs=[radio], outputs=[output_image,output_text1,output_text2])



"""
Here starts the part for the main study
"""


# Initial index for displaying the first image
current_index = 0
# Function to update the displayed image and category
def update_data():
    data_array = pd.read_csv("ratings_" + user + ".csv")
    global current_index
    current_index = (current_index + 1) % len(data_array)
    img_path = data_array['pictures'][current_index]#, data_array[current_index]["category"]
    img = Image.open(img_path)
    return img
    
def save_rating(radio, slider):

    path = "ratings_" + user + ".csv"
    df = pd.read_csv(path)
    categories_radio = gr.Radio(visible=False)
    slider = gr.Slider(visible=False)
    df.loc[df['pictures']==image_path[current_index],['Category']] = radio
    df.loc[df['pictures']==image_path[current_index],['Level']] = slider

    df.to_csv(path, header=True, index=False)

    return update_data(), categories_radio, slider

   
def display_categories():

    categories_radio = gr.Radio(["Alignment Problems", "Incorrect proportions", "Number of features", "Wrong Aspects", "unrealistic"], interactive=True, visible=True) 
    slider = gr.Slider(minimum=0, maximum=5, step=1, interactive=True, visible=True)
    outputs = [categories_radio, slider]
    return outputs


with gr.Blocks() as main:
    gr.Markdown(
        """
        # Main study
        
        """)
    with gr.Column():
        gr.Textbox(label="Promt", value="this is the promt")
        with gr.Row():

            
            image = gr.ImageEditor(height=576,width=416)
        
            
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

                
                submit_button = gr.Button("Submit")
    
        
             
    
    
    no_button.click(fn=update_data, inputs=[], outputs=[image])

    submit_button.click(
        fn=save_rating,
        inputs=[categories_radio, slider],
        outputs=[image, categories_radio, slider]
    )
    


demo = gr.TabbedInterface([introduction, training, main], ["Introduction", "Examples", "Main Study"])

demo.launch(inbrowser=True)
    