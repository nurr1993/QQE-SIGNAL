
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import requests
import time

# ===== Konfigurasi =====
API_KEY = "d6d43adce85a4008a0b9db54e1a89b24"
BOT_TOKEN = "8070244554:AAEvwtvMij8xSeQxXtsjK7AUT6uE6o3VD2k"
CHAT_ID = "50062327"
SYMBOL = "EUR/USD"
INTERVAL = "1h"
LIMIT = 50
ATR_THRESHOLD = 0.001

class QQEApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.status_label = Label(text="Menunggu sinyal...", font_size='18sp')
        self.layout.add_widget(self.status_label)

        self.btn_manual = Button(text="Cek Sinyal Sekarang", size_hint=(1, 0.2))
        self.btn_manual.bind(on_press=self.manual_cek)
        self.layout.add_widget(self.btn_manual)

        # Auto update tiap 1 menit
        Clock.schedule_interval(self.cek_sinyal_loop, 60)
        self.sinyal_terakhir = None
        return self.layout

    def kirim_telegram(self, pesan):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
        try:
            res = requests.post(url, data=payload)
            return res.status_code == 200
        except:
            return False

    def ambil_data(self):
        symbol = SYMBOL.replace("/", "")
        url = f"https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={INTERVAL}&apikey={API_KEY}&outputsize={LIMIT}&format=JSON"
        try:
            res = requests.get(url)
            data = res.json()
            if "values" not in data:
                return None, f"❌ Error: {data.get('message')}"
            candles = data["values"]
            candles.reverse()
            return candles, None
        except Exception as e:
            return None, str(e)

    def rsi(self, prices, period=14):
        deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
        seed = deltas[:period]
        up = sum(x for x in seed if x > 0) / period
        down = -sum(x for x in seed if x < 0) / period
        rs = up / down if down != 0 else 0
        rsi = [100 - 100 / (1 + rs)] * period
        for i in range(period, len(prices)-1):
            delta = deltas[i]
            upval = max(delta, 0)
            downval = -min(delta, 0)
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down if down != 0 else 0
            rsi.append(100 - 100 / (1 + rs))
        return rsi

    def atr(self, high, low, close, period=14):
        tr = []
        for i in range(len(close)):
            if i == 0:
                tr.append(high[i] - low[i])
            else:
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr.append(max(hl, hc, lc))
        atrs = []
        atrs.append(sum(tr[:period]) / period)
        for i in range(period, len(tr)):
            atrs.append((atrs[-1] * (period - 1) + tr[i]) / period)
        return [None]*period + atrs

    def qqe_sinyal(self, close, high, low):
        rsi_vals = self.rsi(close)
        atr_vals = self.atr(high, low, close)

        if len(rsi_vals) < 2 or len(atr_vals) < 1:
            return None

        if atr_vals[-1] is None or atr_vals[-1] < ATR_THRESHOLD:
            return None  # Hindari sideways

        if rsi_vals[-1] > 50 and rsi_vals[-2] < 50:
            return "BUY"
        elif rsi_vals[-1] < 50 and rsi_vals[-2] > 50:
            return "SELL"
        return None

    def cek_sinyal_loop(self, dt):
        self.cek_sinyal()

    def manual_cek(self, instance):
        self.cek_sinyal()

    def cek_sinyal(self):
        self.status_label.text = "📡 Mengambil data..."
        data, error = self.ambil_data()
        if error:
            self.status_label.text = error
            return

        close = [float(d["close"]) for d in data]
        high = [float(d["high"]) for d in data]
        low = [float(d["low"]) for d in data]

        sinyal = self.qqe_sinyal(close, high, low)

        if sinyal and sinyal != self.sinyal_terakhir:
            waktu = data[-1]["datetime"]
            pesan = f"📊 *Sinyal QQE Deteksi*\nPair: `{SYMBOL}`\nWaktu: `{waktu}`\nArah: *{sinyal}*"
            self.kirim_telegram(pesan)
            self.status_label.text = f"✅ Sinyal {sinyal} terkirim.\n{waktu}"
            self.sinyal_terakhir = sinyal
        else:
            self.status_label.text = "⏳ Tidak ada sinyal baru."

if __name__ == "__main__":
    QQEApp().run()

