import subprocess

def test_cli_health_check():
    result = subprocess.run(
        [".venv/bin/python3", "report_cli.py", "--report", "health_check", "--format", "json"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "customers" in result.stdout
