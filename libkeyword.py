import time,threading

now_message = {'message':''}

def exist(lst:list):
    def call(func):
        def thread():
            while True:
                for i in lst:
                    if i in now_message['message']:
                        func(now_message)
                    time.sleep(0.5)
        threading.Thread(target=thread).run()
    return call
def main(data:dict):
    global now_message
    if data['post_type'] == 'message':
        now_message = data
 
