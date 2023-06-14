# -*- coding: utf-8 -*-
"""
Created on Mon May 22 16:45:01 2023

@author: zhaoxiaoxin
"""
import serial
import speech
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import speech_recognition as sr

def ConnectRelay(PORT):
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


"""
r = sr.Recognizer()

mic = sr.Microphone()

while 1:

    print("\n开始录音...")

    with mic as source:

        r.adjust_for_ambient_noise(source)

        audio = r.listen(source)

        audio_data = audio.get_wav_data(convert_rate=16000)#降噪

    print("\n正在识别...")
   

    text = get_text(audio_data)

    print(f"\n{text}")
   
    print('文本内容：',r.recognize_sphinx(mic,language='zh_CN',))
"""
"""
code,master = ConnectRelay("COM3")
print(master)
Switch(master, "on")
"""
"""
flag1 = tuple(map(int, flag))
if  flag1 > 0 : 
    print("串口继电器连接成功...")
    
else:
    print("串口继电器连接超时...")
    
    """
    
if __name__ == '__main__':
    ser = serial.Serial("COM3")
    ser.close()
    code1,master = ConnectRelay("COM3")
    if code1 == -1:
        print("初始化失败...")
    speech.say("请开始讲话")

    while 1:
        usay = speech.input()
        speech.say("语音收集完成")
        print(usay)
        if usay == "开":
            code2 = Switch(master, "on")
           # if code2 < 0:
             #   print("输出错误...")
            
        elif usay == "关掉":
            flag2 = Switch(master, "off")
           # if code2 < 0:
               # print("输出错误...")
            
        else:
            print("指令错误，请重新输入语音...")
            


        
      
        
        





