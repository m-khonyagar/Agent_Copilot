# Messenger Platform

پلتفرم مدیریت پیام‌رسانی چند‌کاناله با پنل مدیریت و اپلیکیشن اندروید.

---

## ویژگی‌ها

| # | ویژگی | توضیح |
|---|---|---|
| 1 | **بررسی پلتفرم‌ها** | بررسی وجود اکانت تلگرام، ایتا، بله، روبیکا، واتساپ برای هر شماره |
| 2 | **آخرین زمان آنلاین** | نمایش آخرین زمان آنلاین کاربر (در صورت در دسترس بودن توسط API) |
| 3 | **ارسال پیام تکی و دسته‌جمعی** | ارسال پیام به یک مخاطب یا کمپین برای گروهی از مخاطبین |
| 4 | **وضعیت مشاهده پیام** | نمایش وضعیت خوانده‌شده (✓✓) برای هر پیام ارسالی |
| 5 | **صندوق دریافت + پاسخ از پنل** | نمایش پاسخ‌های کاربران در پنل ادمین، ارسال پاسخ از همان پنل |
| 6 | **تاریخچه پیام‌ها** | نمایش کامل تاریخچه مکالمات با هر مخاطب |
| 7 | **اعلان‌ها** | اعلان آنی در اندروید برای پیام‌های جدید و وضعیت کمپین‌ها |
| 8 | **محدودیت نرخ ارسال** | تنظیم حداکثر تعداد پیام در روز برای هر پلتفرم (مثلاً ۲۰۰ پیام/روز ایتا) |

---

## معماری

```
messenger_platform/
├── backend/          # FastAPI REST API + WebSocket
├── admin/            # پنل مدیریت React
├── android/          # اپلیکیشن اندروید Kotlin
├── docker-compose.yml
└── .env.example
```

### Backend (FastAPI)

```
backend/app/
├── core/
│   ├── config.py       # تنظیمات از متغیرهای محیطی
│   └── database.py     # اتصال SQLite async
├── models/
│   └── database.py     # مدل‌های SQLAlchemy
│       ├── Contact        – مخاطبین
│       ├── PlatformAccount – وضعیت اکانت هر پلتفرم
│       ├── Message        – پیام‌ها (ارسالی/دریافتی)
│       ├── Campaign       – کمپین‌های دسته‌جمعی
│       ├── CampaignRecipient
│       ├── Notification   – اعلان‌ها
│       └── SendSchedule   – صف زمان‌بندی ارسال
├── api/
│   ├── contacts.py     # CRUD مخاطبین + بررسی پلتفرم‌ها
│   ├── messages.py     # ارسال پیام، کمپین، WebSocket
│   └── admin.py        # داشبورد، صندوق دریافت، پاسخ ادمین، تاریخچه
└── services/
    ├── platform_checker.py  # بررسی وجود اکانت روی پلتفرم‌ها
    ├── message_sender.py    # ارسال پیام از طریق APIهای پلتفرم‌ها
    └── scheduler.py         # صف‌بندی ارسال با محدودیت نرخ
```

### Admin Panel (React + Tailwind)

صفحات:
- **داشبورد** – آمار کلی
- **مخاطبین** – افزودن/حذف/بررسی پلتفرم‌ها
- **پیام‌ها** – ارسال تکی و تاریخچه
- **کمپین‌ها** – ارسال دسته‌جمعی با زمان‌بندی
- **صندوق دریافت** – پاسخ‌های کاربران + ارسال پاسخ
- **تاریخچه** – مکالمه کامل با هر مخاطب
- **اعلان‌ها** – مدیریت اعلان‌ها

### Android App (Kotlin)

صفحات:
- مخاطبین (با وضعیت پلتفرم‌ها و آخرین آنلاین)
- پیام‌ها (چت‌باکس با bubble های ارسالی/دریافتی + وضعیت خوانده‌شده)
- صندوق دریافت (پاسخ مستقیم از اپ)
- تاریخچه
- اعلان‌ها

