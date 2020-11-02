from pathlib import Path
import subprocess

def fill_na(df_file):
    filter_col = [col for col in list(df_file) if col.startswith(('mc'))]
    filter_col1 = [col for col in list(df_file) if col.startswith(('h'))]
    df=df_file[filter_col]
    df=df.bfill(axis=1).ffill(axis=1)
    df_file[filter_col]
    df_file[filter_col]=df
    df_file[filter_col]=df_file[filter_col].astype(int)
    
    df=df_file[filter_col1]
    df=df.bfill(axis=1).ffill(axis=1)
    df_file[filter_col1]=df
    df_file[filter_col1]=df_file[filter_col1].astype(int)
    return df_file


def process_frame_withR(file1):
    com=f"Rscript {Path(__file__).parent.absolute()}/HOME_R_time.R" + " "+file1
    subprocess.call(com, shell=True)


def chunker1(seq, sizes):
    idx=0
    for s in sizes:
        k=seq[idx:idx+s]
        idx=idx+s
        yield k

def smoothing(*a):
    
    import numpy as np
    
    avg_value=[]
    for i in range(len(a)):
        if np.sign(i-1)==-1:
            p=0
        else:
            p=a[i-1]
        if i+1==len(a):
            n=0
        else:
            n=a[i+1]
        avg_value.append(np.divide(float(p+a[i]+n),3))
        
    return avg_value  

def chunker(seq, size):
  
   for pos in range(0, len(seq), size):
    
    start_df=max(0,pos-25)
    start=max(0,pos)
    stop_df=min(len(seq),pos+size+25)
    stop=min(len(seq),((pos+size)-1))
    k=seq[start_df:stop_df]
    
  
    yield (k,start,stop)        


