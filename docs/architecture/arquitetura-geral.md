---
title: Arquitetura geral
type: architecture
created: 2026-11-23
updated: 2026-11-23
sources:
  - code: wokwi/main.py
  - code: wokwi/diagram.json
  - code: supabase/functions/ingest/index.ts
  - code: supabase/functions/api/index.ts
  - code: supabase/schema.sql
  - code: frontend/index.html
  - code: frontend/config.js
verified_at: 5a39e5a
---

# Arquitetura geral

Sistema de **luz de emergência** para uma casa de 4 cômodos (sala, cozinha, quarto e banheiro). Cada cômodo tem um sensor de luz (LDR) independente. Quando a luminosidade do cômodo fica abaixo de 30%, o LED daquele cômodo acende e o painel mostra o alerta.

```
ESP32 (Wokwi) --MQTT/TLS 8883--> EMQX --HTTPS POST--> função ingest --> tabela leituras
                                                                              |
painel (Cloudflare Pages) <--GET HTTPS-- função api <-------------------------+
```

## Etapas do fluxo

1. **Sensor.** Um único ESP32 lê 4 LDRs (pinos 34, 35, 32, 33) e controla 4 LEDs (pinos 15, 2, 4, 5). A cada 5 s publica uma mensagem JSON por cômodo no mesmo tópico, `grupo-luz-emergencia/luminosidade`. O que separa os cômodos é o campo `device_id` (`esp32-sala`, `esp32-cozinha`, `esp32-quarto`, `esp32-banheiro`). Ver `wokwi/main.py:20`.
2. **Broker.** O EMQX valida o usuário `esp32_luz01`, aplica a regra SQL e envia o resultado, por um conector HTTP, para a função `ingest`. Ver [[configuracao-emqx-e-armadilhas]].
3. **Gravação.** A função `ingest` confere o header `x-api-key`, valida os campos e insere uma linha em `public.leituras`. Ver `supabase/functions/ingest/index.ts:13`.
4. **Consulta.** A função `api` devolve `agora`, `ultima` e `historico` de um `device_id`. Ver `supabase/functions/api/index.ts:21`.
5. **Painel.** A página desenha a planta da casa e consulta a `api` uma vez por cômodo, a cada 5 s. Ver `frontend/index.html`.

## Por que um `device_id` por cômodo

Os 4 sensores são **independentes** para o backend: cada um tem seu próprio histórico e seu próprio estado de alerta. Por isso adicionar um cômodo exige só um novo item em `COMODOS` (`frontend/config.js`) e uma nova entrada na lista do `main.py`, sem mudar EMQX nem Supabase.

## Estados de um cômodo no painel

| Estado | Condição | Aparência |
|---|---|---|
| Com luz | `alerta = false` e leitura recente | amarelo |
| Escuro | `alerta = true` e leitura recente | escuro, LED vermelho pulsando |
| Sem sinal | última leitura com mais de 20 s | cinza |
| Sem leituras | nunca chegou dado | cinza |

O tempo de "sem sinal" usa o relógio do **servidor** (`agora` devolvido pela `api`), não o do computador de quem abre o painel. Ver `frontend/index.html` (função `idade`).

> ⚠️ O limite de alerta (30%) existe em **dois lugares**: `LIMITE_ALERTA` em `wokwi/main.py:13` (quem decide `alerta` e acende o LED) e `LIMITE_ALERTA` em `frontend/config.js` (só a linha tracejada do gráfico). Se mudar um, mude o outro.

> ⚠️ O banco guarda o `alerta` calculado pelo ESP32. O painel não recalcula, então mudar só o limite do painel não muda a cor dos cômodos.

> ⚠️ A tabela `leituras` tem RLS ativado e nenhuma política: só as funções (service role) leem e gravam. A `api` é pública e somente leitura, então não coloque dado sensível nela. Ver `supabase/schema.sql:15`.
