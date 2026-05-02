# 🖥️ System Information & Hardware Inventory

Bu modül, üzerinde çalıştığı makinenin donanım mimarisini, işletim sistemi detaylarını, GPU kapasitesini ve çalışma zamanı (uptime) istatistiklerini kapsamlı bir şekilde raporlayan bir Python aracıdır. Karmaşık sistem verilerini kullanıcı dostu, renkli ve yapılandırılmış bir terminal çıktısına dönüştürür.

## ✨ Öne Çıkan Özellikler

* **🎮 GPU Analizi:** `GPUtil` entegrasyonu sayesinde sistemdeki NVIDIA ekran kartlarını tespit eder; model ismi, toplam VRAM miktarı ve sürücü sürümü gibi kritik bilgileri listeler.
* **⏱️ Uptime & Boot Takibi:** Sistemin ne zaman başlatıldığını (`Boot Time`) ve ne kadar süredir kesintisiz çalıştığını (`Uptime`) saniye hassasiyetinde hesaplar.
* **📂 Donanım Özeti:** İşlemci mimarisi, fiziksel çekirdek sayısı, mantıksal izlek (thread) sayısı ve toplam RAM miktarı gibi temel bileşenleri raporlar.
* **🐍 Python Ortam Bilgisi:** Mevcut çalışan Python sürümünü ve yürütülebilir dosya yolunu göstererek geliştirme ortamı hakkında bilgi verir.
* **🔋 Sensör Desteği:** Taşınabilir cihazlar için pil durumunu ve şarj seviyesini izler.

## 🛠 Teknik Analiz

Modül, sistem seviyesindeki bilgileri toplamak için Python'ın standart kütüphanelerini dış bağımlılıklarla harmanlar.

### Kullanılan Kütüphaneler:
* **`platform` & `socket`**: İşletim sistemi detayları ve ağ üzerindeki bilgisayar adını çekmek için.
* **`psutil`**: Bellek (RAM), CPU çekirdek yapısı, pil durumu ve boot zamanı verileri için.
* **`GPUtil`**: Harici grafik işlemci birimi (GPU) verilerini sorgulamak için.
* **`datetime`**: Zaman damgalarını okunabilir tarih formatına dönüştürmek için.



[Image of computer hardware components diagram]


### Kritik Fonksiyon Analizi:
* **`system_time()`**: `psutil.boot_time()` çıktısını kullanarak sistemin çalışma süresini hesaplar. Bu, sunucu stabilitesini kontrol etmek için kritik bir metriktir.
* **`gpu_info()`**: Sisteme bağlı olan tüm GPU'ları döngüye alarak çoklu ekran kartı yapılandırmalarını (SLI/Crossfire) destekler.
* **`get_general_system_info()`**: `platform.processor()` ile işlemcinin ham model ismini yakalar ve `psutil` ile çekirdek sayılarını mantıksal/fiziksel olarak ayırır.

## 🚀 Kurulum

Gereksinimleri yüklemek için:

```bash
pip install psutil rich gputil