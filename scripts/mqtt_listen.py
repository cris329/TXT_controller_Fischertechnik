
import paho.mqtt.client as mqtt, time
def on_msg(c,u,m):
    print('BRIDGE_GOT', m.topic, m.payload.decode())
c=mqtt.Client('bridge-listen')
c.on_connect=lambda c,u,f,rc: c.subscribe('futball/#')
c.on_message=on_msg
c.connect('127.0.0.1',2883,60)
c.loop_start()
time.sleep(12)
c.loop_stop(); c.disconnect()
