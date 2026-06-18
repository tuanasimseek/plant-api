# Plant API

Plant API, akıllı saksı ve bitki takip sistemi için geliştirilmiş Django REST Framework tabanlı backend API projesidir. Proje; kullanıcı yönetimi, JWT kimlik doğrulama, bitki kataloğu, IoT cihaz entegrasyonu, sensör verileri, sulama geçmişi, bildirimler, AI görüntü analizi, ML karar mekanizması ve digital twin modüllerini içerir.

## Özellikler

- JWT tabanlı kullanıcı kayıt, giriş ve token yenileme
- PostgreSQL veritabanı entegrasyonu
- Bitki listeleme, kategori, arama ve detay API'leri
- Akıllı saksı aktivasyonu ve cihaz doğrulama
- IoT cihazları için `X-Device-Token` tabanlı güvenli haberleşme
- Sıcaklık, nem, toprak nemi, ışık ve su seviyesi sensör kayıtları
- Saksı durumu, sensör geçmişi ve sulama geçmişi takibi
- Manuel ve otomatik sulama komutları
- Bildirim ve alarm sistemi
- YOLO ile bitki boy ölçümü
- TensorFlow/Keras ile bitki türü ve sağlık analizi
- ML modeli ile sulama, ışık ve sıcaklık karar önerileri
- Digital Twin ve simülasyon sonuçları
- Swagger/OpenAPI dokümantasyonu

## Kullanılan Teknolojiler

- Python
- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- drf-spectacular
- TensorFlow / Keras
- YOLO / Ultralytics
- scikit-learn / joblib
- NumPy
- Pillow
- django-cors-headers
- python-decouple

## Proje Yapısı

```txt
backend/
├── ai/               # AI görüntü analizi ve ML servisleri
├── config/           # Django ana ayarları ve URL yapılandırması
├── devices/          # IoT cihaz kayıt, heartbeat, log ve komut API'leri
├── ml/               # Simülasyon, karar mekanizması ve digital twin modülü
├── models_ai/        # Eğitilmiş AI/ML model dosyaları
├── notifications/    # Bildirim ve alarm sistemi
├── plants/           # Bitki kataloğu ve seed verileri
├── pots/             # Saksı aktivasyonu, bitki atama ve fuzzy loglar
├── sensors/          # Sensör verileri ve sulama geçmişi
├── users/            # Custom user modeli ve auth API'leri
└── manage.py
```

## Kurulum

Projeyi klonladıktan sonra backend klasörüne girin:

```bash
git clone <repo-url>
cd plant-api-project/backend
```

Sanal ortam oluşturun ve aktif edin:

```bash
python -m venv venv
source venv/bin/activate
```

