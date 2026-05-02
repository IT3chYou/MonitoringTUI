# 🚀 Advanced CPU Performance Monitor & System Analytics (TUI)

This project is a professional monitoring tool that provides an in-depth analysis of the system processor (CPU) via a **Terminal User Interface (TUI)**. Unlike standard tools, it tracks not only usage percentages but also core-based frequency fluctuations and kernel-level statistics in real-time.

## ✨ Key Features

* **📊 Per-Core Monitoring:** Displays the load of each individual CPU core in real-time using visual bar charts (powered by the `rich` library).
* **🔥 Thermal & Power State Analysis (Throttling Detection):** Analyzes the relationship between processor frequency and load to detect states such as **Thermal Throttling**, **Full Performance**, or **Power Limit**.
* **⚙️ Advanced Kernel Statistics:**
    * **Context Switches:** The rate at which the operating system switches between tasks.
    * **Interrupts:** Instant intervention signals coming from hardware and software.
    * **Syscalls:** The density of operations performed by applications at the kernel level.
* **📉 Delta-Based Calculation:** Presents statistics not just as total counts, but by calculating the difference between two measurements (increase rate per second). This allows for understanding the system's instantaneous characteristics (e.g., Thread Heavy, IO Heavy).
* **🎨 Dynamic Coloring:** Offers quick visual analysis with green, yellow, and red color warnings based on critical threshold values.

## 🛠 Technical Details

The code is developed in accordance with Object-Oriented Programming (OOP) principles.

### Technologies Used:
* **`psutil`**: To collect hardware metrics and system statistics.
* **`rich`**: To create modern graphics, progress bars, and live tables in the terminal.

### Critical Function Analysis:
* **`thermal_state()`**: Compares the processor's current frequency (`current`) with its maximum capacity (`max`). If the load is over 85% while the frequency has dropped below 60%, it labels the system as **Thermal Throttling**.
* **`cpu_stats_info()`**: Monitors the number of system calls and interrupts per second. If the number of syscalls exceeds 90,000, it identifies the system as **"IO / SYSCALL HEAVY"**, pointing out the source of the bottleneck.

## 🚀 Installation and Execution

To install the requirements:
```bash
pip install psutil rich