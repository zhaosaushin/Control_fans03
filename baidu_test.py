# -*- coding: utf-8 -*-
"""
Created on Thu May 25 16:49:03 2023

@author: zhaoxiaoxin
"""

import serial
import modbus_tk
import time
import wave
import json
import webbrowser
import requests
import base64
import webbrowser
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from aip import AipSpeech
from pyaudio import PyAudio, paInt16




framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes
FILEPATH = 'speech.wav'

def getToken():
    #获取我的token
    APP_ID = '33977995'
    API_KEY = 'ZhuX9xSZ14w4BPvV7nY44uzR'
    SECRET_KEY = 'ZGMGAoPqi7XuP1bxMoklS6IilGq57MPs'
    base_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s"
    host = base_url % (API_KEY, SECRET_KEY)
    res = requests.post(host)
    return res.json()['access_token']#用json处理返回数据 OR token = json.loads(res.text)["access_token"]

def save_wave_file(filepath, data):
    #设置声音文件格式
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b''.join(data))
    wf.close()

def my_record():
    #录音
    pa = PyAudio()
    #打开一个新的音频stream
    stream = pa.open(format=paInt16, channels=channels,
                     rate=framerate, input=True, frames_per_buffer=num_samples)
    my_buf = [] #存放录音数据

    t = time.time()
    print('-------正在录音-------')
 
    while time.time() < t + 3:  # 设置录音时间（秒）
    	#循环read，每次read 2000frames
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
    print('录音结束.')
    save_wave_file(FILEPATH, my_buf) #设置录音文件格式
    stream.close()

def get_audio(file):
    #音频转码
    with open(file, 'rb') as f:
        data = f.read()
    return data

def speech2text(speech_data, token, dev_pid=1537):
    FORMAT = 'wav'
    RATE = '16000'
    CHANNEL = 1
    CUID = '16d3b6c3f20048a1b11ffd8543340ca8' #用户唯一标识
    SPEECH = base64.b64encode(speech_data).decode('utf-8')
    #JSON 格式 POST 上传本地文件
    data = {
        'format': FORMAT,
        'rate': RATE,
        'channel': CHANNEL,
        'cuid': CUID,
        'len': len(speech_data),
        'speech': SPEECH,
        'token': token,
        'dev_pid':dev_pid
    }
    url = 'http://vop.baidu.com/server_api'
    headers = {'Content-Type': 'application/json'}
    # r=requests.post(url,data=json.dumps(data),headers=headers)
    print('正在识别...')
    #向百度发送语音识别请求
    r = requests.post(url, json=data, headers=headers)
    Result = json.loads(r.text)

    if Result["err_msg"] == "success.":
        message = ''.join(Result['result'])
        print('RETURNED: ' + message)
        return Result['result']
    else:
        print("RETURNED: Recognition failure")
        return -1

    
    #结果通过result返回
    """
    Result = r.json()
    if 'result' in Result:
        return Result['result'][0]
    else:
        return Result
    """

def ConnectRelay(PORT):  
 """
    此函数为连接串口继电器模块，为初始函数，必须先调用 
    :param PORT: USB-串口端口，需要手动填写，须在计算机中手动查看对应端口 
    :return: >0 连接成功，<0 连接超时
 """
 try:
  master = modbus_rtu.RtuMaster(serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='E', stopbits=1))
  master.set_timeout(5.0)
  master.set_verbose(True)
# 读输入寄存器
# c2s03 设备默认 slave=2, 起始地址=0, 输入寄存器个数 2
  master.execute(2, cst.READ_INPUT_REGISTERS, 0, 2)
# 读保持寄存器
# c2s03 设备默认 slave=2, 起始地址=0, 保持寄存器个数 1
  master.execute(2, cst.READ_HOLDING_REGISTERS, 0, 1)
# 这里可以修改
#需要读取的功能码
# 没有报错，返回 1
  response_code = 1
 except Exception as exc:
  print(str(exc))
# 报错，返回<0 并输出错误
  response_code = -1
  master = None

 return  response_code, master


def Switch(master, ACTION):
 """
 此函数为控制继电器开合函数，如果 ACTION=ON 则闭合，如果如果 ACTION=OFF 则断开。
 :param master: 485 主机对象，由 ConnectRelay 产生
 :param ACTION: ON 继电器闭合，开启风扇；OFF 继电器断开，关闭风扇。
 :return: >0 操作成功，<0 操作失败
    # 写单个线圈，状态常量为 0xFF00，请求线圈接通
    # c2s03 设备默认 slave=2, 线圈地址=0, 请求线圈接通即 output_value 不22 等于 0
    # 写单个线圈，状态常量为 0x0000，请求线圈断开
    # c2s03 设备默认 slave=2, 线圈地址=0, 请求线圈断开即 output_value 等
于 0
    # 没有报错，返回 1
    # 报错，返回<0 并输出错误
 """
 try:
     if "on" in ACTION.lower():
         master.execute(2, cst.WRITE_SINGLE_COIL, 0, output_value=1)
     else:
         master.execute(2, cst.WRITE_SINGLE_COIL, 0, output_value=0)
         response_code = 1
 except Exception as exc:
         print(str(exc))
 response_code = -1
 return response_code

if __name__ == '__main__':
    
    ser = serial.Serial("COM3")
    ser.close()
    result = []
    devpid = 1536 #识别普通话
    code1,master = ConnectRelay("COM3")
    if code1 == -1:
        print("初始化失败...")
   
    while 1:
        my_record()

        TOKEN = getToken()
        speech = get_audio(FILEPATH)

        result = speech2text(speech, TOKEN, int(devpid))
        print(result)

        str = ''.join(result) 
        if str == '打开风扇':
            code2 = Switch(master, "on")
            if code2 < 0:
                print("输出错误...")
                
        elif str == '关闭风扇':
            code2 = Switch(master, "off")
         #   if code2 < 0:
          #      print("输出错误...")
                    
        elif str == '退出系统':
            break
        else:
            print("指令错误，请重新输入语音...")
            
        result.clear()
        
        
    


