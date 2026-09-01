# Stardew Valley Mod Manager

A **cross-platform tool** for managing Stardew Valley mods with **profiles, dependency checking, and safe linking**.  

**Note:** This project was created with the assistance of AI and is only tested on Linux (CLI) and MacOS (CLI) with a Steam version of Stardew Valley.

---

## ✨ Features

- **Multiple Profiles**: Each profile has its own set of enabled mods.
- **Install Mods**: From a folder or `.zip` archive.
- **Dependency Checking**: Automatically checks for missing dependencies (including `ContentPackFor`).
- **Symlink-Based Storage**: The same mod can be used by many profiles without re-downloading.
- **Cross-Platform**: Works on Linux, macOS, and Windows.
- **Safe Profile Switching**: Only works with links/junctions (won’t delete regular files).
- **Automatic Recovery**: Recovers from missing or malformed `profiles.json`.
- **Remove Mods**: Delete a mod from a profile and clean the database.
- **Version Detection**: Automatically detects mod versions from manifests or filenames.

---

## 📥 Installation

### Prerequisites

- Python 3.8+
- [SMAPI](https://smapi.io/) installed for Stardew Valley

### Steps

1. Clone or download the project:
  ```bash
   git clone https://github.com/yourusername/stardew-mod-manager.git
   cd stardew-mod-manager
  ```
2. **Create and activate a virtual environment (recommended):**
  ```bash
   python -m venv venv
  ```
  - **On Windows:**
    ```bash
    venv\Scripts\activate
    ```
  - **On macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```
3. Install dependencies:
  ```bash
   pip install -r requirements.txt
  ```

---

## 🛠️ Usage

### Command-Line Interface (CLI)

The CLI tool allows you to manage mods and profiles directly from the terminal. Run commands like this:

```bash
python st_mod_manager_cli.py [command] [args]
```

#### Commands


| Command          | Description                                   | Example                                                  |
| ---------------- | --------------------------------------------- | -------------------------------------------------------- |
| `create-profile` | Create a new mod profile.                     | `python st_mod_manager_cli.py create-profile perso`      |
| `install`        | Install a mod (zip or folder) into a profile. | `python st_mod_manager_cli.py install perso ~/MyMod.zip` |
| `check`          | Validate mods and dependencies for a profile. | `python st_mod_manager_cli.py check perso`               |
| `list-profiles`  | List all defined profiles.                    | `python st_mod_manager_cli.py list-profiles`             |
| `list-mods`      | List all mods in a profile.                   | `python st_mod_manager_cli.py list-mods perso`           |
| `use-profile`    | Activate a profile for SMAPI.                 | `python st_mod_manager_cli.py use-profile perso`         |
| `remove-mod`     | Remove a mod from a profile.                  | `python st_mod_manager_cli.py remove-mod perso MyMod`    |


#### Options

- `--game-dir`: Specify the Stardew Valley root folder (default: auto-detected Steam location).

---

### Graphical User Interface (GUI)

Run the GUI version:

```bash
python st_mod_manager_gui.py
```

- **Tabs**: Profiles, Mods, Check, Use Profile.

---

## 🏗️ How the Core Works

The core script (`st_mod_manager_core.py`) is the backbone of the project. It handles all the logic for managing mods and profiles. Here’s a breakdown of its key components:

### **1. Profile Management**

- **`create_profile(name)`**: Creates a new profile with its own set of mods.
- **`list_profiles()`**: Lists all existing profiles.
- Profiles are stored in the `mod_manager/profiles/` directory, with each profile having its own `mods` folder.

### **2. Mod Installation**

- **`install_mod(profile, mod_path)`**: Installs a mod from a `.zip` file or folder into a profile.
  - Extracts the mod to a temporary directory.
  - Detects the mod root folder containing `manifest.json` or `modinfo.json`.
  - Moves the mod to the profile’s `mods` folder.
  - Records the mod’s version, path, and source in the database (`profiles.json`).

### **3. Dependency Checking**

- **`check_profile(profile)`**: Validates mods and dependencies for a profile.
  - Reads `manifest.json` or `modinfo.json` for each mod.
  - Checks for missing dependencies (including `ContentPackFor`).
  - Reports missing dependencies or mods.

### **4. Profile Activation**

- **`use_profile(profile, game_dir)`**: Activates a profile by linking its `mods` folder to the game’s `Mods` directory.
  - Uses symlinks (Linux/macOS) or directory junctions (Windows).
  - Ensures the game’s `Mods` folder is empty or a link/junction before proceeding.

### **5. Mod Removal**

- **`remove_mod(profile, mod_name)`**: Removes a mod from a profile.
  - Deletes the mod’s folder from the profile’s `mods` directory.
  - Removes the mod’s entry from the database.

### **6. Cross-Platform Linking**

- **`_make_link(src, dst)`**: Creates symlinks (Linux/macOS) or directory junctions (Windows).
- **`_is_junction(p)`**: Checks if a path is a Windows directory junction.
- **`_junction_target(p)`**: Resolves the target path of a Windows junction.

### **7. Database Management**

- **`_load_db()`**: Loads the profiles database (`profiles.json`).
- **`_save_db(db)`**: Saves the current state of the database.
- Automatically recovers from missing or malformed `profiles.json`.

---

## 📂 Project Structure

```
stardew-mod-manager/
├── st_mod_manager_core.py   # Core logic for managing mods and profiles
├── st_mod_manager_cli.py    # Command-line interface
├── st_mod_manager_gui.py    # Graphical user interface
├── requirements.txt          # Dependencies
└── README.md                # This file
```

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0** – see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [SMAPI](https://smapi.io/)
- [Nexus Mods](https://www.nexusmods.com/stardewvalley)
- AI in general
