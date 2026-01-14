from src import servo

from time import sleep


def main():
    servo.run_action(servo.forward, 2, speed=80)


if __name__ == "__main__":
    main()
