from datetime import datetime
import requests
import json
import random
import time
import re
import os
import argparse
import pandas as pd
import sys

class ImageHandler:

    def __init__(self):
        
        self.params = '/Users/kizzyterra/Workspace/midjourney-bot/secure-files/handler_params.json'
        self.handler_initializer()
        self.df = pd.DataFrame(columns = ['prompt', 'url', 'filename', 'is_downloaded'])

    def handler_initializer(self):

        with open(self.params, "r") as json_file:
            params = json.load(json_file)

        self.img_folder = params['img_folder']

        self.channel_id=params['channel_id']
        self.authorization=params['authorization']
        self.header = {'authorization' : self.authorization}

        self.application_id = params['application_id']
        self.guild_id = params['guild_id']
        self.session_id = params['session_id']
        self.version_imagine = params['version_imagine']
        self.id_imagine = params['id_imagine']
        self.version_describe = params['version_describe']
        self.id_describe = params['id_describe']
        self.flags = params['flags']
        
    
    def describe_static(self):
        prompts = ['modern new york city room with big windows, built in wooden shelving with colorful books, green leather and oak modern couch and solid oak flooring 45mm original editorial photo',
                    'moanlisa as top model',
                    'cat and dog surfing in Hawaii',
                    'a horse as a film director']
        random_prompt = random.randint(0,3)
        return prompts[random_prompt]
    
    def upload(self, img_name):
        #https://stackoverflow.com/questions/76092002/uploading-files-to-discord-api-thought-put-using-python-requests
        header = {
                'authorization': self.authorization
            }
        
        img_path = self.img_folder + img_name
        img_size = os.path.getsize(img_path)
        img = open(img_path, 'rb')
        file_id = 1
        payload = {
            "files":[{"filename":img_name,"file_size":img_size,"id":file_id}]
            }
        post_response = requests.post(f'https://discord.com/api/v9/channels/{self.channel_id}/attachments', json = payload , headers = header)
        print(f"POST response: {post_response.status_code}")
        attachment_info = post_response.json()
        post_response.raise_for_status()
        attachment_uploaded_filename = post_response.json()["attachments"][0]['upload_filename']
        
        put_url = post_response.json()['attachments'][0]['upload_url']
        put_headers = {
            'Content-Length': str(img_size), 
            'Connection': 'keep-alive', 
            'Content-Type': 'image/png', 
            'authorization' : self.authorization
            }
        put_response = requests.put(put_url, headers=put_headers, data=img)
        print(f"PUT response: {put_response.status_code}")
        put_response.raise_for_status()

        print('upload successfully sent!')

        return attachment_uploaded_filename
        
    def describe(self, img_name):
            header = {
                'authorization': self.authorization
            }
            
            uploaded_filename = self.upload(img_name)
            filename = uploaded_filename.split("/")[1]

            payload = {'type': 2, 
            'application_id': self.application_id,
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
            'session_id': self.session_id,
            'data': {
                'version': self.version_describe,
                'id': self.id_describe,
                'name': 'describe',
                'type': 1,
                "options":[{"type":11,"name":"image","value":0}],
                "application_command":{"id":"1092492867185950852",
                                       "application_id":"936929561302675456",
                                       "version":"1092492867185950853",
                                       "type":1,
                                       "nsfw":False,
                                       "name":"describe",
                                       "description":"Writes a prompt based on your image.",
                                       "dm_permission":True,
                                        "options":[{"type":11,"name":"image","description":"The image to describe","required":True}]},
                "attachments":[{"id":0,"filename": filename, "uploaded_filename":uploaded_filename}]
                    }
                }
            
            post_response = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = header)
            print(print(f'Describe Status Code: {post_response.status_code}'))
            post_response.raise_for_status()
            if (post_response.status_code == 400):
                exit()
           
            print('describe successfully sent!')
    
    def get_describe_prompts(self):
        message_list = self.retrieve_messages()
        prompts_list = []
        for message in message_list:
            if message['embeds']:
                # print(message['embeds'][0]['description'])
                prompts_list =  message['embeds'][0]['description'].split('\n\n')
                #clean prompts
                #store prompts
        print('prompts succesfully read!')
        return prompts_list     

    def describe_prompt(self, img_name):
        self.describe(img_name)
        prompts = self.get_describe_prompts()
        while len(prompts) == 0:
            time.sleep(5)
            prompts = self.get_describe_prompts()

        return prompts[0]

    def imagine(self, prompt):
        
        # prompt = prompt.replace('_', ' ')
        # prompt = " ".join(prompt.split())
        # prompt = re.sub(r'[^a-zA-Z0-9\s]+', '', prompt)
        prompt = prompt.lower()

        payload = {'type': 2, 
        'application_id': self.application_id,
        'guild_id': self.guild_id,
        'channel_id': self.channel_id,
        'session_id': self.session_id,
        'data': {
            'version': self.version_imagine,
            'id': self.id_imagine,
            'name': 'imagine',
            'type': 1,
            'options': [{'type': 3, 'name': 'prompt', 'value': str(prompt) + ' ' + self.flags}],
            'attachments': []}
            }
        
        r = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = self.header)
        print(f'Imagine Status Code: {r.status_code}')
        if (r.status_code == 400):
                exit()

        while r.status_code != 204:
            r = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = header)

        print(f'imagine prompt [{prompt}] successfully sent!')

    def upsample(self, upsample):
        upsamples_ids = self.get_upsample_ids()
        
        try:
            upscale_job = upsamples_ids[upsample]
            message_id = upsamples_ids['message_id']
        except KeyError:
            print("upsample_ids is empty!")


        header = {
            'authorization': self.authorization
        }

        payload = {'type': 3,
        'guild_id': self.guild_id,
        'channel_id': self.channel_id, 
        'application_id': self.application_id,
        'message_id': message_id,
        'session_id': self.session_id,
        'data': {
            'component_type': 2,
            'custom_id': upscale_job }
            }
        
        r = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = header)
        
        if (r.status_code == 400):
                print(r.status_code)
                exit()

        while r.status_code != 204:
            r = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = header)

        print(f'Upscale request for message_id [{message_id}] and image [{upsample}] successfully sent!')

    def get_upsample_ids(self):
        message_list  = self.retrieve_messages()
        upsamples = {}
        for message in message_list:
            print('********')
            if (message['author']['username'] == 'Midjourney Bot') and (len(message['components'][0]['components'])>3):
                components = message['components'][0]['components']
                # print(components)
                upsamples['message_id'] = message['id']
                upsamples['U1'] = components[0]['custom_id']
                upsamples['U2'] = components[1]['custom_id']
                upsamples['U3'] = components[2]['custom_id']
                upsamples['U4'] = components[3]['custom_id']
                print(upsamples)
            else:
                print("No upsample found!")
            return upsamples

    def retrieve_messages(self):
        r = requests.get(
            f'https://discord.com/api/v10/channels/{self.channel_id}/messages?limit={2}', headers=self.header)
        response = json.loads(r.text)
        
        # print(response)
        print('=========================================')
        
        return response

    def collecting_results(self):
        message_list  = self.retrieve_messages()
        self.awaiting_list = pd.DataFrame(columns = ['prompt', 'status'])
        for message in message_list:
            if (message['author']['username'] == 'Midjourney Bot') and ('Image #1' in message['content']):
                
                if len(message['attachments']) > 0:

                    if (message['attachments'][0]['filename'][-4:] == '.png'):
                        id = message['id']
                        prompt = message['content'].split('**')[1].split(' --')[0]
                        url = message['attachments'][0]['url']
                        filename = message['attachments'][0]['filename']
                        if id not in self.df.index:
                            self.df.loc[id] = [prompt, url, filename, 0]

                    else:
                        id = message['id']
                        prompt = message['content'].split('**')[1].split(' --')[0]
                        if ('(fast)' in message['content']) or ('(relaxed)' in message['content']):
                            try:
                                status = re.findall("(\w*%)", message['content'])[0]
                            except:
                                status = 'unknown status'
                        self.awaiting_list.loc[id] = [prompt, status]

                else:
                    id = message['id']
                    prompt = message['content'].split('**')[1].split(' --')[0]
                    if '(Waiting to start)' in message['content']:
                        status = 'Waiting to start'
                    self.awaiting_list.loc[id] = [prompt, status]
                    
    def outputer(self):
        if len(self.awaiting_list) > 0:
            print(datetime.now().strftime("%H:%M:%S"))
            print('prompts in progress:')
            print(self.awaiting_list)
            print('=========================================')

        waiting_for_download = [self.df.loc[i].prompt for i in self.df.index if self.df.loc[i].is_downloaded == 0]
        if len(waiting_for_download) > 0:
            print(datetime.now().strftime("%H:%M:%S"))
            print('waiting for download prompts: ', waiting_for_download)
            print('=========================================')

    def downloading_results(self):
        processed_prompts = []
        for i in self.df.index:
            if self.df.loc[i].is_downloaded == 0:
                response = requests.get(self.df.loc[i].url)
                with open(os.path.join(self.img_folder, self.df.loc[i].filename), "wb") as req:
                    req.write(response.content)
                self.df.loc[i, 'is_downloaded'] = 1
                processed_prompts.append(self.df.loc[i].prompt)
        if len(processed_prompts) > 0:
            print(datetime.now().strftime("%H:%M:%S"))
            print('processed prompts: ', processed_prompts)
            print('=========================================')
  
    def get_images(self):
        print('=========== listening started ===========')
        self.collecting_results()
        self.outputer()
        self.downloading_results()

    def get_ai_img(self, img_name):
        prompt = self.describe_prompt(img_name)
        self.imagine(prompt)
        self.upsample('U1')
        self.get_images()
        print('image downloaded successfully!')


if __name__ == "__main__":

    # img_path= "/Users/kizzyterra/Workspace/midjourney-bot/img/img-tst-1.jpg"
    handler = ImageHandler() 

    img_name = 'death-stranding.jpg'
    handler.get_ai_img(img_name)
