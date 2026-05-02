import psutil
import time
import threading
from rich.table import Table
from rich.console import Console
from datetime import datetime
import platform
import socket

class Process:
    def __init__(self) -> None:
        self.indices = {"basic": 0, "cpu": 0, "ram": 0, "system": 0, "network": 0}
        self.last_times = {"basic": 0, "cpu": 0, "ram": 0, "system": 0, "network": 0}
        self.last_page_time = time.time()
        self.page_interval = 1
        self.time = 10 #her 10 saniyede bir "Git ve güncel verileri topla,
        self.os = platform.platform()
        self.page_size = 5
        self.index = 0  # 0'dan başlamak listeler için daha güvenlidir
        self.main_process_cache = []
        self.cpu_process_cache = []
        self.ram_process_cache =[]
        self.system_process_cache =  []
        self.network_process_cache = []


        
        self.update_main_process = []
        
        self.threading_lock = threading.Lock()
        for p in psutil.process_iter():
            try:
                p.cpu_percent(None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Arka planda veriyi toplamaya başla
        daemon_thread = threading.Thread(target=self.main_process, daemon=True)
        daemon_thread.start()

        cpu_thread = threading.Thread(target=self.cpu_process, daemon=True)
        cpu_thread.start()

        sys_thread = threading.Thread(target=self.system_process, daemon=True)
        sys_thread.start()

        ram = threading.Thread(target=self.ram_process, daemon=True)
        ram.start()

        network = threading.Thread(target=self.network_process, daemon=True)
        network.start()

        """
            def main_process(self):

                while True:

                    cmdline-exe
                    raw = list(psutil.process_iter(attrs=[
                        "pid"+,"name"+,"exe",+"cmdline","username","status"+,"create_time+",
                        ,"memory_percent"+,"memory_info+",
                        "memory_full_info+","num_threads+","threads","open_files",
                        "cwd+","ppid"+,"nice",+"num_handles+","io_counters+"
                    ]))

                    # LOCK SADECE SWAP İÇİN
                    with self.threading_lock:
                        self.main_process_cache = raw

                    time.sleep(3)
        """
    




    def foreach_process(self, mode="basic"):
        end = 1
        start = 1


        with self.threading_lock:
            now = time.time()
            # 1. Önce Cache kopyasını al
            if mode == "network":
                cache = self.network_process_cache.copy()
                # Önce tüm listeyi sırala
                cache = sorted(cache, key=lambda x: x.pid if x.pid else 0)
            elif mode == "ram":
                cache = self.ram_process_cache.copy()
                # Önce tüm listeyi RAM'e göre sırala
                cache = sorted(cache, key=lambda x: x.get('memory_info').rss if x.get('memory_info') else 0, reverse=True)
            elif mode == "cpu":
                cache = self.cpu_process_cache.copy()
                cache = sorted(cache, key=lambda x: x.get('cpu_percent', 0), reverse=True)

            elif mode == "system":
                cache = self.system_process_cache.copy()
               
          
            else:
                cache = self.main_process_cache.copy()

           
            if not cache: return

            # --- MODA ÖZEL ZAMAN VE INDEX KONTROLÜ ---
            # Eğer bu mod için 3 saniye dolduysa sadece BU modun indexini artır
            if now - self.last_times[mode] > self.page_interval:
                self.indices[mode] += self.page_size
                if self.indices[mode] >= len(cache):
                    self.indices[mode] = 0
                self.last_times[mode] = now

            # Mevcut modun indexine göre subset al
            current_idx = self.indices[mode]
            subset = cache[current_idx : current_idx + self.page_size]
            # ----------------------------------------

            self.update_main_process = []


            for info in subset:
                
                if mode == "basic":
                    self.update_main_process.append({
                        "pid": info.get("pid"),
                        "name": info.get("name", "Unknown"),
                        "status": info.get("status", "Unknown"),
                        "memory": f"{info['memory_info'].rss / (1024*1024):.1f} MB" if info.get("memory_info") else "0 MB",
                        "cpu": f"{info.get('cpu_percent',0):.1f}%",
                        "user_name": info.get("username", "Unknown"),
                        "create_time_zone": datetime.fromtimestamp(info.get("create_time")).strftime("%H:%M:%S")
                    })

                elif mode == "cpu":  # cpu mode
                    self.update_main_process.append({
                        "pid": info.get("pid"),
                        "name": info.get("name", "Unknown"),
                        "status": info.get("status", "Unknown"),
                        "cpu": f"{info.get('cpu_percent',0):.1f}%",
                        "cpu_user": info.get('cpu_user',0),
                        "cpu_system": info.get('cpu_system',0),
                        "children_user": info.get('children_user',0),
                        "children_system": info.get('children_system',0),
                        "create_time_zone": datetime.fromtimestamp(info.get("create_time")).strftime("%H:%M:%S")
                    })

                
                
                elif mode == "ram":

                    cache = sorted(cache, key=lambda x: x.get('memory_info').rss if x.get('memory_info') else 0, reverse=True)
            
                    mem = info.get("memory_info")
                    mem_full = info.get("memory_full_info")
                    io_data = info.get("io_info") 

                    self.update_main_process.append({
                        "pid": info.get("pid", 0),
                        "name": info.get("name", "Unknown"),

                        # RAM Bilgileri
                        "rss": f"{mem.rss / (1024*1024):.1f} MB" if mem else "0 MB",
                        "vms": f"{mem.vms / (1024*1024):.1f} MB" if mem else "0 MB",
                        "ram_percent": f"{info.get('memory_percent', 0):.1f}%",

                        # Detaylı RAM Bilgileri
                        "uss": f"{mem_full.uss / (1024*1024):.1f} MB" if hasattr(mem_full, 'uss') else "N/A",
                        "pss": f"{mem_full.pss / (1024*1024):.1f} MB" if hasattr(mem_full, 'pss') else "N/A",
                        "swap": f"{mem_full.swap / (1024*1024):.1f} MB" if hasattr(mem_full, 'swap') else "0 MB",

                        "shared": f"{getattr(mem, 'shared', 0) / (1024*1024):.1f} MB",
                        "data": f"{getattr(mem, 'data', 0) / (1024*1024):.1f} MB",
                        "text": f"{getattr(mem, 'text', 0) / (1024*1024):.1f} MB",

                        # IO Bilgileri (Güvenli Kontrol)
                        "read_bytes": f"{io_data.read_bytes / (1024*1024):.1f} MB" if io_data else "0 MB",
                        "write_bytes": f"{io_data.write_bytes / (1024*1024):.1f} MB" if io_data else "0 MB",
                        "read_count": str(io_data.read_count) if io_data else "0",

                        "create_time_zone": datetime.fromtimestamp(info.get("create_time", 0)).strftime("%H:%M:%S")
                    })


                elif mode == "system":

                    self.update_main_process.append({
                        "name": info.get("name", "Unknown"),
                        "parentpid": info.get("ppid", "N/A"),
                        "cmd_line": " ".join(info.get("cmdline") or ["N/A"]),
                        "exe_name": info.get("exe", "N/A"),
                        # get() yerine doğrudan veri toplama anındaki ismi kullan:
                        "_num_handle": info.get("num_handles", "0"),
                        "_num_threads": info.get("num_threads", "0"),
                    })


                elif mode == "network":
                    # Ekstra döngüye gerek yok! 'info' zaten o anki bağlantıdır.
                    conn = info 
                    try:
                        p_name = psutil.Process(conn.pid).name() if conn.pid else "System"
                    except:
                        p_name = "Unknown"

                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    proto = "TCP" if conn.type == 1 else "UDP"



                    # 1. FD (File Descriptor): Bağlantının sistemdeki kimlik numarası (varsa)
                    fd = getattr(conn, 'fd', -1) 

                    # 2. Aile (Family): IPv4 mü IPv6 mı? (Teknik bir veri)
                    family = "IPv4" if conn.family == socket.AF_INET else "IPv6"

                    # 3. Tip: Stream mi Dgram mı? (TCP/UDP'nin ham hali)
                    conn_type = "Stream" if conn.type == socket.SOCK_STREAM else "Dgram"

                    self.update_main_process.append({
                        "pid": str(conn.pid) if conn.pid else "0",
                        "process": p_name,
                        "local": laddr,
                        "remote": raddr,
                        "status": conn.status,
                        "protocol": proto,
                        "fd": fd,              # Teknik değer 1
                        "family": family,      # Teknik değer 2
                        "type": conn_type      # Teknik değer 3
                    })

                    



                else:  # cpu mode
                    self.update_main_process.append({
                        "pid": info.get("pid"),
                        "name": info.get("name", "Unknown"),
                        "status": info.get("status", "Unknown"),
                        "cpu": f"{info.get('cpu_percent',0):.1f}%",
                        "cpu_user": info.get('cpu_user',0),
                        "cpu_system": info.get('cpu_system',0),
                        "children_user": info.get('children_user',0),
                        "children_system": info.get('children_system',0),
                        "create_time_zone": datetime.fromtimestamp(info.get("create_time")).strftime("%H:%M:%S")
                    })

            self.index = end if end < len(cache) else 0


#--------------------------------------------------------------------------------------

    def main_process(self):
        while True:
            raw = []
            for proc in psutil.process_iter([
                'pid','name','status','memory_info','create_time','cpu_times','username']):
                try:
                    info = proc.info
                    info["cpu_percent"] = proc.cpu_percent(None)
                    raw.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            with self.threading_lock:
                self.main_process_cache = raw

            time.sleep(self.time)


            
    def print_main_process(self):
        mode = "basic"
        self.foreach_process(mode)
        
        table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="bright_blue",
        row_styles=["none", "dim"],  # zebra efekti
        box=None)
        
        table.add_column("PID", style="yellow",max_width=5,min_width=10,no_wrap="True")
        table.add_column("Proc Name Adı", style="green",max_width=15,min_width=10,no_wrap="True")
        table.add_column("Status", style="bold",max_width=7,min_width=10,no_wrap="True")
        table.add_column("Ram (RSS)", style="magenta",max_width=8,min_width=10,no_wrap="True")
        table.add_column("CPU", style="red",max_width=5,min_width=10,no_wrap="True")
        table.add_column("Username", style="yellow",max_width=20,min_width=10,no_wrap="True")
        table.add_column("Create Time", style="yellow",max_width=20,min_width=10,no_wrap="True")
        

        for proc in self.update_main_process:
            table.add_row(
                str(proc["pid"]),
                proc["name"],
                proc["status"],
                proc["memory"],
                proc["cpu"],
                proc["user_name"],
                str(proc["create_time_zone"])
            )

        return table




