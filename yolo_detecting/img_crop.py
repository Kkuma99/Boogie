import argparse
import time
from sys import platform
import cv2
import numpy as np
import os
#from models import *
#from utils.datasets import *
#from utils.utils import *
from PIL import Image
from PIL import ImageDraw
import random
import glob
import matplotlib.pyplot as plt
#import time
Imagepath = '/data1/pothole/Dataset_2(Complex)/Train data/Positive data/'
Trainpath = '/data1/pothole/Dataset_2(Complex)/complexTrainFullSizeAllPotholes.txt'

class random_crop:
    def img_Crop(self):
        global len_box

        files = glob.glob(Imagepath + '*.JPG')
        #print(files)
        files = random.sample(files,10) # no same image, ramdomly import 400 images
        #print(len(files))
        
        for x in range(0,len(files)):
            image
            images = Image.open(files[x]) # img read

            # xywh save
            names = files[x].split('.')
            name = names[0]
            name = name.split('/')
            img_name = name[-1]
            print(img_name)

            f = open(Trainpath,'r')
            while True:
                lines = f.readline()
                if not lines:
                    break
                # finding datas
                if img_name in lines: # changed
                    print(lines)
                    datas = lines.split(' ')
                    i=0
                    box_x1 =[]
                    box_y1 =[]
                    box_width =[]
                    box_height =[]
                    #print(datas)
                    while i < int(datas[3]):
                        box_x1.append(int(datas[4*(i+1)]))
                        box_y1.append(int(datas[4*(i+1)+1]))
                        box_width.append(int(datas[4*(i+1)+2]))
                        box_height.append(int(datas[4*(i+1)+3]))
                        #print(box_height)
                        i += 1
                    len_box = int(datas[3])
                    #print(box_width)
            f.close()

            #getting random image
            q=0
            list_check_x1 = []
            list_check_y1 = []
            list_check_x2 = []
            list_check_y2 = []
            while q < 5:
                a=1
                while a:
                    #random cropping
                    list_x=[]
                    list_y=[]

                    x1= random.randint(0,3200)
                    y1= random.randint(0,2200)

                    rand_x = random.randint(26,(3680-x1)//16)
                    rand_y = random.randint(62,(2760-y1)//9)
                    k = min(rand_x,rand_y)

                    x2 = x1 + 16*k
                    y2 = y1 + 9*k
                
                    crop_img = images.crop((x1,y1,x2,y2))

                    # check if its the same cropping image
                    for i in range(q):
                        if (list_check_x1[i] == x1) and (list_check_y1[i] == y1) and (list_check_x2[i] == x2) and (list_check_y2[i] == y2):
                            a=1
                        else:
                            pass

                    # cropping rate check
                    for i in range(len_box):
                        area_rate = (float(box_width[i])*float(box_height[i]))/(16*k*9*k)
                        if area_rate >= 0.00009:
                            pass
                        else:
                            a=1

                    # cropping option
                    # cropping object should not be so small, cropped image should contain complete one object

                    for i in range(len_box):
                        cnt = 0
                        if (x1<=box_x1[i] and x2>=box_x1[i]+box_width[i] and y1<=box_y1[i] and y2>=box_y1[i]+box_height[i]):
                            cnt += 1
                        elif (x1 >= box_x1[i]+box_width[i]) or (x2 <= box_x1[i]) or (y1 >= box_y1[i]+box_height[i]) or (y2 <= box_y1[i]):
                            cnt += 0
                        else:
                            a=1
                    
                    if cnt == 0 :
                        a=1

                    # data save
                    else:
                        for i in range(len_box):
                            if(x1<=box_x1[i] and x2>=box_x1[i]+box_width[i] and y1<=box_y1[i] and y2>=box_y1[i]+box_height[i]):
                                train_data = '0 '
                                data= img_name+ q + '.txt'
                                f1 = open('/data1/pothole/Dataset_2(Complex)/label/'+data,'a')
                                x1_re = box_x1[i] - x1
                                y1_re = box_y1[i] - y1
                                x2_re = box_x1[i] + box_width[i] - x1
                                y2_re = box_y1[i] + box_height[i] - y1

                                x_cen_r = ((x2_re+x1_re)/2)
                                y_cen_r = ((y2_re+y1_re)/2)
                                train_data = train_data+str(x_cen_r)+' '+str(y_cen_r)+' '+str(box_width[i])+' '+str(box_height[i])+'\n'
                                print(train_data)
                                f1.write(train_data)
                                f1.close()
                        '''
                        draw_img = ImageDraw.Draw(crop_img)
                        x1, y1= x1_re, y1_re
                        x2, y2= x2_re, y2_re
                        draw_img.rectangle(((x1, y1), (x2, y2)), outline=(0, 0, 255), width=2)
                        image_numpy = np.array(crop_img)
                        plt.imshow(image_numpy)
                        plt.show()
                        '''

                        output='/data1/pothole/Dataset_2(Complex)/output/' + img_name + q
                        with open(output, 'wb') as out:
                            crop_img.save(out,'JPEG')

                        list_check_x1.append(x1)
                        list_check_y1.append(y1)
                        list_check_x2.append(x2)
                        list_check_y2.append(y2)
                        q += 1
                        break
                

if __name__ == '__main__':
    len_box = 0
    a = random_crop()
    a.img_Crop()