from flask import Flask, render_template, Response
import cv2
from two import get_two
from search import search
from camera import cap, VideoCamera

app = Flask(__name__)

@app.route('/')  # 主页
def index():
    # jinja2模板，具体格式保存在index.html文件中
    return render_template('index.html')

def gen(video):
    while True:
        frame = video.get_frame()
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')  # 这个地址返回视频流响应
def video_feed():
    return Response(gen(cap),
                    mimetype='multipart/x-mixed-replace; boundary=frame')   

@app.route('/get_num')
def num_feed():
    return str(cap.get_num())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)