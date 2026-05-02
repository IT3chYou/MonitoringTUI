import psutil
from rich.text import Text
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
import time
import wmi


class Disk:
    def __init__(self) -> None:
        # 1. Sabit olan disk listesini SADECE BİR KEZ alıyoruz
        self.partitions = [p for p in psutil.disk_partitions() if p.fstype and 'cdrom' not in p.opts]

        # 2. İlk IO verilerini al
        self._last_io = psutil.disk_io_counters()
        self._last_time = time.time()
        self.current_io = self._last_io # İlk başta boş kalmasın

        # WMI bağlantısını bir kez kur (Yorum satırını açarsan diye hazır dursun)
        try:
            self._wmi_conn = wmi.WMI()
        except:
            self._wmi_conn = None


    def d_update(self):
        self.current_io = psutil.disk_io_counters()

    def disk_usage(self):
            text = Text()
            # ARTIK SORGULAMA YOK: Hafızadaki self.partitions listesini kullanıyoruz
            for part in self.partitions:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    text.append(f"Disk {part.mountpoint} : {usage.percent}% Dolu\n", style="bold green")
                except:
                    continue
            return text

    def disk_usage_progressbar(self):
        progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(bar_width=80, style="cyan"),
            TextColumn("{task.percentage:.0f}%"),
            expand=False,
        )

        for part in psutil.disk_partitions():
            if not part.fstype:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                continue

            progress.add_task(
                f"Disk {part.mountpoint}",
                total=100,
                completed=usage.percent,
            )

        return progress


    def disk_io_info(self):
        io = self.current_io
        disk_text = Text()
        disk_text.append(f"Read Bytes  : {io.read_bytes / (1024 ** 3):.4f} GB\n", style="bold green")
        disk_text.append(f"Write Bytes : {io.write_bytes / (1024 ** 3):.4f} GB\n", style="orange1")
        disk_text.append(f"Read Count  : {io.read_count}\n", style="cyan")
        disk_text.append(f"Write Count : {io.write_count}\n", style="cyan")
        return disk_text




    def disk_partitions_info(self):
        text = Text()

        for part in psutil.disk_partitions(all=False):
            text.append(f"Aygıt        : {part.device}\n", style="bold cyan")
            text.append(f"Mount Point : {part.mountpoint}\n")
            text.append(f"Dosya Sist. : {part.fstype}\n")
            text.append(f"Opsiyonlar  : {part.opts}\n")
            text.append("-" * 40 + "\n", style="dim")

        return text



    def disk_io_speed(self):
            now = time.time()
            io = self.current_io # d_update'den gelen taze veri
            dt = now - self._last_time

            if dt < 0.1: # Çok hızlı döngülerde hesaplama yapma, bekle
                return Text("...")

            # Hız hesaplama
            r_speed = (io.read_bytes - self._last_io.read_bytes) / dt / (1024**2)
            w_speed = (io.write_bytes - self._last_io.write_bytes) / dt / (1024**2)

            # Bir sonraki tur için verileri sakla
            self._last_io = io
            self._last_time = now

            text = Text()
            text.append(f"Okuma: {r_speed:>6.2f} MB/s\n", style="bold green")
            text.append(f"Yazma: {w_speed:>6.2f} MB/s\n", style="bold orange1")
            return text






    """def disk_health_wmi(self):
        c = wmi.WMI()
        text = Text()

        for disk in c.Win32_DiskDrive():
            text.append(f"Disk: {disk.Model}\n", style="bold green")
            status = disk.Status
            text.append(f"Status: {status}\n")
            text.append("-" * 30 + "\n", style="dim")

        return text
"""

if __name__ == "__main__":
    disk = Disk()
    disk.disk_usage()
    disk.disk_io_info()
