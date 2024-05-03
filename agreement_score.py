import pandas as pd
import matplotlib.pyplot as plt

file_path="./merged_csv_9.csv"

data=pd.read_csv(file_path)
print(len(data))

#function to decide on agreement_score for the slider input
def agreed_level_score(diff):
    if (diff == 0).all():  # If all differences are 0
        agreement_score_level = 1.0
    elif ((diff > 0) & (diff <= 1)).all():  # If all differences are 1
        agreement_score_level = 0.75
    elif ((diff > 1) & (diff <= 2)).all():  # If all differences are 2
        agreement_score_level = 0.50
    elif ((diff > 2) & (diff<=3)).all():  # If all differences are 3
        agreement_score_level = 0.25
    else:  # If any difference is more than 3
        agreement_score_level = 0.0
    return agreement_score_level
            
count_correct_categories = 0
count_no_category = 0

unique_images=data['pictures'].unique()
print(len(unique_images))

duplicates = data['pictures'].value_counts()
print(duplicates)

cat_count = data['Category'].value_counts()
#maximum selected category
max_cat=cat_count.idxmax()

#minimum selected category
min_cat=cat_count.idxmin()

print (f"Maximum selected category is : {max_cat}")

print (f"Minimum selected category is : {min_cat}")

new_data=[]
for picture in unique_images:
    
    # Filter the DataFrame for rows with the current "pictures" value
    rows_for_picture = data[data['pictures'] == picture]
    
    # Check if there are exactly three rows for this picture
    if len(rows_for_picture) == 3:
        # Get the unique categories for this picture
        unique_cat_pic = rows_for_picture['Category'].unique()
        unique_count = rows_for_picture['Category'].value_counts()
        #print(f"unique cats{unique_categories}")
        #print(f"unique counts{unique_count}")

        # If there is exactly one unique category, print the details
        if len(unique_cat_pic) == 1:
            print(f"Image: {picture}")
            print(f"Category: {unique_cat_pic[0]}")
            print("---all 3 agree----")
            count_correct_categories += 1
            agreed_category = unique_cat_pic[0]
            agreement_score_cat = 1.0  # Since all three are the same
            level_values = rows_for_picture['Level']
            #print(f"level{level_values}")
            #taking average of the levels
            level_diff = level_values.diff().abs().dropna()
            diff_first_third = abs(level_values.iloc[2] - level_values.iloc[0])
            differences = pd.concat([pd.Series([diff_first_third]), level_diff], ignore_index=True)
            #average of the differences value
            avg_diff=round(differences.mean(),1)
            print(avg_diff)
            agreement_score_level=agreed_level_score(avg_diff)
            print(f"level diff : {differences}")
            #average level
            avg_level = level_values.mean()
            agreed_level=avg_level.round(2)

        else:
            
            # If there are multiple categories, select the one with the highest count
            max_count_category = unique_count.idxmax()
            max_count = unique_count.max()
            filtered_rows = rows_for_picture[rows_for_picture['Category'] == max_count_category]
            print(f"filtered_row : {filtered_rows}")
            # Check if there are conflicting categories with the same count
            if (unique_count == max_count).sum() == 1:
                print(f"Image: {picture}")
                print(f"Category: {max_count_category}")
                print("---2 out of 3 agree---")
                count_correct_categories += 1
                agreed_category = max_count_category
                agreement_score = max_count / 3  # Divide by 3 for 3 repetitions
                agreement_score_cat=round(agreement_score,2)
                #do double conditioning with the level and the category
                if not filtered_rows.empty:  
                    #taking average of the levels
                    avg_level = filtered_rows['Level'].mean()
                    agreed_level=avg_level.round(2)
                    level_diff = filtered_rows['Level'].diff().abs().dropna()
                    print(f"level_diff{level_diff}")
                    agreement_score_level=agreed_level_score(level_diff) 
            else:
                print(f"Image: {picture}")
                print("Conflicting Categories")
                print("---")
                count_no_category += 1
                agreed_category = None
                agreement_score_cat = 0.0
                agreed_level= None
                agreement_score_level=0.0
          

        new_data.append({
            'pictures': picture,
            'agreed_category': agreed_category,
            'agreement_score_category': agreement_score_cat,
            'level_average':agreed_level,
            'agreement_score_level':agreement_score_level
        })


# Step 4: Create a new DataFrame with the new data
new_df = pd.DataFrame(new_data)

# Step 5: Save the new DataFrame to a new CSV file
new_csv_file = "./unique_images_with_agreement.csv"

new_df.to_csv(new_csv_file, index=False)

modified_data =pd.read_csv(new_csv_file)
avg_lvls={}
std_lvls={}
count_pics_cat={}

def category_agreement():
    unique_category=modified_data['agreed_category'].dropna().unique()

    for cat in unique_category:
        rows_images_cat=modified_data[modified_data['agreed_category']==cat]
        count_pic_cat=len(rows_images_cat)
        avg_lvl=rows_images_cat['level_average'].mean().round(3)
        std_dev_lvl=rows_images_cat['level_average'].std()
        avg_lvls[cat]=avg_lvl
        std_lvls[cat]=round(std_dev_lvl,3)
        count_pics_cat[cat]=count_pic_cat
    print(f"Average level per category {avg_lvls}")   
    print(f"Standard deviation of level per category {std_lvls}")   
    print(f"# images per category {count_pics_cat}")   
    #ploting number of images per category
    categories=list(count_pics_cat.keys())
    counts=list(count_pics_cat.values())
    plt.figure(figsize=(10, 6))  # Optional: Adjusts the figure size
    plt.bar(categories, counts, color='skyblue')  # You can choose any color
    plt.title('Number of Images per Category')
    plt.xlabel('Categories')
    plt.ylabel('Number of Images')
    plt.xticks(rotation=45)  # Rotates labels to prevent overlapping
    plt.tight_layout()  # Adjusts subplots to give some padding
    plt.show()
    

#function to find the average per category, std deviation between values of levels per category, number of images per category
category_agreement()

print(f"New CSV file with unique images and agreement details saved to: {new_csv_file}")

print(f"Count of images with agreement on Category : {count_correct_categories}")

print(f"Count of images with no agreement : {count_no_category}")