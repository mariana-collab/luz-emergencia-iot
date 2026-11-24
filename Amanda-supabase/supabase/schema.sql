-- Tabela de leituras do sensor de luz de emergencia
create table if not exists public.leituras (
  id         bigint generated always as identity primary key,
  device_id  text        not null,
  grandeza   text        not null,
  valor      numeric     not null,
  unidade    text        not null,
  alerta     boolean     not null default false,
  criado_em  timestamptz not null default now()
);

create index if not exists leituras_busca_idx
  on public.leituras (device_id, grandeza, criado_em desc);

-- Seguranca: ninguem acessa a tabela direto pela internet.
-- Somente as Edge Functions (service role) leem e gravam.
alter table public.leituras enable row level security;
