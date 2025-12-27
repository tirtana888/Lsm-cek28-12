# Enable PHP Sodium Extension for Laragon

## Issue
Composer installation fails with: `ext-sodium * -> it is missing from your system`

## Solution Options

### Option 1: Enable Sodium Extension (Recommended)

1. **Open php.ini file:**
   ```
   C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64\php.ini
   ```

2. **Find this line (around line 900-950):**
   ```ini
   ;extension=sodium
   ```

3. **Remove the semicolon to enable it:**
   ```ini
   extension=sodium
   ```

4. **Save the file**

5. **Restart Laragon** (Stop All → Start All)

6. **Verify sodium is enabled:**
   ```bash
   php -m | findstr sodium
   ```

### Option 2: Install with Ignore Flag (Temporary)

Run Composer with platform requirement ignored:
```bash
composer install --ignore-platform-req=ext-sodium
```

**Note:** This is currently running in the background.

### Option 3: Use Laragon Menu (Easiest)

1. Right-click Laragon tray icon
2. PHP → Extensions
3. Check "sodium"
4. Restart Laragon

## Verification

After enabling, verify with:
```bash
php -m
```

Look for `sodium` in the list of loaded extensions.

## Why Sodium is Required

The Laravel application uses packages that require the Sodium extension for:
- Encryption
- Password hashing
- Secure random number generation
- JWT token generation (tymon/jwt-auth)
- Firebase authentication

## Current Status

✅ Composer is installing with `--ignore-platform-req=ext-sodium`  
⚠️ Sodium extension should be enabled for production use
