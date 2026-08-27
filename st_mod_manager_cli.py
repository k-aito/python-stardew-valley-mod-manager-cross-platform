#!/usr/bin/env python3
"""
st_mod_manager_cli.py – Command-line interface for Stardew Valley mod manager.
"""

import argparse
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the core module
sys.path.insert(0, str(Path(__file__).parent))
from st_mod_manager_core import (
    create_profile, install_mod, check_profile, use_profile,
    list_profiles, list_mods, remove_mod, default_steam_dir
)

def main():
    parser = argparse.ArgumentParser(
        description="Stardew Valley mod manager – profiles, install, validation, and safe profile switching."
    )
    parser.add_argument(
        "--game-dir",
        type=Path,
        default=default_steam_dir(),
        help="Root folder of Stardew Valley (default: guessed Steam location).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # create-profile
    p_create = sub.add_parser("create-profile", help="Create a new mod profile.")
    p_create.add_argument("profile", help="Name of the new profile.")
    p_create.set_defaults(func=lambda args: print(create_profile(args.profile)))

    # install
    p_install = sub.add_parser("install", help="Install a zip/folder into a profile.")
    p_install.add_argument("profile", help="Target profile name.")
    p_install.add_argument("mod_path", help="Path to the mod directory or .zip file.")
    p_install.set_defaults(func=lambda args: print(install_mod(args.profile, args.mod_path)))

    # check
    p_check = sub.add_parser("check", help="Validate the installed mods of a profile.")
    p_check.add_argument("profile", help="Profile to check.")
    p_check.set_defaults(func=lambda args: print(check_profile(args.profile)))

    # list-profiles
    p_lp = sub.add_parser("list-profiles", help="Show all defined profiles.")
    p_lp.set_defaults(func=lambda args: print(list_profiles()))

    # list-mods
    p_lm = sub.add_parser("list-mods", help="List mods belonging to a profile.")
    p_lm.add_argument("profile", help="Profile to list mods for.")
    p_lm.set_defaults(func=lambda args: print(list_mods(args.profile)))

    # use-profile
    p_use = sub.add_parser("use-profile", help="Link the chosen profile into <GameRoot>/Mods.")
    p_use.add_argument("profile", help="Name of the profile to activate.")
    p_use.set_defaults(func=lambda args: print(use_profile(args.profile, args.game_dir)))

    # remove-mod
    p_rm = sub.add_parser("remove-mod", help="Delete a mod from a profile.")
    p_rm.add_argument("profile", help="Name of the profile that contains the mod.")
    p_rm.add_argument("mod_name", nargs='?', help="Name of the mod to remove.")
    p_rm.set_defaults(func=lambda args: print(remove_mod(args.profile, args.mod_name)))

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
