import pandas as pd
import gradio as gr
import os
import random
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

folder_path = 'alpha_study_60_img'
batch_size = 20
result = generate_batches_from_folder(folder_path, batch_size)
df_batches = pd.DataFrame()
df_batches['batch'] = result
df_batches['username'] = ''
df_batches.to_csv("batches.csv", index=False)