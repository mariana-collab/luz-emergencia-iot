// Configuracao do painel (tudo publico, pode ir no GitHub).
const CONFIG = {
  API_URL: "https://adfvywhodqxiigcppdib.supabase.co/functions/v1/api",
  GRANDEZA: "luminosidade",
  LIMITE_ALERTA: 30,        // % (mesmo valor do main.py): abaixo disso = escuro
  ATUALIZA_A_CADA_S: 5,     // frequencia de consulta do painel
  DESATUALIZADO_APOS_S: 20, // sem leitura nova ha mais que isso = sem sinal

  // Planta da casa (viewBox 640 x 420). Cada comodo tem seu proprio sensor/device_id.
  COMODOS: [
    { id: "sala",     nome: "Sala",     device_id: "esp32-sala",     x: 20,  y: 20,  w: 370, h: 190 },
    { id: "cozinha",  nome: "Cozinha",  device_id: "esp32-cozinha",  x: 390, y: 20,  w: 230, h: 190 },
    { id: "quarto",   nome: "Quarto",   device_id: "esp32-quarto",   x: 20,  y: 210, w: 290, h: 190 },
    { id: "banheiro", nome: "Banheiro", device_id: "esp32-banheiro", x: 310, y: 210, w: 310, h: 190 },
  ],
  // Portas desenhadas na parede (x, y, comprimento, orientacao)
  PORTAS: [
    { x: 390, y: 90,  len: 44, vertical: true },   // sala <-> cozinha
    { x: 150, y: 210, len: 44, vertical: false },  // sala <-> quarto
    { x: 440, y: 210, len: 44, vertical: false },  // cozinha <-> banheiro
  ],
};
