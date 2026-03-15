import json
import subprocess
import sys
import tempfile
from pathlib import Path


OFFSET = 0x210000
SIZE = 0x1000


def parse_args(argv: list[str]) -> tuple[str, str | None, str | None]:
    port = "COM3"
    expect_mode: str | None = None
    expect_artifact_sha256: str | None = None
    idx = 1
    while idx < len(argv):
        arg = argv[idx]
        if arg == "--expect-mode" and idx + 1 < len(argv):
            expect_mode = argv[idx + 1]
            idx += 2
            continue
        if arg == "--expect-artifact-sha256" and idx + 1 < len(argv):
            expect_artifact_sha256 = argv[idx + 1].lower()
            idx += 2
            continue
        if not arg.startswith("--"):
            port = arg
        idx += 1
    return port, expect_mode, expect_artifact_sha256


def main() -> int:
    port, expect_mode, expect_artifact_sha256 = parse_args(sys.argv)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "board_report.bin"
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
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            return proc.returncode
        raw = out_path.read_bytes()
        nul = raw.find(b"\x00")
        ff = raw.find(b"\xff")
        cut_candidates = [x for x in [nul, ff] if x != -1]
        cut = min(cut_candidates) if cut_candidates else len(raw)
        text = raw[:cut].decode("utf-8", errors="replace").strip()
        if not text:
            print("{}")
            return 1
        obj = json.loads(text)
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
