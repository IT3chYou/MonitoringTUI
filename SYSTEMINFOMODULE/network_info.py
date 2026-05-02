import psutil
import time
from rich.text import Text
import speedtest
import threading
import platform
import socket
import requests
import subprocess
import re
from rich.table import Table




class Network:
    def __init__(self) -> None:
        # --- 1. HIZLI TANIMLAMALAR (Donma Yapmaz) ---
        self._running = True
        self._lock = threading.Lock()
        self.system = platform.system()
        self.connections = []

        # Varsayılan değerler (Veri gelene kadar ekranda bunlar gözükür)
        self.ip_address = "Calculating..."
        self.netmask = "Calculating..."
        self.public_ip_address = "Calculating..."
        self.dhcp_server = "Calculating..."
        self.mac_address = "Calculating..."
        self.dns_list = []
        self.gateway = "Calculating..."
        self.open_public_info = {}
        self.speedtest_result = Text("Waiting...", style="dim cyan")

        # Trafik verileri
        self._last = psutil.net_io_counters()
        self._traffic_last_time = time.time()
        self._cached_connections = []
        self._process_cache = {}
        self.page = 0
        self._page_last_time = time.time()

        # --- 2. DONMA YAPAN ALANI ARKA PLANA AT ---

        # Sadece yerel ve hızlı olanı hemen çalıştır
        self.info_ipv4()

        # ASIL DÜZELTME: subprocess ve requests içeren ağır işleri thread'e taşıyoruz.
        # Böylece bu fonksiyonlar 10 saniye sürse bile terminal arayüzün asla donmaz.
        threading.Thread(target=self._heavy_init_worker, daemon=True).start()

        # Bağlantı listesi toplayıcısı
        threading.Thread(target=self.connection_collector, daemon=True).start()

    def _heavy_init_worker(self):
        """Donmaya sebep olan tüm 'beklemeli' işler burada toplanır."""
        try:
            # Subprocess komutlarını thread içinde bir kez çalıştırıp önbelleğe alıyoruz
            self.ipconfig_command = subprocess.check_output("ipconfig /all", shell=True, text=True)
            self.ip_route_command = subprocess.check_output("ip route", shell=True, text=True) if self.system != "Windows" else ""

            # Statik bilgileri doldur (İnternet ve sistem sorguları)
            self.info_public_ip() # requests içerir
            self.dhcp_server_info()
            self.mac_address_info()
            self.dns_servers()
            self.gateway_info()

            # API sorgusunu thread içinde yapıyoruz
            self.req = requests.get("http://ip-api.com/json/", timeout=5)
            self.public_info()
        except Exception as e:
            # Hata alsa bile ana program donmaz, sadece bu bilgiler eksik kalır
            pass

    def n_update(self):
        """Bu fonksiyon saniyede bir çağrılabilir, artık çok hafif."""
        self.current_net_io = psutil.net_io_counters()


    def public_info(self):
        if not hasattr(self, 'req'): # Eğer req hiç oluşmadıysa çık
            return Text("Offline", style="red")
        try:
            if self.req.status_code != 200:
                return Text("API Error", style="red")
            self.open_public_info = self.req.json()

        except Exception as e:
            print("Error : ", e)

    def print_open_public_info(self):
        text = Text()
        for key , value in self.open_public_info.items():
            text.append(f"{key.capitalize():15}", style="cyan")
            text.append(f": {value}\n", style="white")

        return text



    def connection_collector(self):
        while self._running:
            data = psutil.net_connections(kind='inet')
            with self._lock:
                self._cached_connections = data
            time.sleep(3)


    def update_connections(self):
        per_page = 20
        now = time.time()

        # 5 saniyede bir sayfa artışı
        if now - self._page_last_time >= 5:
            self._page_last_time = now
            self.page += 1

        with self._lock:
            raw = list(self._cached_connections)

        if not raw:
            return

        total = len(raw)

        # Sayfa sınır kontrolü ve başa dönme
        start = (self.page) * per_page
        if start >= total:
            self.page = 0
            start = 0

        end = start + per_page
        self.connections.clear()

        # Dilimleme (Sadece o sayfanın verisini işle, performans kazandırır)
        for conn in raw[start:end]:
            if not conn.pid: continue

            # Cache'den isim çekme
            pid = conn.pid
            if pid not in self._process_cache:
                try:
                    self._process_cache[pid] = psutil.Process(pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self._process_cache[pid] = "N/A"

            process_name = self._process_cache[pid]

            # Adres formatlama
            local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "0.0.0.0"
            remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
            protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"

            self.connections.append({
                "pid": str(pid),
                "process": process_name,
                "local": local,
                "remote": remote,
                "status": conn.status,
                "protocol": protocol
            })

    def print_it(self):
        self.update_connections()
        # Sayfa numarasını başlığa ekledik
        table = Table(
            title=f"[bold cyan]Active Connections[/bold cyan] [dim](Page {self.page + 1})[/dim]",
            show_header=True,
            header_style="bold cyan",
            border_style="bright_blue",
            row_styles=["none", "dim"],
            expand=True,
            box=None
        )

        table.add_column("PID", style="yellow", width=8)
        table.add_column("Process", style="green", ratio=2)
        table.add_column("Local Address", style="magenta", ratio=3)
        table.add_column("Remote Address", style="red", ratio=3)
        table.add_column("Status", style="bold")
        table.add_column("Proto", justify="center", style="magenta", width=6)

        for conn in self.connections:
            table.add_row(
                conn["pid"],
                conn["process"][:20], # Çok uzun isimleri keser
                conn["local"],
                conn["remote"],
                conn["status"],
                conn["protocol"]
            )

        return table






    def info_public_ip(self):
            # Sigorta: Değişken yoksa oluştur (AttributeError'u tamamen bitirir)
            if not hasattr(self, '_public_ip_last_fetch'):
                self._public_ip_last_fetch = 0

            now = time.time()
            # 60 saniye sınırı
            if now - self._public_ip_last_fetch < 60 and self.public_ip_address != "Calculating...":
                return self.public_ip_address

            try:
                response = requests.get("https://api.ipify.org?format=json", timeout=3)
                if response.status_code == 200:
                    self.public_ip_address = response.json()["ip"]
                    self._public_ip_last_fetch = now
            except Exception:
                self.public_ip_address = "Offline"

            return self.public_ip_address

    def dns_servers(self):
        try:
            if self.system.lower() == "windows":
                output = self.ipconfig_command
                self.dns_list = re.findall(r"DNS Servers[ .]*: (\d+\.\d+\.\d+\.\d+)", output)
            else:
                with open("/etc/resolv.conf") as f:
                    self.dns_list = re.findall(r"nameserver (\d+\.\d+\.\d+\.\d+)", f.read())
        except:
            self.dns_list = []


    def gateway_info(self):
        try:
            if self.system.lower() == "windows":
                output = self.ipconfig_command
                match = re.search(r"Default Gateway[ .]*: (\d+\.\d+\.\d+\.\d+)", output)#[ .]* → “boşluk veya nokta olabilir, hiç olmayabilir veya birden fazla olabilir”.
                self.gateway = match.group(1) if match else None
            else:
                output = self.ip_route_command
                match = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", output)
                self.gateway = match.group(1) if match else None
        except Exception:
            self.gateway = None



    def dhcp_server_info(self):
        try:
            if self.system.lower() == "windows":
                output = self.ipconfig_command

                for line in output.splitlines():
                    if re.search(r"DHCP", line, re.IGNORECASE):
                        ip_match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
                        if ip_match:
                            self.dhcp_server = f"{ip_match.group()}"

            else:
                output = self.ip_route_command

                for line in output.splitlines():
                    if line.startswith("default"):
                        ip_match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
                        if ip_match:
                            self.dhcp_server = f"{ip_match.group()}"

        except Exception as e:
            self.dhcp_server = f"Hata: {e}"

    def broadcast_calculator(self):
        ipo1, ipo2, ipo3, ipo4 = self.ip_address.split(".")
        net1, net2, net3, net4 = self.netmask.split(".")

        bc1 = int(ipo1) | (255 - int(net1))# 192 | 255 - 255 = 192 | 0  = 192
        bc2 = int(ipo2) | (255 - int(net2))# 168 | 255 - 255 = 168 | 0 = 168
        bc3 = int(ipo3) | (255 - int(net3))# 1   | 255 - 255 = 1   | 0 = 1
        bc4 = int(ipo4) | (255 - int(net4))# 10   | 255 - 0  = 255 | 0 = 255

        self.broadcast_address = f"{bc1}.{bc2}.{bc3}.{bc4}"
        #Or İşlemi And Opratörü Gibi Alt Alata Hesaplar Ama Eşitlemez Çıkan Sayı Hesaplar Ve Topla
        #66 = 01000010
        #63 = 00111111
        #127 dir

    def network_address_calculator(self):
        ipo1, ipo2, ipo3, ipo4 = self.ip_address.split(".")
        net1, net2, net3, net4 = self.netmask.split(".")

        re1 = int(ipo1) & int(net1)
        re2 = int(ipo2) & int(net2)
        re3 = int(ipo3) & int(net3)
        re4 = int(ipo4) & int(net4)

        self.network_address = f"{re1}.{re2}.{re3}.{re4}"
        #return f"{reocted1}.{reocted2}.{reocted3}.{reocted4}"
        #and İşlemi İse Kalan Biti Hesaplar Ve Yazdırır
        #66 = 01000010
        #63 = 00111111
        #     01000011 = 67 Yapar

    def info_ipv4(self):
        # Önbellekleme ekleyelim: Eğer IP zaten varsa ve kısa süre önce hesaplandıysa tekrar girme
        net_if_addrs = psutil.net_if_addrs()
        text = Text()

        for interface_name, addresses in net_if_addrs.items():
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    # Loopback (127.0.0.1) adresini genellikle görmek istemeyiz, filtreleyebilirsin
                    if addr.address == "127.0.0.1": continue

                    text.append(f"{'Interface:':12}{interface_name}\n")
                    text.append(f"{'IPv4 Addr:':12}{addr.address}\n")
                    text.append(f"{'Netmask:':12}{addr.netmask}\n")

                    # Sadece IP değiştiyse hesaplama yap
                    if self.ip_address != addr.address:
                        self.ip_address = addr.address
                        self.netmask = addr.netmask
                        self.network_address_calculator()
                        self.broadcast_calculator()

                    text.append(f"{'Network:':12}{self.network_address}\n")
                    text.append(f"{'Broadcast:':12}{self.broadcast_address}\n")
                    text.append("-" * 20 + "\n", style="dim")

        return text




    def info_ipv6(self):
        text = Text()
        net_if_addrs = psutil.net_if_addrs()

        for interface_name, addresses in net_if_addrs.items():
            for addr in addresses:
                if addr.family == socket.AF_INET6:
                    text.append(f"{'Interface:':12}{interface_name}\n")
                    text.append(f"{'IPv6 Addr:':12}{addr.address}\n")
                    text.append(f"{'Netmask:':12}{addr.netmask}\n")
                    text.append(""*40 + "\n")  # opsiyonel, ayırıcı

        return text

    def host_info(self):
        text = Text()
        hostname = socket.gethostname()
        pubip = self.info_public_ip()


        text.append(f"{'Hostname:':12}{hostname}\n")
        text.append(f"{'Public Ip:':12}{pubip}\n")
        text.append(f"{'DHCP Server:':12}{self.dhcp_server}\n")
        mac = self.mac_address.replace("-", ":") if self.mac_address else "N/A"
        text.append(f"{'Mac Addr:':10}{mac}\n")
        text.append(f"{'DNS Addr:':10}{self.dns_list}\n")
        text.append(f"{'Getaway Addr:':10}{self.gateway}\n")

        return text

    def mac_address_info(self):
        if self.system.lower() == "windows":
            try:
                output = subprocess.check_output("getmac", shell=True, text=True)

                # MAC adres formatı: XX-XX-XX-XX-XX-XX
                match = re.search(r"([0-9A-F]{2}-){5}[0-9A-F]{2}", output, re.I)

                if match:
                    self.mac_address = match.group(0)
                else:
                    self.mac_address = None

            except Exception as e:
                self.mac_address = None



        else:
            try:
                output = subprocess.check_output("ip link", shell=True, text=True)

                match = re.search(r"([0-9a-f]{2}:){5}[0-9a-f]{2}", output, re.I)

                if match:
                    self.mac_address = match.group(0)
                else:
                    self.mac_address = None

            except Exception:
                self.mac_address = None

    def first_panel_network_info(self):
        text = Text()
        text.append(f"{self.host_info()}\n",style="green")
        text.append(f"{self.info_ipv4()}\n",style="orange1")
        text.append(f"{self.info_ipv6()}\n",style="red")
        text.append(f"{self.net_info2()}\n",style="cyan")
        return text
#Network Panel Finish


#SystemPanel Start
    def upload_and_download_info(self):
        text = Text()
        value = psutil.net_io_counters()
        text.append(f"Download : {value.bytes_recv / (1024**2):.2f} MB\n", style="green")
        text.append(f"Upload   : {value.bytes_sent / (1024**2):.2f} MB\n", style="cyan")
        return text

    def network_speed_in(self):
        now = time.time()
        cur = psutil.net_io_counters()

        dt = now - self._traffic_last_time
        if dt == 0:
            return Text("Hesaplanıyor...\n")

        down = (cur.bytes_recv - self._last.bytes_recv) / dt / 1024  # KB/s
        up   = (cur.bytes_sent - self._last.bytes_sent) / dt / 1024   # KB/s

        self._last = cur
        self._traffic_last_time = now

        text = Text()
        text.append(f"↓ {down:.1f} KB/s\n", style="green")
        text.append(f"↑ {up:.1f} KB/s\n", style="cyan")
        return text

    def start_speedtest(self):
        # speedtest'i thread ile çalıştır
        thread = threading.Thread(target=self._run_speedtest, daemon=True)
        thread.start()

    def _run_speedtest(self):
        try:
            # Başlangıçta kullanıcıya bilgi verelim
            self.speedtest_result = Text("Ölçüm yapılıyor... ⏳", style="bold cyan")

            # secure=True: Sertifika hatalarını önler
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()

            # Ölçümler (Bayt -> MB/s dönüşümü)
            download_speed = st.download() / (1024 * 1024)
            upload_speed = st.upload() / (1024 * 1024)
            ping = st.results.ping

            # Sonuçları Text objesine yaz
            res = Text()
            res.append(f"📥 Download: {download_speed:.2f} MB/s\n", style="bold orange1")
            res.append(f"📤 Upload  : {upload_speed:.2f} MB/s\n", style="bold yellow")
            res.append(f"⚡ Ping    : {ping:.0f} ms\n", style="bold red")

            self.speedtest_result = res

        except Exception as e:
            # Hata durumunda ekrana hata mesajı bas
            self.speedtest_result = Text(f"❌ Speedtest Hatası: {str(e)[:30]}...", style="bold white on red")



    def net_info1(self):
        net_if_addrs = psutil.net_if_addrs()
        text = Text()
        for iface_name, addrs in net_if_addrs.items():

            text.append(f"Interface: {iface_name}\n")
            for addr in addrs:
                text.append(f"  Address family: {addr.family}\n")
                text.append(f"  Address       : {addr.address}\n")
                text.append(f"  Netmask       : {addr.netmask}\n")
                text.append(f"  Broadcast     : {addr.broadcast}\n")
            text.append(f"-"*100,style="dim")

        return text

    def net_info2(self):
        net_if_stats = psutil.net_if_stats()
        text = Text()
        for iface_name, stats in net_if_stats.items():
            text.append(f"Interface: {iface_name}\n")
            text.append(f"  Up?        : {stats.isup}\n")
            text.append(f"  Speed      : {stats.speed} Mbps\n")
            text.append(f"  Duplex     : {stats.duplex}\n")
            text.append(f"  MTU        : {stats.mtu}\n")
        return text
