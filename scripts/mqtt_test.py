
import paho.mqtt.client as mqtt, time
got=[]
def on_msg(c,u,m):
    got.append(m.topic+':'+m.payload.decode('utf-8','ignore'))
    print('DEV', m.topic, m.payload)
c=mqtt.Client('dev-test')
def on_conn(c,u,f,rc):
    print('dev conn', rc)
    c.subscribe('futball/#')
c.on_connect=on_conn
c.on_message=on_msg
c.connect('127.0.0.1',2883,60)
c.loop_start()
time.sleep(1)
c.publish('futball/status', 'hello-from-device', retain=True)
time.sleep(8)
print('GOT', got)
c.loop_stop(); c.disconnect()
