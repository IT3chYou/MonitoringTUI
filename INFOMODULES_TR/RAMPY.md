## 🧠 Sistem Bellek (RAM) Analizörü

Bu modül, sistemin bellek kaynaklarını hem makro hem de mikro düzeyde izlemek için geliştirilmiştir.

### Özellikler
- **Sistem Özeti:** Toplam, kullanılan ve kullanılabilir RAM miktarlarını GB cinsinden raporlar.
- **Süreç Bazlı Takip:** Hangi uygulamanın ne kadar bellek tükettiğini (RSS) anlık olarak listeler.
- **Performans Dostu:** `process_iter` verilerini önbelleğe alarak işlemci yükünü minimize eder.
- **Dinamik UI:** `Rich.Table` yapısı ile süreçleri PID ve Bellek kullanımına göre sıralı gösterir.

### Teknik Fonksiyon Tablosu

| Fonksiyon | Görev | Teknik Detay |
| :--- | :--- | :--- |
| `ram_usage_info` | Genel RAM Durumu | `psutil.virtual_memory` verilerini analiz eder. |
| `ram_process` | Uygulama Listeleme | Süreçleri tarar, RSS (fiziksel bellek) verisini ayıklar. |
| **Sayfalama** | Ekran Yönetimi | 100 süreçlik bloklar halinde veriyi sayfalar. |
| **Önbellekleme** | Kaynak Tasarrufu | 5 saniyelik "Cool-down" süresi ile veri tazeler. |

### Bellek Hesaplama Mantığı
Süreçlerin bellek kullanımı **RSS (Resident Set Size)** üzerinden hesaplanır. Bu, bir sürecin o an fiziksel RAM üzerinde kapladığı gerçek alanı temsil eder.



**Birim Dönüşüm Formülü:**
$$RAM_{GB} = \frac{Bytes}{1024^{3}}$$
$$Process_{MB} = \frac{Bytes}{1024^{2}}$$

---

## 🛠 Kullanım
Sınıfı projenize dahil ederek sistem kaynaklarını izlemeye başlayabilirsiniz:

```python
ram_analiz = RAM()
print(ram_analiz.ram_usage_info())
print(ram_analiz.ram_process())