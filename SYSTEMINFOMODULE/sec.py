from collections import deque
import psutil
import time

bars = "▁▂▃▄▅▆▇█"
bar_width = deque(maxlen=30)

def sparkline(data):
    result = ""
    for value in data:
        index = int(value / 100 * (len(bars) - 1))
        result += bars[index]
    return result

if __name__ == "__main__":
    n = psutil.win_service_iter()
    for x in n:
        print(x)
    while True:
        cpu = psutil.cpu_percent(interval=0.5)
        bar_width.append(cpu)

        print("\033c", end="")  # terminal temizle
        print(f"CPU {cpu:5.1f}%  {sparkline(bar_width)}")

        time.sleep(0.5)
        
