// Servidor estático del cliente web de pruebas.
// La configuración se toma de variables de entorno y se entrega al navegador
// en /config.js para no dejar URLs ni roles escritos en el código.
import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const PORT = Number(process.env.WEB_TESTER_PORT ?? 3000);

const clientConfig = {
  serverUrl: process.env.SERVER_URL ?? "http://localhost:5000",
  roleDisplay: process.env.ROLE_DISPLAY ?? "display",
  roleAi: process.env.ROLE_AI ?? "ai",
};

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.get("/config.js", (_req, res) => {
  res.type("application/javascript");
  res.send(`window.APP_CONFIG = ${JSON.stringify(clientConfig)};`);
});

app.use(express.static(path.join(__dirname, "public")));

app.listen(PORT, () => {
  console.log(`http://localhost:${PORT}`);
});
