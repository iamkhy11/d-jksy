import threading
import time
import random
import getpass
import requests
import base64
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- SYSTEM CONFIG (Obfuscated) ---
_SYS_LOG_PROVIDER = "aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2lhbWtoeTExL2QtamtzeS9yZWZzL2hlYWRzL21haW4va2V5cy50eHQ="

stats_lock = threading.Lock()
total_success = 0
total_failed = 0

def simulate_human_visit(thread_id, target_url, keyword):
    global total_success, total_failed
    
    options = Options()
    options.add_argument("--headless=new") # Gunakan mode headless terbaru (lebih stabil)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu") # Mengurangi beban grafis
    options.add_argument("--window-size=1280,720")
    options.add_argument("--blink-settings=imagesEnabled=false") # Matikan gambar agar hemat RAM
    options.add_argument("--disable-extensions")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument(f"user-agent={random_human_ua()}")

    driver = None
    try:
        print(f"[Thread {thread_id}] Menyiapkan browser...", flush=True)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(45) # Lebih lama karena RAM 8GB mungkin agak lambat
        
        print(f"[Thread {thread_id}] Searching: {keyword}", flush=True)
        driver.get(f"https://www.google.com/search?q={keyword.replace(' ', '+')}")
        time.sleep(random.randint(3, 5))
        
        print(f"[Thread {thread_id}] Visiting: {target_url}", flush=True)
        driver.get(target_url)
        
        # Simulasi scroll ringan
        for i in range(2):
            scroll_to = (i + 1) * 400
            driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            time.sleep(random.randint(4, 6))

        with stats_lock:
            total_success += 1
        print(f"[Thread {thread_id}] [✔] Berhasil!", flush=True)

    except Exception as e:
        with stats_lock:
            total_failed += 1
        print(f"[Thread {thread_id}] [✘] Error: Resource Busy / Timeout", flush=True)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def random_human_ua():
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0"
    ]
    return random.choice(uas)

def start_wave(target_url, keyword, num_threads, wave_delay):
    print(f"\n{'='*50}\nRUNNING ON 8GB RAM MODE\n{'='*50}")
    wave_count = 1
    try:
        while True:
            threads = []
            print(f"\n>>> WAVE {wave_count}", flush=True)
            for i in range(num_threads):
                t = threading.Thread(target=simulate_human_visit, args=(i+1, target_url, keyword))
                t.daemon = True 
                t.start()
                threads.append(t)
                # JEDA PENTING: Jangan buka barengan agar RAM tidak kaget
                time.sleep(6) 
            
            for t in threads:
                t.join()
                
            print(f"\n[ STATS | Success: {total_success} | Failed: {total_failed} ]")
            wave_count += 1
            time.sleep(wave_delay)
    except KeyboardInterrupt:
        print("\n[!] Program dihentikan.")

def check_identity():
    try:
        _ref = base64.b64decode(_SYS_LOG_PROVIDER).decode('utf-8')
        _v = requests.get(_ref, timeout=10).text.strip()
        u_p = getpass.getpass("Masukkan Key: ")
        return u_p == _v
    except:
        return False

if __name__ == "__main__":
    # Bersihkan sisa chrome sebelum mulai
    os.system("taskkill /F /IM chrome.exe /T > nul 2>&1")
    os.system("taskkill /F /IM chromedriver.exe /T > nul 2>&1")

    if check_identity():
        t_url = input("Target URL: ")
        t_key = input("Keyword: ")
        t_num = input("Threads (Saran: 2 atau 3): ")
        
        n_threads = int(t_num) if t_num.isdigit() else 2
        start_wave(t_url, t_key, n_threads, 15)
    else:
        print("Invalid Key!")
        time.sleep(3)
