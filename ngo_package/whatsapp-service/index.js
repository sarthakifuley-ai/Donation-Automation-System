const { Client, LocalAuth } = require("whatsapp-web.js");
const express = require("express");
const qrcode = require("qrcode-terminal");
const QRCode = require("qrcode");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.json());
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "*");
  next();
});

let clientReady = false;
let qrCodeData = null;
let qrCodeImage = null; // base64 PNG

// ── Auto-detect browser executable ──────────────────────────────────────────
function findBrowser() {
  const candidates = [
    // Edge (built into Windows 10/11)
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    // Chrome (if installed)
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    // Brave
    "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) {
      console.log(`[Browser] Using: ${p}`);
      return p;
    }
  }
  console.log("[Browser] No system browser found, using Puppeteer cache.");
  return null;
}

const executablePath = findBrowser();

const puppeteerConfig = {
  headless: true,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
};
if (executablePath) {
  puppeteerConfig.executablePath = executablePath;
}

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: puppeteerConfig,
});

client.on("qr", async (qr) => {
  qrCodeData = qr;
  clientReady = false;
  console.log("\n==========================================");
  console.log("  SCAN THIS QR CODE WITH YOUR WHATSAPP");
  console.log("==========================================\n");
  qrcode.generate(qr, { small: true });

  // Also generate as base64 image for the website
  try {
    qrCodeImage = await QRCode.toDataURL(qr, {
      width: 300,
      margin: 2,
      color: { dark: "#1A1209", light: "#FDF8F2" }
    });
    console.log("QR code image generated for website.\n");
  } catch (err) {
    console.error("Failed to generate QR image:", err.message);
  }
});

client.on("ready", () => {
  clientReady = true;
  qrCodeData = null;
  qrCodeImage = null;
  console.log("\n==========================================");
  console.log("  WhatsApp Connected Successfully!");
  console.log("==========================================\n");
});

client.on("authenticated", () => {
  console.log("WhatsApp authenticated. Loading...");
});

client.on("disconnected", (reason) => {
  clientReady = false;
  qrCodeData = null;
  qrCodeImage = null;
  console.log("WhatsApp disconnected:", reason);
  console.log("Attempting to reconnect...");
  setTimeout(() => client.initialize(), 3000);
});

client.initialize();

// Health check
app.get("/status", (req, res) => {
  res.json({ ready: clientReady });
});

// QR code for website (returns base64 image)
app.get("/qr", (req, res) => {
  if (clientReady) {
    return res.json({ qr: null, ready: true, message: "Already connected!" });
  }
  if (!qrCodeImage) {
    return res.json({ qr: null, ready: false, message: "QR not yet generated. Please wait..." });
  }
  res.json({ qr: qrCodeImage, ready: false, message: "Scan this QR code with WhatsApp" });
});

// Connect trigger
app.post("/connect", (req, res) => {
  res.json({ status: "WhatsApp service is running", ready: clientReady });
});

// Send a message
app.post("/send", async (req, res) => {
  const { phone, message } = req.body;

  if (!clientReady) {
    return res.status(503).json({
      success: false,
      error: "WhatsApp not ready. Please scan the QR code first."
    });
  }

  if (!phone || !message) {
    return res.status(400).json({ success: false, error: "phone and message are required" });
  }

  try {
    const chatId = phone.replace("+", "") + "@c.us";
    await client.sendMessage(chatId, message);
    console.log(`Sent to ${phone}`);
    res.json({ success: true });
  } catch (err) {
    console.error(`Failed to send to ${phone}:`, err.message);
    res.json({ success: false, error: err.message });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log("==========================================");
  console.log("  YUVA NGO - WhatsApp Service Started");
  console.log("==========================================");
  console.log("Initializing WhatsApp, please wait...\n");
});
