import aiohttp
import asyncio
from datetime import datetime
from typing import Coroutine



#Created by: Owlcept

class Replies:
    def __init__(self, message: str, name: str, id: int, date: str, replied: bool):
        self.message = message
        self.name = name
        self.id = id
        self.date = datetime.fromisoformat(date.replace('Z',''))
        self.replied = replied

    def __repr__(self):
        return f"ID: {self.id} | Message: {self.message} | Date: {self.date}"
        

class Client:


    def __init__(self,API: str, prefix: str = '!'):
        ''' 
        Build API key and base url for requests
        Params:
            API: API key given by MTA
            prefix: Prefix for commands in string
        
         '''
        self.messages = {} #Use dict to make updating easier cause lists suck
        self.cmd_list = {}
        self.loop = asyncio.get_event_loop()
        self.prefix = prefix
        self.rate_limit = 2
        self.session = aiohttp.ClientSession()
        self.url = "https://api.mobile-text-alerts.com/v3/"
        self.headers = {'Accept':'application/json', 'Authorization':f'Bearer {API}'}


    def commands(self,func):
        #Add commands to list
        self.cmd_list[func.__name__] = func
        return func

    async def _close(self) -> None:
        await self.session.close()
    
    def run(self) -> None:
        loop = self.loop
        try:
            loop.run_until_complete(asyncio.gather(self.get_replies(),self.check()))
        except KeyboardInterrupt:
            print('\nProgram shutting down')
        finally:
            loop.run_until_complete(self._close())
            loop.close()

    async def check(self) -> Coroutine:
        while True:
            for m in self.messages.values():
                #Check for prefix
                if m.message.startswith(self.prefix) and m.replied != True:
                    #Arg[0] = command // Arg[1] all other vars to be parsed
                    # Eliminate all white space for vars
                    cmd = m.message.strip(self.prefix).split(None,1)
                    if cmd[0] in self.cmd_list:
                        #input the read function here
                        func = self.cmd_list.get(cmd[0])
                        try:
                            await func(m,cmd[1])
                        except:
                            await func(m)
                    else:
                        print('Command not found')
                else:
                    continue
            await asyncio.sleep(self.rate_limit)


    async def send_message(self, message, subs) -> Coroutine:
        '''Use this to send messages to specific number'''
        url = "https://api.mobile-text-alerts.com/v3/send"
        payload = {"subscribers": subs, "message": message}
        x = await self.session.post(url,headers = self.headers, data=payload)
        print(x.response)

    async def get_replies(self) -> Coroutine:
        ''' Use this to get replies
            maybe build a listen tool?'''
        while True:

            url = "https://api.mobile-text-alerts.com/v3/threads"
            r =  await self.session.get(url, headers = self.headers, params = self.params)
            r = await r.json()['data']['rows']
            for x in r:
                if x['id'] not in self.messages:
                    self.messages[x['id']] = Replies(x['latestMessage']['message'],x['name'],x['id'],
                    x['latestMessage']['timestamp'],x['unread'])

            
            await asyncio.sleep(self.rate_limit)

    async def mark_read(self, msg) -> Coroutine:
        ''' Use this to mark messages as read'''
        r = await self.session.patch(f"https://api.mobile-text-alerts.com/v3/threads/{msg.id}/read", headers= self.headers)
        if r.status == 200:
            msg.replied = True
            print(f"Marked {msg.id} as read")
        else:
            print(f"Failed to mark {msg.id} as read")

