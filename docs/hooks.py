import os
import shutil
import subprocess


def on_post_build(config, **kwargs):
    site_dir = config["site_dir"]
    subprocess.run(
        ["pdoc", "-t", "docs/assets/css", "dbterd/api/base.py", "-o", "target/pdoc"]
    )
    shutil.copytree("target/pdoc", os.path.join(site_dir, "api-docs"))
