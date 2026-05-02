# 🌐 Advanced Network Analysis & Monitoring System (Network Analyzer)

This project is a comprehensive terminal tool that analyzes local and external network configurations, active connections, real-time traffic speed, and system services. It combines Python's low-level libraries with high-level visualization tools.

## 🚀 Key Features
* **Real-time Connection Monitoring:** Tracks TCP/UDP connections and identifies which application (PID) is using them.
* **Smart Pagination:** Automatically splits connection lists into pages that fit the terminal screen.
* **Dynamic Traffic Analysis:** Calculates download/upload speeds per second.
* **Hardware Integration:** Queries MAC address, DNS, Gateway, and DHCP information at the operating system level.
* **IP Mathematics:** Calculates subnet and broadcast addresses at the bitwise level.

---

## 🛠 Technical Function Details

### 1. Core Structure and Data Management
* **`__init__(self)`**: The entry point of the class. It establishes a `threading.Lock()` mechanism to prevent data race conditions and starts the background data collector (Thread).
* **`connection_collector(self)`**: Listens to all active sockets in the system using `psutil.net_connections`. It runs in 3-second intervals to minimize CPU usage.
* **`update_connections(self)`**: Processes raw connection data. It uses a cache (`_process_cache`) to resolve application names from PID numbers and formats the data for a `Rich` table.

### 2. OS and External World Integration
* **`dns_servers()`, `gateway_info()`, `dhcp_server_info()`**: Executes OS-specific (Windows/Linux) terminal commands like `ipconfig` or `ip route`. It parses the resulting text blocks using **Regular Expressions (Regex)** to extract critical IP information.
* **`mac_address_info()`**: Validates the device's hardware identity (MAC) by matching `getmac` or `ip link` outputs against a regex pattern (`([0-9a-f]{2}:){5}[0-9a-f]{2}`).
* **`public_info()` & `info_public_ip()`**: Connects to external APIs (like ip-api.com) using the `requests` library to fetch the user's "real" internet identity and geographic location.

### 3. Mathematical Network Calculations
The system does not just display ready-made data; it calculates network boundaries itself using the IP and Netmask:

* **`network_address_calculator()`**: Performs a **Bitwise AND (&)** operation between the IP address and the Subnet Mask.
    * *Logic:* `66 (01000010) & 63 (00111111) = 64`
* **`broadcast_calculator()`**: Performs a **Bitwise OR (|)** operation between the IP address and the inverse of the mask.
    * *Logic:* The broadcast address is found via `IP | (NOT Netmask)`.

---

## 📊 Technologies Used

| Tool | Purpose |
| :--- | :--- |
| **psutil** | Access to system resources and network counters. |
| **Rich** | Table, colored text, and panel-based terminal UI. |
| **Threading** | Asynchronous execution of speed tests and data collection. |
| **Subprocess** | Management of operating system terminal commands. |
| **Regex (re)** | Data extraction from complex system outputs. |

---

## ⚡ Speed and Performance Monitoring
* **`network_speed_in()`**: Measures the byte difference between two time intervals to produce real-time **KB/s** data.
* **`_run_speedtest()`**: Measures actual download/upload potential and ping using `speedtest-cli` integration. This is executed in a separate thread to prevent the UI from freezing.

---

## 🔧 Installation and Execution
To install the required libraries:
```bash
pip install psutil rich requests speedtest-cli