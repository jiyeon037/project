import os
import cv2
import numpy as np
import math
'''
1. 웹캠 이미지 리드
2. 그레이스케일로 변환
3. 픽셀 값의 평균으로 필터링: 평균값보다 크면 255(white), 작으면 0(black)
4. ROI 구역 설정 후 ROI 부분만 출력
'''

def im_trim1(img): #함수로 만든다
    x = 100; y = 100; #자르고 싶은 지점의 x좌표와 y좌표 지정
    w = 200; h = 200; #x로부터 width, y로부터 height를 지정
    img_trim1 = img[y:y+h, x:x+w] #trim한 결과를 img_trim에 담는다
    #cv2.imwrite('org_trim.jpg',img_trim) #org_trim.jpg 라는 이름으로 저장
    return img_trim1 #필요에 따라 결과물을 리턴

def im_trim2(img): #함수로 만든다
    x = 70; y = 185; #자르고 싶은 지점의 x좌표와 y좌표 지정
    w = 200; h = 200; #x로부터 width, y로부터 height를 지정
    img_trim2 = img[y:y+h, x:x+w] #trim한 결과를 img_trim에 담는다
    #cv2.imwrite('org_trim.jpg',img_trim) #org_trim.jpg 라는 이름으로 저장
    return img_trim2 #필요에 따라 결과물을 리턴
    
def resize(img, ratio, dsize=None, dst=None):
    return cv2.resize(img, dsize, dst, ratio, ratio, interpolation=cv2.INTER_AREA)

def grayscale(img): # 그레이스케일로 이미지 변환
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def pixel_value_average(img): # 픽셀 값의 평균 계산
    sum = 0
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            sum += img[i,j]
    pixel_N = img.shape[0] * img.shape[1]
    average = sum/pixel_N
    return average

def Filter(img, value = 0): # 픽셀 값 평균을 기준으로 필터링
    average = pixel_value_average(img)

    if value == 0:
        ret,img_filter = cv2.threshold(img, average, 255, cv2.THRESH_BINARY)
    else:
        ret,img_filter = cv2.threshold(img, value, 255, cv2.THRESH_BINARY)
       
    return img_filter

def count_pixel(img): # 픽셀 값이 0인 픽셀 COUNT
    number = 0
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if img[i,j] == 0:
                number += 1
    return number

def pixel_ratio(img1, img2): # 픽셀 값 0 비율 계산
    
    if count_pixel(img1) < count_pixel(img2):
        ratio = count_pixel(img1)/count_pixel(img2)
    else:
        ratio = count_pixel(img2)/count_pixel(img1)
    return ratio

def vertices_multicam(img, distance, width, direction, angle = 54): 
    '''
    관심 영역 설정 - 거리에 따른 roi 설정
    height = img.shape[0]
    width = img.shape[1]
    distance = 카메라와 측정 대상까지의 거리
    width = 카메라 간격
    !!! distance와 width의 단위는 같아야한다. !!!
    direction = 카메라 위치(0: Right, 1: Left)
    angle = 카메라 화각
    '''
    imshape = img.shape 
    angle = angle * (math.pi/180)
    F = int(width / (2*distance*math.tan(angle)))

    if direction: # Left = 1
        lower_left = [imshape[1]*F, imshape[0]]
        lower_right = [imshape[1], imshape[0]]
        higher_left = [imshape[1]*F, 0]
        higher_right = [imshape[1], 0]
    else: # Right = 0
        lower_left = [0,imshape[0]]
        lower_right = [imshape[1]*(1 - F), imshape[0]]
        higher_left = [0, 0]
        higher_right = [imshape[1]*(1 - F), 0]
    
    vertices = [np.array([lower_left, lower_right, higher_right, higher_left], dtype = np.int32)]
    return vertices

def vertices_road(img): # 관심 영역 설정 - 사다리꼴(도로 부분 할당)
    imshape = img.shape 
        
    lower_left = [0, imshape[0]]
    lower_right = [imshape[1], imshape[0]]
    higher_left = [imshape[1]/2-imshape[1]/8, 5*imshape[0]/8]
    higher_right = [imshape[1]/2+imshape[1]/8, 5*imshape[0]/8]
 
    vertices = [np.array([lower_left, lower_right, higher_right, higher_left], dtype = np.int32)]
    return vertices

def region_of_interest(img, vertices, color3=(255,255,255), color1=255): # ROI 셋팅
 
    mask = np.zeros_like(img) # mask = img와 같은 크기의 빈 이미지
    
    if len(img.shape) > 2: # Color 이미지(3채널)라면 :
        color = color3
    else: # 흑백 이미지(1채널)라면 :
        color = color1
        
    # vertices에 정한 점들로 이뤄진 다각형부분(ROI 설정부분)을 color로 채움 
    cv2.fillPoly(mask, vertices, color)
    
    # 이미지와 color로 채워진 ROI를 합침
    roi_image = cv2.bitwise_and(img, mask)
    return roi_image

def show_convert_video(frame, CAM, direction): # frame과 window창 이름 설정
    vertice_set = vertices_multicam(frame, 20, 3, direction)
    #vertice_set = vertices_road(frame)
    frame = grayscale(frame)
    frame = Filter(frame)
    frame = region_of_interest(frame, vertice_set)
    '''
    h, w = frame.shape[:2]
    M1 = cv2.getRotationMatrix2D((h / 2, w / 2), 90, 1) 
    frame = cv2.warpAffine(frame, M1, (h, w)) 
    '''
    cv2.imshow( CAM , frame)

video_capture_0 = cv2.VideoCapture(0) # 노트북 내장 웹캠
video_capture_1 = cv2.VideoCapture(1) # 외장형 USB 웹캠1
video_capture_2 = cv2.VideoCapture(2) # 외장형 USB 웹캠2

ret0, frame0 = video_capture_0.read()
ret1, frame1 = video_capture_1.read()
ret2, frame2 = video_capture_2.read()

while True:
    ret0, frame0 = video_capture_0.read()
    ret1, frame1 = video_capture_1.read()
    #ret2, frame2 = video_capture_2.read()

    if (ret0 and ret1):
        show_convert_video(frame0, "CAM0", 0)
        show_convert_video(frame1, "CAM1", 1)
        #print(pixel_ratio(frame0, frame1))
        print(pixel_ratio(frame0, frame1))
    
    #if(ret2):
        #show_convert_video(frame2, "CAM2")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # 사용자가 키보드 q 누르면 Opencv 종료
    
video_capture_0.release()
video_capture_1.release()
video_capture_2.release()
cv2.destroyAllWindows() # 리소스 반환