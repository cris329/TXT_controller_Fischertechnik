
import os, glob
print('video devices', glob.glob('/dev/video*'))
print('v4l', os.listdir('/dev')[:50])
import ft
txt=ft.fttxt2('auto')
s=txt.servo(1)
print('servo conn', getattr(s,'conn',None), 'val', getattr(s,'val',None))
# try setLevel values
for meth in ['setLevel','setSpeed','pwm_set','setLevelUs']:
    print('has', meth, hasattr(s,meth))
m1=txt.motor(1)
print('motor1', m1)
try:
    import ftlock
    print('ftlock', dir(ftlock))
    ftlock.notify('R')
    print('ftlock notify R ok')
except Exception as e:
    print('ftlock', e)
# list usb
os.system('lsusb 2>/dev/null | head')
os.system('ls -l /dev/video* 2>/dev/null')
os.system('id; groups')
