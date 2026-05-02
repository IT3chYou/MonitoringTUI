# 🌐 Gelişmiş Ağ Analiz ve İzleme Sistemi (Network Analyzer)

Bu proje, yerel ve dış ağ yapılandırmalarını, aktif bağlantıları, anlık trafik hızını ve sistem servislerini analiz eden kapsamlı bir terminal aracıdır. Python'un düşük seviyeli kütüphanelerini yüksek seviyeli görselleştirme araçlarıyla birleştirir.

## 🚀 Temel Özellikler
* **Anlık Bağlantı İzleme:** TCP/UDP bağlantılarını ve hangi uygulamanın (PID) kullandığını takip eder.
* **Akıllı Sayfalama:** Terminal ekranına sığmayan bağlantıları otomatik sayfalara böler.
* **Dinamik Trafik Analizi:** Saniyelik download/upload hızını hesaplar.
* **Donanım Entegrasyonu:** MAC adresi, DNS, Gateway ve DHCP bilgilerini işletim sistemi seviyesinde sorgular.
* **IP Matematiği:** Alt ağ ve yayın adreslerini bit düzeyinde hesaplar.

---

## 🛠 Teknik Fonksiyon Detayları

### 1. Çekirdek Yapı ve Veri Yönetimi
* **`__init__(self)`**: Sınıfın başlangıç noktasıdır. Veri çakışmalarını önlemek için `threading.Lock()` mekanizmasını kurar ve arka planda sürekli çalışacak olan veri toplayıcıyı (Thread) başlatır.
* **`connection_collector(self)`**: `psutil.net_connections` kullanarak sistemdeki tüm aktif soketleri dinler. İşlemciyi yormamak için 3 saniyelik periyotlarla çalışır.
* **`update_connections(self)`**: Ham bağlantı verilerini işler. Bir önbellek (`_process_cache`) kullanarak PID numaralarından uygulama isimlerini bulur ve veriyi `Rich` tablosuna uygun hale getirir.

### 2. İşletim Sistemi ve Dış Dünya Entegrasyonu
* **`dns_servers()`, `gateway_info()`, `dhcp_server_info()`**: İşletim sistemine (Windows/Linux) özel terminal komutlarını (`ipconfig`, `ip route`) çalıştırır. Gelen metin yığınını **Düzenli İfadeler (Regex)** ile tarayarak kritik IP bilgilerini ayıklar.
* **`mac_address_info()`**: Cihazın donanımsal kimliğini (MAC) bulmak için `getmac` veya `ip link` çıktılarını regex deseniyle (`([0-9a-f]{2}:){5}[0-9a-f]{2}`) doğrular.
* **`public_info()` & `info_public_ip()`**: `requests` kütüphanesiyle dış API'lere (ip-api.com) bağlanır. Kullanıcının internetteki "gerçek" kimliğini ve coğrafi konumunu çeker.

### 3. Matematiksel Ağ Hesaplamaları
Sistem, sadece hazır veriyi göstermez, IP ve Netmask üzerinden ağ sınırlarını kendisi hesaplar:



* **`network_address_calculator()`**: IP adresi ile Alt Ağ Maskesi arasında **Bitwise AND (&)** işlemi yapar. 
    * *Mantık:* `66 (01000010) & 63 (00111111) = 64`
* **`broadcast_calculator()`**: IP adresi ile maskenin tersi arasında **Bitwise OR (|)** işlemi yapar.
    * *Mantık:* `IP | (NOT Netmask)` işlemiyle ağın yayın adresi bulunur.

---

## 📊 Kullanılan Teknolojiler

| Araç | Kullanım Amacı |
| :--- | :--- |
| **psutil** | Sistem kaynakları ve ağ sayaçlarına erişim. |
| **Rich** | Tablo, renkli metin ve panel tabanlı terminal UI. |
| **Threading** | Hız testi ve veri toplamanın asenkron yürütülmesi. |
| **Subprocess** | İşletim sistemi terminal komutlarının yönetimi. |
| **Regex (re)** | Karmaşık sistem çıktılarından veri ayıklama. |

---

## ⚡ Hız ve Performans İzleme
* **`network_speed_in()`**: İki zaman dilimi arasındaki bayt farkını ölçerek anlık **KB/s** verisi üretir.
* **`_run_speedtest()`**: `speedtest-cli` entegrasyonu ile internetin gerçek indirme/yükleme potansiyelini ve ping süresini ölçer. Bu işlem arayüzü dondurmaması için ayrı bir iş parçacığında yürütülür.

---

## 🔧 Kurulum ve Çalıştırma
Gerekli kütüphaneleri yüklemek için:
```bash
pip install psutil rich requests speedtest-cli