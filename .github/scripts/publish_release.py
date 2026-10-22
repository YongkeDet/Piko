"""Publish a build, allowing only the explicitly configured existing-release update."""

import json
import os
import subprocess
import tempfile
from pathlib import Path


def gh(*args: str) -> str:
    return subprocess.check_output(["gh", *args], text=True)


def api(path: str, *args: str):
    return json.loads(gh("api", path, *args))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / "RELEASE.json").read_text(encoding="utf-8"))
    version = config["version"]
    repository = os.environ["GITHUB_REPOSITORY"]
    commit = os.environ["GITHUB_SHA"]
    prefix = f"repos/{repository}"
    replacement = config.get("replace_existing_release")
    assets = [f"dist/{version}.mpp", "dist/build-info.json", "dist/SHA256SUMS", "dist/patches-bundle.json"]

    # Do not let a stale build replace the release after newer source has reached main.
    if api(f"{prefix}/git/ref/heads/main")["object"]["sha"] != commit:
        raise RuntimeError("Main changed during the build; refusing to publish stale source")

    if replacement:
        # An absent/recreated release must fail rather than create another release.
        release = api(f"{prefix}/releases/tags/{version}")
        if release["id"] != replacement["id"]:
            raise RuntimeError("The configured existing release no longer matches")
        tag = api(f"{prefix}/git/ref/tags/{version}")["object"]
        previous = replacement["previous_commit"]
        if tag["type"] != "commit" or tag["sha"] not in (previous, commit):
            raise RuntimeError("Release tag changed unexpectedly; refusing to replace it")
        backup_name = replacement["backup_asset_prefix"]
        backup_branch = replacement["backup_branch"]
        # This rollback branch is created through the repository connection. Actions cannot
        # create a ref to older source when that source has a different workflow definition.
        backup = api(f"{prefix}/git/ref/heads/{backup_branch}")["object"]
        if backup["type"] != "commit" or backup["sha"] != previous:
            raise RuntimeError("Rollback branch points to a different commit")

        backup_names = {
            f"{version}.mpp": f"{backup_name}.mpp",
            "build-info.json": "build-info-before-user-folders.json",
            "SHA256SUMS": "SHA256SUMS-before-user-folders",
            "patches-bundle.json": "patches-bundle-before-user-folders.json",
        }
        note_name = "release-notes-before-user-folders.md"
        existing_names = {asset["name"] for asset in release["assets"]}
        needed = set(backup_names.values()) | {note_name}
        if not needed.issubset(existing_names):
            if tag["sha"] != previous:
                raise RuntimeError("Rollback assets are incomplete after the tag was updated")
            with tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                for original in backup_names:
                    gh("release", "download", version, "--repo", repository, "--pattern", original, "--dir", directory)
                old_info = json.loads((work / "build-info.json").read_text(encoding="utf-8"))
                if old_info["release_commit"] != previous:
                    raise RuntimeError("Existing assets do not belong to the rollback commit")
                for original, backup_name in backup_names.items():
                    if backup_name in existing_names:
                        continue
                    target = work / backup_name
                    (work / original).rename(target)
                    gh("release", "upload", version, "--repo", repository, str(target))
                if note_name not in existing_names:
                    notes = work / note_name
                    notes.write_text(release["body"] or "", encoding="utf-8")
                    gh("release", "upload", version, "--repo", repository, str(notes))

        # All backups must exist before any current download is overwritten.
        backed_up = api(f"{prefix}/releases/tags/{version}")
        if not needed.issubset({asset["name"] for asset in backed_up["assets"]}):
            raise RuntimeError("Rollback asset backup did not finish")
        gh("release", "upload", version, "--repo", repository, "--clobber", *assets)
        gh("release", "edit", version, "--repo", repository, "--title", version, "--notes-file", "dist/release-notes.md")
        api(f"{prefix}/git/refs/tags/{version}", "-X", "PATCH", "-f", f"sha={commit}", "-F", "force=true")
        print(f"Updated existing release {version}; rollback: {backup_branch}", flush=True)
        return

    existing = subprocess.run(["gh", "release", "view", version, "--repo", repository], capture_output=True)
    if existing.returncode == 0:
        print(f"Release {version} already exists; preserving its tag and files", flush=True)
        return
    if api(f"{prefix}/git/matching-refs/tags/{version}"):
        raise RuntimeError(f"Tag {version} already exists; refusing to replace it")
    gh("release", "create", version, "--repo", repository, "--target", commit, "--title", version,
       "--notes-file", "dist/release-notes.md", *assets)


if __name__ == "__main__":
    main()
