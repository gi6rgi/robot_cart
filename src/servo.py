import time
from pathlib import Path

STOP = 1445
SPD = 120
PERIOD = 20_000_000  # ns (50 Hz)

pwm = Path("/sys/class/pwm")
chip = next(c for c in pwm.glob("pwmchip*") if int((c / "npwm").read_text()) >= 2)


def ch(n):
    d = chip / f"pwm{n}"
    if not d.exists():
        (chip / "export").write_text(str(n))
        time.sleep(0.05)
    (d / "enable").write_text("0")
    (d / "period").write_text(str(PERIOD))
    (d / "enable").write_text("1")
    return d


L, R = ch(0), ch(1)  # GPIO12=pwm0, GPIO13=pwm1


def us(dev, u) -> None:
    (dev / "duty_cycle").write_text(str(u * 1000))


def set_lr(l_us: int, r_us: int) -> None:
    us(L, l_us)
    us(R, r_us)


def stop() -> None:
    set_lr(STOP, STOP)


def forward(speed: int = SPD) -> None:
    set_lr(STOP + speed, STOP - speed)


def backward(speed: int = SPD) -> None:
    set_lr(STOP - speed, STOP + speed)


def turn_left(speed: int = SPD) -> None:
    set_lr(STOP - speed, STOP - speed)


def turn_right(speed: int = SPD) -> None:
    set_lr(STOP + speed, STOP + speed)


def run_action(action_fn, seconds: float, *args, **kwargs) -> None:
    """
    Run an action for `seconds`, then stop.
    """
    action_fn(*args, **kwargs)
    time.sleep(seconds)
    stop()
