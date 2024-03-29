import gc, os, math, json, usocket as socket
from time import sleep_ms, ticks_ms
from umqtt.simple2 import MQTTClient
try:
    import network_functions as nf
except:
    pass

#mqtt settings
#hostname_mqtt_broker ='test.mosquitto.org'
hostname_mqtt_broker = '192.168.178.36'
node_name = 'esp32cam-1'
topic = 'iotgg-speedtest'
client = None

def publish_buffer_mqtt(topic, buf, bs, write):

    try:
        numBlocks = math.ceil((len(buf)/bs))
        msgInfo = {'type':'mqtt_camera_image', 'length':len(buf), 'block_size':bs,
                   'num_blocks':numBlocks, 'write_to_file':write }
        msgStr = json.dumps(msgInfo, separators=(',', ':'))
        print(f"publish_buffer_mqtt: {msgStr}")
        # publishing info msg
        client.publish(topic, msgStr, qos=1)
        # publishing buffer in chunks:
        for i in range (numBlocks):
            begin = i*bs
            end = begin+bs
            if end >= len(buf):
                end = len(buf)
            block = buf[begin:end]
            client.publish(topic, block, qos=1)
            #sleep_ms(0) #comment out on ESP32CAM!!
            #print(f"publish_buffer_mqtt: published block {i} of {numBlocks}")
        print("publish_buffer_mqtt: publishing finished")
    except Exception as err:
        print(f"publish_buffer_mqtt: Exc: {err=}, {type(err)=}")
        raise


def send():
    global topic
    for i in range(21):
        buf = bytes(2**i)
        try:
            for block_size in (512, 1024, 2048):
                publish_buffer_mqtt(topic, buf, block_size, False)
                #sleep_ms(10)
            #for block_size in (512, 1024, 2048):
            #    publish_buffer_mqtt(topic, buf, block_size, True)
                #sleep_ms(10)
        except Exception as err:
            print(f'error sending : Exc: {err=}, {type(err)=}')

        except KeyboardInterrupt:
            print("loop: Keyboard Interrupt")
            break
        #sleep_ms(10)

#connect to wlan
try:
    nf.wlan()
except:
    pass

#create mqtt client
client=MQTTClient(node_name, hostname_mqtt_broker, 1883)
client.connect()
send()
