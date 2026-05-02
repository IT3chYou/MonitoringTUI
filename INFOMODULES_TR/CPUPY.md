# 🚀 Advanced CPU Performance Monitor & System Analytics (TUI)

Bu proje, Python kullanarak sistem işlemcisini (CPU) derinlemesine analiz eden ve **Terminal Kullanıcı Arayüzü (TUI)** üzerinden sunan profesyonel bir izleme aracıdır. Standart araçların aksine, sadece kullanım yüzdesini değil, çekirdek bazlı frekans değişimlerini ve çekirdek (kernel) seviyesindeki istatistikleri gerçek zamanlı olarak takip eder.

## ✨ Öne Çıkan Özellikler

* **📊 Çekirdek Bazlı İzleme (Per-Core Monitoring):** Her bir CPU çekirdeğinin yükünü görsel bar grafiklerle (`rich` kütüphanesi yardımıyla) anlık olarak gösterir.
* **🔥 Termal & Güç Durumu Analizi (Throttling Detection):** İşlemci frekansı ile yük arasındaki ilişkiyi analiz ederek; **Isınma Frenlemesi (Throttling)**, **Tam Performans** veya **Güç Sınırı** durumlarını tespit eder.
* **⚙️ Gelişmiş Kernel İstatistikleri:**
    * **Context Switches (Bağlam Geçişleri):** İşletim sisteminin görevler arası geçiş hızı.
    * **Interrupts (Kesintiler):** Donanım ve yazılım tarafından gelen anlık müdahale sinyalleri.
    * **Syscalls (Sistem Çağrıları):** Uygulamaların kernel seviyesinde yaptığı işlemlerin yoğunluğu.
* **📉 Delta-Tabanlı Hesaplama:** İstatistikleri sadece toplam sayı olarak değil, iki ölçüm arasındaki farkı (artış hızı/saniye) hesaplayarak sunar. Bu, sistemin anlık karakteristiğini (Thread Heavy, IO Heavy vb.) anlamayı sağlar.
* **🎨 Dinamik Renklendirme:** Kritik eşik değerlerine göre yeşil, sarı ve kırmızı renk uyarıları ile hızlı görsel analiz sunar.

## 🛠 Teknik Detaylar

Kod, Nesne Yönelimli Programlama (OOP) prensiplerine uygun olarak geliştirilmiştir.

### Kullanılan Teknolojiler:
* **`psutil`**: Donanım metriklerini ve sistem istatistiklerini toplamak için.
* **`rich`**: Terminalde modern grafikler, ilerleme çubukları ve canlı tablolar oluşturmak için.

### Kritik Fonksiyon Analizi:
* **`thermal_state()`**: İşlemcinin mevcut frekansını (`current`) maksimum kapasitesiyle (`max`) kıyaslar. Eğer yük %85 üzerindeyken frekans %60'ın altına düşmüşse, sistemi **Thermal Throttling** (Isınma kaynaklı yavaşlatma) olarak etiketler.
* **`cpu_stats_info()`**: Saniyedeki sistem çağrısı ve kesinti sayılarını izler. Eğer çağrı sayısı (syscalls) 90.000'i aşarsa sistemi **"IO / SYSCALL HEAVY"** olarak tanımlayarak dar boğazın kaynağını gösterir.

## 🚀 Kurulum ve Çalıştırma

Gereksinimleri yüklemek için:

```bash
pip install psutil rich