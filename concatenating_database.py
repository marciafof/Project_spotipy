import os
import glob
import pandas as pd

data_path = "data"
files_path = f"{data_path}/by_genre"

#%%Searching for files recursively (because of the genre folders)
list_of_dfs = []
for f in glob.glob(f"{files_path}/**/*.csv", recursive=True):
    print(f)
    list_of_dfs.append(pd.read_csv(f))
df_by_genre = pd.concat(list_of_dfs,axis=0)
df_by_genre.to_csv(data_path + "/songs_by_genre.csv",index=False)