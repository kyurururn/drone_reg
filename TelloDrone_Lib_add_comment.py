# 必要なライブラリをインポート
import socket  # 通信に使うライブラリ
import time  # タイミング制御に使うライブラリ
import cv2  # カメラの映像取得や表示に使うライブラリ
import threading  # 並行処理に使うライブラリ
import re  # 正規表現処理に使うライブラリ
import os  # ファイルやパスの操作に使うライブラリ

# TelloDroneクラスの定義。ドローンを操作する機能を提供
class TelloDrone:
    # 初期化メソッド。TelloのIPアドレスやポート、設定を指定する
    def __init__(self, tello_ip, tello_port, send_regu = True, capture_setting = False, take_movie = False):
        # IPアドレスとポートの設定
        self.tello_ip = tello_ip
        self.tello_port = tello_port
        self.tello_address = (self.tello_ip, self.tello_port)
        
        # ソケットを作成し、Telloと通信開始
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', tello_port))
        # Telloに「コマンドモード」に切り替える指示を送る
        self.sock.sendto("command".encode("utf-8"), self.tello_address)

        # オプションの設定 (定期的なコマンド送信、カメラ映像の取得、動画撮影)
        self.send_reg_j = send_regu
        self.capture_setting = capture_setting
        self.take_movie = take_movie

        # ログ用リスト、ドローンの高さ情報、スレッド管理フラグ
        self.log = []
        self.receive_thread_j = True
        self.drone_height = "0"

        # 受信スレッドを開始
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True  # プログラム終了時にスレッドも終了するように設定
        self.receive_thread.start()

        # 定期コマンド送信を有効にしている場合、そのスレッドを開始
        if self.send_reg_j:
            self.thread_reg = threading.Thread(target=self.send_reg)
            self.thread_reg.start()

        # カメラ映像の取得を有効にしている場合、カメラストリームをオンにし、映像取得スレッドを開始
        if self.capture_setting:
            self.sock.sendto("streamon".encode(encoding="utf-8"), self.tello_address)  # カメラストリームを有効化
            self.tello_camera_address = 'udp://@0.0.0.0:11111'  # 映像ストリームのアドレス
            time.sleep(1)
            self.cap = cv2.VideoCapture(self.tello_camera_address)  # カメラストリームを取得
            time.sleep(1)
            self.cap.open(self.tello_camera_address)  # カメラストリームを開く
            time.sleep(1)
            self.thread_capture = threading.Thread(target=self.capture)  # 映像取得スレッドを開始
            self.thread_capture.start()

    # カメラ映像を取得するメソッド
    def capture(self):
        try:
            # 動画撮影が有効な場合、映像ファイルの設定を行う
            if self.take_movie:
                fps = int(self.cap.get(cv2.CAP_PROP_FPS))  # フレームレートを取得
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 幅を取得
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 高さを取得
                fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # 動画ファイルのフォーマット
                out = cv2.VideoWriter('movie.mp4', fourcc, fps, (width, height))  # 動画ファイルの準備

            # 映像取得が有効な間、映像を取得して表示
            while self.capture_setting:
                ret, self.frame = self.cap.read()  # カメラ映像を取得
                if self.take_movie: out.write(self.frame)  # 動画撮影が有効なら映像を書き込む
                cv2.imshow('Tello Camera View', self.frame)  # 映像を表示
                # 'q'キーを押すと終了
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass  # キーボード割り込みによる強制終了を無視

    # 写真を撮るメソッド
    def shoot(self):
        frame_id = 1

        # 既に同じファイル名が存在する場合、ファイル名に番号を追加して回避
        while os.path.exists(f"{frame_id}.png"):
            frame_id += 1

        filename = f"{frame_id}.png"
        cv2.imwrite(filename, self.frame)  # 現在の映像フレームをファイルに保存

    # ドローンにコマンドを送るメソッド
    def send_command(self, command):
        if command == "q":  # 'q'を入力した場合は終了
            return self.close()
        elif command == "shoot":  # 'shoot'コマンドで写真を撮る
            self.shoot()
            return True
        else:
            # 短縮コマンドをフルコマンドに変換
            if ' ' in command:
                parts = command.split(' ')
                if parts[0] == 'f':
                    parts[0] = 'forward'
                elif parts[0] == 'b':
                    parts[0] = 'back'
                elif parts[0] == 'r':
                    parts[0] = 'right'
                elif parts[0] == 'l':
                    parts[0] = 'left'
                elif parts[0] == 'u':
                    parts[0] = 'up'
                elif parts[0] == 'd':
                    parts[0] = 'down'
                
                command = " ".join(parts)
            # コマンドをドローンに送信
            self.sock.sendto(command.encode("utf-8"), self.tello_address)
            return True

    # プログラムを終了するメソッド
    def close(self):
        # ドローンが着陸していない場合は終了させない
        if self.drone_height != 0:
            print("着陸していません")
            return True
        else:
            self.receive_thread_j = False  # 受信スレッドを停止
                
            if self.send_reg_j:
                self.send_reg_j = False  # 定期コマンド送信を停止
            
            if self.capture_setting:
                self.cap.release()  # カメラストリームを解放
                cv2.destroyAllWindows()  # 全てのウィンドウを閉じる
                self.sock.sendto("streamoff".encode("utf-8"), self.tello_address)  # カメラストリームをオフにする
                self.capture_setting = False
            
            self.sock.close()  # ソケットを閉じる
            print("QUIT...")  # 終了メッセージを表示

            return False

    # 定期的にドローンの高度情報を取得するメソッド
    def send_reg(self):
        try:
            while self.send_reg_j:  # 定期送信が有効な間、毎秒「高度?」コマンドを送る
                self.sock.sendto("height?".encode(encoding="utf-8"), self.tello_address)
                time.sleep(1)  # 1秒待つ
        except KeyboardInterrupt:
            return

    # 受信スレッド。ドローンからのデータを受信する
    def _receive_thread(self):
        while self.receive_thread_j:
            try:
                # ドローンからのデータを受信
                self.response, ip = self.sock.recvfrom(1024)
                # 高度情報を含む場合、その値を抽出して更新
                if b'dm' in self.response:
                    decoded_data = self.response.decode("utf-8")
                    match_data = re.search(r'\d+', decoded_data)
                    if match_data:
                        self.drone_height = int(match_data.group())  # 高度を更新

            except socket.error as exc:
                pass  # ソケットエラーを無視
            
            except KeyboardInterrupt:
                break  # キーボード割り込みでスレッドを終了
