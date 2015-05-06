# -*- coding: utf-8 -*-
import ImageGrab
import cv2
import cv2.cv as cv
import numpy as np
import random
import time
import sys
import winxpgui
from ctypes import *
user32 = windll.user32

#予約済み変数
#g_img_x,y : chkimgがTrueの場合座標が入る
g_img_x = -1
g_img_y = -1

# 画像を比較する関数
# chkimgで使用
def compareImg(comImgNp,npimg,check):
    detector = cv2.SIFT()
    #比較元画像の特徴量の検出
    kp1, desc1 = detector.detectAndCompute(comImgNp, None)
    # キャプチャ画像の特徴量の検出
    kp2, desc2 = detector.detectAndCompute(npimg, None)

    # BFMatcherをNORM_L2で対応付け
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    # クエリ集合の各ディスクリプタに対して、最も良い上位2個のマッチを取得
    matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2)

    # 距離許容比率
    ratio = 0.75

    # 座標を抽出
    mkp = []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp.append( kp2[m.trainIdx] )
    matchedXY = np.float32([kp.pt for kp in mkp])

    # 共通点が5ポイント以上あったらその中央の座標を返す
    if len(matchedXY) >= check:
        x,y = 0,0;
        for i in matchedXY:
            x += i[0]
            y += i[1]
        avgx = int(x / len(matchedXY))
        avgy = int(y / len(matchedXY))
        return (avgx,avgy)

#画像認識 ファイル名指定だけで使用可能
#imgname : 画像ファイルパス
#capx : キャプチャ左上位置x座標
#capy : キャプチャ左上位置y座標
#capwid : キャプチャ横幅
#caphei : キャプチャ縦幅
def chkimg(imgname,capx = -1,capy = -1,capwid = -1,caphei = -1,check = 5):
    global g_img_x,g_img_y
    #比較に使う画像のロード
    comimg = cv2.imread(imgname,0)

    #キャプチャ
    if(capx > 0 and capy > 0 and capwid > 0 and caphei > 0):
        baseimg = ImageGrab.grab((capx,capy,capwid,caphei))
    else:
        baseimg = ImageGrab.grab()

    #画像をグレースケールに変換
    npimg = np.asarray(baseimg)
    capimg = cv2.cvtColor(npimg,cv2.COLOR_BGR2GRAY)
    
    #座標検索
    retXY = compareImg(comimg,capimg,check)
    #見つかった場合座標を返す
    #なかった場合-1,-1を返す
    if(retXY != None):
        g_img_x = retXY[0]
        g_img_y = retXY[1]
        return(True)
    else:
        return(False)

#指定座標を左クリック
#chkimg実行後に引数無しで実行した場合、img座標をクリック
#x : x座標
#y : y座標
def click(x = -1,y = -1,wait = 0.2):
    if(x != -1 and y != -1):
        user32.SetCursorPos(x,y)
        user32.mouse_event(0x2,0,0,0,0) #クリックする
        sleep(wait)
        user32.mouse_event(0x4,0,0,0,0) #クリックを放す
        return(True)
    else:
        #img座標に数値が入っていた場合
        if(g_img_x != -1 and g_img_y != -1):
            x = g_img_x
            y = g_img_y
            user32.SetCursorPos(x,y)
            user32.mouse_event(0x2,0,0,0,0) #クリックする
            sleep(wait)
            user32.mouse_event(0x4,0,0,0,0) #クリックを放す
            return(True)
        else:
            return(False)


#指定座標にカーソル移動
#chkimg実行後に引数無しで実行した場合、img座標に移動
#x : x座標
#y : y座標
def mmv(x = -1,y = -1):
    if(x != -1 and y != -1):
        user32.SetCursorPos(x,y)
        return(True)
    else:
        if(g_img_x != -1 and g_img_y != -1):
            x = g_img_x
            y = g_img_y
            user32.SetCursorPos(x,y)
            return(True)
        else:
            return(False)

#キーコードを指定してキー入力
#keycode : キーコード
def kbd(keycode):
    user32.keybd_event(keycode,0,0,0)
    sleep(0.2)
    user32.keybd_event(keycode,0,0x2,0)

#ウィンドウ表示
#width : ウィンドウ横幅
#height : ウィンドウ縦幅
#name : ウィンドウタイトル
def winshow(width,height,name = "main"):
    zr = np.zeros((width,height,3),np.uint8)
    cv2.imshow(name,zr)

#ウィンドウを全て閉じる
def winclose():
    cv2.destroyAllWindows()

#ウィンドウ上でキー入力があったか
#key : opencvのキーコード 27がesc
#wait : 待機秒　0が無限待ち　*ミリ秒指定不可
def getkeystate(key,wait = 1):
    if(cv2.waitKey(wait)==key):
        return(True)
    else:
        return(False)

#処理待機
#wait : ミリ秒指定可
def sleep(wait):
    time.sleep(wait)

#getid - EnumWindows用コールバック関数
def proc(hwnd,ar):
    title = winxpgui.GetWindowText(hwnd)
    if ar[0] in title:
        #print hwnd, title
        ar[1].append(hwnd)
    return 1

#titleをウィンドウタイトルに含むウィンドウのウィンドウハンドルを返します
#title : 検索に使うタイトル
#n : 何番目のウィンドウハンドルを返すか
def getid(title,n = 0):
    hwnds = []
    winxpgui.EnumWindows(proc,[title,hwnds])
    print hwnds
    return hwnds[n]

#直接クリック情報を送ります
#hwnd : ウィンドウハンドル
#x : x座標
#y : y座標
#pbtn : 送るクリック情報 L or lで左クリック,R or rで右クリック
def PostClick(hwnd,x,y,pbtn = "L"):
    #WM_LBUTTONDOWN = 0x0201
    #WM_LBUTTONUP = 0x0202
    #WM_RBUTTONDOWN = 0x0204
    #WM_RBUTTONUP = 0x0205
    if pbtn == "L" or "l":
        sbtn = 0x0201
        ebtn = 0x0202
    elif pbtn == "R" or "r":
        sbtn = 0x0204
        ebtn = 0x0205

    #lParam <= x,y
    point = y * int('0xffff',16) + x
    winxpgui.PostMessage(hwnd, sbtn, 0, point) # button down
    m.sleep(0.2)
    winxpgui.PostMessage(hwnd, ebtn, 0, point)   # button up
    