Gerekli paketleri yükleyin:

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-decouple psycopg2-binary drf-spectacular pillow requests numpy tensorflow ultralytics joblib scikit-learn
```

## Ortam Değişkenleri

`backend` klasörü içinde `.env` dosyası oluşturun:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=plant_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Veritabanı ve Çalıştırma

Log klasörünü oluşturun:

```bash
mkdir -p logs
```

Migration işlemlerini çalıştırın:

```bash
python manage.py makemigrations
python manage.py migrate
```

Bitki seed verilerini ekleyin:

```bash
python manage.py seed_plants
```

Admin kullanıcısı oluşturun:

```bash
python manage.py createsuperuser
```

Sunucuyu başlatın:

```bash
python manage.py runserver
```

API varsayılan olarak şu adreste çalışır:

```txt
http://127.0.0.1:8000
```

Swagger dokümantasyonu:

```txt
http://127.0.0.1:8000/api/docs/
```

## Kimlik Doğrulama

Kullanıcı işlemleri JWT ile korunur.

```http
Authorization: Bearer <access_token>
```

IoT cihazlarından gelen isteklerde cihaz tokenı kullanılır.

```http
X-Device-Token: <device_token>
```

## API Endpointleri

### Auth

| Method | Endpoint | Açıklama |
|---|---|---|
| POST | `/api/auth/register` | Yeni kullanıcı kaydı |
| POST | `/api/auth/login` | Kullanıcı girişi |
| POST | `/api/auth/token/refresh` | Access token yenileme |

### Plants

| Method | Endpoint | Açıklama |
|---|---|---|
| GET | `/api/plants` | Bitki listesi |
| GET | `/api/plants/categories` | Bitki kategorileri |
| GET | `/api/plants/search?q=` | Bitki arama |
| GET | `/api/plants/<plant_id>` | Bitki detayı |
| POST | `/api/plants/<plant_id>/image` | Bitki görseli yükleme |

### Pots

| Method | Endpoint | Açıklama |
|---|---|---|
| GET | `/api/pots` | Kullanıcının erişebildiği saksılar |
| GET | `/api/pots/my` | Kullanıcının kendi saksıları |
| GET | `/api/pots/<pot_id>` | Saksı detayı |
| GET | `/api/pots/verify/<device_code>` | Cihaz doğrulama |
| POST | `/api/pots/register` | Cihaz kaydı |
| POST | `/api/pots/activate` | Saksı aktivasyonu |
| POST | `/api/pots/<pot_id>/plant` | Saksıya bitki atama |
| POST | `/api/pots/<pot_id>/fuzzy/log` | Fuzzy karar logu kaydetme |
| GET | `/api/pots/<pot_id>/fuzzy/latest` | Son fuzzy logu getirme |

### Sensors

| Method | Endpoint | Açıklama |
|---|---|---|
| POST | `/api/pots/<pot_id>/readings` | Sensör verisi gönderme |
| GET | `/api/pots/<pot_id>/config` | Cihaz konfigürasyonu |
| GET/PATCH | `/api/pots/<pot_id>/status` | Saksı ve cihaz durumu |
| GET | `/api/pots/<pot_id>/history` | Sensör geçmişi |
| GET | `/api/pots/<pot_id>/watering-history` | Sulama geçmişi |
| POST | `/api/pots/<pot_id>/lightsensorreadings` | Işık sensörü verisi |

### Devices

| Method | Endpoint | Açıklama |
|---|---|---|
| POST | `/api/heartbeat` | Cihaz online durumu |
| POST | `/api/logs/action` | Cihaz aksiyon logu |
| POST | `/api/logs/error` | Cihaz hata bildirimi |
| GET | `/api/firmware/check` | Firmware kontrolü |
| POST | `/api/pots/<pot_id>/commands` | Sulama komutu |
| GET | `/api/pots/<pot_id>/setup-check` | Saksı konum uygunluğu |
| GET | `/api/environment` | Ortam verisi |
| GET | `/api/pots/<pot_id>/newconfig` | Güncel cihaz ayarları |

### AI

| Method | Endpoint | Açıklama |
|---|---|---|
| POST | `/api/ai/analyze-plant` | Bitki sağlık analizi |
| POST | `/api/ai/measure-height` | Görsel URL ile boy ölçümü |
| POST | `/api/ai/measure-height-live` | Anlık görsel ile boy ölçümü |
| POST | `/api/ai/analyze-growth` | Büyüme analizi |
| POST | `/api/ai/classify-plant-species` | Bitki türü sınıflandırma |
| GET | `/api/pots/<pot_id>/analysis` | Son AI analiz sonucu |
| GET | `/api/plants/<plant_id>/health-history` | Bitki sağlık geçmişi |
| POST | `/api/ai/guest-scan` | Misafir kullanıcı için tür tespiti |
| POST | `/api/ai/member-chat` | Üye AI bitki danışmanı |

### ML & Digital Twin

| Method | Endpoint | Açıklama |
|---|---|---|
| GET/PATCH | `/api/state-machine/config` | State machine ayarları |
| GET | `/api/state-machine/config/latest` | Son karar mekanizması ayarı |
| GET | `/api/simulation/params` | Simülasyon parametreleri |
| POST | `/api/simulation/results` | Simülasyon sonucu kaydetme |
| GET | `/api/ml/simulation-results/<pot_id>` | Simülasyon geçmişi |
| POST | `/api/ml/evaluate-optimal-decision` | ML optimal karar analizi |
| POST | `/api/ml/save-optimal-decision` | Optimal karar kaydetme |
| GET/POST | `/api/digital-twin/status` | Digital twin durumu |
| POST | `/api/optimization/best-config` | En iyi optimizasyon konfigürasyonu |

### Notifications

| Method | Endpoint | Açıklama |
|---|---|---|
| GET | `/api/notifications` | Kullanıcı bildirimleri |
| GET | `/api/alerts` | Alarm listesi |
| GET | `/api/pots/<pot_id>/state` | Cihaz state bilgisi |
| GET | `/api/devices/status` | Tüm cihazların durumu |

## Örnek Kullanım

Register request:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "full_name": "Test User"
}
```

Login request:

```json
{
  "email": "test@example.com",
  "password": "123456"
}
```

Başarılı auth cevaplarında `access_token` ve `refresh_token` döner. Korumalı endpointlerde `access_token`, `Bearer` token olarak gönderilir.

## Notlar

- Projede PostgreSQL kullanılmaktadır.
- AI/ML modelleri `backend/models_ai/` klasörü altında tutulur.
- Yüklenen medya dosyaları Django `MEDIA_ROOT` üzerinden servis edilir.
- API şeması `drf-spectacular` ile üretilir.
- Geliştirme ortamında CORS tüm originlere açıktır.

## Geliştirici

Bu projenin backend API geliştirmesi tarafımdan yapılmıştır.
````


