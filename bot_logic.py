import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from yopmail_handler import YopmailHandler

class QobuzBot:
    def __init__(self, logger_callback):
        self.log = logger_callback
        self.stop_event = threading.Event()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(options=options)

    def login_qobuz(self, driver, email_addr, password):
        self.log(f"--- Login con {email_addr} ---")
        if "signin" not in driver.current_url:
            driver.get("https://www.qobuz.com/signin")
        
        wait = WebDriverWait(driver, 15)
        try:
            try:
                cookie_reject_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "didomi-continue-without-agreeing"))
                )
                cookie_reject_btn.click()
                time.sleep(1)
            except: pass

            try:
                email_field = wait.until(EC.element_to_be_clickable((By.NAME, "_username"))) 
                email_field.click()
                email_field.clear()
                email_field.send_keys(email_addr)

                pass_field = wait.until(EC.element_to_be_clickable((By.NAME, "_password")))
                pass_field.clear()
                pass_field.send_keys(password)
                pass_field.send_keys(Keys.RETURN)
            except Exception as e:
                self.log(f"Errore inserimento credenziali: {e}")
                return False
            
            time.sleep(5)
            if "signin" in driver.current_url:
                self.log("ATTENZIONE: Login potrebbe essere fallito.")
                return False
            
            self.log("Login effettuato.")
            return True
        except Exception as e:
            self.log(f"Eccezione Login: {e}")
            return False

    def check_and_leave_family_proactive(self, driver):
        """
        Controlla proattivamente se l'utente è in una famiglia e lo rimuove.
        """
        self.log("Verifica stato famiglia Guest...")
        try:
            # 1. TENTATIVO CLICK SU LINK "VAI AL MIO ACCOUNT" (Dalla pagina invito errore)
            link_clicked = False
            try:
                self.log("Cerco link 'Vai al mio account' (a.family-form__link)...")
                # Attendiamo esplicitamente che il link sia presente
                account_link = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.family-form__link"))
                )
                self.log("Link trovato. Primo click...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", account_link)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", account_link)
                link_clicked = True
                
                # Attesa tattica di 5 secondi e secondo click se necessario (richiesto per evitare redirect loop)
                self.log("Attendo 5s per stabilità pagina...")
                time.sleep(5)
                
                try:
                    # Ricerca fresca dell'elemento per evitare StaleElementReferenceException
                    account_link_retry = driver.find_element(By.CSS_SELECTOR, "a.family-form__link")
                    self.log("Link ancora presente (redirect fallito?). Eseguo SECONDO click di forzatura...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", account_link_retry)
                    driver.execute_script("arguments[0].click();", account_link_retry)
                except:
                    self.log("Link non più presente dopo il primo click (navigazione avvenuta).")

            except Exception as e:
                # Se non lo trova la prima volta, logga solo se non abbiamo mai cliccato
                if not link_clicked:
                    self.log(f"Link 'Vai al mio account' non trovato subito (o timeout): {e}")
            
            if not link_clicked:
                self.log("Fallback: Navigazione diretta a /profile/household/...")
                driver.get("https://www.qobuz.com/profile/household/")
            
            time.sleep(4)

            leave_btn = None
            
            # Strategia 1: Classe CSS specifica
            try:
                leave_btn = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".account-remove-link--remove"))
                )
            except:
                pass

            # Strategia 2: Link parziale
            if not leave_btn:
                try:
                    leave_btn = driver.find_element(By.XPATH, "//a[contains(@href, '/profile/household/leave/display/')]")
                except:
                    pass

            # Strategia 3: Fallback generico sul testo
            if not leave_btn:
                try:
                    leave_btn = driver.find_element(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quitter') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'leave')]")
                except:
                    pass

            if leave_btn:
                self.log("RILEVATO: Utente in famiglia. Uscita in corso...")
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", leave_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", leave_btn)
                
                self.log("Click su 'Quitter' (JS), attesa conferma...")
                
                try:
                    confirm_btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-unsubscribe"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", confirm_btn)
                    
                    self.log("Confermato: 'Oui, je souhaite quitter...'")
                    time.sleep(5)
                    self.log("Uscita completata. Sessione mantenuta attiva.")
                except Exception as e:
                    self.log(f"Errore conferma uscita: {e}")
                    return False
                
                return True
            else:
                self.log("Nessun pulsante di uscita trovato (Utente libero).")
                return False

        except Exception as e:
            self.log(f"Errore durante controllo famiglia: {e}")
            return False

    def process_single_cycle(self, master_email, master_pass, guest_email, guest_pass, yopmail_user):
        driver = self.setup_driver()
        yop_handler = YopmailHandler(driver, self.log)

        try:
            # 1. Master Invita
            if not self.login_qobuz(driver, master_email, master_pass):
                return
            
            self.log("Gestione Famiglia Master...")
            driver.get("https://www.qobuz.com/profile/household/") 
            time.sleep(3)
            
            try:
                invite_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-invite")))
                invite_btn.click()
                email_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "household_invite_email")))
                email_input.clear()
                email_input.send_keys(yopmail_user)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "household_invite_save_changes"))).click()
                self.log("Invito inviato.")
            except Exception as e:
                self.log(f"Nota invito: {e}")

            self.log("Logout Master...")
            driver.delete_all_cookies()
            time.sleep(2)

            # 2. Recupero Link
            self.log("Attesa ricezione email (15s)...")
            time.sleep(15)
            
            invite_link = yop_handler.get_invite_link(yopmail_user)
            
            if not invite_link:
                self.log("ERRORE: Link non trovato. Stop.")
                return

            # 3. Apertura Link e Login
            self.log(f"Apro link invito...")
            driver.get(invite_link)
            time.sleep(3)

            # --- CONTROLLO LOGIN PRIORITARIO ---
            # Controlla se siamo sulla pagina di login PRIMA di fare qualsiasi altra cosa
            if "signin" in driver.current_url or driver.find_elements(By.NAME, "_username"):
                self.log("Login richiesto dal link...")
                if self.login_qobuz(driver, guest_email, guest_pass):
                    self.log("Login OK. Ritorno al link invito...")
                    driver.get(invite_link)
                    time.sleep(3)
                else:
                    self.log("Fallito login guest. Abort.")
                    return

            # 4. Verifica Stato e Azioni
            
            # Controllo successo immediato
            if "success" in driver.current_url:
                self.log(f"SUCCESSO: {guest_email} aggiunto!")
                return

            # Controllo Già Membro (SOLO SE LOGGATO)
            # Evitiamo falsi positivi sulla pagina di login controllando che non ci sia il campo username
            if not driver.find_elements(By.NAME, "_username"):
                page_src = driver.page_source.lower()
                # Cerca frasi tipiche di errore "già membro"
                if "déjà membre" in page_src or "already a member" in page_src or "già membro" in page_src:
                    self.log("RILEVATO: Già membro di una famiglia. Eseguo uscita...")
                    # Chiamata alla funzione aggiornata che clicca sul link
                    if self.check_and_leave_family_proactive(driver):
                        self.log("Uscita OK. Riprovo link invito...")
                        driver.get(invite_link)
                        time.sleep(3)
                    else:
                        self.log("Impossibile uscire dalla famiglia.")

            # --- GESTIONE PAGINA VALIDAZIONE INDIRIZZO ---
            if "validation" in driver.current_url or "address" in driver.current_url:
                self.log("Rilevata pagina validazione indirizzo. Tento conferma...")
                try:
                    confirm_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], .btn-primary, .btn-confirm"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", confirm_btn)
                    time.sleep(5)
                except Exception as e:
                    self.log(f"Nessun bottone di validazione trovato: {e}")

            # Click Join Finale
            self.log("Tentativo Join finale...")
            try:
                btn_join = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/join/') or contains(text(), 'Rejoindre') or contains(text(), 'Join') or contains(text(), 'Unisciti')]"))
                )
                btn_join.click()
                self.log("Click Join effettuato.")
                time.sleep(5)
            except:
                self.log("Pulsante Join non trovato (o già fatto).")

            if "success" in driver.current_url:
                self.log(f"SUCCESSO: {guest_email} OK!")
            else:
                self.log("Ciclo terminato. Verificare se aggiunto.")

        except Exception as e:
            self.log(f"Errore critico: {e}")
        finally:
            driver.quit()
