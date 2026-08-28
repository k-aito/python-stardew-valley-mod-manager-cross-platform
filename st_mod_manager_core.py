"""
st_mod_manager_core.py – Core logic for Stardew Valley mod manager.
This module contains all the core functions for managing mods and profiles.
"""

import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from json import JSONDecodeError
from pathlib import Path

import json_repair

# ----------------------------------------------------------------------
# 0️⃣ Helpers for cross‑platform linking
# ----------------------------------------------------------------------
def _make_link(src: Path, dst: Path) -> None:
    if dst.exists():
        if dst.is_symlink() and Path(dst.readlink()) == src:
            return
        if os.name == "nt" and dst.is_dir() and _is_junction(dst) and _junction_target(dst) == src:
            return
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    if os.name == "nt":
        os.system(f'mklink /J "{dst}" "{src}"')
    else:
        dst.symlink_to(src, target_is_directory=True)

def _is_junction(p: Path) -> bool:
    return os.name == "nt" and p.is_dir() and p.stat().st_file_attributes & 0x400

def _junction_target(p: Path) -> Path:
    return Path(os.readlink(p))

# ----------------------------------------------------------------------
# 1️⃣ Paths that hold the manager’s data
# ----------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "mod_manager" / "data"
PROFILES_DB = DATA_DIR / "profiles.json"
PROFILES_ROOT = Path(__file__).parent / "mod_manager" / "profiles"
CURRENT_FILE = Path(__file__).parent / "mod_manager" / "current_profile.txt"

def _ensure_data_paths() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_ROOT.mkdir(parents=True, exist_ok=True)
    if not PROFILES_DB.exists():
        PROFILES_DB.write_text(json.dumps({}, indent=2))

def _load_db() -> dict:
    _ensure_data_paths()
    try:
        with PROFILES_DB.open() as f:
            return json_repair.load(f)
    except (JSONDecodeError, FileNotFoundError):
        empty = {}
        with PROFILES_DB.open("w") as f:
            json.dump(empty, f, indent=2)
        return empty

def _save_db(db: dict) -> None:
    with PROFILES_DB.open("w") as f:
        json.dump(db, f, indent=2)

