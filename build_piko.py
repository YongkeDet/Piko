import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET

PIKO_REPO = "crimera/piko"
PIKO_REPOSITORY = f"https://github.com/{PIKO_REPO}.git"
PIKO_BRANCH = "x-lite"
XLITE_CONSTANTS = (
    "patches/src/main/kotlin/app/crimera/patches/newx/utils/Constants.kt"
)
NEWX_CHINESE_STRINGS = Path("values-zh-rCN/newx/strings.xml")


def apply_download_dialog_localization(piko_directory: Path) -> None:
    """Connect download dialog display text to the translated resource bundle."""
    root = Path(__file__).resolve().parent
    source_patch = root / "source-patches/0001-localize-download-dialogs.patch"
    subprocess.run(
        ["git", "apply", "--check", str(source_patch)], cwd=piko_directory, check=True
    )
    subprocess.run(["git", "apply", str(source_patch)], cwd=piko_directory, check=True)
    strings = piko_directory / "patches/src/main/resources/addresources/values/newx/strings.xml"
    additions = ET.parse(root / "localizations/values/newx/download-dialogs.xml").getroot()
    names = [entry.get("name") for entry in additions]
    existing_names = {entry.get("name") for entry in ET.parse(strings).getroot()}
    if len(names) != len(set(names)) or existing_names.intersection(names):
        raise ValueError("Download dialog resource IDs are duplicated")
    content = strings.read_text(encoding="utf-8")
    if content.count("</resources>") != 1:
        raise ValueError("Unexpected upstream resource document")
    extra = "".join("    " + ET.tostring(entry, encoding="unicode").strip() + "\n" for entry in additions)
    strings.write_text(content.replace("</resources>", extra + "</resources>"), encoding="utf-8")


