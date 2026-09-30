# Permanent ARP Entry Registerer

[English](README.md) | [Türkçe](README-tr.md)

**Permanent ARP Entry Registerer, ZTE ZXHN H298A V1.0 router üzerinde SSH, CLI, shell ve BusyBox arayüzleri üzerinden kalıcı bir neighbor/ARP kaydı oluşturma işlemini otomatikleştiren bir Python aracıdır.**

Script router'a bağlanır, interaktif komut ortamında gerekli aşamalardan geçer ve sonunda şu komutu çalıştırır:

```text
ip neighbour replace <ARP_IP> lladdr <ARP_MAC> dev br0 nud permanent
```

Bu depo özellikle **ZTE ZXHN H298A V1.0** tarafından sunulan komut akışına göre geliştirilmiştir. Herhangi bir router üzerinde çalışacak genel amaçlı bir ARP yönetim aracı değildir.

## Ne Yapar?

Script aşağıdaki etkileşimi otomatikleştirir:

```text
Python / Paramiko
      |
      v
SSH bağlantısı
      |
      v
"Username:" bekle
      |
      +--> Linux kullanıcı adını gönder
      |
      v
"Password:" bekle
      |
      +--> Linux parolasını gönder
      |
      v
"CLI>" bekle
      |
      +--> "shell" gönder
      |
      v
"Login:" bekle
      |
      +--> Linux kullanıcı adını gönder
      |
      v
"Password:" bekle
      |
      +--> mevcut implementasyonun beklediği shell parolasını gönder
      |
      v
"BusyBox" bekle
      |
      v
ip neighbour replace <IP> lladdr <MAC> dev br0 nud permanent
```

Son komut, verilen IP/MAC çifti için `br0` arayüzündeki neighbor tablosu kaydını oluşturur veya değiştirir ve Linux neighbor durumunu `permanent` olarak ayarlar.

## Özellikler

- Router'ın interaktif SSH/CLI giriş zincirini otomatikleştirir.
- Verilen IPv4/MAC eşlemesini kalıcı neighbor kaydı olarak ekler.
- `ip neighbour replace` kullandığı için hedef kayıt oluşturulabilir veya aynı IP için mevcut kayıt değiştirilebilir.
- Router'ın `br0` arayüzünü hedefler.
- SSH bağlantı parametrelerini komut satırından alır.
- Router tarafındaki Linux kullanıcı adı ve parolasını komut satırından alır.
- Opsiyonel sessiz mod banner, komut ilerleme ve timeout çıktılarını bastırır.
- SSH iletişimi için Paramiko kullanır.
- Script kendi başına router firmware'inde değişiklik yapmaz.

## Gereksinimler

