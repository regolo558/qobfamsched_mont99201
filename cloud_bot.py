"""
Qobuz Bot Cloud Integration
Versione modificata che legge/scrive da Supabase invece che da file JSON locali.

Requisiti:
pip install selenium supabase

Configurazione:
1. Crea un file .env nella cartella backend con:
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key

2. Esegui: python cloud_bot.py
"""

import os
import time
from datetime import datetime
from supabase import create_client, Client
from bot_logic import QobuzBot
from dotenv import load_dotenv

load_dotenv()

class CloudQobuzManager:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devono essere configurati nel file .env")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.bot = QobuzBot(self.log_message)
        self.current_schedule_id = None

    def log_message(self, message: str, log_type: str = 'info', guest_id: str = None):
        """Logga un messaggio sia su console che su database"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")

        try:
            self.supabase.table('execution_logs').insert({
                'schedule_id': self.current_schedule_id,
                'guest_id': guest_id,
                'message': message,
                'log_type': log_type
            }).execute()
        except Exception as e:
            print(f"Errore logging: {e}")

    def get_master_account(self):
        """Recupera l'account master dal database"""
        try:
            response = self.supabase.table('master_accounts').select('*').order('created_at', desc=True).limit(1).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                self.log_message("ERRORE: Nessun account master configurato nel database", 'error')
                return None
        except Exception as e:
            self.log_message(f"Errore recupero master account: {e}", 'error')
            return None

    def get_pending_guests(self):
        """Recupera i guest con status 'pending' dal database"""
        try:
            response = self.supabase.table('guest_accounts').select('*').eq('status', 'pending').order('created_at').execute()
            return response.data if response.data else []
        except Exception as e:
            self.log_message(f"Errore recupero guest: {e}", 'error')
            return []

    def update_guest_status(self, guest_id: str, status: str):
        """Aggiorna lo status di un guest"""
        try:
            self.supabase.table('guest_accounts').update({
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', guest_id).execute()
        except Exception as e:
            self.log_message(f"Errore aggiornamento status: {e}", 'error')

    def get_next_scheduled_execution(self):
        """Trova il prossimo schedule da eseguire"""
        try:
            now = datetime.utcnow().isoformat()
            response = self.supabase.table('schedules').select('*').eq('status', 'pending').lte('scheduled_date', now).order('scheduled_date').limit(1).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            self.log_message(f"Errore ricerca schedule: {e}", 'error')
            return None

    def update_schedule_status(self, schedule_id: str, status: str):
        """Aggiorna lo status di uno schedule"""
        try:
            self.supabase.table('schedules').update({
                'status': status
            }).eq('id', schedule_id).execute()
        except Exception as e:
            self.log_message(f"Errore aggiornamento schedule: {e}", 'error')

    def run_scheduled_execution(self):
        """Esegue il prossimo schedule pianificato"""
        schedule = self.get_next_scheduled_execution()

        if not schedule:
            print("Nessun schedule da eseguire al momento")
            return False

        self.current_schedule_id = schedule['id']
        self.log_message(f"=== AVVIO SCHEDULE: {schedule['name']} ===", 'info')
        self.update_schedule_status(schedule['id'], 'running')

        master = self.get_master_account()
        if not master:
            self.update_schedule_status(schedule['id'], 'completed')
            return False

        guests = self.get_pending_guests()
        if not guests:
            self.log_message("Nessun guest in stato 'pending'", 'warning')
            self.update_schedule_status(schedule['id'], 'completed')
            return False

        self.log_message(f"Trovati {len(guests)} guest da processare", 'info')

        for i, guest in enumerate(guests):
            if i > 0:
                self.log_message(f"--- Pausa 30s prima del prossimo guest ---", 'info')
                time.sleep(30)

            self.log_message(f"Processando guest: {guest['email']}", 'info', guest['id'])
            self.update_guest_status(guest['id'], 'processing')

            try:
                self.bot.process_single_cycle(
                    master['email'],
                    master['password'],
                    guest['email'],
                    guest['password'],
                    guest['yopmail_user']
                )
                self.update_guest_status(guest['id'], 'completed')
                self.log_message(f"Guest {guest['email']} completato con successo", 'success', guest['id'])
            except Exception as e:
                self.update_guest_status(guest['id'], 'failed')
                self.log_message(f"Errore processando {guest['email']}: {e}", 'error', guest['id'])

        self.update_schedule_status(schedule['id'], 'completed')
        self.log_message("=== SCHEDULE COMPLETATO ===", 'success')
        return True

    def run_manual_execution(self):
        """Esegue manualmente tutti i guest pending senza schedule specifico"""
        self.log_message("=== AVVIO ESECUZIONE MANUALE ===", 'info')

        master = self.get_master_account()
        if not master:
            return False

        guests = self.get_pending_guests()
        if not guests:
            self.log_message("Nessun guest in stato 'pending'", 'warning')
            return False

        self.log_message(f"Trovati {len(guests)} guest da processare", 'info')

        for i, guest in enumerate(guests):
            if i > 0:
                self.log_message(f"--- Pausa 30s prima del prossimo guest ---", 'info')
                time.sleep(30)

            self.log_message(f"Processando guest: {guest['email']}", 'info', guest['id'])
            self.update_guest_status(guest['id'], 'processing')

            try:
                self.bot.process_single_cycle(
                    master['email'],
                    master['password'],
                    guest['email'],
                    guest['password'],
                    guest['yopmail_user']
                )
                self.update_guest_status(guest['id'], 'completed')
                self.log_message(f"Guest {guest['email']} completato con successo", 'success', guest['id'])
            except Exception as e:
                self.update_guest_status(guest['id'], 'failed')
                self.log_message(f"Errore processando {guest['email']}: {e}", 'error', guest['id'])

        self.log_message("=== ESECUZIONE COMPLETATA ===", 'success')
        return True

def main():
    print("=" * 60)
    print("Qobuz Bot - Cloud Edition")
    print("=" * 60)
    print()
    print("Opzioni:")
    print("1. Esegui schedule pianificato (se disponibile)")
    print("2. Esegui manualmente tutti i guest pending")
    print("3. Esci")
    print()

    choice = input("Scegli un'opzione (1-3): ").strip()

    try:
        manager = CloudQobuzManager()

        if choice == '1':
            manager.run_scheduled_execution()
        elif choice == '2':
            manager.run_manual_execution()
        elif choice == '3':
            print("Uscita...")
            return
        else:
            print("Opzione non valida")
    except Exception as e:
        print(f"ERRORE CRITICO: {e}")

if __name__ == "__main__":
    main()