def apply_chinese_localization(piko_directory: Path) -> None:
    """Include the local NewX settings translation in the patch bundle."""
    source = Path(__file__).resolve().parent / "localizations" / NEWX_CHINESE_STRINGS
    validate_chinese_localization(piko_directory, source)
    target = (
        piko_directory
        / "patches/src/main/resources/addresources"
        / NEWX_CHINESE_STRINGS
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def validate_chinese_localization(piko_directory: Path, translation: Path) -> int:
    """Fail before building if resource IDs or formatting no longer match upstream."""
    original = ET.parse(
        piko_directory / "patches/src/main/resources/addresources/values/newx/strings.xml"
    ).getroot()
    translated = ET.parse(translation).getroot()
    expected = {
        entry.get("name"): entry
        for entry in original
        if entry.get("translatable") != "false"
    }
    actual = {entry.get("name"): entry for entry in translated}
    if len(actual) != len(translated) or expected.keys() != actual.keys():
        raise ValueError("Chinese resource IDs are duplicated or do not match upstream")
    placeholders = re.compile(r"%(?:\d+\$)?[-#+ 0,(<]*\d*(?:\.\d+)?(?:[tT][a-zA-Z]|[a-zA-Z%])")
    for name, entry in expected.items():
        text = actual[name].text or ""
        original_text = entry.text or ""
        if not text.strip():
            raise ValueError(f"Empty translation: {name}")
        if Counter(placeholders.findall(text)) != Counter(placeholders.findall(original_text)):
            raise ValueError(f"Format placeholders differ: {name}")
        if re.findall(r"\{[^}]+\}", text) != re.findall(r"\{[^}]+\}", original_text):
            raise ValueError(f"Filename tokens differ: {name}")
        if text.count(r"\n") != original_text.count(r"\n"):
            raise ValueError(f"Escaped newlines differ: {name}")
        if text.startswith(("@", "?")) or re.search(r"(?<!\\)[\"']", text):
            raise ValueError(f"Unescaped Android string syntax: {name}")
    print(f"Validated {len(actual)} Chinese settings strings", flush=True)
    return len(actual)


@dataclass(frozen=True)
class PikoBuild:
    commit: str
    supported_versions: frozenset[str]


def get_supported_versions(constants: str) -> frozenset[str]:
    """Return the X-Lite app versions supported by the checked-out Piko source."""
    versions = frozenset(
        re.findall(r'AppTarget\(version\s*=\s*"([^"]+)"\)', constants)
    )
    if not versions:
        raise ValueError("Could not find X-Lite compatible app versions in Piko")
    return versions


def pre_build_cleanup(piko_directory: Path) -> None:
    """Remove Instagram, Twitter, and legacy patches/extensions before building."""
    # Remove non-NewX patch source packages
    for path in [
        piko_directory / "patches/src/main/kotlin/app/crimera/patches/instagram",
        piko_directory / "patches/src/main/kotlin/app/crimera/patches/twitter",
        piko_directory / "patches/src/main/kotlin/app/revanced",
    ]:
        if path.exists():
            shutil.rmtree(path)

    # Remove non-NewX extension modules
    for path in [
        piko_directory / "extensions/instagram",
        piko_directory / "extensions/twitter",
    ]:
        if path.exists():
            shutil.rmtree(path)

    # Keep twitter/bringbacktwitter assets for Bring back twitter patch
    twitter_res = piko_directory / "patches/src/main/resources/twitter"
    if twitter_res.exists():
        for item in twitter_res.iterdir():
            if item.name != "bringbacktwitter":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

    addresources_dir = piko_directory / "patches/src/main/resources/addresources"
    if addresources_dir.exists():
        for res_name in ("instagram", "twitter"):
            for matched in addresources_dir.glob(f"*/{res_name}"):
                if matched.is_dir():
                    shutil.rmtree(matched)


def set_project_version(piko_directory: Path, version: str) -> None:
    """Set the version only in the temporary Piko checkout used for a build."""
    properties_path = piko_directory / "gradle.properties"
    lines = properties_path.read_text(encoding="utf-8").splitlines(keepends=True)
    version_indexes = [
        index
        for index, line in enumerate(lines)
        if re.match(r"^\s*version\s*=", line)
    ]
    if len(version_indexes) != 1:
        raise ValueError("Piko gradle.properties must contain exactly one version")

    lines[version_indexes[0]] = f"version = {version}\n"
    properties_path.write_text("".join(lines), encoding="utf-8")


def build_piko_patches(
    patch_version: str, output: str | None = None, source_commit: str | None = None
) -> PikoBuild:
    if output is None:
        output = f"bins/patches-{patch_version}.mpp"
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if patch_version.startswith("v"):
        raise ValueError("patch_version must not include the leading v")
    if source_commit is not None and re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
        raise ValueError("source_commit must be a full Git commit SHA")

    with tempfile.TemporaryDirectory(prefix="piko-") as temporary_directory:
        piko_directory = Path(temporary_directory) / "piko"

        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                PIKO_BRANCH,
                PIKO_REPOSITORY,
                str(piko_directory),
            ],
            check=True,
        )

        if source_commit is not None:
            subprocess.run(
                ["git", "fetch", "--depth", "1", "origin", source_commit],
                cwd=piko_directory,
                check=True,
            )
            subprocess.run(
                ["git", "checkout", "--detach", source_commit],
                cwd=piko_directory,
                check=True,
            )

        supported_versions = get_supported_versions(
            (piko_directory / XLITE_CONSTANTS).read_text()
        )

        pre_build_cleanup(piko_directory)
        apply_download_dialog_localization(piko_directory)
        apply_chinese_localization(piko_directory)
        set_project_version(piko_directory, patch_version)

        subprocess.run(
            ["./gradlew", "clean", "buildAndroid"],
            cwd=piko_directory,
            env=os.environ.copy(),
            check=True,
        )

        artifacts_directory = piko_directory / "patches" / "build" / "libs"
        artifact = artifacts_directory / f"patches-{patch_version}.mpp"
        if not artifact.is_file():
            raise FileNotFoundError(
                f"Piko did not produce the expected artifact {artifact.name}"
            )

        shutil.copy2(artifact, output_path)

        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=piko_directory,
            check=True,
            capture_output=True,
            text=True,
        )

    return PikoBuild(commit=commit.stdout.strip(), supported_versions=supported_versions)
