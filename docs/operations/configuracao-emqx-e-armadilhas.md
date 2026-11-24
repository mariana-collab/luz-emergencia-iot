---
title: Configuração do EMQX e armadilhas
type: operation
created: 2026-11-23
updated: 2026-11-23
sources:
  - code: wokwi/main.py
  - code: wokwi/ca_cert.py
  - code: wokwi/config.py
  - code: supabase/functions/ingest/index.ts
  - code: supabase/functions/api/index.ts
verified_at: 5a39e5a
---

# Configuração do EMQX e armadilhas

Passo a passo completo em `docs/emqx.md`. Esta página guarda os **erros reais** que apareceram ao montar o fluxo, para não repeti-los. Contexto em [[arquitetura-geral]].

## Valores que precisam bater entre as peças

| Valor | Onde aparece |
|---|---|
| Tópico `grupo-luz-emergencia/luminosidade` | permissão do usuário, `FROM` da regra, `TOPIC` no `wokwi/config.py` |
| Usuário `esp32_luz01` | Authentication do EMQX, `MQTT_USER` no `wokwi/config.py` |
| Header `x-api-key` | ação do EMQX e `supabase/functions/ingest/index.ts:13` |
| URL Path `/functions/v1/ingest` | ação do EMQX (não vai na URL do conector) |

Nenhuma senha vai para o GitHub: a senha MQTT, o `INGEST_KEY` e os tokens ficam só no EMQX, no Supabase e no projeto Wokwi.

## Armadilhas

> ⚠️ **`sql not match` no Try It Out da regra.** O teste vem com o tópico padrão `t/a`. Troque por `grupo-luz-emergencia/luminosidade`, igual ao `FROM` do SQL.

> ⚠️ **URL do conector sem caminho.** O conector usa só `https://<projeto>.supabase.co`. O caminho `/functions/v1/ingest` vai no campo *URL Path* da **ação**. Colocar nos dois duplica o caminho.

> ⚠️ **CA do conector HTTP: no máximo 2 certificados.** Colar a cadeia completa dá erro de limite. A cadeia do Supabase é Google Trust Services (GTS Root R4) cruzada com a GlobalSign. Usar só a GTS Root R4 deu `Unknown CA` no EMQX; funcionou com as duas raízes juntas (`docs/certificados/supabase-ca-2-raizes.pem`). Se a cadeia mudar, confira de novo.

> ⚠️ **`Quota is exceeded` no EMQX Serverless.** Conectores e regras pela metade de tentativas anteriores ocupam a cota. Apague os antigos ou reaproveite o conector, e mantenha um conector, uma regra e uma ação.

> ⚠️ **Regra Deny para todos.** A permissão `#` Deny bloqueia qualquer outro usuário, incluindo o cliente WebSocket do próprio console. O teste de ponta a ponta é feito pelo Wokwi.

> ⚠️ **`ca_cert.py` truncado.** O certificado do **broker** (DigiCert Global Root G2) tem 20 linhas de base64 e termina em `MrY=`. Um certificado cortado faz o Wokwi mostrar `invalid cert`. Não digite o PEM à mão: copie do arquivo.

> ⚠️ **`erro MQTT: -202`.** É falha de DNS: o `MQTT_HOST` do `wokwi/config.py` ainda está com o placeholder ou com erro de digitação. Deve conter só o domínio, sem `mqtts://` e sem `:8883`.

> ⚠️ **`ETIMEDOUT` no NTP.** O relógio precisa estar certo para validar o certificado TLS. O servidor de horas às vezes demora no Wokwi, e por isso `wokwi/main.py:35` tenta até 10 vezes antes de desistir.

> ⚠️ **Verify JWT desligado nas duas funções.** A `ingest` se protege com `x-api-key` e a `api` é pública. Com o JWT ligado o EMQX recebe 401 e nada é gravado.

## Checagem rápida de que tudo funciona

1. Serial do Wokwi mostra `MQTT CONECTADO` e `PUBLICADO sala` (e os outros 3).
2. `GET /functions/v1/api?device_id=esp32-sala&limit=1` devolve uma `ultima` com horário recente.
3. O painel mostra os 4 cômodos coloridos, e só o cômodo cujo slider foi abaixado fica escuro.