- Python 3
- [Paramiko](https://www.paramiko.org/)
- Router'ın SSH servisine ağ erişimi
- Scriptin beklediği router CLI ve shell akışına erişebilen kimlik bilgileri
- Bu implementasyonda kullanılan prompt ve komutlarla uyumlu ZTE ZXHN H298A V1.0 firmware/ortamı

Python bağımlılığını kurmak için:

```bash
python -m pip install paramiko
```

## Kurulum

Depoyu klonlayın:

```bash
git clone https://github.com/sezgynus/permanent-arp-entry-registerer.git
cd permanent-arp-entry-registerer
```

Paramiko'yu kurun:

```bash
python -m pip install paramiko
```

Projenin kendisi için ayrıca bir paket kurulumu gerekmez; depo bağımsız çalışan tek bir Python scripti içerir.

## Kullanım

```text
python permanent_arp_entry_registerer.py \
  --host HOST \
  --port PORT \
  --username SSH_USERNAME \
  --password SSH_PASSWORD \
  --arp_ip ARP_IP \
  --arp_mac ARP_MAC \
  --linux_user LINUX_USERNAME \
  --linux_password LINUX_PASSWORD \
  [-q]
```

Örnek:

```bash
python permanent_arp_entry_registerer.py \
  --host 192.168.1.1 \
  --port 22 \
  --username ssh-user \
  --password ssh-password \
  --arp_ip 192.168.1.50 \
  --arp_mac 00:11:22:33:44:55 \
  --linux_user linux-user \
  --linux_password linux-password
```

Örnek değerleri kendi router ve ağınıza uygun değerlerle değiştirin.

## Kullanım Videosu

YouTube üzerinde kullanım demosu bulunmaktadır:

https://youtu.be/vuDeCseHWLg?t=789

## Komut Satırı Argümanları

| Argüman | Zorunlu | Görevi |
|---|---:|---|
| `--host` | Evet | Paramiko'ya verilen router hostname veya IP adresi |
| `--port` | Evet | SSH TCP portu |
| `--username` | Evet | İlk Paramiko SSH bağlantısında kullanılan kullanıcı adı |
| `--password` | Evet | İlk Paramiko SSH bağlantısında kullanılan parola |
| `--arp_ip` | Evet | Kalıcı neighbor kaydına yazılacak IP adresi |
| `--arp_mac` | Evet | `--arp_ip` ile eşleştirilecek MAC adresi |
| `--linux_user` | Evet | Router'ın interaktif CLI/shell giriş promptlarına gönderilen kullanıcı adı |
| `--linux_password` | Evet | İlk interaktif `Password:` promptuna gönderilen parola |
| `-q`, `--quiet` | Hayır | Normal script çıktısını ve prompt beklemeyi devre dışı bırakır |

Sessiz mod dışındaki tüm argümanlar `argparse` tarafından zorunlu tanımlanmıştır. Script ayrıca ikinci bir zorunlu argüman kontrolü de içerir.

## Sessiz Mod

Kullanım:

```bash
python permanent_arp_entry_registerer.py ... --quiet
```

Normal modda `wait_for_message()`, beklenen her prompt için 10 saniyeye kadar bekler ve SSH kanalından alınan veriyi ekrana basar.

Sessiz modda ise `wait_for_message()` kanalı okumadan ve beklenen promptu doğrulamadan doğrudan başarılı sonuç döndürür. Böylece script, router'ın beklenen aşamaya ulaştığını doğrulamadan sabit 200 ms gecikmelerle komutları gönderir.

Dolayısıyla sessiz mod yalnızca çıktıyı kapatmaz; **prompt senkronizasyonunu da devre dışı bırakır**.

## SSH ve Host-Key Davranışı

Script bir Paramiko `SSHClient` oluşturur ve şu ayarı kullanır:

```python
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
```

Bu nedenle bilinmeyen bir SSH host key, interaktif doğrulama istenmeden bağlantı için otomatik kabul edilir.

Bağlantı, verilen host, port, SSH kullanıcı adı ve SSH parolasıyla açılır.

## Router Komut Zinciri

Mevcut komut tablosu:

| Beklenen prompt | Gönderilen değer |
|---|---|
| `Username:` | `--linux_user` |
| `Password:` | `--linux_password` |
| `CLI>` | `shell` |
| `Login:` | `--linux_user` |
| ikinci `Password:` | Mevcut kaynak koda gömülü router shell parolası |
| `BusyBox` | `ip neighbour replace <ARP_IP> lladdr <ARP_MAC> dev br0 nud permanent` |

İkinci shell parolası mevcut implementasyonda **hard-coded** durumdadır; `--linux_password` argümanından alınmaz. Bu durum scripti belirli firmware/ortama bağımlı hale getirir ve farklı firmware revizyonlarında kullanmadan önce kaynak kodun kontrol edilmesini gerektirir.

## Prompt Senkronizasyonu

Normal moddaki her adım için `wait_for_message()`:

1. Paramiko kanalında veri oluşmasını bekler;
2. en fazla 4096 byte okur;
3. veriyi UTF-8 olarak decode eder;
4. alınan veriyi ekrana basar;
5. beklenen metnin içerikte bulunup bulunmadığını kontrol eder;
6. 10 saniye içinde bulunamazsa timeout bildirir.

Her komuttan sonra `send_command()` satır sonu ekler ve 200 ms bekler.

Beklenen prompt timeout süresinde bulunamazsa komut döngüsü durur.

## ARP / Neighbor Kaydı Komutu

Router'a gönderilen komut:

```text
ip neighbour replace ARP_IP lladdr ARP_MAC dev br0 nud permanent
```

Parametre eşlemesi:

```text
ARP_IP   -> --arp_ip
ARP_MAC  -> --arp_mac
arayüz   -> br0
durum    -> permanent
```

Script ağ arayüzünü veya neighbor durumunu komut satırı seçeneği olarak sunmaz.

## Girdi Doğrulama

Script zorunlu komut satırı değerlerinin mevcut olup olmadığını kontrol eder ancak aşağıdakilerin biçimini veya aralığını doğrulamaz:

- host;
- integer dönüşümü dışında SSH portu;
- ARP IP adresi;
- MAC adresi;
- kullanıcı adları veya parolalar.

Geçersiz değerler bu nedenle Paramiko'ya veya router komut akışına aktarılır ve hata orada oluşabilir.

## Hata Yönetimi ve Sınırlamalar

Mevcut implementasyon küçük tutulmuştur ve bazı operasyonel sınırlamalara sahiptir:

- SSH bağlantı/kimlik doğrulama exception'ları uygulamaya özel bir hata yönetimiyle yakalanmaz.
- Prompt timeout kontrolü yalnızca sessiz mod kapalıyken çalışır.
- Sessiz mod prompt algılamasını atlar.
- SSH kanalı sabit prompt metinleriyle yönetildiği için firmware değişiklikleri, lokalizasyon veya farklı CLI çıktılarından etkilenebilir.
- Router arayüzü `br0` olarak sabittir.
- İkinci shell parolası kaynak koda gömülüdür.
- Script komutu gönderdikten sonra oluşan neighbor-table kaydını doğrulamaz.
- Kayıt silme komutu sağlamaz.
- Her çalıştırmada tek bir IP/MAC eşlemesi işler.
- IP veya MAC sözdizimini doğrulamaz.

Bunlar mevcut kaynak kod davranışını açıklar; her ZXHN H298A firmware revizyonu için garanti anlamına gelmez.

## Güvenlik Notları

Komut satırı argümanlarıyla verilen kimlik bilgileri, işletim sistemi ve kullanılan shell'e bağlı olarak diğer yerel process'ler tarafından görülebilir veya shell geçmişinde kalabilir.

Mevcut kaynak kod ayrıca bir router shell kimlik bilgisini literal string olarak içerir. Kullanmadan veya yeniden dağıtmadan önce scripti ve bunun güvenlik etkilerini inceleyin.

`AutoAddPolicy` bilinmeyen SSH host key'lerini otomatik kabul ettiği için script katı bir known-hosts politikasıyla aynı host kimliği doğrulamasını sağlamaz.

Aracı yalnızca sahibi olduğunuz veya yönetmeye yetkili olduğunuz ağ ekipmanlarında kullanın.

## Kaynak Yapısı

```text
permanent-arp-entry-registerer/
├── .github/
│   └── workflows/
│       └── sign-commits.yml
├── .gitignore
├── LICENSE
├── README.md
└── permanent_arp_entry_registerer.py
```

| Dosya | Görevi |
|---|---|
| `permanent_arp_entry_registerer.py` | SSH bağlantısı, prompt senkronizasyonu ve kalıcı neighbor kaydı oluşturma |
| `.github/workflows/sign-commits.yml` | Depo commit imzalama workflow'u |
| `LICENSE` | MIT lisansı |

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında dağıtılmaktadır.

Telif hakkı © 2023 Sezgin AÇIKGÖZ.
