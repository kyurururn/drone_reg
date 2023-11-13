import socket
import time
import cv2
import threading
import re
import os

class TelloDrone:
    def __init__(self, tello_ip, tello_port, send_reg_j, capture_setting, take_movie):
        self.tello_ip = tello_ip
        self.tello_port = tello_port
        self.tello_address = (self.tello_ip, self.tello_port)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', tello_port))
        self.sock.sendto("command".encode("utf-8"), self.tello_address)

        self.send_reg_j = send_reg_j
        self.capture_setting = capture_setting
        self.take_movie = take_movie

        self.log = []
        self.receive_thread_j = True
        self.drone_height = "0"

        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()


        if self.send_reg_j:
            self.thread_reg = threading.Thread(target=self.send_reg)
            self.thread_reg.start()

        if self.capture_setting:
            self.sock.sendto("streamon".encode(encoding="utf-8"), self.tello_address)
            self.tello_camera_address = 'udp://@0.0.0.0:11111'
            time.sleep(1)
            self.cap = cv2.VideoCapture(self.tello_camera_address)
            time.sleep(1)
            self.cap.open(self.tello_camera_address)
            time.sleep(1)
            self.thread_capture = threading.Thread(target=self.capture)
            self.thread_capture.start()


    def capture(self):
        try:
            if self.take_movie:
                fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                out = cv2.VideoWriter('movie.mp4', fourcc, fps, (width, height))
            while self.capture_setting:
                ret,  self.frame = self.cap.read()
                if self.take_movie: out.write(self.frame)
                cv2.imshow('Tello Camera View', self.frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass

    def shoot(self):
        frame_id = 1

        while os.path.exists(f"{frame_id}.png"):
            frame_id += 1

        filename = f"{frame_id}.png"
        cv2.imwrite(filename, self.frame)

    def send_command(self, command):
        if command == "q":
            return self.close()
        elif command == "shoot":
            self.shoot()
            return True
        else:
            self.sock.sendto(command.encode("utf-8"), self.tello_address)
            return True

    def close(self):
        if self.drone_height != 0:
            print("着陸していません")
            return True
        else:
            self.receive_thread_j = False
                
            if self.send_reg_j:
                self.send_reg_j = False
            
            if self.capture_setting:
                self.cap.release()
                cv2.destroyAllWindows()
                self.sock.sendto("streamoff".encode("utf-8"), self.tello_address)
                self.capture_setting = False
            
            self.sock.close()
            print("QUIT...")

            return False

    def send_reg(self):
        try:
            while self.send_reg_j:
                self.sock.sendto("height?".encode(encoding="utf-8"), self.tello_address)
                time.sleep(1)
        except KeyboardInterrupt:
            return

    def _receive_thread(self):
        while self.receive_thread_j:
            try:
                self.response, ip = self.sock.recvfrom(1024)
                if b'dm' in self.response:
                    decoded_data = self.response.decode("utf-8")
                    match_data = re.search(r'\d+', decoded_data)
                    if match_data:
                        self.drone_height = int(match_data.group())

            except socket.error as exc:
                pass
            
            except KeyboardInterrupt:
                break

drone = TelloDrone("192.168.10.1", 8889, send_reg_j=True, capture_setting=True, take_movie=True)

while True:
    msg = input()
    answer = drone.send_command(msg)
    if not answer:
        break