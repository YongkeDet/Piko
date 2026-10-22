"""Build the pinned Chinese patch bundle without the upstream publishing pipeline."""

import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from build_piko import build_piko_patches


def main() -> None:
    root = Path(__file__).resolve().parent
    release = json.loads((root / "RELEASE.json").read_text(encoding="utf-8"))
    upstream = json.loads((root / "UPSTREAM.json").read_text(encoding="utf-8"))
    version = release["version"]
    if re.fullmatch(r"X\.\d{2}\.\d{2}", version) is None:
        raise ValueError("Release names must use X.YY.NN, for example X.26.01")
    translation = root / "localizations/values-zh-rCN/newx/strings.xml"
    if len(ET.parse(translation).getroot()) != release["translated_strings"]:
        raise ValueError("The release string count does not match the translation")
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    bundle = dist / f"{version}.mpp"
    build = build_piko_patches(
        patch_version=version,
        output=str(bundle),
        source_commit=upstream["source_commit"],
    )
    if build.commit != upstream["source_commit"]:
        raise ValueError("The built source does not match the pinned commit")
    if upstream["app_version"] not in build.supported_versions:
        raise ValueError("The expected X app version is not supported")
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    provenance = {
        **release,
        **upstream,
        "release_commit": source_commit,
        "supported_app_versions": sorted(build.supported_versions),
        "translation_sha256": hashlib.sha256(translation.read_bytes()).hexdigest(),
        "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
        "workflow_run": os.environ.get("GITHUB_RUN_ID"),
        "source_patch_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((root / "source-patches").glob("*.patch"))
        },
        "download_dialog_resources_sha256": hashlib.sha256(
            (root / "localizations/values/newx/download-dialogs.xml").read_bytes()
        ).hexdigest(),
    }
    (dist / "build-info.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    changes = "\n".join(f"- {change}" for change in release["changes"])
    subscription = {
        "version": version,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "description": f"Piko NewX 简体中文补丁 {version}\n\n{changes}",
        "download_url": f"https://github.com/YongkeDet/Piko/releases/download/{version}/{version}.mpp",
        "signature_download_url": "",
    }
    (dist / "patches-bundle.json").write_text(
        json.dumps(subscription, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (dist / "SHA256SUMS").write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in (bundle, dist / "build-info.json", dist / "patches-bundle.json")
        ),
        encoding="utf-8",
    )
    (dist / "release-notes.md").write_text(
        f"# {version}\n\n"
        f"Piko NewX 简体中文第 {release['translation_revision']} 版，共 {release['translated_strings']} 条界面文本。\n\n"
        f"{changes}\n\n"
        f"适用 X 版本：{', '.join(sorted(build.supported_versions))}。\n\n"
        f"上游源码：`{build.commit}`\n\n"
        f"本仓库提交：`{source_commit}`\n\n"
        "订阅补丁：[一键添加到 Morphe](https://morphe.software/add-source?github=YongkeDet/Piko)。\n\n"
        "也可在 Morphe 的来源 → 添加 → 远程中填入 `https://github.com/YongkeDet/Piko`。后续刷新同一来源即可，无需重复导入本地补丁。已安装的 X 仍需重新应用补丁后更新安装。\n\n"
        "此发布包含补丁包，未包含第三方 X 安装包。\n\n"
        "回退时请使用此前版本的 Git 标签和发布产物；汉化前基线保存在 `upstream-baseline` 分支。\n",
        encoding="utf-8",
    )
    print(f"Built {bundle.name} from {build.commit}", flush=True)


if __name__ == "__main__":
    main()
