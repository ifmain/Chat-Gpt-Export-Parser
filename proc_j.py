from math import fabs
import os
from os import listdir
from os.path import isfile, join
import json
from datetime import datetime

def print_dialog_tree(dialog, conv, visited=None, indent=0):
    if visited is None:
        visited = set()
    if id(dialog) in visited:
        return
    visited.add(id(dialog))
    for msg in dialog:
        if msg['children']:
            for child_id in msg['children']:
                child_dialog = next((d for d in conv if d[0]['id'] == child_id), None)
                if child_dialog:
                    print_dialog_tree(child_dialog, conv, visited, indent + 2)

def process_conversations(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        f = json.load(file)
    all_conversations = []
    for conversation in f:
        conv = []
        for msg_id in conversation['mapping']:
            msg = conversation['mapping'][msg_id]
            conv.append(msg)
        all_conversations.append(conv)
    dataset = []
    for dialog in all_conversations:
        print_dialog_tree(dialog, all_conversations)
        dataset.append(dialog)
    return dataset

def prepareData(dir_path):
    final_dataset = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file == 'conversations.json':
                file_path = os.path.join(root, file)
                conv_data = process_conversations(file_path)
                final_dataset.extend(conv_data)
    # Сохранение итогового результата
    with open('final_output.json', 'w', encoding='utf-8') as out_file:
        json.dump(final_dataset, out_file, ensure_ascii=False, indent=4)


def getText(msg):
    text=None
    texts=msg['content'].get('parts')
    #print(texts)
    out=[]
    if texts==None:
        text=msg['content'].get('text')
    else:
        if type(texts)==type([]):
            for a in texts:
                if type(a)==type(""):
                    out.append(a)
                else:
                    content_type=a.get('content_type')
                    if content_type!=None:
                        if content_type:
                            if (a['content_type']=='image_asset_pointer'):
                                return False,'Image detector'
                        else:
                            #print('Error',content_type)
                            exit()
                text=" ".join(out)
        elif type(texts[0])==type(""):
            text="".join(texts).replace('\r','').replace('\n\n','\n').replace('\n\n','\n').replace('\n\n','\n')
            # In the current version of ChatGPT OpenAi Export Api (10.11.23) there is nothing interesting in type!=text
        else:
            print("\n\n\n",text,"n\n\n")
    if text==None:
        text=msg['content'].get('result')

    if text!=None:
        return True,"".join(out)
    else:
        return True,''


def cleanDS(dataset):
    file_dw=open('remove_word.json',encoding='UTF-8')
    denyword=json.load(file_dw)
    file_dw.close()
    xx=[]
    for a in dataset.split(' '):
        for b in denyword:
            a=a.replace(b[0],b[1])
        
        xx.append(a)
    xx=" ".join(xx)
    xx=xx.split('\n')
    return "\n".join(xx)

def appendAU(msgs_counter,Allow_collect_after,x1,u_up,info):
    if Allow_collect_after:
        if u_up[0]:
            x1.append(u_up[1])
            u_up=False,''
        x1.append(info)
        msgs_counter={'used':msgs_counter['used']+1,'unused':msgs_counter['unused'],'not_allowed':msgs_counter['not_allowed'],'passed_space':msgs_counter['passed_space']}
    else:
        msgs_counter={'used':msgs_counter['used'],'unused':msgs_counter['unused']+1,'not_allowed':msgs_counter['not_allowed'],'passed_space':msgs_counter['passed_space']}
    return x1,u_up,msgs_counter

file_dalle=open('dall-e.jsonl','w',encoding='UTF-8')


def assistantProc(msgs_counter,m,x1,autor,text,Allow_collect_after,Allow,u_up,stupid_stop_stat,msg):
    if text!='':
        if (autor=='assistant') and ('{\n  \"prompts\": [' in text):
            x1,u_up,msgs_counter = appendAU(msgs_counter,Allow_collect_after,x1,u_up,json.dumps({"role":autor,"text":{"dall-e":text }},ensure_ascii=False))
            x0p=[]
            for a in x1:
                x0p.append(json.loads(a))
            file_dalle.write(json.dumps(x0p,ensure_ascii=False)+'\n')
        else:
            if text!='':
                if text[-1]=='.':
                    x1,u_up,msgs_counter = appendAU(msgs_counter,Allow_collect_after,x1,u_up,json.dumps({"role":autor,"text":text},ensure_ascii=False))
                elif text[-1]=='!':
                    x1,u_up,msgs_counter = appendAU(msgs_counter,Allow_collect_after,x1,u_up,json.dumps({"role":autor,"text":text},ensure_ascii=False))
                elif text[-1]=='?':
                    x1,u_up,msgs_counter = appendAU(msgs_counter,Allow_collect_after,x1,u_up,json.dumps({"role":autor,"text":text},ensure_ascii=False))
                else:
                    pass
                    Allow_collect_after=False
                    stupid_stop_stat=True
    else:
        msgs_counter={'used':msgs_counter['used'],'unused':msgs_counter['unused'],'not_allowed':msgs_counter['not_allowed'],'passed_space':msgs_counter['passed_space']+1}

    return x1,Allow,Allow_collect_after,stupid_stop_stat,u_up,msgs_counter

def userProc(msgs_counter,m,x1,autor,text,Allow_collect_after,Allow,u_up,stupid_stop_stat,msg):
    if text!='':
        u_up=True,json.dumps({"role":autor,"text":text},ensure_ascii=False)
    else:
        msgs_counter={'used':msgs_counter['used'],'unused':msgs_counter['unused'],'not_allowed':msgs_counter['not_allowed'],'passed_space':msgs_counter['passed_space']+1}
    return x1,Allow,Allow_collect_after,stupid_stop_stat,u_up,msgs_counter

def toolProc(msgs_counter,m,x1,autor,text,Allow_collect_after,Allow,u_up,stupid_stop_stat,msg):
    if text!='':
        if Allow_collect_after:
            if u_up[0]:
                x1.append(u_up[1])
                u_up=False,''
            plug_name=msg['author']['name']
            if plug_name in ['code_repo_interaction.callOctokitMethod',
                                         'repo_inspector.inspectFile',
                                         'repo_inspector.inspectFolder',
                                         'Ai_PDF.summarize_pdf',
                                         'Ai_PDF.upload_and_search_pdf',
                                         'MixerBox_ChatVideo_YouTube_video_summarizer.searchVideo',
                                         'MixerBox_ChatVideo_YouTube_video_summarizer.queryVideo']:
                Allow=False
            elif plug_name=='myfiles_browser':
                #print(msg)
                #x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':msg['content']['text'] }},ensure_ascii=False))
                Allow=False
            else:
                
                if plug_name=='python':
                    try:
                        x1.append(json.dumps({"role":'python',"text":msg['metadata']['aggregate_result']['code']},ensure_ascii=False))
                    except:
                        Allow=False
                elif plug_name=='dalle.text2im':
                    x1.append(json.dumps({"role":'dall-e',"text":text},ensure_ascii=False))
                    #print('Dall-e',Allow)
                    if text=='DALL·E returned some images. They are already displayed to the user. DO NOT UNDER ANY CIRCUMSTANCES list the DALL·E prompts or images in your response.':
                        pass
                    elif 'content policy' in text: 
                        pass
                    elif '''DALL·E experienced an error when generating images.Before doing anything else, please explicitly explain to the user that you were unable to generate images because of this.''' in text:
                        pass
                    elif "You're generating images too quickly." in text:
                        pass
                    elif "DALL·E is currently experiencing high demand." in text:
                        pass
                elif plug_name=='browser':
                    Allow=False
                    # The Bing browser is very buggy and I'm too lazy to do it (but the code below for parsing works) (is code to old BING brower - before update on 2023)
                    '''
                    if msg['content'].get('result')!=None:
                        x1.append(json.dumps({"role":'browser-bing',"text":{'status':msg['metadata']['status'],'text':msg['content']['result']}},ensure_ascii=False))
                    elif msg['content'].get('text')!=None:
                        if msg['content']['content_type']=='tether_quote':
                            x1.append(json.dumps({"role":'browser-bing',"text":{'status':msg['metadata']['status'],'text':msg['content']['text']}},ensure_ascii=False))
                        elif msg['content']['content_type']=='system_error':
                            x1.append(json.dumps({"role":'browser-bing',"text":{'status':'system_error','text':''}},ensure_ascii=False))    
                        else:
                            print('Ошибка в типе браузерного статуса')
                            exit()
                            
                    else:
                        x1.append(json.dumps({"role":'browser-bing',"text":{'status':msg['metadata']['status'],'text':""}},ensure_ascii=False))
                        print(msg['content'])
                        exit()
                    '''
                elif plug_name=='plugin_service':
                    x1.append(json.dumps({"role":'plugin_service',"text":msg['content']['parts']},ensure_ascii=False))
                elif plug_name=='linkReader.apiSearch':
                    x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':"\n".join(msg['content']['parts']) }},ensure_ascii=False))
                elif plug_name=='linkReader.getContent':
                    x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':"\n".join(msg['content']['parts']) }},ensure_ascii=False))
                elif plug_name=='web_requests.scrape_url':
                    x1.append(json.dumps({"role":'browser',"text":{'status':msg['status'],'text':"\n".join(msg['content']['parts']) }},ensure_ascii=False))
                else:
                    m.append(plug_name) # ['linkReader.apiSearch', 'linkReader.getContent', 'web_requests.scrape_url']
    else:
        msgs_counter={'used':msgs_counter['used'],'unused':msgs_counter['unused'],'not_allowed':msgs_counter['not_allowed'],'passed_space':msgs_counter['passed_space']+1}

    return x1,Allow,Allow_collect_after,stupid_stop_stat,u_up,msgs_counter

def chatGPT_proc(dirr):
    prepareData(dirr)
    
    msgs_counter={'used':0,'unused':0,'not_allowed':0,'passed_space':0}
    
    m=[]

    dataset=[]
    f=json.load(open(f'final_output.json',encoding='utf-8'))
    img_detect=0
    stupid_stop=0
    noresp_detect=0
    for i in range(len(f)):

        x1=[]
        Allow=True
        Allow_collect_after=True
        img_detect_stat=False
        stupid_stop_stat=False
        
        if f[i][len(f[i])-1]['message']['author']['role']=='assistant':
            u_up=False,''
            for j in range(len(f[i])):
                msg=f[i][j]['message']
                if msg!=None:
                    status_text,text=getText(msg)
                    if status_text==False:
                        if text=='Image detector':
                            Allow=False
                            img_detect_stat=True
                        
                    else:
                        autor=msg['author']['role']
                        if autor=='assistant':
                            x1,Allow,Allow_collect_after,stupid_stop_stat,u_up,msgs_counter = assistantProc(msgs_counter,m,x1,autor,text,Allow_collect_after,Allow,u_up,stupid_stop_stat,msg)
                        elif autor=='user':
                            x1,Allow,Allow_collect_after,stupid_stop_stat,u_up,msgs_counter = userProc(msgs_counter,m,x1,autor,text,Allow_collect_after,Allow,u_up,stupid_stop_stat,msg)
                        elif autor=='tool':
                            x1,Allow,Allow_collect_after,stupid_stop_stat,u_up,msgs_counter = toolProc(msgs_counter,m,x1,autor,text,Allow_collect_after,Allow,u_up,stupid_stop_stat,msg)
                        elif autor=='system':
                            pass
                        else:
                            print("New Author:",autor)
                            exit()
        else:
            Allow=False
            noresp_detect+=1
        
        if Allow:
            dataset.append("\n".join(x1))
        else:
            msgs_counter={'used':msgs_counter['used'],'unused':msgs_counter['unused'],'not_allowed':msgs_counter['not_allowed']+len(x1),'passed_space':msgs_counter['passed_space']}
        
        if img_detect_stat:
            img_detect+=len(x1)
        
        if stupid_stop_stat:
            stupid_stop+=1
    
    out_buf=''
    out_buf+='\n'
    out_buf+=str(f'Found {img_detect} uses of GPT4(V) messages')+'\n'
    out_buf+=str(f'Found {stupid_stop} impatiently finished chats')+'\n'
    out_buf+=str(f'Found {noresp_detect} chats without response')+'\n'
    out_buf+=str(f'Total chats (allowed): {len(f)}')+'\n'
    out_buf+=str(f'Messages {msgs_counter}')+'\n'
    out_buf+=str(f'New raw roles {list(set(m))}')+'\n'
    out_buf+=str('"role": "dall-e"' in "\n".join(dataset))+'\n'
    out_buf+=str('\n')

    
    return "\n".join(dataset),out_buf


def ls(mypath):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]
def lss(mypath):
    return [f for f in listdir(mypath) if not isfile(join(mypath, f))]
