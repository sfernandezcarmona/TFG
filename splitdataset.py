import pandas as pd
import math
import csv

csv.field_size_limit(1000000000)
def split_csv_by_percentage(input_file_path, output_file_paths, percentage):
    # Define the number of rows to process at a time
    chunk_size = 70000

    # Create a Pandas DataFrame iterator for the input CSV file
    input_iterator = pd.read_csv(input_file_path, chunksize=chunk_size, engine="python")

    # Calculate the total number of rows in the input CSV file
    num_rows = sum(1 for _ in pd.read_csv(input_file_path, chunksize=chunk_size, engine="python"))

    # Calculate the number of rows to write to the first output file
    num_rows_file1 = math.ceil(num_rows * percentage)

    # Initialize counters for the number of rows written to each output file
    num_rows_written_file1 = 0
    num_rows_written_file2 = 0

    # Loop over the input DataFrame iterator and split the data into two parts
    for chunk in input_iterator:
        # Determine which output file to write the chunk to
        if num_rows_written_file1 < num_rows_file1:
            output_file_path = output_file_paths[0]
            num_rows_written_file1 += len(chunk)
        else:
            output_file_path = output_file_paths[1]
            num_rows_written_file2 += len(chunk)

        # Write the chunk to the output file
        with open(output_file_path, "a", newline="", encoding="utf-8") as f:
            chunk.to_csv(f, index=False)

        # Calculate and print the percentage of rows processed
        percent_complete = (num_rows_written_file1 + num_rows_written_file2) / num_rows * 100
        print(f"{percent_complete:.2f}% complete", end="\r")



input_file_path = "D:/Descargas/news.csv/verdaderas.csv"
split_percentage = 80
output_file_paths = ["D:/Descargas/news.csv/verdaderastest.csv","D:/Descargas/news.csv/verdaderastrain.csv"]
split_csv_by_percentage(input_file_path, output_file_paths, split_percentage)