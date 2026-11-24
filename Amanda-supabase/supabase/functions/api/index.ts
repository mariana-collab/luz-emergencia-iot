// API REST (somente leitura) usada pelo painel.
// GET /api?device_id=esp32-luz-01&grandeza=luminosidade&limit=50
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
  "Content-Type": "application/json",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: cors });
  if (req.method !== "GET") return new Response("Use GET", { status: 405, headers: cors });

  const p = new URL(req.url).searchParams;
  const device_id = p.get("device_id") ?? "esp32-luz-01";
  const grandeza = p.get("grandeza") ?? "luminosidade";
  const limit = Math.min(Number(p.get("limit")) || 50, 500);

  const { data, error } = await supabase
    .from("leituras")
    .select("device_id,grandeza,valor,unidade,alerta,criado_em")
    .eq("device_id", device_id)
    .eq("grandeza", grandeza)
    .order("criado_em", { ascending: false })
    .limit(limit);

  if (error) return new Response(JSON.stringify({ erro: error.message }), { status: 500, headers: cors });

  return new Response(
    JSON.stringify({
      agora: new Date().toISOString(),   // o painel usa para saber se esta desatualizado
      ultima: data[0] ?? null,
      historico: data,
    }),
    { headers: cors },
  );
});
