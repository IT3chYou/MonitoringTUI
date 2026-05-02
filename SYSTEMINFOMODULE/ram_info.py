import platform
import subprocess
import psutil
from rich.text import Text
from rich.console import Console
from rich.table import Table
import time


class RAM:
    def __init__(self):
        self.os = platform.system().lower()
        self.console = Console()
        self.byte = (1024 ** 3)
        self.page = 0
        self.process_cache = []
        self.last_time = 0
        self.time = 3


    def ram_usage_info(self): # -> list kısmını sildik, çünkü liste döndürmüyoruz
            text = Text()

            ram = psutil.virtual_memory()
            self.byte = 1024**3 # Byte çevrimi için

            # Verileri ekliyoruz
            text.append(f"Total Ram : {ram.total / self.byte:.2f} GB\n", style="green")
            text.append(f"Used Ram : {ram.used / self.byte:.2f} GB\n", style="red")
            text.append(f"Available Ram: {ram.available / self.byte:.2f} GB\n", style="orange1")
            text.append(f"Free Ram : {ram.free / self.byte:.2f} GB\n")
            text.append(f"Ram Percent : {ram.percent}%\n", style="cyan")

            return text # Geriye 'Text' objesi dönüyor, Panel bunu anlar.






    def ram_process(self):
            peace = 30
            now = time.time()

            # 1. VERİYİ LİSTEYE ÇEVİR VE CACHE'E AT
            if not self.process_cache or now - self.last_time >= self.time:
                # ÖNEMLİ: list() ekledik ki dilimleme yapılabilsin
                try:
                    processes = list(psutil.process_iter(['pid', 'name', 'memory_info']))

                    self.process_cache = sorted(
                        processes,
                        key=lambda p: (p.info['memory_info'].rss if p.info['memory_info'] else 0),
                        reverse=True
                    )
                    self.page += 1
                    self.last_time = now
                except Exception:
                    # Eğer süreç okuma sırasında bir hata olursa cache'i bozma
                    pass

            total = len(self.process_cache)
            # Eğer henüz veri çekilmediyse boş dönmek yerine bilgi dön
            if total == 0:
                return Panel("Süreçler taranıyor...", title="Lütfen Bekleyin")

            # 2. Sayfa Sınır Kontrolü
            start = (self.page - 1) * peace
            if start >= total or start < 0:
                self.page = 1
                start = 0

            end = start + peace

            # 3. Tabloyu Oluştur (expand=True ve box=None kalsın, güzel durur)
            table = Table(
                title=f"RAM SÜREÇLERİ (Sayfa: {self.page})",
                show_header=True,
                header_style="bold magenta",
                expand=True,
                box=None
            )
            table.add_column("PID", justify="center", width=8)
            table.add_column("İsim", justify="left")
            table.add_column("RSS (MB)", justify="right", width=10)

            # 4. Listeleme
            # Burada dilimleme (slicing) yapıyoruz: [0:25] gibi
            for proc in self.process_cache[start:end]:
                try:
                    # psutil.process_iter ile 'info' sözlüğü zaten dolmuş olmalı
                    p_info = proc.info
                    rss = p_info['memory_info'].rss / (1024**2) if p_info['memory_info'] else 0

                    table.add_row(
                        str(p_info['pid']),
                        str(p_info['name'])[:25], # Uzun isimler tabloyu bozmasın
                        f"{rss:.2f}"
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue

            return table










if __name__ == "__main__":
    ram = RAM()
    ram.ram_process()
