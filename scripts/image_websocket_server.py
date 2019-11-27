#!/usr/bin/env python
#! coding utf-8

from threading import Thread
import time
import cv2
import numpy as np
from PIL import Image as PILImage
import base64

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.util import PY3

# https://stackoverflow.com/questions/24851207/tornado-403-get-warning-when-opening-websocket
if PY3:
    from urllib.parse import urlparse  # py2
    xrange = range
else:
    from urlparse import urlparse  # py3

#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

sending_data = ""
sending_dict = dict()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print("main")
        self.write("Hello, world")

class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.value = 0
        self.state = True

    def open(self):
        print("connection opend: ", self.request.remote_ip)
        t = Thread(target = self.loop)
        t.setDaemon(True)
        t.start()
        while True:
            print(t.isAlive())
            if not t.isAlive():
                break
            time.sleep(1)
        print("thread is dead")
        t.join()
        # tornado.ioloop.IOLoop.instance().stop()
        # self.state = False

    def loop(self):
        print("loop start")
        while self.state:
            global sending_data
            self.value += 1
            print(self.value)
            # self.write_message(sending_data + str(self.value))
            self.write_message(sending_dict)
            # self.write(sending_dict)
            time.sleep(0.1)
        print("loop end")

    def on_close(self):
        self.state = False
        self.close()
        print("connection closed: ", self.request.remote_ip)

    def check_origin(self, origin):
       # parsed_origin = urlparse(origin)
       # return parsed_origin.hostname in self.CORS_ORIGINS
       return True

def callback(data):
    global sending_data
    rospy.loginfo(rospy.get_caller_id()+"I heard %s",data.data)
    sending_data = data.data

def image_callback(data):
    global sending_dict
    # print("image received")
    try:
        cv_image = CvBridge().imgmsg_to_cv2(data, "bgr8")
        result, bin_image = cv2.imencode('.jpg', cv_image)
        bin_image64 = base64.b64encode(bin_image)
        # print(bin_image64)
        sending_dict['image'] = bin_image64
        cv2.imshow("image", cv_image)
        cv2.waitKey(1)
    except CvBridgeError as e:
        print(e)

def listener():
    rospy.Subscriber("chatter", String, callback)
    rospy.Subscriber("/usb_cam/image_raw", Image, image_callback)
    rospy.spin()
    print("killed ros")

def main():
    rospy.init_node('listener', anonymous=True, disable_signals=True)

    t = Thread(target = listener)
    t.setDaemon(True)
    t.start()

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/image", WSHandler)
    ])
    application.listen(8080)
    print("waiting for connection from client...")
    tornado.ioloop.IOLoop.instance().start()

    rospy.signal_shutdown("end")
    print("end")

if __name__ == '__main__':
    try:
        main()
    except:
        print("killed by Ctrl-C")
