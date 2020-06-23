from flask import Flask, render_template, Response, make_response, jsonify, request

from HandPose.HandPose import HandPosePredictor
import cv2 as cv
import urllib
import json

app = Flask(__name__)
hand_pose_predictor = HandPosePredictor()

@app.route('/')
def index():    
    return render_template('index.html')
    # "/" を呼び出したときには、indexが表示される。

continue_flag = True
def gen(camera):
    continue_flag = True    
    while continue_flag and cv.waitKey(1) < 0:
        continue_flag, frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    print("end")

@app.route('/video_feed')
def video_feed():
    return Response(gen(hand_pose_predictor),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/axios', methods=['GET'])#POST
def send():

    full_path = urllib.parse.unquote(request.full_path)
    start = full_path.find("=") + 1
    json_str = full_path[start:]

    # jsonで受け取った内容をセット
    json_dict = json.loads(json_str)    
    hand_pose_predictor.set_hand_skelton(json_dict)

    return make_response(jsonify({'result': 'success'}))

    

if __name__ == '__main__':
    app.run(threaded=True)
# 0.0.0.0はすべてのアクセスを受け付けます。    
# webブラウザーには、「localhost:5000」と入力
