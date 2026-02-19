# src/swipl_bootstrap.py
from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path


def _setenv_if_missing(key: str, value: str) -> None:
    if not os.environ.get(key):
        os.environ[key] = value


def configure_swipl() -> None:
    """
    Configure SWI-Prolog for PySWIP in a portable way.

    Strategy:
    1) If env already set, do nothing.
    2) Try locate swipl via PATH.
    3) On Windows, try common install locations under Program Files.
    """

    # If already configured, do not override
    if os.environ.get("SWI_HOME_DIR") and (os.environ.get("LIBSWIPL_PATH") or os.environ.get("SWIPL")):
        return

    swipl_exe: Path | None = None

    # 1) Try PATH
    swipl_path = shutil.which("swipl") or (shutil.which("swipl.exe") if sys.platform.startswith("win") else None)
    if swipl_path:
        swipl_exe = Path(swipl_path).resolve()

    # 2) Windows: try common locations if not found in PATH
    if swipl_exe is None and sys.platform.startswith("win"):
        candidates = []

        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

        # Typical layouts
        candidates += [
            Path(program_files) / "swipl" / "bin" / "swipl.exe",
            Path(program_files_x86) / "swipl" / "bin" / "swipl.exe",
        ]

        # Also search a bit inside swipl folder (handles swipl-9.x, etc.)
        for base in [Path(program_files) / "swipl", Path(program_files_x86) / "swipl"]:
            if base.exists():
                # shallow-ish search for swipl.exe
                for p in base.rglob("swipl.exe"):
                    candidates.append(p)

        for p in candidates:
            if p and p.exists():
                swipl_exe = p.resolve()
                break

    if swipl_exe is None:
        print(
            "[ERRORE] SWI-Prolog non trovato.\n"
            "Installa SWI-Prolog 64-bit e assicurati che 'swipl' sia nel PATH.\n"
            "Oppure imposta le variabili d'ambiente:\n"
            "  SWI_HOME_DIR=<cartella swipl>\n"
            "  LIBSWIPL_PATH=<percorso libswipl.dll>\n",
            file=sys.stderr
        )
        return

    bin_dir = swipl_exe.parent
    root_dir = bin_dir.parent

    # Library filename by OS
    if sys.platform.startswith("win"):
        lib_name = "libswipl.dll"
    elif sys.platform == "darwin":
        lib_name = "libswipl.dylib"
    else:
        lib_name = "libswipl.so"

    lib_path = bin_dir / lib_name

    # Fallback search if not in bin
    if not lib_path.exists():
        candidates = list(root_dir.rglob(lib_name))
        if candidates:
            lib_path = candidates[0]

    if not lib_path.exists():
        print(
        "[ERRORE] SWI-Prolog trovato, ma la libreria 'libswipl' non è stata trovata.\n"
        f"Provato a cercare: {lib_path}\n"
        "Imposta manualmente la variabile d'ambiente:\n"
        "  LIBSWIPL_PATH=<percorso completo di libswipl.dll>\n",
        file=sys.stderr
        )
        return

    _setenv_if_missing("SWI_HOME_DIR", str(root_dir))
    _setenv_if_missing("LIBSWIPL_PATH", str(lib_path))
    _setenv_if_missing("SWIPL", str(lib_path))

    # Ensure bin is in PATH
    current_path = os.environ.get("PATH", "")
    bin_str = str(bin_dir)
    if bin_str.lower() not in current_path.lower():
        os.environ["PATH"] = bin_str + os.pathsep + current_path