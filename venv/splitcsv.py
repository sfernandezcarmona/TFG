import pandas as pd
import csv

# Define the path to the input CSV file

csv.field_size_limit(1000000000)

input_file_path = "D:/Descargas/news.csv/news_cleaned_2018_02_13.csv"

# Define the path to the output CSV files
output_file_paths = [
    "D:/Descargas/news.csv/file1.csv",
    "D:/Descargas/news.csv/file2.csv",
    "D:/Descargas/news.csv/file3.csv",
    "D:/Descargas/news.csv/file4.csv",
]

# Define the number of rows to process at a time
chunk_size = 70000

# Create a Pandas DataFrame iterator for the input CSV file
input_iterator = pd.read_csv(input_file_path, chunksize=chunk_size, engine="python")

# Loop over the input DataFrame iterator and split the data into four parts
for i, chunk in enumerate(input_iterator):
    # Calculate which output file to write the chunk to
    output_file_index = i % 4
    output_file_path = output_file_paths[output_file_index]

    # Write the chunk to the output file
    with open(output_file_path, "a", newline="",encoding="utf-8") as f:
        chunk.to_csv(f, index=False)
