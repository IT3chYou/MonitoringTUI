# 💾 Advanced Disk Performance & Health Analyzer

Bu modül, sistemdeki fiziksel ve mantıksal disklerin kullanım oranlarını, anlık veri transfer hızlarını ve donanım sağlığını izlemek için geliştirilmiş bir Python aracıdır. `psutil` ve `wmi` kütüphanelerinin gücünü birleştirerek hem istatistiksel hem de donanımsal veriler sunar.

## ✨ Öne Çıkan Özellikler

* **📈 Anlık I/O Hızı Hesaplama:** `disk_io_speed` metodu ile diskin o anki gerçek okuma ve yazma hızlarını **MB/s** cinsinden dinamik olarak hesaplar.
* **🏥 Donanım Sağlık Kontrolü:** Windows Yönetim Araçları (`wmi`) üzerinden fiziksel disk sürücülerinin S.M.A.R.T durumlarını ve genel çalışma sağlıklarını (`Status`) raporlar.
* **📊 Görsel Doluluk Oranları:** `rich.progress` kullanarak her bir bölümün (partition) doluluk oranını terminal üzerinde şık ve anlaşılır ilerleme çubuklarıyla gösterir.
* **🔍 Detaylı Bölüm Analizi:** Mount point, dosya sistemi tipi (NTFS, FAT32 vb.) ve sürücü seçeneklerini listeler.
* **💾 Veri Transfer İstatistikleri:** Sistemin açılışından itibaren toplam okunan/yazılan veri miktarını GB cinsinden takip eder.

## 🛠 Teknik Analiz

Kod, performans verilerini işlemek için zaman tabanlı fark (delta) mantığını kullanır.

### Kullanılan Kütüphaneler:
* **`psutil`**: Bölümleme bilgileri ve I/O sayaçlarını almak için.
* **`wmi`**: Windows tabanlı donanım sorguları ve disk sağlığı verileri için.
* **`rich`**: Terminal arayüzünü renklendirmek ve grafiksel bar yapıları oluşturmak için.

### Kritik Fonksiyon Analizi:
* **`disk_io_speed()`**: Bir önceki ölçüm ile mevcut ölçüm arasındaki byte farkını geçen süreye (`dt`) bölerek, anlık transfer hızını yüksek hassasiyetle hesaplar.
* **`disk_health_wmi()`**: İşletim sistemi seviyesinden daha derine inerek doğrudan fiziksel disk sürücüsünün (Win32_DiskDrive) donanımsal yanıtını kontrol eder.



## 🚀 Kurulum

Gerekli bağımlılıkları yükleyin:

```bash
pip install psutil rich wmi