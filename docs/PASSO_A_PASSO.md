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

## Ordem de execução
1. Mariana cria o repositório (Etapa 0) e o sensor no Wokwi (Etapa 1)
2. Amanda faz o Supabase (Etapa 2)
3. Murilo faz o EMQX (Etapa 3), que precisa da URL e da chave da Amanda
4. Isabella faz o painel (Etapa 4), que precisa da URL da API da Amanda
5. Todas fazem os testes, o vídeo e o relatório (Etapa 5)

---

## Etapa 0 - Mariana: criar o repositório
1. No GitHub, crie o repositório `luz-emergencia-iot` (público é mais simples).
2. Na pasta do projeto no computador:
   ```
   git init
   git add .
   git commit -m "Estrutura inicial do projeto"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/luz-emergencia-iot.git
   git push -u origin main
   ```
3. Em Settings > Collaborators, convide Amanda, Isabella e Murilo.
4. Se o repositório for privado, convide também o professor: `borbavictor`.
5. Cada integrante clona: `git clone <link do repositório>`.

## Etapa 1 - Mariana: sensor no Wokwi (pasta `wokwi/`)
1. No wokwi.com, abra o projeto e clique em SAVE para criar a sua cópia. Renomeie para "Luz de Emergência IoT".
2. Cole o `main.py` e o `diagram.json` de `wokwi/` nas abas do projeto.
3. Rode a simulação e teste: pouca luz acende o LED e muita luz apaga.
4. Depois que o Murilo passar os dados do EMQX, preencha `MQTT_HOST`, `MQTT_USER` e `MQTT_PASS` só no Wokwi, nunca no GitHub.
5. Copie o `main.py` e o `diagram.json` finais para `wokwi/` (com os placeholders no lugar das senhas), faça commit e push.
6. Guarde o link do projeto Wokwi para o relatório.

## Etapa 2 - Amanda: banco e API no Supabase (pasta `supabase/`)
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
1. A Claude vai gerar os arquivos do painel em `frontend/` (`index.html`, e assim por diante). Peça à Mariana para passá-los.
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
| Mariana | Repositório e sensor no Wokwi | `wokwi/` |
| Amanda | Banco e API no Supabase | `supabase/` |
| Murilo | Broker MQTT no EMQX | `docs/emqx.md` |
| Isabella | Painel no Cloudflare Pages | `frontend/` |
| Todas | Testes, vídeo, relatório, README | `docs/`, `README.md` |
