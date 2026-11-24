# Luz de emergencia - casa com 4 comodos (ESP32 + 4 LDRs + 4 LEDs, Wokwi, MicroPython)
# Cada comodo tem um sensor independente (device_id proprio).
# Sem luz no comodo -> LED do comodo acende e alerta = true.
# Conexao MQTT/TLS no mesmo modelo da Aula 13 (mqtt_client.py + CA do EMQX).
# Dependencias na raiz do projeto Wokwi: config.py, ca_cert.py, mqtt_client.py
import network, time, ssl, ntptime, os, binascii
from machine import Pin, ADC
from mqtt_client import MQTTClient
from ca_cert import ca_der
from config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, TOPIC, INTERVALO_S

LIMITE_ALERTA = 30      # % abaixo disso = escuro
INVERTER_LDR = True

# nome, device_id (usado pelo painel), pino do LDR (AO), pino do LED
COMODOS = [
    ("sala",     "esp32-sala",     34, 15),
    ("cozinha",  "esp32-cozinha",  35, 2),
    ("quarto",   "esp32-quarto",   32, 4),
    ("banheiro", "esp32-banheiro", 33, 5),
]

CLIENT_ID = ("esp32-casa-" + binascii.hexlify(os.urandom(4)).decode()).encode()

sensores = []
for nome, dev, pin_ldr, pin_led in COMODOS:
    adc = ADC(Pin(pin_ldr))
    adc.atten(ADC.ATTN_11DB)          # le de 0 a 3.3V (0..4095)
    sensores.append((nome, dev, adc, Pin(pin_led, Pin.OUT)))


def conecta_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect("Wokwi-GUEST", "")
    while not wlan.isconnected():
        time.sleep(0.3)
    print("WiFi ok", wlan.ifconfig()[0])
    ntptime.timeout = 3
    # relogio correto: necessario para validar o certificado. Tenta varias vezes
    # porque o servidor de horas as vezes demora a responder no Wokwi.
    for tentativa in range(1, 11):
        try:
            ntptime.settime()
            break
        except OSError as e:
            print("NTP falhou (%d/10): %s" % (tentativa, e))
            time.sleep(2)
    else:
        raise OSError("Nao foi possivel sincronizar o relogio")
    print("Relogio sincronizado", time.gmtime()[:6])


def conecta_mqtt():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_verify_locations(cadata=ca_der())
    cli = MQTTClient(client_id=CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT,
                     user=MQTT_USER.encode(), password=MQTT_PASSWORD.encode(),
                     keepalive=60, ssl=ctx)
    cli.connect(timeout=5)
    print("MQTT CONECTADO")
    return cli


def ler_luminosidade(adc):
    soma = 0
    for _ in range(10):            # media de 10 leituras
        soma += adc.read()
        time.sleep_ms(5)
    pct = int(soma / 10 * 100 / 4095)   # converte para %
    if INVERTER_LDR:
        pct = 100 - pct
    return max(0, min(100, pct))        # validacao: limita entre 0 e 100


conecta_wifi()
cliente = None

while True:
    for nome, dev, adc, led in sensores:
        lum = ler_luminosidade(adc)
        alerta = lum < LIMITE_ALERTA
        led.value(1 if alerta else 0)       # escuro -> LED do comodo acende

        msg = '{"device_id":"%s","grandeza":"luminosidade","valor":%d,"unidade":"%%","alerta":%s}' % (
            dev, lum, "true" if alerta else "false")
        print(nome, msg)

        try:
            if cliente is None:
                cliente = conecta_mqtt()
            cliente.publish(TOPIC, msg)
            print("PUBLICADO", nome)
        except Exception as e:
            print("erro MQTT:", e)
            try:
                cliente.sock.close()
            except Exception:
                pass
            cliente = None                  # tenta reconectar no proximo ciclo

    time.sleep(INTERVALO_S)
