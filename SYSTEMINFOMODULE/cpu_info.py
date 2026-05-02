import psutil
import platform
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from rich.console import Group
from rich.table import Table
from rich.columns import Columns



class CPU:

    def __init__(self) -> None:
        self.console = Console()
        # Verileri tutacağımız kasalar (değişkenler)
        self.cpu_percent = []
        self.current_freq = None
        self.prev_stats = psutil.cpu_stats()
        self.c_update()





    def c_update(self):
        # interval=None ASLA bekleme yapmaz, o anki veriyi fırlatır geçer.
        self.cpu_percent = psutil.cpu_percent(percpu=True, interval=None)
        self.current_freq = psutil.cpu_freq()
        # Buraya istersen stats'ı da ekleyebilirsin
        self.current_stats = psutil.cpu_stats()


    def avg(self):
        if not self.cpu_percent:
            return 0
        return sum(self.cpu_percent) / len(self.cpu_percent)



    def progress_cpu_info(self):

        cpu_avg = sum(self.cpu_percent) / len(self.cpu_percent)
        color = "green" if cpu_avg < 50 else "yellow" if cpu_avg < 80 else "red"

        progress = Progress(TextColumn("{task.description}"),
        BarColumn(bar_width=80,style=color),
        TextColumn("{task.percentage:.0f}%"),expand=False)
        progress.add_task("CPU AVG", total=100, completed=cpu_avg)
        return progress



    def all_core(self):
        core_panels = []
        for i, usage in enumerate(self.cpu_percent):
            color = "green" if usage < 40 else "yellow" if usage < 70 else "red"

            # Her çekirdek için mini bir tablo yapısı
            grid = Table.grid(expand=True)
            grid.add_column(width=8)
            grid.add_column(width=12)
            grid.add_column(justify="right", width=7)

            prog = Progress(
                BarColumn(bar_width=None, style="black", complete_style=color, finished_style=color),
                expand=True
            )
            prog.add_task(f"c{i}", total=100, completed=usage)

            grid.add_row(f"Core {i}", prog, f"[{color}]{usage:>5.1f}%[/]")

            # Her çekirdeği küçük bir Panel içine sarıp listeye ekle
            core_panels.append(Panel(grid, border_style="dim"))

        # Sütunlar halinde döndür (Terminal genişliğine göre yan yana dizer)
        return Columns(core_panels, expand=True)



#-------------------------------------------------------

    def freq_info(self):
        freq = psutil.cpu_freq()
        if not freq:
            return Text("Freq N/A", style="red")

        text = Text()

        text.append(f"Current : {freq.current:.0f} MHz\n", style="green")
        text.append(f"Min     : {freq.min:.0f} MHz\n", style="dim")
        text.append(f"Max     : {freq.max:.0f} MHz\n", style="cyan")
        return text

    def freq_info_per_cpu(self):

        text = Text()
        for i, f in enumerate(psutil.cpu_freq(percpu=True)):
            text.append(f"Core {i}: {f.current:.0f} MHz\n")

        return text


    def thermal_state(self):
        # psutil.cpu_freq() SİLİNDİ -> Yerine c_update'deki değişken geldi
        f = self.current_freq

        if f is None or f.max == 0:
            return "Thermal State : [dim]N/A (Frekans Okunamadı)[/dim]"

        freq = f.current
        maxf = f.max
        cpu_avg = self.avg()


        # 2. Mantıksal Kontroller
        # Kullanım çok yüksek ama frekans maksimumun %60'ının altındaysa: Throttling (Kısıtlama)
        if cpu_avg > 85 and freq < (maxf * 0.6):
            return "Thermal State : [bold red]THERMAL / POWER THROTTLING[/bold red]"

        # Kullanım yüksek ve frekans normalse: Tam Performans
        elif cpu_avg > 85:
            return "Thermal State : [bold yellow]FULL PERFORMANCE[/bold yellow]"

        # Kullanım düşük ve frekans çok düşükse: Güç Tasarrufu (Power Limited/Idle)
        elif cpu_avg < 50 and freq < (maxf * 0.4):
            return "Thermal State : [bold blue]POWER SAVER / IDLE[/bold blue]"

        # Geri kalan durumlar: Normal
        else:
            return "Thermal State : [bold green]NORMAL[/bold green]"

#----------------------------------------------------------

    def cpu_times_info(self):
        t = psutil.cpu_times_percent()
        text = Text()
        text.append(f"User   :{t.user}%      APPs\n",style="yellow")
        text.append(f"System :{t.system}%    Kernel vb\n",style="red")
        text.append(f"Idle   :{t.idle}%      Free Space\n",style="green")
        return text


#---------------------------------------------------------------------


    def cpu_stats_info(self):
        try:
            stats = psutil.cpu_stats()
            #yukarıda sınıdrma olarak adlandırılan ilk ölçüm bir önceki ölçüm oluyor

            ctx_delta = stats.ctx_switches - self.prev_stats.ctx_switches
            int_delta = stats.interrupts - self.prev_stats.interrupts
            soft_delta = stats.soft_interrupts - self.prev_stats.soft_interrupts
            sys_delta = stats.syscalls - self.prev_stats.syscalls

            self.prev_stats = stats  # güncelle

            text = Text()
            text.append(f"CTX Switch : +{ctx_delta}/s\n", style="cyan")
            text.append(f"Interrupts: +{int_delta}/s\n", style="yellow")
            text.append(f"Soft Int  : +{soft_delta}/s\n", style="magenta")
            text.append(f"Syscalls  : +{sys_delta}/s\n", style="red")
            text.append("─" * 1000 +" \n", style="dim")
            text.no_wrap = True
            if ctx_delta > 75000:
                text.append("THREAD HEAVY\n", style="yellow")
            elif sys_delta > 90000:
                text.append("IO / SYSCALL HEAVY\n", style="red")
            elif int_delta > 30000:
                text.append("INTERRUPT HEAVY\n", style="magenta")
            else:
                text.append("NORMAL\n", style="green")
        except Exception as e:
            return Text(f"İstatistik hatası: {e}", style="dim red")

        return text
