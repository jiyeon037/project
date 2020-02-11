# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# pip3 install pyserial
# 파이썬에서 연결가능한 시리얼포트를 검색하고 알아서 연결함.
# 
# https://www.gpsinformation.org/dale/nmea.htm
# GPS 프로토콜 : DMM ( 도 및 십진수 분 )
import serial
from serial.tools import list_ports

# GUI 표현해주는 내용
import pygame
import time

# 서버쪽에 데이터 전
import requests

#라즈베리파이 GPIO
import RPi.GPIO as GPIO
GPIO_SIGNAL = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)

pygame.init()
window = pygame.display.set_mode((1000, 656))
window.fill((255, 255, 255))
pygame.display.update()

LAT= ''
LONG=''
H=''
T=''
ALARM = ''
send_flag = False


def drow_ice_image():
    window.blit(pygame.image.load("2.png"), (0, 0))
    pygame.display.update()


def drow_image():
    window.blit(pygame.image.load("1.png"), (0, 0))
    pygame.display.update()


        
port_lists = list_ports.comports()
for i in range(len(port_lists)):
    print(port_lists[i][0])
sel_num = 0
ser = serial.Serial(port_lists[sel_num][0],9600,timeout=1)


drow_image()

while True:
    data_list = list()
    temp_data = str(ser.readline())    
    print(temp_data)
    temp_data = str(temp_data)
    if GPIO.input(GPIO_SIGNAL)==0 or temp_data == 'B\r\n':
        drow_image()
        pygame.display.update()

        if send_flag == False:
            send_flag = True
            print("SEND TO SERVER")
            message = 'B'
            ser.write(message.encode())
           
        
    else:
        drow_ice_image()
        send_flag = False
        pygame.display.update()


        
GPIO.cleanup()
pygame.quit()
quit()
