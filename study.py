import gradio as gr
import pandas as pd
from PIL import Image

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

#iface = gr.Interface(fn=show_image, inputs=gr.Dropdown(choices=categories), outputs="image")
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
    

#demo = gr.Interface(training, "Training")  
#iface = gr.Interface(fn=show_image, inputs=gr.Radio(choices=categories,label="Category of Mistake",info="Choose an option from 1-6 to understand each category"), outputs=["image","text","text"])
#iface.launch()  
training.launch()
