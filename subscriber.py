import paho.mqtt.client as mqtt
import MySQLdb
import datetime
import json

mensaje = ""
db = MySQLdb.connect(host = "192.168.0.106",
                     user="admin",
                     passwd ="1234",
                     db = "sensores")
cursor = db.cursor()
MQTT_HOST="192.168.0.190"
MQTT_PORT=1883
MQTT_KEEPALIVE_INTERVAL=5
MQTT_TOPIC="counter"

print 'database connected'
def on_connect(mosq,obj,rc):
    print 'connected '+ str(rc)
    mqttc.subscribe(MQTT_TOPIC, 0)
def on_subscribe(mosq,obj,mid,granted_qos):
    print "subscribe to MQQT topic"
def on_message(mosq,obj,msg):
    mensaje = msg.payload
    json_decoded = json.loads(mensaje)
    dia = datetime.datetime.now()
    counter_id = json_decoded['id']
    origen = json_decoded['entrada']
    destino = json_decoded['salida']
    contador = json_decoded['counter']
    moto = json_decoded['moto']
    auto = json_decoded['auto']
    camion = json_decoded['camion']
    print dia, mensaje
    try:
        cursor.execute("""INSERT INTO registro VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                       (None,counter_id,dia,origen,destino,contador,moto,auto,camion))
        db.commit()
        print 'hecho'
    except :
        print 'no hecho'
        db.rollback()
        
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect=on_connect
mqttc.on_subscribe= on_subscribe
mqttc.connect(MQTT_HOST,MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
mqttc.loop_forever()
db.close()