# ----------------------------------------------------------------------
# 2️⃣ Guess default Steam install
# ----------------------------------------------------------------------
def default_steam_dir() -> Path:
    home = Path.home()
    if sys.platform.startswith("win"):
        return Path(os.getenv("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "Steam" / "steamapps" / "common" / "Stardew Valley"
    if sys.platform == "darwin":
        return home / "Library/Application Support/Steam/steamapps/common/Stardew Valley/Contents/MacOS"
    return home / ".steam/steam/steamapps/common/Stardew Valley"

# ----------------------------------------------------------------------
# 3️⃣ Core logic
# ----------------------------------------------------------------------
def _extract_version_from_filename(filename: str) -> str:
    version_patterns = [
        r'\b\d+\.\d+\.\d+[a-zA-Z0-9\-\.]*\b',
        r'\b\d+\.\d+[a-zA-Z0-9\-\.]*\b',
    ]
    for pattern in version_patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group()
    return "unknown"

def _detect_version(mod_root: Path, mod_src: Path) -> str:
    for fname in ("manifest.json", "modinfo.json"):
        f = mod_root / fname
        if f.is_file():
            try:
                data = json_repair.loads(f.read_text())
                version = data.get("Version") or data.get("VersionString")
                if version:
                    return version
            except Exception:
                pass
    if mod_src.suffix.lower() == ".zip":
        version = _extract_version_from_filename(mod_src.name)
        if version != "unknown":
            return version
        return f"unknown (from {mod_src.name})"
    return "unknown"

def _get_short_source(mod_src: Path) -> str:
    return mod_src.name

# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def create_profile(name: str) -> str:
    """Create a new profile. Returns a status message."""
    db = _load_db()
    if name in db:
        return f'⚠️ Profile "{name}" already exists.'
    profile_path = PROFILES_ROOT / name / "mods"
    profile_path.mkdir(parents=True, exist_ok=True)
    db[name] = {"mods": {}}
    _save_db(db)
    return f'✅ Created profile "{name}" at {profile_path}'

def install_mod(profile: str, mod_path: str) -> str:
    """Install a mod into a profile. Returns a status message."""
    db = _load_db()
    if profile not in db:
        return f'❌ Profile "{profile}" does not exist. Create it first.'
    mod_src = Path(mod_path).expanduser().resolve()
    if not mod_src.exists():
        return f'❌ No such file or directory: {mod_src}'

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        if mod_src.is_file() and mod_src.suffix.lower() == ".zip":
            with zipfile.ZipFile(mod_src, "r") as z:
                z.extractall(tmp_path)
        elif mod_src.is_dir():
            shutil.copytree(mod_src, tmp_path / mod_src.name)
        else:
            return "❌ Mod must be a directory or a .zip archive."

        manifest_paths = list(tmp_path.rglob("manifest.json")) + list(tmp_path.rglob("modinfo.json"))
        if not manifest_paths:
            return "❌ No manifest file (manifest.json / modinfo.json) found in the archive."
        if len(manifest_paths) > 1:
            return "❌ Multiple manifest files detected in the archive. Please clean the archive so that only a single mod root folder remains."

        manifest_file = manifest_paths[0]
        mod_root = manifest_file.parent
        storage_dir = PROFILES_ROOT / profile / "mods"
        storage_dir.mkdir(parents=True, exist_ok=True)
        target_dir = storage_dir / mod_root.name

        if target_dir.exists():
            if target_dir.is_dir() and not target_dir.is_symlink():
                shutil.rmtree(target_dir)
            else:
                target_dir.unlink()

        try:
            shutil.move(str(mod_root), str(target_dir))
        except Exception as e:
            return f"❌ Failed to move mod into profile storage: {e}"

        if not (target_dir / "manifest.json").exists() and not (target_dir / "modinfo.json").exists():
            if target_dir.is_dir():
                shutil.rmtree(target_dir)
            return "❌ Verification failed: the moved folder no longer contains a manifest."

        mod_name = target_dir.name
        version = _detect_version(target_dir, mod_src)
        if version == "unknown" or version.startswith("unknown (from"):
            return f'⚠️ Could not detect version for "{mod_name}". Zip/Folder: {mod_src.name}'

        db[profile]["mods"][mod_name] = {
            "version": version,
            "path": str(target_dir),
            "source": _get_short_source(mod_src)
        }
        _save_db(db)
        return f'✅ Installed "{mod_name}" (v{version}) into profile "{profile}". Files are stored at: {target_dir}'

def check_profile(profile: str) -> str:
    """Check a profile for missing mods or dependencies. Returns a status message."""
    db = _load_db()
    if profile not in db:
        return f'❌ Profile "{profile}" does not exist.'

    bad = False
    missing_deps = {}
    mod_name_to_uid = {}
    for mod_name, info in db[profile]["mods"].items():
        mod_path = Path(info["path"])
        manifest_path = mod_path / "manifest.json"
        modinfo_path = mod_path / "modinfo.json"
        uid = None
        if manifest_path.exists():
            try:
                manifest = json_repair.loads(manifest_path.read_text())
                uid = manifest.get("UniqueID")
            except Exception:
                pass
        if not uid and modinfo_path.exists():
            try:
                modinfo = json_repair.loads(modinfo_path.read_text())
                uid = modinfo.get("UniqueID")
            except Exception:
                pass
        mod_name_to_uid[mod_name] = uid if uid else mod_name

    installed_uids = set(mod_name_to_uid.values())
    output = []

    for mod_name, info in db[profile]["mods"].items():
        mod_path = Path(info["path"])
        if not mod_path.is_dir():
            output.append(f'❌ Missing folder for "{mod_name}" (expected at {mod_path})')
            bad = True
            continue

        manifest_path = mod_path / "manifest.json"
        modinfo_path = mod_path / "modinfo.json"
        if not manifest_path.exists() and not modinfo_path.exists():
            output.append(f'⚠️  No manifest detected for "{mod_name}" – may not load correctly.')
            continue

        dependencies = set()
        if manifest_path.exists():
            try:
                manifest = json_repair.loads(manifest_path.read_text())
                for dep in manifest.get("Dependencies", []):
                    if isinstance(dep, dict) and dep.get("IsRequired", True):
                        uid = dep.get("UniqueID")
                        if uid:
                            dependencies.add(uid)
                cp = manifest.get("ContentPackFor", {})
                uid = cp.get("UniqueID")
                if uid:
                    dependencies.add(uid)
            except Exception:
                pass
        if modinfo_path.exists():
            try:
                modinfo = json_repair.loads(modinfo_path.read_text())
                for dep in modinfo.get("Dependencies", []):
                    if isinstance(dep, dict) and dep.get("IsRequired", True):
                        uid = dep.get("UniqueID")
                        if uid:
                            dependencies.add(uid)
                cp = modinfo.get("ContentPackFor", {})
                uid = cp.get("UniqueID")
                if uid:
                    dependencies.add(uid)
            except Exception:
                pass

        missing = dependencies - installed_uids
        if missing:
            missing_deps[mod_name] = missing
            bad = True

        if (manifest_path.exists() or modinfo_path.exists()) and not missing:
            output.append(f'✅ "{mod_name}" (v{info["version"]}) looks OK.')

    if missing_deps:
        output.append("\n❗ Missing dependencies:")
        for mod, deps in missing_deps.items():
            output.append(f'   • "{mod}" is missing: {", ".join(sorted(deps))}')

    if not bad and not missing_deps:
        output.append("🎉 All mods for this profile are present and dependencies are satisfied.")
    elif not missing_deps:
        output.append("❗ Some mods are missing – consider reinstalling them.")

    return "\n".join(output)

def use_profile(profile: str, game_dir: Path = None) -> str:
    """Activate a profile by linking its mods folder into the game directory."""
    db = _load_db()
    if profile not in db:
        return f'❌ Profile "{profile}" does not exist.'

    if game_dir is None:
        game_dir = default_steam_dir()

    # Check if SMAPI is installed
    if not check_smapi_installed(game_dir):
        return (
            f'❌ SMAPI is not installed in {game_dir}. '
            'Please install SMAPI first: https://smapi.io/'
        )

    game_dir = game_dir.resolve()
    mods_dir = game_dir / "Mods"
    src = PROFILES_ROOT / profile / "mods"

    if not src.is_dir():
        return f'❌ Profile "{profile}" has no mods folder at {src}'

    if mods_dir.exists():
        if mods_dir.is_symlink() or (os.name == "nt" and _is_junction(mods_dir)):
            mods_dir.unlink()
        else:
            bad_items = [p for p in mods_dir.iterdir()]

            # Prepare the list of bad items as a single string
            bad_list = "\n".join(f"- {p}" for p in bad_items)

            # Now insert it into the message
            return (
                f"⚠️ The existing Mods is not a link or junction and contains regular "
                f"files/folders:\n{bad_list}. Please move or delete them before "
                f"switching profiles."
            )
    try:
        _make_link(src, mods_dir)
        CURRENT_FILE.write_text(profile)
        return f'✅ Profile "{profile}" is now the active SMAPI mods set.\nLinked {mods_dir} → {src}'
    except Exception as exc:
        return f'❌ Failed to link profile: {exc}'

def list_profiles() -> str:
    """List all defined profiles."""
    db = _load_db()
    if not db:
        return "ℹ️ No profiles defined yet."
    return "📂 Existing profiles:\n   - " + "\n   - ".join(sorted(db))

def list_mods(profile: str) -> str:
    """List all mods in a profile."""
    db = _load_db()
    if profile not in db:
        return f'❌ Profile "{profile}" does not exist.'
    if not db[profile]["mods"]:
        return f'ℹ️ Profile "{profile}" has no mods installed.'
    output = [f'📦 Mods installed in profile "{profile}":']
    for mod, info in db[profile]["mods"].items():
        src = info.get("source", "unknown")
        output.append(f"   * {mod} – v{info['version']} (source: {src})")
    return "\n".join(output)

def remove_mod(profile: str, mod_name: str = None) -> str:
    """Remove a mod from a profile."""
    db = _load_db()
    if profile not in db:
        return f'❌ Profile "{profile}" does not exist.'
    if not mod_name:
        if not db[profile]["mods"]:
            return f'ℹ️ Profile "{profile}" has no mods installed.'
        output = [f'📦 Mods installed in profile "{profile}":']
        for mod in db[profile]["mods"]:
            output.append(f"   * {mod}")
        output.append("\nPlease specify a mod name to remove.")
        return "\n".join(output)
    if mod_name not in db[profile]["mods"]:
        return f'❌ Mod "{mod_name}" is not installed in profile "{profile}".'
    mod_info = db[profile]["mods"][mod_name]
    mod_path = Path(mod_info["path"])
    if mod_path.is_dir():
        try:
            shutil.rmtree(mod_path)
        except Exception as e:
            return f'❌ Failed to delete mod folder: {e}'
    del db[profile]["mods"][mod_name]
    _save_db(db)
    return f'✅ Removed mod "{mod_name}" from profile "{profile}".'

def check_smapi_installed(game_dir: Path = None) -> bool:
    """
    Check if SMAPI is installed in the specified Stardew Valley directory.
    Returns True if SMAPI is detected, False otherwise.
    """
    if game_dir is None:
        game_dir = default_steam_dir()

    # Check for SMAPI's main DLL file (Windows) or the presence of SMAPI's files
    smapi_files = [
        "StardewModdingAPI.dll",  # Windows
        "StardewModdingAPI",      # Linux/macOS (directory)
    ]

    for smapi_file in smapi_files:
        smapi_path = game_dir / smapi_file
        if smapi_path.exists():
            return True

    return False
