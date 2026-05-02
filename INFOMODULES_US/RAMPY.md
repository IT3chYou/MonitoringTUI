# 🧠 System Memory (RAM) Analyzer

This module is developed to monitor system memory resources at both macro and micro levels.

### Features
- **System Summary:** Reports total, used, and available RAM amounts in GB.
- **Process-Based Tracking:** Instantly lists which application is consuming how much memory (RSS).
- **Performance Friendly:** Minimizes CPU load by caching `process_iter` data.
- **Dynamic UI:** Displays processes sorted by PID and Memory usage using the `Rich.Table` structure.

### Technical Function Table

| Function | Task | Technical Detail |
| :--- | :--- | :--- |
| `ram_usage_info` | General RAM Status | Analyzes `psutil.virtual_memory` data. |
| `ram_process` | Application Listing | Scans processes and extracts RSS (physical memory) data. |
| **Pagination** | Screen Management | Pages data in blocks of 100 processes. |
| **Caching** | Resource Saving | Refreshes data with a 5-second "Cool-down" period. |

### Memory Calculation Logic
The memory usage of processes is calculated via **RSS (Resident Set Size)**. This represents the actual physical RAM space a process occupies at that moment.



**Unit Conversion Formula:**
$$RAM_{GB} = \frac{Bytes}{1024^{3}}$$
$$Process_{MB} = \frac{Bytes}{1024^{2}}$$

---

## 🛠 Usage
You can start monitoring system resources by including the class in your project:
```python
ram_analyzer = RAM()
print(ram_analyzer.ram_usage_info())
print(ram_analyzer.ram_process())