import time
import threading
import json
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from bot_logic import QobuzBot

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Qobuz Family Manager v3.0 Modular")
        self.geometry("600x750")
        self.config_file = "qobuz_config.json"
        
        self.bot = QobuzBot(self.log_message)
        self.guests = []
        
        self.create_widgets()
        self.load_config()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Segoe UI", 9, "bold"))

        frame_master = ttk.LabelFrame(self, text="Account Master (Admin)")
        frame_master.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_master, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_master_email = ttk.Entry(frame_master, width=30)
        self.entry_master_email.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_master, text="Password:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_master_pass = ttk.Entry(frame_master, width=20, show="*")
        self.entry_master_pass.grid(row=0, column=3, padx=5, pady=5)

        frame_guest = ttk.LabelFrame(self, text="Aggiungi Guest alla Coda")
        frame_guest.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_guest, text="Guest Email:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_guest_email = ttk.Entry(frame_guest, width=25)
        self.entry_guest_email.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_guest, text="Password:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_guest_pass = ttk.Entry(frame_guest, width=15)
        self.entry_guest_pass.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_guest, text="Yopmail User:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_yopmail = ttk.Entry(frame_guest, width=25)
        self.entry_yopmail.grid(row=1, column=1, padx=5, pady=5)
        
        btn_add = ttk.Button(frame_guest, text="Aggiungi alla Lista", command=self.add_guest)
        btn_add.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        frame_list = ttk.LabelFrame(self, text="Coda di Lavoro")
        frame_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("email", "yopmail")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", height=5)
        self.tree.heading("email", text="Guest Email")
        self.tree.heading("yopmail", text="Yopmail")
        self.tree.column("email", width=250)
        self.tree.column("yopmail", width=250)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        btn_clear = ttk.Button(frame_list, text="Pulisci Lista", command=self.clear_list)
        btn_clear.pack(pady=2)

        frame_actions = ttk.Frame(self)
        frame_actions.pack(fill="x", padx=10, pady=10)
        
        self.btn_start = ttk.Button(frame_actions, text="AVVIA AUTOMAZIONE", command=self.start_thread)
        self.btn_start.pack(fill="x", ipady=5)

        self.log_area = scrolledtext.ScrolledText(self, height=12, state='disabled', font=("Consolas", 9))
        self.log_area.pack(fill="both", padx=10, pady=5)

    def log_message(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def load_config(self):
        if not os.path.exists(self.config_file): return
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            if "master_email" in data:
                self.entry_master_email.delete(0, tk.END)
                self.entry_master_email.insert(0, data["master_email"])
            if "master_pass" in data:
                self.entry_master_pass.delete(0, tk.END)
                self.entry_master_pass.insert(0, data["master_pass"])
            saved_guests = data.get("guests", [])
            for guest in saved_guests:
                self.guests.append(guest)
                self.tree.insert("", tk.END, values=(guest["email"], guest["yop"]))
        except Exception as e:
            self.log_message(f"Errore config: {e}")

    def save_config(self):
        data = {
            "master_email": self.entry_master_email.get().strip(),
            "master_pass": self.entry_master_pass.get().strip(),
            "guests": self.guests
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.log_message(f"Errore salvataggio: {e}")

    def on_close(self):
        self.save_config()
        self.destroy()

    def add_guest(self):
        email = self.entry_guest_email.get().strip()
        pwd = self.entry_guest_pass.get().strip()
        yop = self.entry_yopmail.get().strip()
        
        if not email or not pwd or not yop:
            messagebox.showwarning("Errore", "Compila tutti i campi Guest")
            return

        self.guests.append({"email": email, "pass": pwd, "yop": yop})
        self.tree.insert("", tk.END, values=(email, yop))
        self.save_config()
        self.entry_guest_email.delete(0, tk.END)
        self.entry_yopmail.delete(0, tk.END)

    def clear_list(self):
        self.guests = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.save_config()

    def start_thread(self):
        master_email = self.entry_master_email.get()
        master_pass = self.entry_master_pass.get()
        self.save_config()
        
        if not master_email or not master_pass or not self.guests:
            messagebox.showerror("Errore", "Dati mancanti o lista vuota")
            return

        self.btn_start.config(state="disabled")
        t = threading.Thread(target=self.run_automation, args=(master_email, master_pass))
        t.daemon = True
        t.start()

    def run_automation(self, m_email, m_pass):
        self.log_message("=== INIZIO ===")
        for i, guest in enumerate(self.guests):
            if i > 0:
                self.log_message(f"--- Pause 30s ---")
                time.sleep(30)
            self.log_message(f"Processando: {guest['email']}")
            self.bot.process_single_cycle(m_email, m_pass, guest['email'], guest['pass'], guest['yop'])
        self.log_message("=== COMPLETATO ===")
        self.btn_start.config(state="normal")