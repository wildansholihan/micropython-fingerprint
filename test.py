from oledText import OLEDTextDisplay

# Tampilkan teks panjang di tengah layar
oled = OLEDTextDisplay()
oled.display_centered_text("Hello World! This text is centered and wrapped automatically.", wrap_at=20)
