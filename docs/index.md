# Luz de Emergência IoT -- documentation

Sistema IoT de luz de emergência para uma casa de 4 cômodos: cada cômodo tem um sensor de luz independente, e o painel mostra a planta da casa com o alerta de cada um.

This directory is a wiki maintained by an LLM: linked markdown pages, nothing outside the
repository. The rules are in [`CLAUDE.md`](CLAUDE.md).

## Start here

1. [[arquitetura-geral]] -- o fluxo do sensor até o painel e os estados de cada cômodo
2. [[configuracao-emqx-e-armadilhas]] -- como o EMQX é configurado e os erros reais que apareceram

---

## concepts

_(ainda sem páginas)_

## architecture

- [[arquitetura-geral]] -- fluxo ESP32 → EMQX → Supabase → painel, 4 cômodos

## subsystems

_(ainda sem páginas)_

## decisions

_(ainda sem páginas)_

## reference

_(ainda sem páginas)_

## operations

- [[configuracao-emqx-e-armadilhas]] -- valores que precisam bater e erros já resolvidos

## history

_(ainda sem páginas)_

---

## Using this wiki

```
/docs-sync     right after a deploy or release -- reads only what changed since verified_at
/docs-lint     integrity check (orphans, broken links, broken sources, stale, unverified)
/docs-query    ask the docs. If it is not there, the answer says so
/docs-status   commits not yet reflected, stale pages, recent work
```

Every page carries `verified_at`, the commit it was checked against. Change code, run
`/docs-sync`.
