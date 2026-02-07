"""
Auto Scheduler - Controlla ed esegue automaticamente gli schedule pianificati

Questo script può essere eseguito da cron/task scheduler ogni ora.
Controlla se ci sono schedule da eseguire e li lancia automaticamente.

Uso: python auto_scheduler.py
"""

import os
import sys
from datetime import datetime
from cloud_bot import CloudQobuzManager

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto Scheduler - Avvio controllo...")

    try:
        manager = CloudQobuzManager()
        schedule = manager.get_next_scheduled_execution()

        if schedule:
            print(f"Schedule trovato: {schedule['name']} (ID: {schedule['id']})")
            print(f"Data pianificata: {schedule['scheduled_date']}")
            print("Avvio esecuzione...")

            success = manager.run_scheduled_execution()

            if success:
                print("Esecuzione completata con successo")
                sys.exit(0)
            else:
                print("Esecuzione completata con errori")
                sys.exit(1)
        else:
            print("Nessun schedule da eseguire al momento")
            sys.exit(0)

    except Exception as e:
        print(f"ERRORE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