#------------------------------------------------------------------------------------


    def cpu_process(self):
        # Ölçümü başlat
        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        while True:
            raw = []
            for proc in psutil.process_iter([
                'pid','name','status','create_time','cpu_times'
            ]):
                try:
                    info = proc.info #Burada Dict Oluşturuyorum Ve Dizinin İçini Sonra Gezmek İçin Raw İçine Atıcam
                    cpu_times = proc.cpu_times()  # metod çağırılır
                    info["cpu_user"] = cpu_times.user
                    info["cpu_system"] = cpu_times.system
                    info["children_user"] = cpu_times.children_user
                    info["children_system"] = cpu_times.children_system
                    if not self.os.lower().startswith("windows"):
                        info["iowait"] = cpu_times.iowait
                    



                    raw.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            with self.threading_lock:
                self.cpu_process_cache = raw

            time.sleep(self.time)

            
    def print_cpu_process(self):
        mode = "cpu"
        self.foreach_process(mode)
        
        table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="bright_blue",
        row_styles=["none", "dim"],  # zebra efekti
        box=None)
        
        table.add_column("PID", style="yellow",min_width=10, max_width=5,no_wrap="True")
        table.add_column("Proc Name", style="green",min_width=10, max_width=15,no_wrap="True")
        table.add_column("Status", style="bold",min_width=10, max_width=7,no_wrap="True")
        table.add_column("CPU %", style="red",min_width=10, max_width=5,no_wrap="True")
        table.add_column("CPU User", style="yellow",min_width=10, max_width=10,no_wrap="True")
        table.add_column("CPU System", style="yellow", min_width=10,max_width=10,no_wrap="True")
        table.add_column("CPU Child User", style="yellow", min_width=10,max_width=10,no_wrap="True")
        table.add_column("CPU Child System", style="yellow", min_width=10,max_width=10,no_wrap="True")
        table.add_column("Create Time", style="yellow",min_width=10,max_width=10,no_wrap="True")

        for proc in self.update_main_process:
            table.add_row(
            str(proc["pid"]),
            proc["name"],
            proc["status"],
            proc["cpu"],
            f"{proc.get('cpu_user',0):.2f}",
            f"{proc.get('cpu_system',0):.2f}",
            f"{proc.get('children_user',0):.2f}",
            f"{proc.get('children_system',0):.2f}",
            str(proc["create_time_zone"])
        )

        return table










