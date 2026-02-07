import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class YopmailHandler:
    def __init__(self, driver, logger_callback):
        self.driver = driver
        self.log = logger_callback

    def get_invite_link(self, yopmail_user):
        """
        Logica ottimizzata:
        1. Check immediato mail aperta (ifmail).
        2. Se fallisce, check 2^ mail in lista (ifmails -> click index 1).
        3. Se fallisce, check 1^ mail in lista.
        """
        self.log(f"--- [Yopmail] Accesso: {yopmail_user} ---")
        
        main_window = self.driver.current_window_handle
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get("https://yopmail.com/it/")
        
        link_found = None
        
        try:
            # --- Login & Cookie ---
            self._handle_cookies()
            wait = WebDriverWait(self.driver, 15)
            try:
                login_input = wait.until(EC.element_to_be_clickable((By.ID, "login")))
                login_input.clear()
                login_input.send_keys(yopmail_user)
                login_input.send_keys(Keys.RETURN)
            except:
                self._handle_cookies() # Riprova cookie
                try:
                    self.driver.find_element(By.ID, "login").send_keys(yopmail_user + Keys.RETURN)
                except:
                    self.log("Errore login Yopmail.")
                    self._close_tab(main_window)
                    return None

            self.log("Inbox caricata. Controllo rapido...")
            time.sleep(3) # Tempo tecnico caricamento frame
            
            # --- TENTATIVO 1: CONTROLLO MAIL GIÀ APERTA (Default) ---
            self.driver.switch_to.default_content()
            try:
                # Vai subito al frame di lettura
                WebDriverWait(self.driver, 4).until(EC.frame_to_be_available_and_switch_to_it("ifmail"))
                link_found = self._extract_link_from_body()
                
                if link_found:
                    self.log("LINK TROVATO SUBITO (Mail già aperta)!")
                    self._close_tab(main_window)
                    return link_found
                else:
                    self.log("Link non trovato nella mail aperta. Controllo lista...")
            except:
                self.log("Nessuna mail aperta o frame non pronto.")

            # --- TENTATIVO 2: CONTROLLO 2^ MAIL (Penultima) ---
            self.driver.switch_to.default_content()
            try:
                WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it("ifmails"))
                messages = self.driver.find_elements(By.CSS_SELECTOR, "div.m")
                
                # Se ci sono almeno 2 mail, clicca la seconda (indice 1)
                if len(messages) >= 2:
                    self.log("Clicco sulla 2^ mail della lista...")
                    self.driver.execute_script("arguments[0].click();", messages[1])
                    time.sleep(2)
                    
                    # Controllo contenuto
                    self.driver.switch_to.default_content()
                    WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it("ifmail"))
                    link_found = self._extract_link_from_body()
                    
                    if link_found:
                        self.log("LINK TROVATO (nella 2^ mail)!")
                        self._close_tab(main_window)
                        return link_found
                
                # Se fallisce o ce n'è una sola, prova la prima (indice 0)
                elif messages:
                    self.log("Clicco sulla 1^ mail (fallback)...")
                    self.driver.execute_script("arguments[0].click();", messages[0])
                    time.sleep(2)
                    
                    self.driver.switch_to.default_content()
                    WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it("ifmail"))
                    link_found = self._extract_link_from_body()
                    if link_found:
                        self.log("LINK TROVATO (nella 1^ mail)!")
            except Exception as e:
                self.log(f"Errore navigazione lista: {e}")

        except Exception as e:
            self.log(f"Errore Critico Yopmail: {e}")
        finally:
            self._close_tab(main_window)
        
        return link_found

    def _handle_cookies(self):
        try:
            cookie_spec = self.driver.find_elements(By.XPATH, "//p[contains(@class, 'fc-button-label') and contains(text(), 'Acconsento')]")
            if cookie_spec:
                self.driver.execute_script("arguments[0].click();", cookie_spec[0])
                time.sleep(1)
                return
            cookie_btn = self.driver.find_elements(By.ID, "accept")
            if cookie_btn:
                self.driver.execute_script("arguments[0].click();", cookie_btn[0])
                time.sleep(1)
        except: pass

    def _extract_link_from_body(self):
        """
        Estrae link cercando SPECIFICATAMENTE il bottone 'ACCEPTER L'INVITATION'.
        Pulisce il testo da spazi e newlines per evitare falsi negativi.
        """
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    # Ottieni testo grezzo e puliscilo da \n, \t e spazi multipli
                    raw_txt = link.get_attribute("textContent") or ""
                    clean_txt = " ".join(raw_txt.split()).upper()
                    href = link.get_attribute("href")
                    
                    if not href: continue

                    # Controllo ESATTO sulla frase richiesta
                    if "ACCEPTER L'INVITATION" in clean_txt:
                        self.log(f"Trovato bottone esatto: {clean_txt}")
                        return href
                    
                    # Fallback sul testo "JOIN"
                    if "JOIN" in clean_txt:
                        return href
                    
                    # Fallback estremo solo su dominio di tracciamento
                    if "clicks.qobuz.com" in href and ("token" in href or "join" in href):
                        return href
                        
                except: continue
        except: pass
        return None

    def _close_tab(self, main_window):
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
            self.driver.switch_to.window(main_window)
        except: pass
