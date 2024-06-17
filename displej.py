import smbus2
import time

# I2C adresa (proverite sa sudo i2cdetect -y 1)
I2C_ADDR = 0x3f
# I2C bus (obicno 1 za Raspberry Pi 4)
I2C_BUS = 1

# LCD konstante
LCD_CHR = 1  # Karakter mod
LCD_CMD = 0  # Komanda mod

LCD_LINE_1 = 0x80  # 1. linija
LCD_LINE_2 = 0xC0  # 2. linija

LCD_BACKLIGHT = 0x08  # Ukljuci pozadinsko osvetljenje
ENABLE = 0b00000100  # Omoguci pin

# Postavljanje I2C komunikacije
bus = smbus2.SMBus(I2C_BUS)

def lcd_byte(bits, mode):
    """Posalji byte podataka na LCD."""
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    """Toggle enable pin"""
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)

def lcd_init():
    """Inicijalizacija LCD ekrana."""
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.0005)

def lcd_string(message, line):
    """Posalji string na LCD ekran."""
    message = message.ljust(16, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(16):
        lcd_byte(ord(message[i]), LCD_CHR)

def lcd_clear():
    """Obri?i sadr?aj LCD ekrana."""
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.0005)