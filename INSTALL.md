# Rocket LMS v2.1 - Panduan Instalasi cPanel

## Langkah 1: Upload ke cPanel

1. **Zip folder ini** (kecuali folder `.git`)
2. **Login ke cPanel** > File Manager
3. **Upload** ke folder `public_html` atau subdomain yang diinginkan
4. **Extract** file zip

---

## Langkah 2: Buat Database

1. Di cPanel, buka **MySQL Databases**
2. **Create New Database**: Contoh `rocketlms`
3. **Create New User**: Contoh `rocketlms_user` dengan password kuat
4. **Add User to Database**: Pilih "ALL PRIVILEGES"

---

## Langkah 3: Konfigurasi .env

Edit file `.env` dan isi:

```env
APP_URL=https://domain-anda.com

DB_DATABASE=cpanel_rocketlms
DB_USERNAME=cpanel_rocketlms_user  
DB_PASSWORD=password_database_anda

MAIL_HOST=mail.domain-anda.com
MAIL_USERNAME=noreply@domain-anda.com
MAIL_PASSWORD=password_email
MAIL_FROM_ADDRESS=noreply@domain-anda.com
```

> **Catatan:** Di cPanel, nama database & user biasanya diawali dengan username cPanel, contoh: `nusaslno_rocketlms`

---

## Langkah 4: Import Database

1. Buka **phpMyAdmin** dari cPanel
2. Pilih database yang baru dibuat
3. Klik **Import**
4. Upload file `database/demo_db.sql`
5. Klik **Go**

---

## Langkah 5: Set Permissions

Di File Manager, set permission **755** untuk folder-folder ini:
- `storage/`
- `bootstrap/cache/`

Atau via SSH:
```bash
chmod -R 755 storage bootstrap/cache
```

---

## Langkah 6: Clear Cache (Penting!)

Buat file `clear_cache.php` di folder `public/`:

```php
<?php
require __DIR__ . '/../vendor/autoload.php';
$app = require_once __DIR__ . '/../bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Http\Kernel::class);
Illuminate\Support\Facades\Artisan::call('optimize:clear');
echo "Cache cleared!";
```

Lalu akses: `https://domain-anda.com/clear_cache.php`

**HAPUS file ini setelah selesai!**

---

## Langkah 7: Login Admin

Buka: `https://domain-anda.com/admin`

**Kredensial Default:**
- Email: `admin@demo.com`
- Password: `admin123`

> ⚠️ **SEGERA GANTI PASSWORD** setelah login!

---

## Troubleshooting

### Error 500
- Cek permission folder `storage/` dan `bootstrap/cache/`
- Pastikan `.htaccess` ada dan benar

### Blank Page
- Set `APP_DEBUG=true` sementara untuk melihat error
- Jangan lupa kembalikan ke `false` setelah selesai

### Database Connection Error
- Pastikan nama database, username, dan password di `.env` sudah benar
- Di cPanel, nama biasanya: `cpanelusername_databasename`

---

## Fitur Bypass

Script ini sudah di-bypass sehingga:
- ✅ Tidak perlu Purchase Code
- ✅ Tidak ada pengecekan lisensi online
- ✅ Semua fitur aktif tanpa batasan

---

*Rocket LMS v2.1 - Bypassed Edition*
