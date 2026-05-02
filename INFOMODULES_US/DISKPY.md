# 💾 Advanced Disk Performance & Health Analyzer

This module is a Python tool developed to monitor the usage rates, instantaneous data transfer speeds, and hardware health of physical and logical disks in the system. By combining the power of the `psutil` and `wmi` libraries, it provides both statistical and hardware-level data.

## ✨ Key Features

* **📈 Real-time I/O Speed Calculation:** Dynamically calculates the disk's current actual read and write speeds in **MB/s** using the `disk_io_speed` method.
* **🏥 Hardware Health Check:** Reports S.M.A.R.T status and general operational health (`Status`) of physical disk drives via Windows Management Instrumentation (`wmi`).
* **📊 Visual Capacity Rates:** Displays the occupancy rate of each partition on the terminal using sleek and intuitive progress bars powered by `rich.progress`.
* **🔍 Detailed Partition Analysis:** Lists mount points, file system types (NTFS, FAT32, etc.), and drive options.
* **💾 Data Transfer Statistics:** Tracks the total amount of data read/written since system boot in GB.

## 🛠 Technical Analysis

The code utilizes a time-based delta logic to process performance data.

### Libraries Used:
* **`psutil`**: To retrieve partition information and I/O counters.
* **`wmi`**: For Windows-based hardware queries and disk health data.
* **`rich`**: To colorize the terminal interface and create graphical bar structures.

### Critical Function Analysis:
* **`disk_io_speed()`**: Calculates instantaneous transfer speed with high precision by dividing the byte difference between the previous and current measurement by the elapsed time (`dt`).
* **`disk_health_wmi()`**: Goes deeper than the OS level to directly check the hardware response of the physical disk drive (Win32_DiskDrive).

## 🚀 Installation

Install the required dependencies:

```bash
pip install psutil rich wmi