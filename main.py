PORT = 8088

from flask import Flask,request
import json
app = Flask(__name__)

#加载插件
import printmsg,printrecall,libkeyword
plugins = (printmsg,printrecall,libkeyword)

#接收消息
@app.route('/',methods=['POST'])
def main():
    data = json.loads(request.get_data().decode())
##    print(data)

    #向各插件推送
    for i in plugins:
        i.main(data)

    if data['post_type'] != 'message':
        print(data)
    return ''

app.run(host='localhost',port=PORT,debug=True)
#change2
