# یکپارچه‌سازی ONLYOFFICE با پلتفرم Amline
# ONLYOFFICE Integration for Amline Platform

این دایرکتوری شامل تمام فایل‌های لازم برای یکپارچه‌سازی ONLYOFFICE Document Server
با پلتفرم Amline_namAvaran است.

## ساختار فایل‌ها

```
onlyoffice-integration/
├── backend/
│   ├── app/
│   │   ├── services/onlyoffice.py       ← سرویس JWT و config builder
│   │   ├── models/office_document.py    ← مدل SQLAlchemy
│   │   └── api/routes/onlyoffice_docs.py ← API endpoints
│   ├── alembic/versions/
│   │   └── 20240407_add_office_documents.py ← مایگریشن دیتابیس
│   └── patches/
│       ├── config.py.patch.txt          ← تغییرات config.py
│       ├── router.py.patch.txt          ← تغییرات router.py
│       └── requirements.txt.patch.txt   ← وابستگی‌های جدید
├── admin-ui/
│   └── src/
│       ├── components/DocumentEditor/
│       │   └── DocumentEditor.tsx       ← کامپوننت ویرایشگر
│       ├── pages/office/
│       │   └── OfficePage.tsx           ← صفحه مدیریت اسناد
│       └── patches/
│           ├── App.tsx.patch.txt        ← اضافه کردن Route
│           └── navigation.ts.patch.txt  ← اضافه کردن آیتم منو
└── docker/
    ├── docker-compose.onlyoffice.yml    ← سرویس Docker
    ├── nginx/onlyoffice.conf            ← Nginx reverse proxy
    └── .env.onlyoffice.example          ← متغیرهای محیطی
```

---

## مراحل نصب (Installation Steps)

### مرحله ۱ — متغیرهای محیطی

محتوای فایل `docker/.env.onlyoffice.example` را به فایل `.env` اصلی اضافه کنید:

```bash
cat onlyoffice-integration/docker/.env.onlyoffice.example >> .env
```

مقدار `ONLYOFFICE_JWT_SECRET` را با یک مقدار تصادفی امن جایگزین کنید:

```bash
openssl rand -hex 32
```

### مرحله ۲ — Docker Compose

محتوای `docker/docker-compose.onlyoffice.yml` را به `docker-compose.yml` اصلی اضافه کنید.

یا می‌توانید از overlay استفاده کنید:

```bash
docker compose -f docker-compose.yml -f onlyoffice-integration/docker/docker-compose.onlyoffice.yml up -d
```

اولین اجرا چند دقیقه طول می‌کشد (Image حدود 2 گیگابایت است).

### مرحله ۳ — بکند: فایل‌های جدید

فایل‌های زیر را به مخزن Amline_namAvaran کپی کنید:

```bash
# سرویس ONLYOFFICE
cp onlyoffice-integration/backend/app/services/onlyoffice.py \
   backend/backend/app/services/onlyoffice.py

# مدل جدید
cp onlyoffice-integration/backend/app/models/office_document.py \
   backend/backend/app/models/office_document.py

# API routes
cp onlyoffice-integration/backend/app/api/routes/onlyoffice_docs.py \
   backend/backend/app/api/routes/onlyoffice_docs.py

# مایگریشن
cp onlyoffice-integration/backend/alembic/versions/20240407_add_office_documents.py \
   backend/backend/alembic/versions/20240407_add_office_documents.py
```

### مرحله ۴ — بکند: تغییر config.py

فایل `backend/backend/app/core/config.py` را باز کرده و داخل کلاس `Settings`
فیلدهای زیر را اضافه کنید (بعد از فیلدهای موجود):

```python
# ONLYOFFICE Document Server integration
onlyoffice_jwt_secret: str = "change-me-onlyoffice-secret"
onlyoffice_server_url: str = "http://localhost:8180"
onlyoffice_callback_base_url: str | None = None
```

### مرحله ۵ — بکند: تغییر router.py

فایل `backend/backend/app/api/router.py` را باز کرده و دو تغییر بدهید:

**الف) اضافه کردن import:**
```python
from app.api.routes import onlyoffice_docs
```

**ب) ثبت router:**
```python
api_router.include_router(
    onlyoffice_docs.router,
    prefix="/onlyoffice-docs",
    tags=["onlyoffice"],
)
```

