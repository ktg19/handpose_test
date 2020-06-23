# -*- coding: utf-8 -*-
"""

"""

import cv2 as cv
import time
import sys
import numpy as np
import pandas as pd
import math
import pickle
import requests

class HandPosePredictor(object):
    def __init__(self):
        self.finger_annotations = None

        self.fingers = ['thumb','indexFinger','middleFinger','ringFinger','pinky']
        
        self.hand_poses = ['ZERO', 'ONE','TWO','THREE','FOUR','FIVE']

        self.last_sent_time = None

        # Open a video file or an image file or a camera stream
        self.padding = 20

        # モデル読み込み
        filename = 'randome_forest_depending_on_distance.pickle'
        self.model = pickle.load(open(filename, 'rb'))
        
        self.video = cv.VideoCapture(0)
        # Opencvのカメラをセットします。(0)はノートパソコンならば組み込まれているカメラ

    def __del__(self):
        self.video.release()
        
    def restart_camera(self):
        self.video.release()
        self.video = cv.VideoCapture(0)
    
    def drawFinger(self, base, finger, img):
        """各指の展を描画"""
        for i in range(len(finger) -1):
            img = cv.line(img, (int(finger[i][0]), int(finger[i][1])), (int(finger[i+1][0]), int(finger[i+1][1])), (0, 255, 0), thickness=5, lineType=cv.LINE_4)
        
        img = cv.line(img, (int(base[0][0]), int(base[0][1])), (int(finger[0][0]), int(finger[0][1])), (0, 255, 0), thickness=5, lineType=cv.LINE_4)
        
        return img

    def draw_hand(self, img):
        """手の描画"""
        palm_base = self.finger_annotations['palmBase']

        for finger in self.fingers:
            img = self.drawFinger(palm_base, self.finger_annotations[finger], img)

        return img

    def get_image(self):

        # Read frame
        hasFrame, frame = self.video.read()

        frame = frame[0:500,0:300]
    
        if not hasFrame:
            print("has no Frame")
            cv.waitKey()
            return False, frame
            # break

        # 指があった場合
        if self.finger_annotations is not None:
            # 推測
            hand_pose = self.predict_hand_pose()

            if hand_pose == self.hand_poses[3]:
                # 指の形が三だったらエアコンつける
                self.send_webhook()

            # 画像のラベル表示
            cv.putText(frame, hand_pose, (10, 50), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv.LINE_AA)
            # 指を描画
            frame = self.draw_hand(frame)
            cv.imshow("frame",frame)
        
            
        return True, frame
        print("time : {:.3f}".format(time.time() - t))
    
    def get_frame(self):
        """
        年齢と性別を判定したフレームの結果をjpegに直して返す。
        """
        success = True
        try:
            # success, image = self.video.read()
            success, image = self.get_image()
            ret = True
            ret, jpeg = cv.imencode('.jpg', image)
        except Exception as e:
            self.restart_camera()
            hasFrame, frame = self.video.read()
            ret, jpeg = cv.imencode('.jpg', frame)
            print(e)
        return success, jpeg.tobytes()

    def set_hand_skelton(self, jsonfile):
        self.finger_annotations = jsonfile['annotations']

    def make_finger_values(self):
        """スケルトンから特徴量を作る"""
        finger_val = []
        for finger in self.fingers:
            first = self.finger_annotations[finger][0]
            fourth = self.finger_annotations[finger][3]
            distance = self.getDistance(float(first[0]), float(first[1]), float(fourth[0]), float(fourth[1]))
            finger_val.append(distance)
        return finger_val
        
    def predict_hand_pose(self):
        """#セットされたスケルトンから指のポーズを推測"""
        finger_val = self.make_finger_values()
        df = self.makeDF(finger_val)
        result = self.model.predict(df)

        hand_pose = self.hand_poses[int(result[0])]

        return hand_pose
    
    def makeDF(self, python_list):
        """リストをデータフレームにして返す"""
        np_array = np.array([python_list])
        df = pd.DataFrame(np_array)#.T 
        return df
    
    def getDistance(self, x1, y1, x2, y2):
        """# それぞれの指の一つ目と4つ目の点の距離を測って特徴量にする"""
        # print([x1, y1, x2, y2])
        x = (x2 - x1) ** 2
        y = (y2 - y1) ** 2
        distance = math.sqrt(x + y)
        # print(distance)
        return distance
    
    def send_webhook(self):
        """webhookを送信"""
        if not self.can_send_webhook():
            # webhookを送った直後だったらwebhookを送らない
            return

        url = ""
        # requests.post(url)

    def can_send_webhook(self, seconds = 5):
        """webhookを送って良いかチェック"""
        if self.last_sent_time is None:
            self.last_sent_time = time.time()
            return True
        
        now = time.time()
        past_seconds = now - self.last_sent_time
        print(past_seconds)
        if int(past_seconds) > seconds:
            self.last_sent_time = now
            return True
        else:
            return False




