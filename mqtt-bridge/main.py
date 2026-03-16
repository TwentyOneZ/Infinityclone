import paho.mqtt.client as mqtt
import json
import os

# Configurações do Broker MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "cerise.freeddns.org")
MQTT_PORT = int(os.getenv("MQTT_PORT", 30001))
MQTT_USER = os.getenv("MQTT_USER", "infinitwin_user")
MQTT_PASS = os.getenv("MQTT_PASS", "IwtLab#2025!")

# Tópicos de entrada (sem o prefixo do ditto)
INPUT_TOPICS = [
    ("/painelfotovoltaico.gerador/#", 0),
    ("/painelfotovoltaico.referencia/#", 0),
    ("/painelfotovoltaico.node/#", 0)       # <-- NOVO: Escuta o estado agregado (all) e os comandos (pvConfig)
]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao Broker MQTT com sucesso!")
        client.subscribe(INPUT_TOPICS)
        print(f"📥 Inscrito nos tópicos: {[t[0] for t in INPUT_TOPICS]}")
    else:
        print(f"❌ Falha ao conectar. Código: {rc}")

def on_message(client, userdata, msg):
    try:
        # ---- PREVENÇÃO DE LOOP INFINITO ----
        # Ignora a potência estimada gerada pelo próprio backend (evita o spam)
        if "estimatedPower" in msg.topic:
            return
        # ------------------------------------

        # Decodifica o payload de entrada
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # O novo tópico precisa ter o prefixo esperado /ditto/events/
        out_topic = f"/ditto/events{msg.topic}"
        
        # Separa o namespace do thingId real do equipamento
        original_thing_id = payload.get("thingId", "")
        if ":" in original_thing_id:
            namespace, thing_id = original_thing_id.split(":", 1)
        else:
            namespace = ""
            thing_id = original_thing_id
            
        # Constrói o novo payload
        out_payload = {
            "namespace": namespace,
            "thingId": thing_id,
            "sensorData": payload.get("sensorData", {})
        }
        
        # Publica no tópico formatado
        client.publish(out_topic, json.dumps(out_payload), qos=0)
        print(f"🔄 Convertido e republicado -> Tópico: {out_topic}")
        
    except json.JSONDecodeError:
        print(f"⚠️ Payload ignorado (não é um JSON válido) no tópico {msg.topic}")
    except Exception as e:
        print(f"⚠️ Erro ao processar mensagem no tópico {msg.topic}: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"🔌 Conectando ao MQTT Broker {MQTT_BROKER}:{MQTT_PORT}...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"❌ Erro fatal de conexão: {e}")