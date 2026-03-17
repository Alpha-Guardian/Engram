import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


OFFSET = 0x210000
SIZE = 0x1000
USAGE = """Usage:
  py scripts/read_board_report.py COM3 [--expect-mode MODE] [--expect-artifact-sha256 SHA256]
  py scripts/read_board_report.py COM3 --retries 6 --retry-delay-ms 1000
  py scripts/read_board_report.py COM3 --pre-read-delay-ms 3000

Reads the JSON report partition from the published ESP32-C3 board-proof line.
This script expects `esptool` to be available in the invoking Python
environment because it shells out to `python -m esptool`.
"""


def parse_args(argv: list[str]) -> tuple[str, str | None, str | None, int, int, int]:
    port = "COM3"
    expect_mode: str | None = None
    expect_artifact_sha256: str | None = None
    retries = 6
    retry_delay_ms = 1000
    pre_read_delay_ms = 3000
    idx = 1
    while idx < len(argv):
        arg = argv[idx]
        if arg in {"-h", "--help"}:
            print(USAGE.strip())
            raise SystemExit(0)
        if arg == "--expect-mode" and idx + 1 < len(argv):
            expect_mode = argv[idx + 1]
            idx += 2
            continue
        if arg == "--expect-artifact-sha256" and idx + 1 < len(argv):
            expect_artifact_sha256 = argv[idx + 1].lower()
            idx += 2
            continue
        if arg == "--retries" and idx + 1 < len(argv):
            retries = max(1, int(argv[idx + 1]))
            idx += 2
            continue
        if arg == "--retry-delay-ms" and idx + 1 < len(argv):
            retry_delay_ms = max(0, int(argv[idx + 1]))
            idx += 2
            continue
        if arg == "--pre-read-delay-ms" and idx + 1 < len(argv):
            pre_read_delay_ms = max(0, int(argv[idx + 1]))
            idx += 2
            continue
        if not arg.startswith("--"):
            port = arg
        idx += 1
    return (
        port,
        expect_mode,
        expect_artifact_sha256,
        retries,
        retry_delay_ms,
        pre_read_delay_ms,
    )


def decode_report_bytes(raw: bytes) -> dict | None:
    nul = raw.find(b"\x00")
    ff = raw.find(b"\xff")
    cut_candidates = [x for x in [nul, ff] if x != -1]
    cut = min(cut_candidates) if cut_candidates else len(raw)
    text = raw[:cut].decode("utf-8", errors="replace").strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    # Treat structurally empty or partial JSON as an invalid transient read and
    # let the caller retry.
    required_keys = {"artifact_sha256", "evaluation_mode"}
    if not required_keys.issubset(obj):
        return None
    return obj


def main() -> int:
    (
        port,
        expect_mode,
        expect_artifact_sha256,
        retries,
        retry_delay_ms,
        pre_read_delay_ms,
    ) = parse_args(sys.argv)
    with tempfile.TemporaryDirectory() as tmpdir:
        last_error: tuple[int, str, str] | None = None
        obj: dict | None = None
        for attempt in range(1, retries + 1):
            if pre_read_delay_ms > 0:
                time.sleep(pre_read_delay_ms / 1000.0)
            out_path = Path(tmpdir) / f"board_report_{attempt}.bin"
            cmd = [
                sys.executable,
                "-m",
                "esptool",
                "--chip",
                "esp32c3",
                "--port",
                port,
                "--baud",
                "460800",
                "read-flash",
                hex(OFFSET),
                hex(SIZE),
                str(out_path),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                last_error = (proc.returncode, proc.stdout, proc.stderr)
            else:
                obj = decode_report_bytes(out_path.read_bytes())
                if obj is not None:
                    break
                last_error = (1, "", "board report was empty or invalid JSON\n")
            if attempt < retries and retry_delay_ms > 0:
                time.sleep(retry_delay_ms / 1000.0)
        if obj is None:
            if last_error is not None:
                code, stdout, stderr = last_error
                if "No module named esptool" in stderr:
                    sys.stderr.write(
                        "esptool is not installed in this Python environment. Run "
                        "`py -m pip install esptool` and retry.\n"
                    )
                sys.stderr.write(stdout)
                sys.stderr.write(stderr)
                return code
            print("{}")
            return 1
        if expect_mode is not None:
            actual_mode = str(obj.get("evaluation_mode", "") or "")
            if actual_mode != expect_mode:
                sys.stderr.write(
                    f"evaluation_mode mismatch: expected={expect_mode} actual={actual_mode}\n"
                )
                return 2
        if expect_artifact_sha256 is not None:
            actual_sha = str(obj.get("artifact_sha256", "") or "").lower()
            if actual_sha != expect_artifact_sha256:
                sys.stderr.write(
                    f"artifact_sha256 mismatch: expected={expect_artifact_sha256} actual={actual_sha}\n"
                )
                return 3
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
