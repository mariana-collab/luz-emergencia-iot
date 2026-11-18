# Passo a passo do grupo - Luz de Emergência IoT

Fluxo do sistema:
ESP32 (Wokwi) -> EMQX (MQTT) -> função `ingest` (Supabase) -> tabela `leituras` -> função `api` -> painel (Cloudflare Pages)

## Regras para todas (importante para a nota)
- Cada uma faz os próprios commits, com o próprio nome e e-mail no Git.
- Faça commits pequenos e com mensagem clara (ex.: "Adiciona função api do Supabase").
- Nunca coloque senhas, chaves ou tokens no GitHub. Senhas são passadas por mensagem privada.
- Antes de começar a trabalhar: `git pull`. Ao terminar: `git add .`, `git commit -m "..."` e `git push`.
- Configurar o Git no seu computador (uma vez só):
  ```
  git config --global user.name "Seu Nome"
  git config --global user.email "seu-email-do-github"
  ```

## Andamento
- [x] Etapa 0: repositório criado (público): https://github.com/mariana-collab/luz-emergencia-iot
- [x] Etapa 1: sensor no Wokwi pronto e commitado na pasta `wokwi/` (falta só ligar o MQTT depois da Etapa 3)
- [ ] Etapa 2: Supabase (Amanda)
- [ ] Etapa 3: EMQX (Murilo)
- [ ] Etapa 4: painel (Isabella)
- [ ] Etapa 5: testes, vídeo e relatório (todas)

## Ordem de execução
1. Mariana: repositório (Etapa 0) e sensor no Wokwi (Etapa 1), **já feitos**
2. Amanda faz o Supabase (Etapa 2)
3. Murilo faz o EMQX (Etapa 3), que precisa da URL e da chave da Amanda
4. Isabella faz o painel (Etapa 4), que precisa da URL da API da Amanda
5. Todas fazem os testes, o vídeo e o relatório (Etapa 5)

---

## Etapa 0 - Mariana: repositório (CONCLUÍDA)
O repositório já existe e é público: https://github.com/mariana-collab/luz-emergencia-iot
Ele contém por enquanto `README.md`, `.gitignore`, `wokwi/` e `docs/PASSO_A_PASSO.md`. As pastas `supabase/` e `frontend/` ainda não estão nele, e cada responsável deve adicioná-las com o próprio commit.

**Como cada integrante começa (Amanda, Isabella e Murilo):**
1. A Mariana convida vocês em Settings > Collaborators. Aceitem o convite que chega por e-mail.
2. Configure o Git (uma vez só):
   ```
   git config --global user.name "Seu Nome"
   git config --global user.email "seu-email-do-github"
   ```
3. Clone o repositório:
   ```
   git clone https://github.com/mariana-collab/luz-emergencia-iot.git
   ```
4. Crie a sua pasta (se ela não existir), copie para dentro os arquivos que a Mariana enviou e faça:
   ```
   git add pasta-da-sua-parte/
   git commit -m "mensagem clara do que você fez"
   git pull
   git push
   ```
   Se o Git pedir senha, use um Personal Access Token do GitHub (a senha normal não funciona).

## Etapa 1 - Mariana: sensor no Wokwi (CONCLUÍDA, pasta `wokwi/`)
O `main.py` e o `diagram.json` já estão commitados em `wokwi/`.
Pendente só para depois da Etapa 3: preencher `MQTT_HOST`, `MQTT_USER` e `MQTT_PASS` **apenas no Wokwi**, nunca no GitHub, e guardar o link do projeto Wokwi para o relatório.

## Etapa 2 - Amanda: banco e API no Supabase (pasta `supabase/`)
0. A Mariana envia para você a pasta `supabase/` (`schema.sql` e `functions/`). Coloque-a dentro do seu clone do repositório e faça o commit dela.
1. Em supabase.com, crie o projeto `luz-emergencia`.
2. Em SQL Editor, rode todo o `supabase/schema.sql`.
3. Em Edge Functions > Secrets, crie `INGEST_KEY` com uma senha longa e envie para o Murilo em mensagem privada.
4. Crie as funções `ingest` e `api` (Deploy via Editor) colando o `index.ts` de cada pasta em `supabase/functions/`. Nas duas, desligue **Verify JWT**.
5. Teste a `ingest` com o curl que está na conversa com a Claude. Deve responder `ok`.
6. Abra `https://SEU_PROJETO.supabase.co/functions/v1/api` no navegador. A leitura deve aparecer em `ultima`.
7. Passe a URL da `ingest` para o Murilo e a URL da `api` para a Isabella.
8. Faça commit e push de qualquer ajuste em `supabase/`.

