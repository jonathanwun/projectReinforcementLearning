'''
import pandas as pd
import numpy as np
from scipy.stats import ttest_rel, wilcoxon
import matplotlib.pyplot as plt
import seaborn as sns

# data from demo Phase 
phase_1_data = {
    'category': ['Number of Features', 'No Errors', 'Unrealistic', 'Incorrect Proportion', 'Alignment Problem', 'Wrong Aspect'],
    'average_level': [3.61, 0.0, 3.272 , 1.708,1.638, 3.125],
    'std_dev': [ 0.892, 0.0,0.987,  0.534, 0.561,0.629],
    'num_images': [9, 12 ,16,4 , 6, 4]
}

# Convert to DataFrame
df_phase_1 = pd.DataFrame(phase_1_data)

# Normalizing the average levels using Min-Max Normalization
min_level = df_phase_1['average_level'].min()
max_level = df_phase_1['average_level'].max()

df_phase_1['normalized_level'] = (df_phase_1['average_level'] - min_level) / (max_level - min_level)

# data from final Phase 
phase_2_data = {
   'category': ['Number of Features', 'No Errors', 'Unrealistic', 'Incorrect Proportion', 'Alignment Problem', 'Wrong Aspect'],
   'average_level' : [2.9, 0.0, 3.083, 1.786, 1.544, 1.778],
   'std_dev' : [0.945, 0.0, 0.888, 0.513, 0.709, 0.575],
  'num_images' : [15, 35, 70, 14, 15, 6]
}

# Convert to DataFrame
df_phase_2 = pd.DataFrame(phase_2_data)

min_level_2 = df_phase_2['average_level'].min()
max_level_2 = df_phase_2['average_level'].max()
# Normalizing the average levels for Phase 2 using the same min-max range as Phase 1
df_phase_2['normalized_level'] = (df_phase_2['average_level'] - min_level_2) / (max_level_2 - min_level_2)

# Merge the two DataFrames on the 'category' column
comparison_df = pd.merge(
    df_phase_1[['category', 'normalized_level']],  # Selecting category and normalized level from phase 1
    df_phase_2[['category', 'normalized_level']],  # Selecting category and normalized level from phase 2
    on='category',  # Merging on the 'category' column
    suffixes=('_phase_1', '_phase_2')  # Adding suffixes to distinguish columns from the two DataFrames
)

# Calculate the difference in normalized levels between Phase 1 and Phase 2
comparison_df['level_difference'] = comparison_df['normalized_level_phase_2'] - comparison_df['normalized_level_phase_1']

print("Comparison of Normalized Levels with Differences:")
print(comparison_df)

# Paired t-test
t_stat, p_value = ttest_rel(comparison_df['normalized_level_phase_1'], comparison_df['normalized_level_phase_2'])
print(f"Paired t-test: t-statistic = {t_stat}, p-value = {p_value}")

# Wilcoxon signed-rank test
w_stat, p_value_wilcoxon = wilcoxon(comparison_df['normalized_level_phase_1'], comparison_df['normalized_level_phase_2'])
print(f"Wilcoxon signed-rank test: statistic = {w_stat}, p-value = {p_value_wilcoxon}")

# Bar plot comparison
plt.figure(figsize=(12, 6))
comparison_df.plot(kind='bar', x='category', y=['normalized_level_phase_1', 'normalized_level_phase_2'], 
                   title='Normalized Error Levels Comparison per Category', 
                   ylabel='Normalized Error Level', xlabel='Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Difference plot
plt.figure(figsize=(12, 6))
sns.barplot(x='category', y='level_difference', data=comparison_df)
plt.title('Difference in Normalized Levels between Phase 1 and Phase 2')
plt.xlabel('Category')
plt.ylabel('Difference in Normalized Level (Phase 2 - Phase 1)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
'''

import numpy as np
from scipy.stats import spearmanr

# Average levels from both tables
table1_avg = [3.083, 2.9, 1.778, 0.0, 1.544, 1.786]
table2_avg = [3.272, 3.610, 3.125, 0.0, 1.638, 1.708]

# Calculate Spearman's correlation
correlation, p_value = spearmanr(table1_avg, table2_avg)
print(f"Spearman's correlation: {correlation}, p-value: {p_value}")