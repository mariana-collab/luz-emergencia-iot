// Recebe a leitura (enviada pelo EMQX via HTTPS) e grava no banco.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Use POST", { status: 405 });

  // chave simples para so aceitar dados do nosso broker
  if (req.headers.get("x-api-key") !== Deno.env.get("INGEST_KEY")) {
    return new Response("Nao autorizado", { status: 401 });
  }

  let b: any;
  try { b = await req.json(); } catch { return new Response("JSON invalido", { status: 400 }); }

  const valor = Number(b.valor);
  if (!b.device_id || !b.grandeza || !b.unidade || !Number.isFinite(valor)) {
    return new Response("Campos invalidos", { status: 400 });
  }

  const { error } = await supabase.from("leituras").insert({
    device_id: String(b.device_id),
    grandeza: String(b.grandeza),
    valor,
    unidade: String(b.unidade),
    alerta: b.alerta === true,
  });

  if (error) return new Response(error.message, { status: 500 });
  return new Response("ok", { status: 201 });
});
