from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
BIN = ROOT.parent / "firmware" / "open_input_demo"

USAGE = """Usage:
  py scripts/flash_open_input_firmware.py COM3

Flashes the published ESP32-C3 open-input demo firmware from `firmware/open_input_demo/`.
This script expects `esptool` to be installed in the invoking Python environment.
"""


def parse_args(argv: list[str]) -> str:
    for arg in argv[1:]:
        if arg in {"-h", "--help"}:
            print(USAGE.strip())
            raise SystemExit(0)
    port = "COM3"
    for arg in argv[1:]:
        if not arg.startswith("--"):
            port = arg
    return port


def main() -> None:
    port = parse_args(sys.argv)
    if not BIN.exists():
        raise SystemExit(f"firmware directory not found: {BIN}")
    required = ["bootloader.bin", "partitions.bin", "boot_app0.bin", "firmware.bin"]
    missing = [name for name in required if not (BIN / name).exists()]
    if missing:
        raise SystemExit(f"missing firmware files in {BIN}: {', '.join(missing)}")
    try:
        import esptool
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "esptool is not installed in this Python environment. Run "
            "`py -m pip install esptool` and retry."
        ) from exc
    esptool.main(
        [
            "--chip",
            "esp32c3",
            "--port",
            port,
            "--baud",
            "460800",
            "--before",
            "default-reset",
            "--after",
            "hard-reset",
            "write-flash",
            "0x0",
            str(BIN / "bootloader.bin"),
            "0x8000",
            str(BIN / "partitions.bin"),
            "0xe000",
            str(BIN / "boot_app0.bin"),
            "0x10000",
            str(BIN / "firmware.bin"),
        ]
    )


if __name__ == "__main__":
    main()
