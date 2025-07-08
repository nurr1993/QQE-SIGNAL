[app]
title = QQE Signal Notifier
package.name = qqe_signal
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,requests
orientation = portrait
osx.kivy_version = 2.1.0

# (opsional) ganti jadi iconmu
icon.filename = %(source.dir)s/icon.png

# include data
presplash.filename = %(source.dir)s/loading.png
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
android.enable_androidx = 1
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 24
android.ndk_path = 
android.sdk_path = 
android.p4a_whitelist = 
android.archs = armeabi-v7a
android.permissions = INTERNET

# Untuk mempercepat build awal (opsional)
# android.bootstrap = sdl2

# jika butuh telepon, SMS, atau notifikasi
# android.permissions = INTERNET,RECEIVE_BOOT_COMPLETED

# Agar file .apk muncul di `bin/`
android.debug = 1
