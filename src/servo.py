from pathlib import Path
import time

STOP = 1450
SPD  = 120
PERIOD = 20_000_000  # ns (50 Hz)

pwm = Path("/sys/class/pwm")
chip = next(c for c in pwm.glob("pwmchip*") if int((c/"npwm").read_text()) >= 2)


def ch(n):
    d = chip/f"pwm{n}"
    if not d.exists():
        (chip/"export").write_text(str(n))
        time.sleep(0.05)
    (d/"enable").write_text("0")
    (d/"period").write_text(str(PERIOD))
    (d/"enable").write_text("1")
    return d


L, R = ch(0), ch(1)  # GPIO12=pwm0, GPIO13=pwm1


def us(dev, u): (dev/"duty_cycle").write_text(str(u*1000))


def stop():
    us(L, STOP); us(R, STOP)


def forward():
    us(L, STOP + SPD)
    us(R, STOP - SPD)


def turn_left():
    us(R, STOP - SPD)


def turn_right():
    us(L, STOP + SPD)

