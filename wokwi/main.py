# Luz de emergencia - ESP32 + LDR + LED (Wokwi, MicroPython)
# Sem luz -> LED acende e alerta = true
import network, time
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# ---------- CONFIGURACAO (NAO coloque senhas reais no GitHub) ----------
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
MQTT_HOST = "SEU_HOST.emqxsl.com"      # preencher com o host do EMQX
MQTT_PORT = 8883                       # porta TLS
MQTT_USER = "USUARIO_EMQX"
MQTT_PASS = "SENHA_EMQX"
TOPICO    = "grupo-luz-emergencia/luminosidade"   # topico proprio do grupo
DEVICE_ID = "esp32-luz-01"

PIN_LED = 15            # pino onde o LED esta ligado
PIN_LDR = 34            # pino AO do sensor de luz
LIMITE_ALERTA = 30      # % abaixo disso = escuro
INTERVALO_S = 5         # intervalo de coleta (segundos)
INVERTER_LDR = True   
# -----------------------------------------------------------------------

led = Pin(PIN_LED, Pin.OUT)
ldr = ADC(Pin(PIN_LDR))
ldr.atten(ADC.ATTN_11DB)   # le de 0 a 3.3V (0..4095)


def conecta_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        time.sleep(0.3)
    print("WiFi ok")


def conecta_mqtt():
    cli = MQTTClient(DEVICE_ID, MQTT_HOST, port=MQTT_PORT,
                     user=MQTT_USER, password=MQTT_PASS, ssl=True)
    cli.connect()
    print("MQTT ok")
    return cli


def ler_luminosidade():
    soma = 0
    for _ in range(10):            # media de 10 leituras
        soma += ldr.read()
        time.sleep_ms(5)
    pct = int(soma / 10 * 100 / 4095)   # converte para %
    if INVERTER_LDR:
        pct = 100 - pct
    return max(0, min(100, pct))        # validacao: limita entre 0 e 100


conecta_wifi()
cliente = None

while True:
    lum = ler_luminosidade()
    alerta = lum < LIMITE_ALERTA
    led.value(1 if alerta else 0)       # escuro -> LED acende

    msg = '{"device_id":"%s","grandeza":"luminosidade","valor":%d,"unidade":"%%","alerta":%s}' % (
        DEVICE_ID, lum, "true" if alerta else "false")
    print(msg)

    try:
        if cliente is None:
            cliente = conecta_mqtt()
        cliente.publish(TOPICO, msg)
    except Exception as e:
        print("erro MQTT:", e)
        cliente = None                  # tenta reconectar no proximo ciclo

    time.sleep(INTERVALO_S)
