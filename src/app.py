import os
import json
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from nicegui import ui
import webview

# Configurazione globale per pywebview
webview.settings['ALLOW_DOWNLOADS'] = True

CONFIG_FILE = "config.json"
SESSION_NAME = "pineapple_session"

client = None
login_state = "config"  # Stati: 'config', 'phone', 'code', 'password', 'logged'
selected_chat_id = None
selected_chat_name = "Seleziona una chat"
chat_title_label = None
messages_container = None

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(api_id, api_hash):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_id": api_id, "api_hash": api_hash}, f)

@ui.refreshable
def auth_or_main_view():
    global client, login_state, chat_title_label, messages_container
    config = load_config()
    
    # --- STEP 1: Richiesta credenziali API se mancano ---
    if not config.get("api_id") or not config.get("api_hash"):
        with ui.column().classes('w-full h-screen items-center justify-center bg-gray-950 text-white gap-4 p-6'):
            ui.label('🍍 Configurazione Iniziale PineappleGram').classes('text-2xl font-bold text-orange-400')
            ui.label('Inserisci le tue credenziali da my.telegram.org:').classes('text-sm text-gray-400')
            
            api_id_in = ui.input(placeholder='API ID (es. 123456)').classes('w-80 bg-gray-900 text-white').props('dark dense outlined')
            api_hash_in = ui.input(placeholder='API HASH').classes('w-80 bg-gray-900 text-white').props('dark dense outlined')
            
            def handle_save_creds():
                if api_id_in.value and api_hash_in.value:
                    save_config(api_id_in.value.strip(), api_hash_in.value.strip())
                    ui.notify('Credenziali salvate!', type='positive')
                    auth_or_main_view.refresh()
                else:
                    ui.notify('Compila entrambi i campi!', type='negative')

            ui.button('Salva e Continua', on_click=handle_save_creds).classes('bg-orange-500 text-white font-bold')
        return

    # Inizializziamo il client Telethon se non esiste
    if client is None:
        try:
            client = TelegramClient(SESSION_NAME, int(config["api_id"]), config["api_hash"])
        except Exception as e:
            ui.label(f'Errore client: {e}').classes('text-red-500')
            return

    # --- STEP 2: Schermata di Autenticazione Telegram (Telefono / Codice) ---
    if login_state == "config":
        async def check_auth():
            global login_state
            await client.connect()
            if await client.is_user_authorized():
                login_state = "logged"
            else:
                login_state = "phone"
            auth_or_main_view.refresh()
        
        ui.timer(0.1, check_auth, once=True)
        
        with ui.column().classes('w-full h-screen items-center justify-center bg-gray-950 text-white'):
            ui.spinner('tail', size='lg', color='orange')
            ui.label('Controllo sessione Telegram...').classes('text-sm text-gray-400 mt-2')
        return

    if login_state == "phone":
        with ui.column().classes('w-full h-screen items-center justify-center bg-gray-950 text-white gap-4 p-6'):
            ui.label('📱 Autenticazione Telegram').classes('text-2xl font-bold text-orange-400')
            ui.label('Inserisci il tuo numero di telefono (con prefisso, es. +39...):').classes('text-sm text-gray-400')
            
            phone_in = ui.input(placeholder='+393331234567').classes('w-80 bg-gray-900 text-white').props('dark dense outlined')
            
            async def send_code_action():
                global phone_number
                phone_number = phone_in.value.strip()
                try:
                    await client.connect()
                    await client.send_code_request(phone_number)
                    ui.notify('Codice inviato su Telegram!', type='positive')
                    global login_state
                    login_state = "code"
                    auth_or_main_view.refresh()
                except Exception as e:
                    ui.notify(f'Errore: {e}', type='negative')

            ui.button('Invia Codice OTP', on_click=send_code_action).classes('bg-orange-500 text-white font-bold')
        return

    if login_state == "code":
        with ui.column().classes('w-full h-screen items-center justify-center bg-gray-950 text-white gap-4 p-6'):
            ui.label('🔑 Inserisci Codice OTP').classes('text-2xl font-bold text-orange-400')
            ui.label('Controlla i messaggi ufficiali sull app di Telegram.').classes('text-sm text-gray-400')
            
            code_in = ui.input(placeholder='Codice a 5 cifre').classes('w-80 bg-gray-900 text-white').props('dark dense outlined')
            
            async def sign_in_action():
                global login_state
                try:
                    await client.sign_in(phone_number, code_in.value.strip())
                    login_state = "logged"
                    ui.notify('Login effettuato con successo!', type='positive')
                    auth_or_main_view.refresh()
                except SessionPasswordNeededError:
                    login_state = "password"
                    auth_or_main_view.refresh()
                except Exception as e:
                    ui.notify(f'Codice errato o errore: {e}', type='negative')

            ui.button('Conferma Codice', on_click=sign_in_action).classes('bg-orange-500 text-white font-bold')
        return

    if login_state == "password":
        with ui.column().classes('w-full h-screen items-center justify-center bg-gray-950 text-white gap-4 p-6'):
            ui.label('🔒 Verifica in Due Passaggi').classes('text-2xl font-bold text-orange-400')
            ui.label('Inserisci la password del tuo account Telegram:').classes('text-sm text-gray-400')
            
            pwd_in = ui.input(placeholder='Password', password=True, password_toggle_button=True).classes('w-80 bg-gray-900 text-white').props('dark dense outlined')
            
            async def sign_in_pwd_action():
                global login_state
                try:
                    await client.sign_in(password=pwd_in.value.strip())
                    login_state = "logged"
                    ui.notify('Login completato!', type='positive')
                    auth_or_main_view.refresh()
                except Exception as e:
                    ui.notify(f'Password errata: {e}', type='negative')

            ui.button('Verifica Password', on_click=sign_in_pwd_action).classes('bg-orange-500 text-white font-bold')
        return

    # --- STEP 3: L'INTERFACCIA PRINCIPALE DI PINEAPPLEGRAM ---
    with ui.row().classes('w-full h-screen no-wrap m-0 p-0'):
        
        # --- SIDEBAR (Lista Chat) ---
        with ui.column().classes('w-80 h-full bg-gray-900 text-white p-3 gap-2 border-r border-gray-800'):
            with ui.row().classes('items-center justify-between w-full mb-2'):
                ui.label('🍍 PineappleGram').classes('text-lg font-bold text-orange-400')
                ui.icon('settings', size='sm').classes('cursor-pointer text-gray-400 hover:text-white')
            
            ui.input(placeholder='Cerca chat...').classes('w-full bg-gray-800 rounded px-2 text-white').props('dark dense borderless')
            
            with ui.scroll_area().classes('w-full flex-grow') as chat_list:
                async def load_dialogs():
                    async for dialog in client.iter_dialogs(limit=20):
                        def make_click_handler(d_id, d_name):
                            async def handler():
                                global selected_chat_id, selected_chat_name
                                selected_chat_id = d_id
                                selected_chat_name = d_name
                                chat_title_label.text = d_name
                                
                                # Carica i messaggi della chat selezionata
                                messages_container.clear()
                                with messages_container:
                                    ui.label(f"--- Caricamento messaggi da {d_name} ---").classes('text-xs text-gray-500 italic')
                                    async for msg in client.iter_messages(d_id, limit=15):
                                        bg_color = "bg-orange-600 ml-auto" if msg.out else "bg-gray-800"
                                        with ui.row().classes(f'{bg_color} p-3 rounded-xl max-w-md text-sm my-1'):
                                            ui.label(f"{msg.text or '[Media/Altro]'}")
                            return handler

                        with chat_list:
                            with ui.row().classes('w-full items-center gap-3 p-2 rounded-lg hover:bg-gray-800 cursor-pointer').on('click', make_click_handler(dialog.id, dialog.name)):
                                ui.avatar(icon='account_circle', color='orange-500', text_color='white').classes('w-10 h-10')
                                with ui.column().classes('gap-0'):
                                    ui.label(dialog.name).classes('font-semibold text-sm truncate w-48')
                                    last_text = dialog.message.text if dialog.message and dialog.message.text else 'File o media'
                                    ui.label(last_text).classes('text-xs text-gray-400 truncate w-48')
                
                ui.timer(0.1, load_dialogs, once=True)

        # --- AREA PRINCIPALE (Chat & Messaggi) ---
        with ui.column().classes('flex-grow h-full bg-gray-950 text-white justify-between p-0'):
            with ui.row().classes('w-full items-center bg-gray-900 p-3 border-b border-gray-800 gap-3'):
                ui.avatar(icon='chat', color='orange-500', text_color='white').classes('w-9 h-9')
                with ui.column().classes('gap-0'):
                    chat_title_label = ui.label(selected_chat_name).classes('font-bold text-sm')
                    ui.label('connesso via MTProto').classes('text-xs text-green-400')

            messages_container = ui.scroll_area().classes('w-full flex-grow p-4 gap-3 flex flex-col')
            with messages_container:
                with ui.row().classes('bg-gray-800 p-3 rounded-xl max-w-md text-sm'):
                    ui.label("Seleziona una chat dalla barra a sinistra per iniziare a chattare 🍍")

            # Barra input messaggio in basso
            with ui.row().classes('w-full items-center bg-gray-900 p-3 gap-2 border-t border-gray-800'):
                msg_input = ui.input(placeholder='Scrivi un messaggio...').classes('flex-grow bg-gray-800 rounded px-3 text-white').props('dark dense borderless')
                
                async def send_message_action():
                    global selected_chat_id
                    if not selected_chat_id:
                        ui.notify('Prima seleziona una chat!', type='warning')
                        return
                    
                    text = msg_input.value.strip()
                    if not text:
                        return
                    
                    try:
                        # Invio effettivo con Telethon
                        await client.send_message(selected_chat_id, text)
                        
                        # Aggiunge il messaggio in tempo reale nella vista grafica
                        with messages_container:
                            with ui.row().classes('bg-orange-600 p-3 rounded-xl max-w-md text-sm ml-auto my-1'):
                                ui.label(text)
                        
                        msg_input.value = ''
                        ui.notify('Messaggio inviato!', type='positive', color='green')
                    except Exception as e:
                        ui.notify(f'Errore invio: {e}', type='negative')

                msg_input.on('keydown.enter', send_message_action)
                ui.button(icon='send', on_click=send_message_action).classes('bg-orange-500 text-white')

@ui.page('/')
def index():
    auth_or_main_view()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        port=8080, 
        title='PineappleGram', 
        native=True,           
        reload=False,         
        window_size=(1100, 750)
    )