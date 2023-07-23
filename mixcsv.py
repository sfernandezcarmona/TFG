import pandas as pd
from tqdm import tqdm
import os
tqdm.pandas()
# Define a list of CSV file names to be concatenated
csv_files = ["D:/Descargas/news.csv/verdaderastest.csv", "D:/Descargas/news.csv/verdaderastrain.csv", "D:/Descargas/news.csv/faketest.csv","D:/Descargas/news.csv/faketrain.csv"]  # Add more file names as needed

# Initialize an empty list to store the processed chunks
processed_chunks = []

# Process CSV files in chunks
for file in csv_files:
    chunk_size = 10000  # Set the chunk size according to your memory capacity
    file_size = os.path.getsize(file)
    total_chunks = file_size // chunk_size + 1

    chunk_generator = pd.read_csv(file, chunksize=chunk_size)

    for chunk in tqdm(chunk_generator, total=total_chunks, desc=f"Processing {file}"):
        # Add 'label' column based on 'type' column
        chunk['label'] = chunk['type'].map({'fake': 0, 'reliable': 1})

        processed_chunks.append(chunk)

# Concatenate the processed chunks into a single DataFrame
df_concatenated = pd.concat(processed_chunks)

# If you want to mix the rows randomly, uncomment the following line
# df_concatenated = df_concatenated.sample(frac=1).reset_index(drop=True)

# Output the concatenated and processed dataframe to a new CSV file
df_concatenated.to_csv("D:/Descargas/news.csv/dataset.csv", index=False)

print("CSV files concatenated, processed, and saved as combined.csv.")