#------------------------------------------------------------------------------------


    def system_process(self):
        
        while True:
            raw = []
            for proc in psutil.process_iter([
                'pid','name','status','create_time','cmdline','exe','num_handles','num_threads','ppid'
            ]):
                try:
                    info = proc.info #Burada Dict Oluşturuyorum Ve Dizinin İçini Sonra Gezmek İçin Raw İçine Atıcam
                    raw.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            with self.threading_lock:
                self.system_process_cache = raw

            time.sleep(self.time)

            
    def print_system_process(self):
        mode = "system"
        self.foreach_process(mode)
        
        table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="bright_blue",
        row_styles=["none", "dim"],  # zebra efekti
        box=None)
        
   
        table.add_column("Process Name", style="cyan", min_width=10, max_width=20, no_wrap=True)
        table.add_column("Parent PID", style="magenta", min_width=5, max_width=10, no_wrap=True)
        table.add_column("Command Line", style="green", min_width=10, max_width=50, no_wrap=True)
        table.add_column("Path", style="yellow", min_width=10, max_width=50, no_wrap=True)
        table.add_column("Handles", style="red", min_width=5, max_width=10, no_wrap=True)
        table.add_column("Threads", style="blue", min_width=5, max_width=10, no_wrap=True)
   
     

        for proc in self.update_main_process:
            table.add_row(
            proc["name"],
            str(proc["parentpid"]),
            proc['cmd_line'],
            proc['exe_name'],
            str(proc['_num_handle']),
            str(proc['_num_threads'])
            
            
        )

        return table










