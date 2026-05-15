"""Run self-test capturing stdout to a UTF-8 file (no shell involvement)."""
import io
import os
import sys

os.environ["PYTHONUTF8"] = "1"

# Replace stdout/stderr with UTF-8 file streams BEFORE importing anything else
out_path = os.path.join(os.path.dirname(__file__), "..", ".cache", "self_test_output.txt")
out_path = os.path.abspath(out_path)
os.makedirs(os.path.dirname(out_path), exist_ok=True)

original_stdout = sys.stdout
original_stderr = sys.stderr
fp = open(out_path, "w", encoding="utf-8", buffering=1)
sys.stdout = fp
sys.stderr = fp

try:
    from main import main as _main
    rc = _main(["--log-level", "WARNING", "self-test"])
except SystemExit as e:
    rc = e.code
finally:
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    fp.close()

print(f"Wrote self-test output to: {out_path}")
print(f"Exit code: {rc}")
sys.exit(0 if rc == 0 else 1)
