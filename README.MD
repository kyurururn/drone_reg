## Telloドローン ライブラリ
このプロジェクトは、Telloドローンを制御するためのライブラリです。

## 必要ライブラリのインストール
```pip install opencv-python```  
コマンドライン上で、上記のプログラムを実行させてください。

## 追加されているコマンド
```shoot```  
ドローンカメラで撮影を行います。  
```q```  
ドローンの制御を終わらせ、プログラムを終了します。  
離陸しているときは、実行することができません。

## サンプルコード

```python
from TelloDrone_Lib import TelloDrone

drone = TelloDrone("192.168.10.1",
                    8889,
                    send_reg_j=True,
                    capture_setting=True,
                    take_movie=True)

while True:
    msg = input()
    answer = drone.send_command(msg)
    if not answer:
        break
```
