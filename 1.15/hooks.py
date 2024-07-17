import subprocess


def on_post_build(config, **kwargs):
    site_dir = config["site_dir"]
    subprocess.run(
        ["pdoc", "-t", "docs/assets/css", "dbterd/api/", "-o", f"{site_dir}/api-docs"]
    )
