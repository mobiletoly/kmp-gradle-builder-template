#!/usr/bin/env python3
"""
Template bootstrap utility.

Usage example:
python tools/setup_template.py \
    --plugin-id dev.example.helloplugin \
    --package-name dev.example.helloplugin \
    --project-name hello-plugin \
    --output-dir /tmp/hello-plugin
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
OLD_PACKAGE = "dev.goquick.kmpprofiles"
OLD_PLUGIN_ID = "dev.goquick.kmpprofiles"
OLD_PROJECT_NAME = "kmp-profiles"
OLD_DEV_TEAM = "8MU5M984Q6"
OLD_BUNDLE_ID = f"{OLD_PACKAGE}.sampleapp.SampleApp$(TEAM_ID)"
OLD_BUNDLE_ID = f"{OLD_PACKAGE}.sampleapp.SampleApp$(TEAM_ID)"

TEXT_EXTENSIONS = {
    ".kt",
    ".kts",
    ".gradle",
    ".md",
    ".txt",
    ".swift",
    ".plist",
    ".pbxproj",
    ".xcconfig",
    ".gitignore",
    ".properties",
    ".json",
    ".xml",
}

OPTIONAL_TEXT_FILES = {
    "gradlew",
    "gradlew.bat",
    "README",
    "README.md",
    "LICENSE",
}

PACKAGE_RELOCATE_ROOTS = [
    "plugin/src/main/kotlin",
    "plugin/src/test/kotlin",
    "sample-app/composeApp/src/androidMain/kotlin",
    "sample-app/composeApp/src/commonMain/kotlin",
    "sample-app/composeApp/src/commonTest/kotlin",
    "sample-app/composeApp/src/jvmMain/kotlin",
    "sample-app/composeApp/src/jvmTest/kotlin",
    "sample-app/composeApp/src/iosMain/kotlin",
]

CLEAN_DIR_NAMES = {
    ".gradle",
    "build",
    "DerivedData",
    "Frameworks",
    ".idea",
    ".kotlin",
    ".konan",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a new plugin project from this template.")
    parser.add_argument("--plugin-id", required=True, help="Gradle plugin id to register, e.g. dev.example.myplugin")
    parser.add_argument("--package-name", required=True, help="Kotlin package used for plugin sources, e.g. dev.example.myplugin")
    parser.add_argument(
        "--project-name",
        help="Root project name (defaults to last segment of plugin id).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to copy the template into (must not already exist).",
    )
    return parser.parse_args()


def copy_template(dest: Path) -> None:
    ignore = shutil.ignore_patterns(".git", "__pycache__")
    shutil.copytree(REPO_ROOT, dest, ignore=ignore)


def remove_metadata(dest: Path) -> None:
    git_dir = dest / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)

    for path in dest.rglob("*"):
        if path.is_dir() and path.name in CLEAN_DIR_NAMES:
            shutil.rmtree(path, ignore_errors=True)


def relocate_package_dirs(dest: Path, new_package: str) -> None:
    old_parts = Path(*OLD_PACKAGE.split("."))
    new_parts = Path(*new_package.split("."))

    for relative in PACKAGE_RELOCATE_ROOTS:
        base = dest / relative
        old_dir = base / old_parts
        if old_dir.exists():
            target_dir = base / new_parts
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.move(str(old_dir), str(target_dir))
            cleanup_empty_parents(old_dir.parent)


def cleanup_empty_parents(start: Path) -> None:
    current = start
    while current != current.parent and not any(current.iterdir()):
        current.rmdir()
        current = current.parent


def update_project_name(dest: Path, project_name: str) -> None:
    settings_file = dest / "settings.gradle.kts"
    replace_in_file(
        settings_file,
        {"rootProject.name = \"{}\"".format(OLD_PROJECT_NAME): f"rootProject.name = \"{project_name}\""},
    )


def update_plugin_id(dest: Path, plugin_id: str) -> None:
    files = [
        dest / "plugin/build.gradle.kts",
        dest / "sample-app/composeApp/build.gradle.kts",
    ]
    replacements = {
        f"id = \"{OLD_PLUGIN_ID}\"": f'id = "{plugin_id}"',
        f'id("{OLD_PLUGIN_ID}")': f'id("{plugin_id}")',
    }
    for file in files:
        if file.exists():
            replace_in_file(file, replacements)


def replace_in_file(path: Path, replacements: Dict[str, str]) -> None:
    if not path.exists():
        return
    content = path.read_text()
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
    if new_content != content:
        path.write_text(new_content)


def replace_text(dest: Path, replacements: Dict[str, str]) -> None:
    for path in dest.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in TEXT_EXTENSIONS or path.name in OPTIONAL_TEXT_FILES:
            try:
                content = path.read_text()
            except UnicodeDecodeError:
                continue
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
            if new_content != content:
                path.write_text(new_content)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if output_dir.exists():
        sys.exit(f"Output directory {output_dir} already exists. Please provide a new path.")

    project_name = args.project_name or args.plugin_id.split(".")[-1]

    copy_template(output_dir)
    remove_metadata(output_dir)
    update_plugin_id(output_dir, args.plugin_id)
    relocate_package_dirs(output_dir, args.package_name)
    bundle_id = f"{args.package_name}.sampleapp"
    replace_text(
        output_dir,
        {
            OLD_BUNDLE_ID: bundle_id,
            OLD_PACKAGE: args.package_name,
            OLD_PROJECT_NAME: project_name,
            f"DEVELOPMENT_TEAM = {OLD_DEV_TEAM};": 'DEVELOPMENT_TEAM = "";',
        },
    )
    update_project_name(output_dir, project_name)

    print(f"Template copied to {output_dir}")
    print("Next steps:")
    print(f"  cd {output_dir}")
    print("  ./gradlew :plugin:build")


if __name__ == "__main__":
    main()
