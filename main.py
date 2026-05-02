import platform
import threading
import time
import subprocess
from datetime import datetime
import sys
import keyboard
import psutil
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from rich.prompt import Prompt
from rich.spinner import Spinner

# -----------------------------
from SYSTEMINFOMODULE.cpu_info import CPU
from SYSTEMINFOMODULE.disk_info import Disk
from SYSTEMINFOMODULE.network_info import Network
from SYSTEMINFOMODULE.process_info import Process
from SYSTEMINFOMODULE.ram_info import RAM
from SYSTEMINFOMODULE.sysinfo import Sysinfo


class System:
    def __init__(self) -> None:

        keyboard.add_hotkey("1", self.toggle_network_info)
        keyboard.add_hotkey("2", self.toogle_all_process_info)
        keyboard.add_hotkey("i",self.toogle_input)
        self.input = False
        self.show_network_info = False
        self.all_process_info = False
        self.show_sysinfo = False
        self.panel_size = 0
        self.panel_ratio = 0
        self.system = platform.system()
        self.proc = Process()
        self.cpu = CPU()
        self.ram = RAM()
        self.disk = Disk()
        self.network = Network()
        self.sysinfo = Sysinfo()
        self.speedtest = False
        self.console = Console(
            color_system="truecolor",
            force_terminal=True,
            emoji=True,
            highlight=False,
            soft_wrap=True,
            record=False,)
        self.prompt = Prompt()
        self.built_layout()  # Layout Bir Kez Oluşturulmalı

    # Toogle Function Start
    def toggle_network_info(self):
        self.show_network_info = not self.show_network_info
        self.speedtest = False  # Her n Harfine Bastığımda Girip Çıktığımda Birr Daha Speed Test Yapsın

    def toogle_all_process_info(self):
        self.all_process_info = not self.all_process_info

    def toogle_input(self):
        self.input = not self.input
    # Toogle Functio End

    # Layout Design Function  Toogle a Göre Düzemlenmeli
    def built_layout(self):

        # Advance Info Layoput Desıgn Function
        if self.show_network_info:
            self.layout = Layout(name="network_panel")
            self.layout["network_panel"].split(
                Layout(name="net_header", size=3),
                Layout(name="net_body"),
                Layout(name="net_footer", size=3),
            )

            self.layout["net_body"].split_row(
                Layout(name="network_panel_one", ratio=2),
                Layout(name="network_panel_two", ratio=2),
                Layout(name="network_process_panel", ratio=5),
            )

            self.layout["network_panel_two"].split_column(
                Layout(name="io_info", ratio=self.panel_ratio + 1),
                Layout(name="network_speed", ratio=self.panel_ratio + 1),
                Layout(name="network_speed_test", ratio=self.panel_ratio + 1),
                Layout(name="open_network_info", ratio=self.panel_ratio + 2),
            )
#----------------------------------------------------------------------------------------------
        elif self.all_process_info:
            self.layout = Layout(name="processing_panel")
            self.layout["processing_panel"].split_column(
                Layout(name="proc_main1", ratio=1),
                Layout(name="proc_main2", ratio=1),
            )

            self.layout["proc_main1"].split(
                Layout(name="proc_sub_main1", ratio=1),
                Layout(name="proc_sub_main2", ratio=1),
            )

            self.layout["proc_sub_main1"].split_row(
                Layout(name="basic_proc", ratio=1), Layout(name="cpu_proc", ratio=1)
            )

            self.layout["proc_main2"].split(
                Layout(name="ram", ratio=1), Layout(name="network", ratio=1)
            )