---

## راه‌اندازی سریع

### پیش‌نیازها

- Docker ≥ 24.0 و Docker Compose ≥ 2.20
- (برای اندروید) Android Studio Hedgehog یا بالاتر

### اجرا با Docker Compose

```bash
cd messenger_platform

# کپی و تنظیم متغیرهای محیطی
cp .env.example .env
# ویرایش .env و وارد کردن توکن‌های پلتفرم‌ها

# اجرا
docker compose up --build

# Backend API:   http://localhost:8000/docs
# Admin Panel:   http://localhost:3001
```

### اجرای محلی Backend

```bash
cd messenger_platform/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### اجرای محلی Admin Panel

```bash
cd messenger_platform/admin
npm install
npm start   # http://localhost:3001
```

### اجرای Android App

1. پروژه `messenger_platform/android` را در Android Studio باز کنید
2. در `app/build.gradle.kts` آدرس API را تنظیم کنید:
   ```kotlin
   buildConfigField("String", "API_BASE_URL", "\"http://YOUR_SERVER_IP:8000\"")
   ```
3. Run کنید

---

## تنظیمات پلتفرم‌ها

### تلگرام (MTProto – کاربر واقعی)

برای بررسی اکانت و ارسال پیام از حساب واقعی:
1. به [https://my.telegram.org/apps](https://my.telegram.org/apps) مراجعه کنید
2. `TELEGRAM_API_ID` و `TELEGRAM_API_HASH` را دریافت کنید
3. برای اولین اجرا، session را با اجرای زیر بسازید:
   ```python
   from telethon.sync import TelegramClient
   client = TelegramClient('messenger_session', API_ID, API_HASH)
   client.start(phone='+989XXXXXXXXX')
   ```
4. فایل `messenger_session.session` را کنار backend قرار دهید

### تلگرام (Bot API)

```
TELEGRAM_BOT_TOKEN=your_bot_token
```

### ایتا (Eitaa Bot API)

```
EITAA_TOKEN=your_eitaa_bot_token
```

### بله (Bale Bot API)

```
BALE_TOKEN=your_bale_bot_token
```

> **نکته:** واتساپ و روبیکا API عمومی برای بررسی شماره و ارسال پیام از طریق سرور ارائه نمی‌دهند. این پلتفرم‌ها به ابزارهای غیررسمی نیاز دارند.

---

## محدودیت نرخ ارسال (Rate Limiting)

هنگام ایجاد کمپین، فیلد `rate_limit_per_day` را تنظیم کنید:

| پلتفرم | پیشنهاد |
|---|---|
| تلگرام | ۵۰ پیام/روز |
| ایتا | ۲۰۰ پیام/روز |
| بله | ۱۰۰ پیام/روز |

پیام‌ها به صورت خودکار در طول ۲۴ ساعت توزیع می‌شوند.

---

## API Endpoints

| Method | Path | توضیح |
|---|---|---|
| GET | `/contacts` | لیست مخاطبین |
| POST | `/contacts` | افزودن مخاطب |
| POST | `/contacts/{id}/check-platforms` | بررسی همه پلتفرم‌ها |
| POST | `/messages/send` | ارسال پیام تکی |
| POST | `/messages/campaigns` | ایجاد کمپین دسته‌جمعی |
| POST | `/messages/{id}/mark-read` | علامت‌گذاری به‌عنوان خوانده‌شده |
| POST | `/messages/inbound` | دریافت پیام ورودی (webhook) |
| WS | `/messages/ws` | WebSocket برای به‌روزرسانی آنی |
| GET | `/admin/dashboard` | آمار کلی |
| GET | `/admin/inbox` | صندوق دریافت |
| POST | `/admin/reply` | ارسال پاسخ از ادمین |
| GET | `/admin/history/{id}` | تاریخچه مخاطب |
| GET | `/admin/notifications` | اعلان‌ها |

مستندات کامل Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
