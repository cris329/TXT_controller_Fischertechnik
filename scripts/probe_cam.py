
import cv2
c=cv2.VideoCapture(0)
print("opened", c.isOpened())
r,f=c.read()
print("frame", r, None if f is None else f.shape)
c.release()
import ft, ftlock
ftlock.notify("R")
txt=ft.fttxt2("auto")
s=txt.servo(1)
s.setLevel(250)
print("servo set 250")