#----------------------------------------------------------------------------------------------
        # System Info Layout Design Function
        else:
            self.layout = Layout(name="sysinfo_panel")
            self.layout["sysinfo_panel"].split(
                Layout(name="header", size=6),
                Layout(name="sysinfo_body"),
                Layout(name="footer", size=3),
            )

            self.layout["sysinfo_body"].split_row(
                Layout(name="cpu_panel", ratio=1),
                Layout(name="ram_panel", ratio=1),
                Layout(name="disk_panel", ratio=1),
                Layout(name="cmd_panel", ratio=2),


            )
            self.layout["cpu_panel"].split_column(
                Layout(name="cpu_avg", size=self.panel_size + 3),
                Layout(name="thermal", size=self.panel_size + 3),
                Layout(name="freq", size=self.panel_size + 5),
                Layout(name="times", size=self.panel_size + 5),
                Layout(name="cpu_stats", size=self.panel_size + 8),
                Layout(name="core_usage", ratio=self.panel_ratio + 3),
            )

            self.layout["ram_panel"].split_column(
                Layout(name="ram_usage", size=self.panel_size + 8),
                Layout(name="network_avg_info",size=self.panel_size + 4),
                Layout(name="network_speed_in",size=self.panel_size + 4),
                Layout(name="network_speed_out",size=self.panel_size + 5),
                Layout(name="process_using",ratio=self.panel_ratio + 1),
            )
            self.layout["disk_panel"].split_column(
                Layout(name="progressbar_using", size=self.panel_size + 10),
                Layout(name="disk_io_info", size=self.panel_size + 10),
                Layout(name="disk_speed", size=self.panel_size + 8),
                #Layout(name="disk_health", ratio=self.panel_ratio + 3),
                #Layout(name="disk_info", ratio=self.panel_ratio + 4),
                Layout(name="disk_usage",size=self.panel_size + 10),
                Layout(name="general_info",ratio=self.panel_ratio + 1),
            )
            spinner = Spinner("dots",text=" Enter The Command For Processing!")
            self.layout["cmd_panel"].update(Panel(spinner))



    def main_process_layout(self):
        self.layout["basic_proc"].update(Panel(self.proc.print_main_process()))

    def cpu_process_layout(self):
        self.layout["cpu_proc"].update(Panel(self.proc.print_cpu_process()))

    def sys_process_layout(self):
        self.layout["proc_sub_main2"].update(Panel(self.proc.print_system_process()))

    def ram_process_layout(self):
        self.layout["ram"].update(Panel(self.proc.print_ram_process()))

    def network_process_layout(self):
        self.layout["network"].update(Panel(self.proc.print_network_process()))

    # Netwrok Function Start
    def network_header(self):
        self.layout["net_header"].update(
            Panel(Text("Advance Network Monitoring"), style="cyan")
        )

    def network_body_b1(self):
        self.layout["network_panel_one"].update(
            Panel(self.network.first_panel_network_info(), title="Network Overview")
        )

    def network_body_b2(self):
        self.layout["io_info"].update(
            Panel(self.network.upload_and_download_info(), title="Network I/O")
        )

        self.layout["network_speed"].update(
            Panel(self.network.network_speed_in(), title="Network Speed")
        )

        if not self.speedtest:
            self.network.start_speedtest()
            self.speedtest = True

        self.layout["network_speed_test"].update(
            Panel(self.network.speedtest_result, title="Speed Test")
        )

        self.layout["open_network_info"].update(
            Panel(self.network.print_open_public_info(), title="Speed Test")
        )

    def network_body_b3(self):
        self.layout["network_process_panel"].update(Panel(self.network.print_it()))

    def network_footer(self):
        self.layout["net_footer"].update(Panel(time.strftime("%H:%M:%S"), style="cyan"))

    # Network Function End



#--------------------------------------------------------------------------------------------
    # SytemInfo Layout Start
    def sysinfo_header(self) -> None:
        self.layout["header"].update(
            Panel(self.sysinfo.get_header_text(), style="red")
        )

    def sysinfo_body_b1(self):
        self.layout["cpu_avg"].update(
            Panel(self.cpu.progress_cpu_info(), title="CPU AVG")
        )

        self.layout["core_usage"].update(
            Panel(self.cpu.all_core(), title="Core Usage", padding=(1, 0))
        )

        self.layout["thermal"].update(
            Panel(self.cpu.thermal_state(), title="Thermal State")
        )

        self.layout["freq"].update(Panel(self.cpu.freq_info(), title="CPU Frequency"))

        self.layout["times"].update(Panel(self.cpu.cpu_times_info(), title="CPU Times"))

        self.layout["cpu_stats"].update(
            Panel(self.cpu.cpu_stats_info(), title="CPU Stats")
        )

    def sysinfo_body_b2(self):
        self.layout["ram_usage"].update(
            Panel(self.ram.ram_usage_info(), title="Ram Usage")
        )

        self.layout["process_using"].update(
            Panel(self.ram.ram_process(), title="Process Using")
        )

    def sysinfo_body_b3(self):
        self.layout["disk_usage"].update(
            Panel(self.disk.disk_usage(), title="All Disk Usage")
        )

        self.layout["progressbar_using"].update(
            Panel(self.disk.disk_usage_progressbar(), title="Disk Usage")
        )

        self.layout["disk_io_info"].update(
            Panel(self.disk.disk_io_info(), title="IO Info")
        )

        self.layout["disk_speed"].update(
            Panel(self.disk.disk_io_speed(), title="Disk Partition Info")
        )

        #self.layout["disk_info"].update(Panel(self.disk.disk_partitions_info(), title="Disk Partition Info"))



    def sysinfo_body_b4(self):
        self.layout["disk_usage"].update(
            Panel(self.disk.disk_usage(), title="All Disk Usage")
        )

        self.layout['general_info'].update(Panel(self.sysinfo.all_info()))

        self.layout["network_avg_info"].update(
            Panel(
                self.network.upload_and_download_info(), title="Avg Download And Upload"
            )
        )

        self.layout["network_speed_in"].update(
            Panel(self.network.network_speed_in(), title="Network Speed")
        )

        if not self.speedtest:
            self.network.start_speedtest()
            self.speedtest = True

        self.layout["network_speed_out"].update(
            Panel(self.network.speedtest_result, title="Speed Test")
        )


    def sysinfo_footer(self):
        text = "Enter (i) For Input"
        self.layout['footer'].update(Panel(text,style="green"))

