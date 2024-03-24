from datetime import datetime
import time


mode=''

if mode=='notool':
    from proc_j_no_tools import *
else:
    from proc_j import *

full_out='\n\n\n\n'

# Get Date
current_date = datetime.now()
formatted_date = f"{current_date.strftime('%Y')[2:]}W{str(int(current_date.strftime('%U'))+1).zfill(2)}"

# Prepare Dataset
dataset,out_buf=chatGPT_proc('chats')
cleaned_dataset=cleanDS(dataset)

full_out+=f'Dataset Main:\n{out_buf}\n\n'

#Write Dataset
s=open(f'gpt_{formatted_date}.txt','w',encoding='utf-8')
s.write(cleaned_dataset)

s.close()