## Etapa 3 - Murilo: broker MQTT no EMQX (pasta `docs/`)
1. Em emqx.com, crie uma implantação **Serverless** (plano gratuito).
2. Anote o endereço de conexão (algo como `xxxx.emqxsl.com`) e a porta TLS **8883**.
3. Em Access Control > Authentication, crie um usuário e senha para o ESP32. Envie host, usuário e senha para a Mariana em mensagem privada.
4. Em Data Integration, crie um **Webhook** com estas configurações:
   - URL: a URL da função `ingest` (passada pela Amanda)
   - Método: POST
   - Header `Content-Type`: `application/json`
   - Header `x-api-key`: a `INGEST_KEY`
5. Crie uma regra (Rule) com este SQL e associe ao Webhook:
   ```
   SELECT payload.device_id AS device_id, payload.grandeza AS grandeza,
          payload.valor AS valor, payload.unidade AS unidade, payload.alerta AS alerta
   FROM "grupo-luz-emergencia/luminosidade"
   ```
6. Teste com o cliente WebSocket do próprio EMQX, publicando no tópico `grupo-luz-emergencia/luminosidade` este JSON:
   `{"device_id":"esp32-luz-01","grandeza":"luminosidade","valor":10,"unidade":"%","alerta":true}`
   A linha deve aparecer na tabela `leituras` do Supabase.
7. Escreva em `docs/emqx.md` o que foi feito (sem senhas), com prints, faça commit e push.

## Etapa 4 - Isabella: painel web (pasta `frontend/`)
1. A Mariana envia para você os arquivos `index.html` e `config.js`. Coloque-os em uma pasta `frontend/` dentro do seu clone do repositório.
2. Coloque a URL da `api` da Amanda no arquivo, no campo indicado.
3. No Cloudflare Pages, crie um projeto conectado ao repositório GitHub, com o diretório de saída `frontend` e sem comando de build.
4. Teste: o painel deve mostrar o valor atual, a unidade, o horário, o histórico, o alerta e o aviso de dados desatualizados.
5. Guarde o link do painel para o relatório. Faça commit e push.

## Etapa 5 - Todas: testes, vídeo e relatório
1. Teste o fluxo completo: mude a luz no Wokwi, e o dado chega à API e aparece no painel.
2. Teste um alerta: escureça no Wokwi. O LED acende e o painel mostra o alerta.
3. Teste a interrupção: pare a simulação. O painel deve indicar "desatualizado". Ao retomar, deve voltar a mostrar leituras novas.
4. Teste com o painel fechado: feche o painel, deixe a simulação rodar, reabra e confira que há leituras guardadas no período.
5. Grave o vídeo (YouTube, não listado) mostrando: mudar a leitura no Wokwi, o dado chegando à API (log ou consulta) e a leitura no painel.
6. Relatório em PDF (2 a 4 páginas) com: problema, diagrama da arquitetura, funcionamento, testes, limitações, contribuições de cada uma e **todos os links** (repositório, Wokwi, painel, vídeo).
7. O README deve conter instruções de reprodução, a estrutura do banco e a configuração sem segredos.
8. Uma só integrante envia tudo no Moodle em nome do grupo.

## Resumo de quem faz o quê
| Quem | Parte | Pasta |
|---|---|---|
| Mariana | Repositório e sensor no Wokwi (feito) | `wokwi/` |
| Amanda | Banco e API no Supabase | `supabase/` |
| Murilo | Broker MQTT no EMQX | `docs/emqx.md` |
| Isabella | Painel no Cloudflare Pages | `frontend/` |
| Todas | Testes, vídeo, relatório, README | `docs/`, `README.md` |
