# 🖥️ System Information & Hardware Inventory

This module is a comprehensive Python tool designed to report the hardware architecture, operating system details, GPU capacity, and runtime (uptime) statistics of the machine it is running on. It transforms complex system data into a user-friendly, colorful, and structured terminal output.

## ✨ Key Features

* **🎮 GPU Analysis:** Detects NVIDIA graphics cards in the system via `GPUtil` integration; lists critical information such as model name, total VRAM, and driver version.
* **⏱️ Uptime & Boot Tracking:** Calculates when the system was started (`Boot Time`) and how long it has been running without interruption (`Uptime`) with per-second precision.
* **📂 Hardware Summary:** Reports core components such as processor architecture, physical core count, logical thread count, and total RAM amount.
* **🐍 Python Environment Info:** Provides details about the development environment by showing the currently running Python version and the executable file path.
* **🔋 Sensor Support:** Monitors battery status and charge levels for portable devices.

## 🛠 Technical Analysis

The module blends Python's standard libraries with external dependencies to collect system-level information.

### Libraries Used:
* **`platform` & `socket`**: To fetch operating system details and the computer's network hostname.
* **`psutil`**: For memory (RAM), CPU core structure, battery status, and boot time data.
* **`GPUtil`**: To query external graphics processing unit (GPU) data.
* **`datetime`**: To convert timestamps into readable date formats.

### Critical Function Analysis:
* **`system_time()`**: Calculates the system's runtime using the `psutil.boot_time()` output. This is a critical metric for checking server stability.
* **`gpu_info()`**: Supports multi-GPU configurations (SLI/Crossfire) by looping through all GPUs connected to the system.
* **`get_general_system_info()`**: Captures the raw processor model name with `platform.processor()` and distinguishes between logical/physical core counts using `psutil`.

## 🚀 Installation

To install the requirements:
```bash
pip install psutil rich gputil