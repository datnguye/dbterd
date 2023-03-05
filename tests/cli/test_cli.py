import os
import importlib.metadata


def test_entrypoint():
    exit_status = os.system("dbterd -h")
    assert exit_status == 0
    exit_status = os.system("dbterd --help")
    assert exit_status == 0


def test_version(capfd):
    exit_status = os.system("dbterd --version")
    cap = capfd.readouterr()
    assert exit_status == 0
    assert cap.out.strip() == f"dbterd, version {importlib.metadata.version('dbterd')}"
