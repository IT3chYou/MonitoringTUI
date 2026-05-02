import platform
import psutil
import socket
from requests.models import parse_header_links
from rich.text import Text
import sys
import GPUtil
import time
import threading
from datetime import datetime
from SYSTEMINFOMODULE.network_info import Network





class Sysinfo:
    def __init__(self) -> None:
        self.network = Network()
        # info_public_ip zaten Network.__init__ içinde thread ile başlıyor,
        # burada tekrar başlatmana gerek yok (eğer Network sınıfında varsa).

        # Sabit bilgiler
        self.os_info = f"{platform.system()} {platform.release()}"
        self.pyt_version = platform.python_version()
        self.pyt_exe = sys.executable
        self.hostname = socket.gethostname()






    def all_info(self):
            """Header dahil tüm sistem bilgilerini tek bir gövdede toplar."""
            final_text = Text()

            # 1. BÖLÜM: SİSTEM KİMLİĞİ (Eskiden Header'da olanlar)
            final_text.append(" [SİSTEM KİMLİĞİ] \n", style="bold underline cyan")
            final_text.append(f"• İşletim S. : ", style="bold")
            final_text.append(f"{self.os_info}\n", style="cyan")
            final_text.append(f"• Bilgisayar : ", style="bold")
            final_text.append(f"{self.hostname}\n", style="bold red")

            # IP ve Batarya Durumu
            current_ip = getattr(self.network, 'public_ip_address', 'Bağlantı Yok')
            final_text.append(f"• Dış IP     : ", style="bold")
            final_text.append(f"{current_ip}\n", style="bold magenta")

            battery = psutil.sensors_battery()
            if battery:
                plugged = "Prizde" if battery.power_plugged else "Pilde"
                bat_color = "bold green" if battery.percent > 30 else "bold red"
                final_text.append(f"• Batarya    : ", style="bold")
                final_text.append(f"%{battery.percent} ({plugged})\n", style=bat_color)

            final_text.append("─" * 45 + "\n", style="dim cyan")

            # 2. BÖLÜM: DONANIM DETAYLARI
            final_text.append(" [DONANIM MİMARİSİ] \n", style="bold underline yellow")
            final_text.append(f"• İşlemci     : ", style="bold")
            final_text.append(f"{platform.processor()}\n", style="white")
            final_text.append(f"• Çekirdek    : ", style="bold")
            final_text.append(f"{psutil.cpu_count(logical=False)} Fiziksel / {psutil.cpu_count(logical=True)} İzlek\n", style="orange1")

            total_ram = psutil.virtual_memory().total / (1024 ** 3)
            final_text.append(f"• Toplam RAM  : ", style="bold")
            final_text.append(f"{total_ram:.2f} GB\n", style="yellow")

            final_text.append("─" * 45 + "\n", style="dim cyan")

            # 3. BÖLÜM: YAZILIM ORTAMI & ZAMAN
            final_text.append(" [YAZILIM & ZAMAN] \n", style="bold underline green")
            final_text.append(f"• Python Ver  : ", style="bold")
            final_text.append(f"{self.pyt_version}\n", style="bold orange1")
            final_text.append(f"• Mimari      : ", style="bold")
            final_text.append(f"{platform.machine()} ({platform.architecture()[0]})\n", style="white")
            final_text.append(f"• Yerel Saat  : ", style="bold")
            final_text.append(f"{datetime.now().strftime('%H:%M:%S')}\n", style="bold white on blue")

            final_text.append("─" * 45 + "\n", style="dim cyan")

            # 4. BÖLÜM: EKRAN KARTI (GPU)
            final_text.append(" [EKRAN KARTI ÜNİTESİ] \n", style="bold underline magenta")
            final_text.append(self.gpu_info())

            return final_text



    def gpu_info(self):
        """GPU bilgilerini Rich.Text formatında döner"""
        text = Text()
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return Text("GPU Tespit Edilemedi", style="dim red")

            for gpu in gpus:
                # GPU İsmi ve Sıcaklık Durumu
                temp_style = "green" if gpu.temperature < 75 else "bold red"
                text.append(f"• Model: ", style="bold")
                text.append(f"{gpu.name}\n", style="magenta")

                text.append(f"  Isı  : ", style="bold")
                text.append(f"{gpu.temperature}°C", style=temp_style)
                text.append(f" | Yük: %{gpu.load*100:.1f}\n", style="cyan")

                # VRAM Barı gibi gösterim
                vram_percent = (gpu.memoryUsed / gpu.memoryTotal) * 100
                vram_style = "green" if vram_percent < 80 else "red"
                text.append(f"  VRAM : ", style="bold")
                text.append(f"{gpu.memoryUsed:.0f}/{gpu.memoryTotal:.0f} MB", style=vram_style)
                text.append(f" (%{vram_percent:.1f})\n", style="dim")

                text.append("  " + "─" * 20 + "\n", style="dim")
        except Exception as e:
            text.append(f"GPU Hatası: {str(e)}", style="bold red")
        return text



    def get_header_text(self):
            text = Text()

            # Dinamik verileri fonksiyona girdiğimizde tazeleyelim
            battery = psutil.sensors_battery()

            # Sol: Sistem
            text.append(f" {self.os_info} ", style="bold cyan")
            text.append(" | ", style="dim")
            text.append(f"{self.hostname} ", style="bold red")

            # Orta: Python
            text.append(" | ", style="dim")
            text.append(f"PY: {self.pyt_version} ", style="bold orange1")

            # Sağ: Donanım & Zaman
            if battery:
                plugged = "🔌" if battery.power_plugged else "🔋"
                color = "bold green" if battery.percent > 25 else "bold red"
                text.append(" | ", style="dim")
                text.append(f"{plugged} %{battery.percent} ", style=color)

            # Public IP (Arka plandaki Network sınıfından besleniyor)
            current_ip = getattr(self.network, 'public_ip_address', 'N/A')
            text.append(" | ", style="dim")
            text.append(f" IP: {current_ip} ", style="bold magenta")

            # Canlı Saat (Arka plan rengiyle vurgula)
            text.append(" | ", style="dim")
            text.append(f" {datetime.now().strftime('%H:%M:%S')} ", style="bold white on blue")

            return text



    def get_default_health_text(self):
            text = Text()
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory().percent

            # Görsel Uyarı Renkleri
            cpu_style = "bold green" if cpu_usage < 75 else "bold red"
            ram_style = "bold green" if ram_usage < 80 else "bold red"

            text.append(f" 💻 CPU: {cpu_usage}% ", style=cpu_style)
            text.append(" | ", style="dim")

            text.append(f" 🧠 RAM: {ram_usage}% ", style=ram_style)

            # Güvenli GPU Kontrolü
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_style = "bold green" if gpu.temperature < 70 else "bold orange1"
                    text.append(" | ", style="dim")
                    text.append(f" 🎮 GPU: {gpu.temperature}°C ", style=gpu_style)
            except:
                pass

            return text



    def get_general_system_info(self):
        text = Text()

        text.append(f"OS: {platform.system()}\n", style="red")
        text.append(f"Version: {platform.version()}\n", style="red")
        text.append(f"Release: {platform.release()}\n", style="red")
        text.append(f"Architecture: {platform.machine()}\n", style="white")

        text.append(f"CPU: {platform.processor()}\n", style="red")
        text.append(f"CPU Cores: {psutil.cpu_count(logical=False)}\n", style="cyan")
        text.append(f"CPU Threads: {psutil.cpu_count(logical=True)}\n", style="orange1")
        battery = psutil.sensors_battery()
        if battery:
            plugged = "Prizde" if battery.power_plugged else "Pilde"
            text.append(f"Batarya: %{battery.percent} ({plugged})\n", style="bold yellow")
        else:
            text.append("Batarya: Bulunamadı\n", style="dim")

        text.append(
            f"Total RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB\n",
            style="yellow"
        )

        text.append(f"Computer Name: {socket.gethostname()}\n", style="green")

        return text
