from datetime import datetime
import time
import os

def procGPT(path,save_path):
    full_out='\n\n\n\n'

    # Get Date
    current_date = datetime.now()
    formatted_date = f"{current_date.strftime('%Y')[2:]}W{str(int(current_date.strftime('%U'))+1).zfill(2)}"

    # Prepare Dataset
    dataset,out_buf=chatGPT_proc(path)
    cleaned_dataset=cleanDS(dataset)

    for i in range(200):
        cleaned_dataset=cleaned_dataset.replace(f'【{i}†source】','')
        cleaned_dataset=cleaned_dataset.replace('\n\n\n','\n\n')


    full_out+=f'Dataset Main:\n{out_buf}\n\n'

    #Write Dataset
    s=open(f'{save_path}_{formatted_date}.txt','w',encoding='utf-8')
    s.write(cleaned_dataset)

    s.close()
    os.remove("final_output.json")

def proc_ez(root,model):
    procGPT(f"in/{root}/{model}",f"ds/{root}_{model}")

mode=''
if mode=='notool':
    from proc_j_no_tools import *
else:
    from proc_j import *


proc_ez("private","gpt4")
proc_ez("public","gpt3")
proc_ez("public","gpt4")