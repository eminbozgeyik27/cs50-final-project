

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, RadioButtons
from matplotlib.widgets import Button
import matplotlib.animation as animation
from scipy import signal
import csv


# Başlangıç değerleri
print("Running...")
genlik = 1
frekans = 1
zaman_araligi_s = 0.002
zaman_tipi = "Second"  # 🔧 Varsayılan zaman tipi

# Ana figür ve eksenler
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, right=0.7, top=0.8, bottom=0.1)

# Radio buttons (dalga tipi ve zaman birimi seçimi)
dalgatip_radio = plt.axes([0.85, 0.35, 0.1, 0.15])
zaman_radio = plt.axes([0.85, 0.11, 0.1, 0.15])
radio = RadioButtons(dalgatip_radio, ("Sinus", "Square", "Triangle"))
radio_zaman = RadioButtons(zaman_radio, ("Second", "Milisecond", "Mikrosecond"))

# TextBox kutuları
frekanskutu = fig.add_axes([0.85, 0.83, 0.1, 0.05])
genlikkutusu = fig.add_axes([0.85, 0.75, 0.1, 0.05])
rmskutusu = fig.add_axes([0.85, 0.67, 0.1, 0.05])
vppkutusu = fig.add_axes([0.85, 0.59, 0.1, 0.05])
kaydetkutusu = fig.add_axes([0.85, 0.51, 0.1, 0.05])

frekansbox = TextBox(frekanskutu, 'Frequency (Hz)', initial=str(frekans))
genlikbox  = TextBox(genlikkutusu, 'Voltage (V)', initial=str(genlik))
rmsbox = TextBox(rmskutusu, 'Root Mean Square (RMS)', initial="{:.3f}".format(genlik / np.sqrt(2)))
vppbox = TextBox(vppkutusu, 'Vpp', initial=str(2 * genlik))
kaydetbutton = Button(kaydetkutusu, "Save as Excel")

# Zaman tipi seçilince çağrılacak fonksiyon
def zaman_secimi(label):
    global zaman_tipi
    zaman_tipi = label

radio_zaman.on_clicked(zaman_secimi)

# Zaman aralığını hesapla
def zaman_hesaplama(tip):
    if tip == 'Second':
        return 0.1       # 100 ms
    elif tip == 'Milisecond':
        return 0.005     # 5 ms
    elif tip == 'Mikrosecond':
        return 0.0005    # 500 µs
    else:
        return 0.002     # default

# Başlangıç x ekseni
x = np.linspace(0, zaman_hesaplama(zaman_tipi), 1000)
line, = ax.plot(x, genlik * np.sin(2 * np.pi * frekans * x))

# Dalga tipi başlangıç
dalga_tipi = 'Sinus'

def rms_degeri(genlik, tip):
    if tip == 'Sinus':
        return genlik / np.sqrt(2)
    elif tip == 'Square':
        return genlik
    elif tip == 'Triangle':
        return genlik / np.sqrt(3)
    else:
        return 0

def vpp_degeri(genlik):
    return 2 * genlik

def olcum():
    try:
        yeni_frekans = float(frekansbox.text.strip())
        yeni_genlik = float(genlikbox.text.strip())
        if yeni_frekans <= 0 or yeni_genlik <= 0:
            raise ValueError
        return yeni_frekans, yeni_genlik
    except ValueError:
        return frekans, genlik

def grafik(frekans, genlik):
    ax.set_xlim(0, zaman_hesaplama(zaman_tipi))
    ax.set_ylim(-genlik * 2.2, genlik * 2.2)

# Dalga tipi değişince güncelle
def dalga_secimi(label):
    global dalga_tipi
    dalga_tipi = label

radio.on_clicked(dalga_secimi)

# Animasyon fonksiyonu
def animate(i):
    yeni_frekans, yeni_genlik = olcum()
    x = np.linspace(0, zaman_hesaplama(zaman_tipi), 1000)

    if dalga_tipi == 'Sinus':
        y = yeni_genlik * np.sin(2 * np.pi * yeni_frekans * x + i / 10)
    elif dalga_tipi == 'Square':
        y = yeni_genlik * signal.square(2 * np.pi * yeni_frekans * x + i / 10)
    elif dalga_tipi == 'Triangle':
        y = yeni_genlik * signal.sawtooth(2 * np.pi * yeni_frekans * x + i / 10, width=0.5)
    else:
        y = np.zeros_like(x)

    line.set_xdata(x)
    line.set_ydata(y)

    grafik(yeni_frekans, yeni_genlik)

    # Eksen etiketini zaman türüne göre dinamik güncelle
    if zaman_tipi == "Second":
        ax.set_xlabel("Time (s)")
    elif zaman_tipi == "Milisecond":
        ax.set_xlabel("Time (ms)")
    elif zaman_tipi == "Mikrosecond":
        ax.set_xlabel("Time (µs)")

    rmsbox.set_val(f"{rms_degeri(yeni_genlik, dalga_tipi):.3f}")
    vppbox.set_val(f"{vpp_degeri(yeni_genlik):.2f}")

    return line,


def kaydet(event):
    # Güncel x ve y verilerini oluştur
    f, g = olcum()
    x = np.linspace(0, zaman_hesaplama(zaman_tipi), 1000)

    if dalga_tipi == 'Sinus':
        y = g * np.sin(2 * np.pi * f * x)
    elif dalga_tipi == 'Square':
        y = g * signal.square(2 * np.pi * f * x)
    elif dalga_tipi == 'Triangle':
        y = g * signal.sawtooth(2 * np.pi * f * x, width=0.5)
    else:
        y = np.zeros_like(x)

    # Dosya ismi örneği: "veri_sinus_100Hz.csv"
    dosya_adi = f"veri_{dalga_tipi.lower()}_{int(f)}Hz.csv"

    with open(dosya_adi, mode='w', newline='') as dosya:
        writer = csv.writer(dosya)
        writer.writerow(['Time (s)', 'Voltage (V)'])  # Başlık
        for xi, yi in zip(x, y):
            writer.writerow([xi, yi])

    print(f"Veri dosyası kaydedildi: {dosya_adi}")


kaydetbutton.on_clicked(kaydet)

# Animasyonu başlat
ani = animation.FuncAnimation(fig, animate, interval=50, cache_frame_data=False)

# Başlık ve grid
ax.set_title("Oscilloscope Simulation")
ax.set_ylabel("Voltage (V)")
ax.grid(True)


try:
    plt.show()
except Exception as e:
    print("Grafik gösterilemedi:", e)
