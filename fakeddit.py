import pandas as pd
import os
import csv

file_paths = [
    "D:/Descargas/news.csv/file1.csv",
    "D:/Descargas/news.csv/file2.csv",
    "D:/Descargas/news.csv/file3.csv",
    "D:/Descargas/news.csv/file4.csv",
]

csv.field_size_limit(1000000000)
chunk_size = 85000
for file in file_paths:
    # Get the total file size and number of rows in the input file
    file_size = os.path.getsize(file)
    dtf = pd.read_csv(file, engine='python', iterator=True)
    # Read the input file in chunks and write each chunk to a new CSV file
    dtf = pd.read_csv(file, engine='python', chunksize=chunk_size)
    cuantolleva = 0
    for chunk_idx, chunk in enumerate(dtf):
        # Filter out rows that do not have type "fake" or "credible"
        fake_chunk = chunk.loc[chunk['type'] == 'fake']
        credible_chunk = chunk.loc[chunk['type'] == 'reliable']

        # Get chunk sizes and total number of rows processed so far
        total_rows = (chunk_idx * chunk_size)
        cuantolleva = chunk.memory_usage().sum() + cuantolleva
        # Calculate percentage of done
        percent_done = (chunk_idx / (25)) * 100
        print(f"Processed {percent_done:.2f}% of the input file. ("+str(chunk_idx) + "/"+str(25)+")")

        # Write filtered chunks to separate CSV files
        fake_output_file = "D:/Descargas/news.csv/falsas.csv"
        fake_chunk.to_csv(fake_output_file, mode='a', index=False, header=not os.path.exists(fake_output_file), encoding="utf-8")

        credible_output_file = "D:/Descargas/news.csv/verdaderas.csv"
        credible_chunk.to_csv(credible_output_file, mode='a', index=False, header=not os.path.exists(credible_output_file), encoding="utf-8")

    print(f"Processed {chunk_idx + 1} chunks in total.")
