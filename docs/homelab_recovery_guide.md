# ⚓️ Mac Mini HomeLab: AI Twin Recovery Guide

This is your manual for keeping `mini-llm-twin` alive on your own dedicated hardware. 

---

## 🚨 Scenario 1: My Mac Mini Restarted / Power Outage
If your Mac boots up fresh, your API and Tunnel are **OFF**. You must restart them manually:

1. **Open Terminal 1 (The Brain)**:
   ```bash
   cd /Users/kelvinnguyen/Projects/mini-llm-twin
   source .venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Open Terminal 2 (The Bridge)**:
   ```bash
   ngrok http --domain=lunchless-rosaria-unrepugnantly.ngrok-free.dev 8000
   ```

---

## 🛠 Scenario 2: Error `Address already in use` (Port 8000 Hijacked)
If you try to start `uvicorn` and it fails, another process (like an old Docker container) is hiding in the background.

1. **Find the "Ghost" Process**:
   ```bash
   lsof -i :8000
   ```
2. **If it's Docker**: 
   ```bash
   docker ps  # Find the ID
   docker stop <ID>
   ```
3. **If it's a hidden Python process**:
   ```bash
   kill -9 <PID_FROM_LSOF_COMMAND>
   ```

---

## 🔌 Scenario 3: Internet Interrupted / Ngrok "Offline"
If your Wi-Fi drops, Ngrok usually reconnects automatically. If it doesn't:

1. Stop the Ngrok terminal (`Ctrl + C`).
2. Check your internet connection.
3. Restart the Ngrok command (it will **always** use your permanent `lunchless-rosaria` domain).

---

## 🏗 Scenario 4: I Updated My Code (Prompt/Logic)
If you change `src/rag/generation.py` or any other file:
* **If using Terminal (`--reload`)**: You don't need to do anything! The server restarts itself.
* **If using Docker**: You **MUST** rebuild the image:
  ```bash
  docker build -t mini-llm-twin .
  docker stop <OLD_ID>
  docker run -p 8000:8000 --env-file .env mini-llm-twin
  ```

---

## 🧐 Quick Health Check
If you are unsure if your Twin is "alive," visit this URL from your phone (5G):
`https://lunchless-rosaria-unrepugnantly.ngrok-free.dev/health`

* **Result `{"status": "ok"}`**: You are a Port-Forwarding Legend.
* **Result `404/502/Timeout`**: Check your Mac Mini!
