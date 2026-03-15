from pathlib import Path
import sys

import esptool


ROOT = Path(__file__).resolve().parent
BIN = ROOT.parent / "firmware"


def parse_args(argv: list[str]) -> tuple[str, str]:
    port = "COM3"
    variant = "audited"
    idx = 1
    while idx < len(argv):
        arg = argv[idx]
        if arg == "--variant" and idx + 1 < len(argv):
            variant = argv[idx + 1].strip().lower() or "audited"
            idx += 2
            continue
        if not arg.startswith("--"):
            port = arg
        idx += 1
    return port, variant


def main() -> None:
    port, variant = parse_args(sys.argv)
    bin_dir = BIN if variant == "audited" else BIN / variant
    if not bin_dir.exists():
        raise SystemExit(f"unknown firmware variant: {variant}")
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
            str(bin_dir / "bootloader.bin"),
            "0x8000",
            str(bin_dir / "partitions.bin"),
            "0xe000",
            str(bin_dir / "boot_app0.bin"),
            "0x10000",
            str(bin_dir / "firmware.bin"),
        ]
    )


if __name__ == "__main__":
    main()
