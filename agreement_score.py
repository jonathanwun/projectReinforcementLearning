import pandas as pd

file_path="./merged_csv_9.csv"
data=pd.read_csv(file_path)
print(len(data))

#function to decide on agreement_score for the slider input
def agreed_level_score(diff):
    if (diff == 0).all():  # If all differences are 0
        agreement_score_level = 1.0
    elif (diff == 1).all():  # If all differences are 1
        agreement_score_level = 0.75
    elif (diff == 2).all():  # If all differences are 2
        agreement_score_level = 0.50
    elif (diff == 3).all():  # If all differences are 3
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
        unique_categories = rows_for_picture['Category'].unique()
        unique_count = rows_for_picture['Category'].value_counts()
        #print(f"unique cats{unique_categories}")
        #print(f"unique counts{unique_count}")

        # If there is exactly one unique category, print the details
        if len(unique_categories) == 1:
            print(f"Image: {picture}")
            print(f"Category: {unique_categories[0]}")
            print("---all 3 agree----")
            count_correct_categories += 1
            agreed_category = unique_categories[0]
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

print(f"New CSV file with unique images and agreement details saved to: {new_csv_file}")

print(f"Count of images with atleast 2 agreements out of 3 {count_correct_categories}")

print(f"Count of images with no agreement {count_no_category}")