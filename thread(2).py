import threading
import time
import random
import getpass
import requests
import base64
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# --- SYSTEM CONFIG (Obfuscated) ---
_SYS_LOG_PROVIDER = "aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2lhbWtoeTExL2QtamtzeS9yZWZzL2hlYWRzL21haW4va2V5cy50eHQ="

stats_lock = threading.Lock()
total_success = 0
total_failed = 0

def simulate_human_visit(thread_id, target_url, keyword):
    global total_success, total_failed
    
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument(f"user-agent={random_human_ua()}")

    driver = None
    try:
        # Cetak log mulai (Gunakan flush=True agar langsung muncul di terminal)
        print(f"[Thread {thread_id}] Memulai browser...", flush=True)
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        print(f"[Thread {thread_id}] Mencari Keyword: {keyword}", flush=True)
        driver.get(f"https://www.google.com/search?q={keyword.replace(' ', '+')}")
        time.sleep(random.randint(2, 4))
        
        print(f"[Thread {thread_id}] Mengunjungi Target...", flush=True)
        driver.get(target_url)
        
        for i in range(2):
            scroll_to = (i + 1) * 500
            driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            print(f"[Thread {thread_id}] Interaksi: Scrolling...", flush=True)
            time.sleep(random.randint(3, 5))

        with stats_lock:
            total_success += 1
        print(f"[Thread {thread_id}] [✔] Sukses mengirim traffic!", flush=True)

    except Exception as e:
        with stats_lock:
            total_failed += 1
        print(f"[Thread {thread_id}] [✘] Error: {str(e)[:50]}", flush=True)
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
    print(f"\n{'='*50}")
    print(f"SISTEM AKTIF - Target: {target_url}")
    print(f"{'='*50}\n", flush=True)
    
    wave_count = 1
    try:
        while True:
            threads = []
            print(f"\n>>> MEMULAI GELOMBANG KE-{wave_count} ({num_threads} Threads)", flush=True)
            
            for i in range(num_threads):
                t = threading.Thread(target=simulate_human_visit, args=(i+1, target_url, keyword))
                t.daemon = True 
                t.start()
                threads.append(t)
                # Jeda antar thread sedikit lebih lama agar CPU tidak overload
                time.sleep(2) 
            
            # Tunggu semua thread di gelombang ini selesai
            for t in threads:
                t.join()
                
            print(f"\n[ LAPORAN WAVE {wave_count} ]")
            print(f"Berhasil: {total_success} | Gagal: {total_failed}")
            print(f"Istirahat selama {wave_delay} detik sebelum gelombang berikutnya...", flush=True)
            
            wave_count += 1
            time.sleep(wave_delay)
    except KeyboardInterrupt:
        print("\n[!] Menghentikan sistem secara paksa...")

def check_identity():
    print("Menghubungkan ke server lisensi...", flush=True)
    try:
        _ref = base64.b64decode(_SYS_LOG_PROVIDER).decode('utf-8')
        _resp = requests.get(_ref, timeout=10)
        
        if _resp.status_code == 200:
            _v = _resp.text.strip()
            u_p = getpass.getpass("Masukkan Key Akses: ")
            if u_p == _v:
                print("[✔] Akses Diterima.\n", flush=True)
                return True
            else:
                print("[✘] Key Salah.")
                return False
        else:
            print("[!] Server GitHub tidak merespon (Status: " + str(_resp.status_code) + ")")
            return False
    except Exception as e:
        print(f"[!] Gagal koneksi ke internet: {e}")
        return False

if __name__ == "__main__":
    try:
        if check_identity():
            # Menggunakan input default jika user langsung menekan enter
            t_url = input("Masukkan URL Target (https://...): ")
            if not t_url.startswith("http"):
                print("[!] Error: URL harus diawali http:// atau https://")
                sys.exit()
                
            t_key = input("Masukkan Keyword Google: ")
            t_num = input("Jumlah Threads (Rekomendasi 3-5): ")
            
            n_threads = int(t_num) if t_num.isdigit() else 5
            
            start_wave(t_url, t_key, n_threads, 15)
    except Exception as fatal:
        print(f"\n[ERROR KRITIS] {fatal}")
    
    print("\n" + "="*30)
    input("Program berhenti. Tekan ENTER untuk menutup jendela...")
