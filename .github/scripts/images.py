import argparse
import os
from pathlib import Path
import subprocess

import yaml


def images(path):
    config = yaml.safe_load(path.read_text()) or {}
    return {
        service["image"]
        for challenge in config.get("challenges", [])
        for service in challenge.get("instancerConfig", {}).get("config", {}).get("services", {}).values()
    }


parser = argparse.ArgumentParser()
parser.add_argument("challenge", nargs="?")
parser.add_argument("--prune", action="store_true")
args = parser.parse_args()
if not os.environ.get("DOCKER_HOST", "").startswith("ssh://"):
    raise SystemExit("Set CTF_DOCKER_HOST to the worker's ssh:// Docker endpoint")

if args.prune:
    referenced = set().union(*(images(p) for p in Path(".").rglob("kona.yaml")))
    namespaces = {image.rsplit("/", 1)[0] + "/" for image in referenced if "/" in image}
    used = set(subprocess.check_output(["docker", "ps", "-a", "--format", "{{.Image}}"], text=True).splitlines())
    tags = subprocess.check_output(["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"], text=True).splitlines()
    for tag in sorted(set(tags) - referenced - used):
        if any(tag.startswith(prefix) for prefix in namespaces) and "<none>" not in tag:
            subprocess.run(["docker", "image", "rm", tag], check=True)
else:
    path = Path(args.challenge).resolve()
    path.relative_to(Path.cwd().resolve())
    targets = images(path / "kona.yaml")
    if targets:
        dockerfiles = list((path / "source").rglob("Dockerfile"))
        if len(targets) != 1 or len(dockerfiles) != 1:
            raise SystemExit(f"Expected one instancer image and one source Dockerfile in {path}")
        image = next(iter(targets))
        dockerfile = dockerfiles[0]
        subprocess.run([
            "docker", "build", "--tag", image,
            "--label", "org.opencontainers.image.revision=" + os.environ["GITHUB_SHA"],
            "--file", str(dockerfile), str(dockerfile.parent),
        ], check=True)
        subprocess.run(["docker", "image", "inspect", image, "--format", "{{.Id}}"], check=True)
