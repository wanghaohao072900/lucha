# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, request, jsonify
import Queue

app = Flask(__name__)
app.secret_key = '1'


@app.route('/index')
def hello_world():
    return render_template('index.html')


user_dict = {}


@app.route('/web_chat', methods=['GET', 'POST'])
def web_chat():
    # 前端发送过来信息，将信息群发给除发送用户外的所有用户
    if request.method == 'POST':
        msg = request.form.get('msg')
        username = request.form.get('username')
        msg = {'send_msg': msg, 'send_user': username}
        current_username = session['current_username']
        for user, q in user_dict.items():
            if user != current_username:
                q.put(msg)
        return jsonify({'status': True})
    else:
        return render_template('index.html')


@app.route('/get_msg', methods=['GET', 'POST'])
def get_msg():
    # 前端长轮询，后端等待数据，把username存入session中
    if request.method == 'POST':
        username = session['current_username']
        ret = {'status': True, 'data': None}
        q = user_dict[username]
        try:
            msg = q.get(timeout=3)
            ret['data'] = msg
        except Exception, e:
            print str(e)
            ret['status'] = False
        return jsonify(ret)


@app.route('/web_chat_join', methods=['GET', 'POST'])
def web_chat_join():
    # 加入聊天室，把用户加入user_dict，并为用户创建消息队列
    if request.method == 'POST':
        username = request.form.get('username')
        q = Queue.Queue()
        user_dict[username] = q
        session['current_username'] = username
        msg = {'send_msg': '加入房间！', 'send_user': username}
        q.put(msg)
        return jsonify({'status': True})


if __name__ == '__main__':
    # 使用长轮询时，由于消息队列会阻塞，所以必须使用多线程
    app.run(host='0.0.0.0', port='8888', threaded=True)
