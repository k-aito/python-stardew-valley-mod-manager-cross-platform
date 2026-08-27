# Stardew Valley Mod Manager

A **cross-platform tool** for managing Stardew Valley mods with **profiles, dependency checking, and safe linking**.  

**Note:** This project was created with the assistance of AI and is only tested on Linux with a Steam version of Stardew Valley.

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

Run commands like this:

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

## 📂 Project Structure

```
stardew-mod-manager/
├── st_mod_manager_core.py   # Core logic
├── st_mod_manager_cli.py    # CLI interface
├── st_mod_manager_gui.py    # GUI interface
├── requirements.txt         # Dependencies
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