#---------------------------------------------------------------------

    
    def ram_process(self):
        while True:
            raw = []
            for proc in psutil.process_iter(['pid','name','memory_full_info','memory_info','create_time','username','io_counters']):
                try:
                    info = proc.info
                    mem_full = proc.memory_full_info()
                    mem = proc.memory_info()
                    io = proc.io_counters()
                    
                    raw.append({
                        "pid": info.get("pid"),
                        "name": info.get("name", "Unknown"),
                        "memory_info": mem,
                        "memory_full_info": mem_full,
                        "memory_percent": proc.memory_percent(),
                        "io_info":io,
                        "create_time": info.get("create_time", 0),
                        "username": info.get("username", "Unknown")

                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            with self.threading_lock:
                self.ram_process_cache = raw

            time.sleep(self.time)


            
    def print_ram_process(self):
        mode = "ram"
        self.foreach_process(mode)
        
        table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="bright_blue",
        row_styles=["none", "dim"],  # zebra efekti
        box=None)
        
        table.add_column("PID", style="yellow", width=8, no_wrap=True)
        table.add_column("Proc Name", style="green", width=18, no_wrap=True)
        table.add_column("RSS", style="cyan", width=10, no_wrap=True)
        table.add_column("VMS", style="magenta", width=10, no_wrap=True)
        table.add_column("RAM %", style="red", width=6, no_wrap=True)
        table.add_column("USS", style="bright_blue", width=10, no_wrap=True)
        table.add_column("PSS", style="bright_blue", width=10, no_wrap=True)
        table.add_column("SWAP", style="yellow", width=10, no_wrap=True)
        table.add_column("SHARED", style="green", width=10, no_wrap=True)
        table.add_column("DATA", style="cyan", width=10, no_wrap=True)
        table.add_column("TEXT", style="magenta", width=10, no_wrap=True)
        table.add_column("Read Bytes", style="bright_blue", width=10, no_wrap=True)
        table.add_column("Write Bytes", style="orange1", width=10, no_wrap=True)
        table.add_column("Read Count", style="yellow", width=10, no_wrap=True)
        table.add_column("Create Time", style="white", width=12, no_wrap=True)



        for proc in self.update_main_process:
            table.add_row(
                str(proc["pid"]),
                proc["name"],
                proc['rss'],
                proc["vms"],
                proc["ram_percent"],
                proc["uss"],
                proc["pss"],
                proc["swap"],
                proc["shared"],
                proc["data"],
                proc["text"],
                proc["read_bytes"],
                proc["write_bytes"],
                proc["read_count"],
                str(proc["create_time_zone"])
            )

        return table







#----------------------------------------------------------------------------
         
 

    def network_process(self):
        while True:
            try:
                # Bağlantıları al
                raw = psutil.net_connections(kind='inet') 
            except:
                raw = []

            with self.threading_lock:
                self.network_process_cache = raw # Veriyi cache'e attık

            time.sleep(self.time)
      
     

    def print_network_process(self):
        mode = "network"
        self.foreach_process(mode) 
        
        table = Table(
            title="[bold white]🌐 Active Network Connections[/]",
            show_header=True,
            header_style="bold cyan",
            border_style="bright_blue",
            box=None)

        # Mevcut Sütunlar
        table.add_column("PID", style="yellow", width=10)
        table.add_column("Process", style="green", width=15)
        table.add_column("Local Address", style="magenta",width=20)
        table.add_column("Remote Address", style="red")
        
        # Yeni Eklediğimiz Teknik Sütunlar
        table.add_column("Status", style="bold",width=10)
        table.add_column("Proto", style="cyan", width=10)
        table.add_column("FD", style="white", justify="right", width=4)    # File Descriptor
        table.add_column("Family", style="blue", width=6)                 # IPv4/6
        table.add_column("Type", style="dim yellow", width=8)             # Stream/Dgram

        for item in self.update_main_process:
            table.add_row(
                item["pid"],
                item["process"],
                item["local"],
                item["remote"],
                item["status"],
                item["protocol"],
                str(item["fd"]),      # Sayısal değerleri str() yapmayı unutma abi
                item["family"],
                item["type"]
            )

        return table