import subprocess
import sys


def test_hi_claude():
    print("Running: claude -p 'hi'")
    result = subprocess.run(
        ["claude", "-p", "hi"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    print(f"Exit code: {result.returncode}")
    print(f"Stdout: {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"Stderr: {result.stderr.strip()}")

    assert result.returncode == 0, f"claude exited with code {result.returncode}"
    assert len(result.stdout.strip()) > 0, "claude returned empty response"

    print("\nPASS: claude responded successfully")


if __name__ == "__main__":
    try:
        test_hi_claude()
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("\nFAIL: claude timed out after 120 seconds")
        sys.exit(1)