#-------------------------------------------------------------------------------------------------------------------------------------------------------
    # System Info Layout End


    def run(self):
            current_mode = -1
            with Live(self.layout,console=self.console,refresh_per_second=4,screen=True) as live:
                while True:
                    # 1. Mod Belirleme
                    #
                    if self.input:
                        live.stop()  # Ekranı dondur (Rich kontrolü bıraksın)

                        # 1. Paneli giriş için boşalt (Yeşil çerçeve hazır)
                        self.layout['footer'].update(Panel("", style="green", title="Enter Command"))

                        # 2. Mevcut tabloyu ekrana son kez bas (Görüntü sabit kalsın)
                        self.console.print(self.layout)

                        # 3. HİLE: İmleci 2 satır yukarı, panelin tam içine zıplat
                        # 2A (2 satır yukarı), 3A (3 satır yukarı) - Panele göre dene
                        self.console.print("\033[2A", end="")

                        # 4. Girişi al (İmleç artık panelin içinde yanıp sönecek)
                        message = self.prompt.ask(" [bold cyan]  />[/]")

                        # 5. Sonucu panele yazdır
                        self.layout['footer'].update(Panel(f"Son Komut: {message}", style="red"))

                        # 6. Kontroller ve Çıkış
                        if message.startswith("exit"):
                            break

                        if message.startswith("cmd"):
                            try:
                                # Mesajı ayır ve komutu al
                                _, command_str = message.split(maxsplit=1)

                                # Komutu çalıştır ve çıktıyı yakala
                                # stderr=subprocess.STDOUT hataları da görmeni sağlar
                                output = subprocess.check_output(
                                    command_str,
                                    shell=True,
                                    text=True,
                                    stderr=subprocess.STDOUT,
                                    encoding="cp857" # Windows Türkçe karakter desteği
                                )

                                # Sadece çıktı renkli olsun dediğin için style="bold yellow" veya "cyan" ekledik
                                # Panelin taşmaması için son 20 satırı alıyoruz
                                display_text = "\n".join(output.splitlines()[-20:])

                                self.layout["cmd_panel"].update(
                                    Panel(display_text, title=f"Sonuç: {command_str}", border_style="green", style="bold cyan")
                                )

                            except subprocess.CalledProcessError as e:
                                # Komut hatalıysa hatayı kırmızı basar
                                self.layout["cmd_panel"].update(Panel(f"[red]Hata:[/] {e.output}", title="Hata"))
                            except Exception as e:
                                self.layout["footer"].update(Panel(f"[red]Sistem Hatası: {str(e)}"))

                            # Giriş bittiği için ekranı bir kez tazele ve Live'ı geri başlat
                            self.console.clear()
                            self.console.print(self.layout)




                        self.input = False # Döngüden kurtul
                        live.start() # Tabloları tekrar canlandır



                    if self.show_network_info:
                        mode = 1
                    elif self.all_process_info:
                        mode = 2
                    else:
                        mode = 0

                    # 2. İskelet Güncelleme
                    if mode != current_mode:
                        self.built_layout()
                        live.update(self.layout)
                        current_mode = mode

                    # 3. İçerik Güncelleme
                    try:
                        self.cpu.c_update()

                        if mode == 1:
                            self.network_header()
                            self.network_body_b1()
                            self.network_body_b2()
                            self.network_body_b3()
                            # HATA ÖNLEYİCİ KONTROL: .get() kullanıyoruz
                            if self.layout.get("net_footer"):
                                self.network_footer()

                        elif mode == 2:
                            self.main_process_layout()
                            self.cpu_process_layout()
                            self.sys_process_layout()
                            self.ram_process_layout()
                            self.network_process_layout()

                        else:
                            self.sysinfo_header()
                            self.sysinfo_body_b1()
                            self.sysinfo_body_b2()
                            self.sysinfo_body_b3()
                            self.sysinfo_body_b4()

                            if self.layout.get("footer"):
                                self.sysinfo_footer()

                    except Exception as e:
                        # ÇÖKME ÖNLEYİCİ: Hata anında KeyError fırlatmasını engelliyoruz
                        error_msg = f"⚠️ [bold red]Hata: {str(e)}[/]"
                        footer = self.layout.get("footer") or self.layout.get("net_footer")
                        if footer:
                            footer.update(Panel(error_msg))
                        else:
                            # Eğer hiçbir footer yoksa programı kırma, sessizce devam et
                            pass

                    time.sleep(0.05)

if __name__ == "__main__":
    sys = System()
    sys.run()
