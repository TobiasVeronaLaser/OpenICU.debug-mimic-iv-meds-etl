from pathlib import Path
import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class PatchConfig:
    project_root: Path
    patches_dir: Path
    venv_site_packages: Path
    dry_run: bool


@dataclass(frozen=True)
class CopyOperation:
    source: Path
    destination: Path


@dataclass
class PatchResult:
    copied_files: list[CopyOperation]
    created_dirs: list[Path]


def find_site_packages(project_root: Path) -> Path:
    lib_dir = project_root / ".venv" / "lib"

    if not lib_dir.exists():
        raise FileNotFoundError(f"Venv lib directory not found: {lib_dir}")

    python_dirs = sorted(
        path for path in lib_dir.iterdir()
        if path.is_dir() and path.name.startswith("python")
    )

    if not python_dirs:
        raise FileNotFoundError(f"No pythonX.Y directory found in: {lib_dir}")

    if len(python_dirs) > 1:
        print("Warning: multiple python directories found:")
        for path in python_dirs:
            print(f"  - {path}")

    site_packages = python_dirs[0] / "site-packages"

    if not site_packages.exists():
        raise FileNotFoundError(f"site-packages directory not found: {site_packages}")

    return site_packages


def build_config(
    project_root: Path | None = None,
    venv_site_packages: Path | None = None,
    dry_run: bool = False,
) -> PatchConfig:
    if project_root is None:
        project_root = Path.cwd().resolve()

    if venv_site_packages is None:
        venv_site_packages = find_site_packages(project_root)

    return PatchConfig(
        project_root=project_root,
        patches_dir=project_root / "patches",
        venv_site_packages=venv_site_packages,
        dry_run=dry_run,
    )


def validate_paths(config: PatchConfig) -> None:
    if not config.patches_dir.exists():
        raise FileNotFoundError(f"Patches directory not found: {config.patches_dir}")

    if not config.venv_site_packages.exists():
        raise FileNotFoundError(f"site-packages directory not found: {config.venv_site_packages}")


def print_config(config: PatchConfig) -> None:
    print(f"Project root:         {config.project_root}")
    print(f"Patches directory:    {config.patches_dir}")
    print(f"Target site-packages: {config.venv_site_packages}")
    print(f"Dry run:              {config.dry_run}")


def collect_patch_files(patches_dir: Path) -> list[Path]:
    return [
        path for path in patches_dir.rglob("*")
        if path.is_file()
        and path.suffix != ".ipynb"
        and "__pycache__" not in path.parts
    ]


def build_copy_operation(source: Path, config: PatchConfig) -> CopyOperation:
    relative_path = source.relative_to(config.patches_dir)
    destination = config.venv_site_packages / relative_path
    return CopyOperation(source=source, destination=destination)


def ensure_parent_directory(destination: Path, dry_run: bool) -> Path:
    parent = destination.parent
    if not parent.exists() and not dry_run:
        parent.mkdir(parents=True, exist_ok=True)
    return parent


def print_copy_operation(operation: CopyOperation, dry_run: bool) -> None:
    action = "WOULD COPY" if dry_run else "COPY"
    print(action)
    print(f"  from: {operation.source}")
    print(f"  to:   {operation.destination}")


def execute_copy(operation: CopyOperation, dry_run: bool) -> None:
    if not dry_run:
        shutil.copy2(operation.source, operation.destination)


def process_patch_file(source: Path, config: PatchConfig) -> tuple[CopyOperation, Path]:
    operation = build_copy_operation(source, config)
    created_dir = ensure_parent_directory(operation.destination, config.dry_run)
    print_copy_operation(operation, config.dry_run)
    execute_copy(operation, config.dry_run)
    return operation, created_dir


def apply_patches(config: PatchConfig) -> PatchResult:
    copied_files: list[CopyOperation] = []
    created_dirs: list[Path] = []

    for source in collect_patch_files(config.patches_dir):
        operation, created_dir = process_patch_file(source, config)
        copied_files.append(operation)
        created_dirs.append(created_dir)

    return PatchResult(copied_files=copied_files, created_dirs=created_dirs)


def print_result(result: PatchResult) -> None:
    print()
    print("Done.")
    print(f"Directories created: {len(set(result.created_dirs))}")
    print(f"Files processed:     {len(result.copied_files)}")