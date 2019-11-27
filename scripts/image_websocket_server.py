#!/usr/bin/env python
#! coding utf-8

from threading import Thread
import time
import cv2
import numpy as np
from PIL import Image as PILImage

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

sending_data = ""

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
        tornado.ioloop.IOLoop.instance().stop()
        self.state = False

    def loop(self):
        print("loop start")
        while self.state:
            global sending_data
            self.value += 1
            print(self.value)
            # self.write_message(str(self.value))
            self.write_message(sending_data + str(self.value))
            time.sleep(1)
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

def listener():
    rospy.Subscriber("chatter", String, callback)
    rospy.spin()
    print("killed ros")

if __name__ == '__main__':
    rospy.init_node('listener', anonymous=True)

    t = Thread(target = listener)
    # t.start()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/image", WSHandler)
    ])
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
    rospy.shutdown()
