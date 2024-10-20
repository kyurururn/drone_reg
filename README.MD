## Telloドローン ライブラリ
このプロジェクトは、Telloドローンを制御するためのライブラリです。

## 必要ライブラリのインストール
```pip install opencv-python```  
コマンドライン上で、上記のプログラムを実行させてください。

## 追加されているコマンド
```shoot```  
ドローンカメラで画像の撮影を行います。  
capture_settingをTrueにする必要があります。  
  
```q```  
ドローンの制御を終わらせ、プログラムを終了します。  
離陸しているときは、実行することができません。

## サンプルコード

### コマンドの送受信を行うプログラム
```python
from TelloDrone_Lib import TelloDrone

drone = TelloDrone("192.168.10.1",8889)

while True:
    msg = input()
    answer = drone.send_command(msg)
    if not answer:
        break
```  

### 映像収録や写真撮影を行うプログラム
```python
from TelloDrone_Lib import TelloDrone

drone = TelloDrone("192.168.10.1",8889,
                    send_regu=True,
                    capture_setting=True,
                    take_movie=True)

while True:
    msg = input()
    answer = drone.send_command(msg)
    if not answer:
        break
```  
## 設定
### send_regu
長時間コマンドが送られていない時に自動で着陸**しない**ようにします。
### capture_setting
映像や画像の設定を行います。
### take_movie
映像を撮影します。

## 標準コマンド
### 離陸/着陸

```takeoff```  
離陸

```land```
着陸

### 移動
  
{数値}の部分は、30や40のように数字のみで記述してください。
また、{数値}は10～500までの値で指定してください。
  
```up {数値}```  
上に{数値}cm移動する  
  
```down {数値}```  
下に{数値}cm移動する  
  
```forward {数値}```  
前に{数値}cm移動する  
  
```back {数値}```  
後ろに{数値}cm移動する  
  
```left {数値}```  
左に{数値}cm移動する  
  
```right {数値}```  
右に{数値}cm移動する  
  
### 回転
  
```cw {数値}```  
右回りに{数値}cm回転する  
  
```ccw {数値}```  
左回りに{数値}cm回転する  

### 撮影
  
```shoot```  
ドローンカメラで画像を撮影する。  
capture_settingをTrueにする必要があります。  

## 短縮コマンド
```up {数値}```      -> ```u {数値}```  
```down {数値}```    -> ```d {数値}```  
```forward {数値}``` -> ```f {数値}```  
```back {数値}```    -> ```b {数値}```  
```left {数値}```    -> ```l {数値}```  
```right {数値}```   -> ```r {数値}```
