import argparse
import time

import serial


def read_until_idle(ser: serial.Serial, idle_seconds: float) -> str:
    chunks: list[bytes] = []
    last_data = time.monotonic()
    while True:
        data = ser.read(4096)
        if data:
            chunks.append(data)
            last_data = time.monotonic()
            continue
        if time.monotonic() - last_data >= idle_seconds:
            break
    return b"".join(chunks).decode("utf-8", errors="replace")


def send_command(ser: serial.Serial, command: str, idle_seconds: float) -> str:
    ser.reset_input_buffer()
    ser.write((command.strip() + "\n").encode("utf-8"))
    ser.flush()
    return read_until_idle(ser, idle_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="Interact with the Engram ESP32-C3 interactive demo firmware")
    parser.add_argument("port", nargs="?", default="COM3")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--idle-seconds", type=float, default=0.35)
    parser.add_argument("--command", help="Send one command and exit")
    args = parser.parse_args()

    with serial.Serial(args.port, args.baud, timeout=0.05) as ser:
        time.sleep(0.2)
        banner = read_until_idle(ser, args.idle_seconds)
        if banner.strip():
            print(banner, end="" if banner.endswith("\n") else "\n")
        if args.command:
            out = send_command(ser, args.command, args.idle_seconds)
            print(out, end="" if out.endswith("\n") else "\n")
            return 0
        print("Interactive shell. Type HELP, INFO, LIST GPU, SHOW GPU 0, RUN GPU 0, REPORT, or EXIT.")
        while True:
            try:
                command = input("engram> ").strip()
            except EOFError:
                return 0
            if not command:
                continue
            if command.upper() in {"EXIT", "QUIT"}:
                return 0
            out = send_command(ser, command, args.idle_seconds)
            print(out, end="" if out.endswith("\n") else "\n")


if __name__ == "__main__":
    raise SystemExit(main())
