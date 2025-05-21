# ✅ L10 & L11 Validation Test List

## 🔍 L10 Test Items

### 🔧 Firmware & System Info Checks
- **Check/Update BIOS/BMC/CPLD FW** – FW can be updated and match defined versions
- **Check/Update GPU FW**
- **Check/Update NVL Switch OS & FW**
- **Check/Update CDU FW**
- **Check/Update PowerShelf FW**
- **Check DMI/FRU** – Must match database
- **Check FW Version** – Must match database
- **Check system configuration** – Must match data
- **Check component FW version / SN / quantity** – Must match database
- **Check system SN** – Must match database
- **Check SDR sensor list** – Must match database

### 🧪 Diagnostic & Stress Tests
- **NVIDIA Field Diag (L10)** – No GPU error, pass result
- **NCCL Single Node Test** – No network/GPU errors, return pass, no reboot or dmesg errors
- **NVIDIA GPU gpu_burn** – Use 98% of memory, return = 0, must pass
- **MCE / EDAC / DMESG log check** – No errors (checked after every stress test)
- **Disk FIO stress test**
- **STREAM Memory Test**
- **StressAppTest**

### 💾 Storage Validation
- **Disk Smart Data Check** – No CRC/ECC/Media/Critical errors
- **Disk Block Size Check** – Must be consistent
- **Disk Firmware Consistency Check**

### 🌐 Networking / System Interfaces
- **Check IPv4 and IPv6** – Must be reachable
- **Check PCIe Speed/Width** – No downgrade
- **Power Consumption Check** – No critical logs after test
- **Network Connection Check** – Status must be "Yes"
- **LAN Self-test** – No rx/tx/crc errors
- **Redfish Self-test** – No errors
- **IPMI Port Self-test** – No port down or errors
- **IPMI User Self-test** – Passwords must be unique

---

## 🔍 L11 Test Items

### 🧪 Multi-node & Extended Stress Testing
- **NCCL Multi-node Test** – Performance must meet or exceed expected values
- **OSU Micro-benchmark / Mellanox RDMA Perftest**
- **NVIDIA NVL Switch Tray Diag (L11)** – No GPU errors, pass result
- **NVIDIA Compute Tray Switch Diag (L11)** – No GPU errors, pass result
- **Power Cycle Test (3x)** – No MCE/EDAC/DMESG/SEL errors after each cycle
- **MCE-EDAC Log Check**
- **Disk Smart Data Check**
- **Disk DD stress test**
- **Disk FIO stress test**
- **STREAM Memory Test (CPU + GPU)**
- **StressAppTest**
- **NVIDIA GPU DCGM-R4** – Return = 0, must pass
- **NVIDIA GPU gpu_burn**
- **NVIDIA GPU nvbandwidth**
- **Mprime Stress Test**

### 🔧 Consistency & Metadata Checks (Same as L10)
- Check FW, system configuration, component SN, quantity, etc.

---

## 📌 Notes

- All stress tests must not trigger MCE, EDAC, DMESG, or SEL errors.
- Logs are evaluated post-test automatically.
- Database matching ensures traceability and consistency across components.

