# 🍍 PineappleGram

**PineappleGram** è un client desktop per Telegram leggero, moderno e ad alte prestazioni, sviluppato in Python utilizzando **NiceGUI**, **pywebview** e **Telethon**. È progettato per offrire un'interfaccia grafica pulita e priva di fronzoli, sfruttando tutta la potenza del protocollo MTProto.

## 🚀 Caratteristiche Principali

* **Esperienza Desktop Nativa:** Grazie a `pywebview`, l'applicazione gira fluidamente all'interno di una finestra dedicata senza la necessità di aprire il browser.

* **Interfaccia Moderna:** Realizzata con **NiceGUI** e Tailwind CSS, caratterizzata da un tema scuro ed elegante ispirato alle migliori app di messaggistica.

* **Integrazione MTProto:** Sfrutta **Telethon** per una comunicazione rapida, sicura e nativa con i server di Telegram.

* **Procedura Guidata (Wizard) Integrata:** Gestisce la configurazione iniziale, l'inserimento del numero e il codice OTP direttamente dentro la GUI, senza mai dover aprire il terminale!

* **Pronto all'uso:** Nessuna installazione complessa necessaria, basta avviare l'eseguibile.

## 🛠️ Stack Tecnologico

* **Interfaccia Grafica:** NiceGUI (framework Python basato su Tailwind CSS)

* **Finestra Nativa:** pywebview (motore Chromium/web nativo)

* **Protocollo Telegram:** Telethon (client MTProto asincrono in Python)

## ⚙️ Come si usa

Non hai bisogno di clonare repository o scrivere codice nel terminale:

1. Vai nella sezione delle **Release** del progetto e scarica l'eseguibile (`.exe`) di **PineappleGram**.

2. Avvia l'applicazione con un doppio clic.

3. Al primo avvio, inserisci le tue credenziali API (ottenute gratuitamente su [my.telegram.org](https://my.telegram.org/?utm_source=gemini)), il tuo numero di telefono e il codice di verifica che riceverai su Telegram.

4. Fatto! L'app ricorderà la sessione e caricherà automaticamente le tue chat.

## 🔒 Sicurezza e Privacy

* **Dati al sicuro:** Le tue credenziali vengono salvate localmente in un file `config.json` sul tuo computer e non vengono mai condivise o caricate online.

* **Sessioni private:** I file di sessione di Telethon vengono memorizzati esclusivamente in locale in modo sicuro.

## 📝 Licenza

Distribuito sotto licenza **ISC**. Consulta il file `LICENSE` per maggiori informazioni.