# Luz de Emergência IoT

Sistema IoT de luz de emergência para uma **casa de 4 cômodos** (sala, cozinha, quarto e banheiro). Cada cômodo tem um sensor de luz independente. Quando a luminosidade de um cômodo fica abaixo de 30%, o LED daquele cômodo acende e o painel, que mostra a planta da casa, destaca o alerta.

## Integrantes
| Nome | RA |
|---|---|
| Mariana da Silva | 2037575 |
| Murilo Tozoni | 2038850 |
| Isabella Machado de Souza Duarte | 2031107 |
| Amanda Villar Moura | 2023278 |

## Arquitetura
```
ESP32 (Wokwi) -> EMQX (MQTT/TLS) -> função ingest (Supabase) -> tabela leituras -> função api -> painel (Cloudflare Pages)
```

| Parte | Tecnologia | Pasta |
|---|---|---|
| 4 sensores (LDR + LED por cômodo) | ESP32, MicroPython, Wokwi | `wokwi/` |
| Broker MQTT | EMQX Serverless | `docs/emqx.md` |
| Banco e API | Supabase (Postgres + Edge Functions) | `supabase/` |
| Painel (planta da casa) | HTML/JS estático, Cloudflare Pages | `frontend/` |

## Links
- Repositório: https://github.com/mariana-collab/luz-emergencia-iot
- Projeto Wokwi: https://wokwi.com/projects/481527143544837121
- Painel: https://luz-de-emergencia.pages.dev/
- Vídeo: https://youtu.be/EYRWaTbrPoc

## Estrutura do banco
Tabela `public.leituras` (`supabase/schema.sql`):

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | bigint (identity) | chave primária |
| `device_id` | text | sensor do cômodo (`esp32-sala`, `esp32-cozinha`, `esp32-quarto`, `esp32-banheiro`) |
| `grandeza` | text | grandeza medida (`luminosidade`) |
| `valor` | numeric | valor lido |
| `unidade` | text | unidade (`%`) |
| `alerta` | boolean | `true` quando valor < 30% |
| `criado_em` | timestamptz | horário de gravação (padrão `now()`) |

Há um índice em `(device_id, grandeza, criado_em desc)`. O RLS está ativado e nenhuma política foi criada: só as Edge Functions (service role) leem e gravam.

## API
- `POST /functions/v1/ingest` (usada só pelo EMQX): exige o header `x-api-key`. Corpo JSON com `device_id`, `grandeza`, `valor`, `unidade`, `alerta`. Responde `201 ok`; `401` sem a chave; `400` se os campos forem inválidos.
- `GET /functions/v1/api?device_id=esp32-sala&grandeza=luminosidade&limit=50`: devolve `agora`, `ultima` e `historico`.

## Como reproduzir
1. **Supabase**: crie um projeto, rode `supabase/schema.sql` no SQL Editor, crie o secret `INGEST_KEY` e publique as funções `ingest` e `api` (com *Verify JWT* desligado).
2. **EMQX**: crie uma implantação Serverless, um usuário/senha para o ESP32 e um Webhook para a `ingest` com os headers `Content-Type: application/json` e `x-api-key`. Detalhes em `docs/emqx.md`.
3. **Wokwi**: crie um projeto ESP32 MicroPython e copie `diagram.json`, `main.py`, `mqtt_client.py`, `config.py` e `ca_cert.py` de `wokwi/`. No Wokwi, preencha `MQTT_HOST` e `MQTT_PASSWORD` em `config.py` e cole o certificado do seu broker (baixado do *Deployment Overview* do EMQX) em `ca_cert.py`. Essas credenciais ficam **somente no Wokwi**.
4. **Painel**: em `frontend/config.js`, troque `API_URL` pela URL da função `api` (e ajuste `COMODOS`, se mudar os cômodos). Publique a pasta `frontend` no Cloudflare Pages (sem comando de build).

## Testes
- Fluxo completo: o valor do LDR muda no Wokwi, chega à API e aparece no cômodo do painel.
- Alerta: abaixo de 30% o LED do cômodo acende e só aquele cômodo fica escuro no painel.
- Independência: cada cômodo reage ao próprio sensor, sem afetar os outros.
- Interrupção: com a simulação parada por mais de 20 s, os cômodos mostram "sem sinal"; ao retomar, voltam ao normal.
- Painel fechado: as leituras continuam gravadas no banco e aparecem no histórico ao reabrir.
- Segurança: `ingest` sem a chave responde `401`.

A documentação detalhada (arquitetura e erros enfrentados) está em [`docs/index.md`](docs/index.md).

## Configuração (sem segredos)
| Item | Onde fica | Vai no GitHub? |
|---|---|---|
| `INGEST_KEY` | Secrets do Supabase e header do Webhook no EMQX | Não |
| Usuário/senha MQTT | EMQX e `main.py` dentro do Wokwi | Não |
| `SUPABASE_SERVICE_ROLE_KEY` | Injetada pelo Supabase nas funções | Não |
| `API_URL` | `frontend/config.js` | Sim (URL pública) |

## Limitações
- O painel consulta a API a cada 5 s (polling), não usa tempo real.
- A API é pública e somente leitura.
- Os 4 sensores são simulados por um único ESP32 no Wokwi (cada cômodo tem seu `device_id`, mas não há 4 placas físicas).
- Os planos gratuitos do Supabase, EMQX e Cloudflare têm limites de uso.