### مرحله ۶ — مایگریشن دیتابیس

قبل از اجرا، `down_revision` را در فایل مایگریشن به آخرین revision موجود در پروژه تنظیم کنید:

```bash
# پیدا کردن آخرین migration
cd backend/backend && alembic heads

# ویرایش فایل مایگریشن
# down_revision = "آخرین_revision_id"

# اجرای مایگریشن
alembic upgrade head
```

### مرحله ۷ — فرانت‌اند: فایل‌های جدید

```bash
# کپی کامپوننت ویرایشگر
mkdir -p admin-ui/src/components/DocumentEditor
cp onlyoffice-integration/admin-ui/src/components/DocumentEditor/DocumentEditor.tsx \
   admin-ui/src/components/DocumentEditor/DocumentEditor.tsx

# کپی صفحه اسناد
mkdir -p admin-ui/src/pages/office
cp onlyoffice-integration/admin-ui/src/pages/office/OfficePage.tsx \
   admin-ui/src/pages/office/OfficePage.tsx
```

### مرحله ۸ — فرانت‌اند: تغییر App.tsx

فایل `admin-ui/src/App.tsx` را باز کرده و دو تغییر بدهید:

**الف) اضافه کردن lazy import (در کنار imports دیگر):**
```tsx
const OfficePage = lazy(() => import('./pages/office/OfficePage'))
```

**ب) اضافه کردن Route (داخل `<Route path="/">`, قبل از catch-all):**
```tsx
<Route
  path="office"
  element={
    <RouteSuspense>
      <OfficePage />
    </RouteSuspense>
  }
/>
```

### مرحله ۹ — فرانت‌اند: تغییر navigation.ts

فایل `admin-ui/src/config/navigation.ts` را باز کرده و در آرایه `APP_NAV_ITEMS`
آیتم زیر را اضافه کنید (بعد از CRM):

```ts
{
  to: '/office',
  label: 'اسناد آفیس',
  icon: '📝',
  permission: 'contracts:read',
},
```

### مرحله ۱۰ — Nginx (در محیط Production)

فایل `docker/nginx/onlyoffice.conf` را به دایرکتوری Nginx کپی کرده و دامنه
`office.amline.ir` را در DNS ثبت کنید.

```bash
# دستور certbot برای گواهی SSL
certbot --nginx -d office.amline.ir
```

---

## Build و Deploy

```bash
# بازسازی image‌ها
docker compose build backend admin-ui

# راه‌اندازی همه سرویس‌ها
docker compose up -d

# اجرای مایگریشن
docker compose exec backend alembic upgrade head
```

---

## تست یکپارچه‌سازی

۱. وارد پنل ادمین شوید
۲. در منوی کناری، گزینه **اسناد آفیس** را ببینید
۳. روی **سند جدید** کلیک کنید
۴. یک سند Word ایجاد کنید
۵. روی **ویرایش** کلیک کنید — ویرایشگر ONLYOFFICE باز می‌شود
۶. تغییری ایجاد کنید — سند به‌صورت خودکار در MinIO/S3 ذخیره می‌شود

---

## معماری نهایی

```
کاربر (مرورگر)
     │
     ▼
Admin Panel (admin-ui :3002)
  └── OfficePage.tsx
       └── DocumentEditor.tsx
            └── ONLYOFFICE DocsAPI (JS SDK)
                     │
                     ├── دریافت سند از MinIO (presigned URL)
                     │
                     └── ارسال callback به Backend
                              │
                              ▼
                    Backend FastAPI (:8000)
                    /onlyoffice-docs/{id}/callback
                              │
                              └── ذخیره سند جدید در MinIO/S3
                                         │
                                         ▼
                              ONLYOFFICE Document Server (:8180)
                              (Docker container)
```

---

## نکات امنیتی

- **JWT Secret**: حتماً یک مقدار تصادفی ۳۲+ بایتی برای `ONLYOFFICE_JWT_SECRET` استفاده کنید
- **Callback URL**: باید فقط از شبکه داخلی Docker در دسترس باشد
- **HTTPS**: در محیط Production حتماً SSL فعال کنید
- **MinIO bucket**: برای اسناد آفیس از یک bucket جداگانه `office-docs` استفاده کنید
