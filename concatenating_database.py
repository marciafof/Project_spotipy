#%%
import os
import glob
import pandas as pd
import pandas.io.common 

data_path = "data"
files_path = f"{data_path}/by_genre"

#%%Searching for files recursively (because of the genre folders)
concat_by_genre = True
if concat_by_genre:
    print(f"Concatenating files inside by_genre directory and subfolders")
    list_of_dfs = []
    for file_ in glob.glob(f"{files_path}/**/*.csv", recursive=True):
        print(file_)
        list_of_dfs.append(pd.read_csv(file_))
    df_by_genre = pd.concat(list_of_dfs,axis=0)
    nduplicates = df_by_genre[df_by_genre.duplicated(subset="id")].shape[0]
    print(f"Number of duplicated track id's is {nduplicates}")
    df_by_genre.drop_duplicates(subset="id",inplace=True)
    df_by_genre.to_csv(data_path + "/songs_by_genre.csv",index=False)

#%% Searching for all csv files for playlists
concat_by_playlists = True
if concat_by_playlists:
    print(f"Concatenating files inside by_playlist directory")
    files_path = f"{data_path}/by_playlist"
    list_of_dfs = []
    for file_ in glob.glob(f"{files_path}/*.csv", recursive=True):
        try:
            print(file_)
            list_of_dfs.append(pd.read_csv(file_))
        except pandas.errors.EmptyDataError:
            print(f"Empty data file :{file_}")
            continue

    all_playlists_df = pd.concat(list_of_dfs)
    nduplicates = all_playlists_df[all_playlists_df.duplicated(subset="id")].shape[0]
    print(f"Number of duplicated track id's is {nduplicates}")
    all_playlists_df.drop_duplicates(subset="id",inplace=True)
    all_playlists_df.to_csv(data_path + "/songs_by_our_playlists.csv",index=False)
# %%ADD songs dowloaded from other sources and combine by genre
fname_1 = data_path +"/songs_by_genre.csv"
fname_2 = data_path +"/songs_by_our_playlists.csv"
fname_3 = data_path +"/miscellaneous_songs_2018.csv"
lists_of_fnames = [fname_1,fname_2,fname_3]
list_of_dfs = []
for fname_ in lists_of_fnames:
    print(f"Opening file {fname_}")
    list_of_dfs.append(pd.read_csv(fname_))
final_df = pd.concat(list_of_dfs)
nduplicates = final_df[final_df.duplicated(subset="id")].shape[0]
print(f"Number of duplicated track id's is {nduplicates}")
final_df.drop_duplicates(subset="id",inplace=True)
print(f"Final number of rows in dataframe is {final_df.shape[0]}")
final_df.to_csv(data_path + "/all_songs_attributes.csv",index=False)