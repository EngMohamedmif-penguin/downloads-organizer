#!/usr/bin/env python3
"""Downloads Organizer - محرك تنظيم التنزيلات لويندوز."""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from shutil import move
from typing import Any

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

APP_NAME = "DownloadsOrganizer"
SINGLE_INSTANCE_PORT = 47653
CONFIG_VERSION = 2

DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Documents/PDF": [".pdf"],
    "Documents/Word": [".doc", ".docx", ".odt", ".rtf", ".dotx"],
    "Documents/Excel": [".xls", ".xlsx", ".xlsm", ".csv", ".ods"],
    "Documents/Presentations": [".ppt", ".pptx", ".odp", ".key"],
    "Documents/Text": [".txt", ".md", ".log", ".tex"],
    "Documents/Ebooks": [".epub", ".mobi", ".azw3", ".djvu"],
    "Images/Photos": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".tiff", ".ico", ".jfif", ".avif"],
    "Images/Design": [".svg", ".psd", ".ai", ".xd", ".fig", ".sketch", ".eps"],
    "Media/Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Media/Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"],
    "Software/Installers": [".exe", ".msi", ".msix", ".appx", ".dmg", ".pkg", ".deb", ".rpm", ".apk"],
    "Software/DiskImages": [".iso", ".img", ".vhd", ".vhdx"],
    "Code/Scripts": [".py", ".js", ".ts", ".ps1", ".bat", ".sh", ".html", ".css", ".sql", ".ipynb"],
    "Code/Data": [".json", ".xml", ".yaml", ".yml", ".db", ".sqlite"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
    "Torrents": [".torrent"],
}
DEFAULT_OTHER_FOLDER = "Other"
DEFAULT_DUPLICATES_FOLDER = "_Duplicates"
PARTIAL_EXTENSIONS = {".crdownload", ".tmp", ".temp", ".part", ".partial", ".download", ".opdownload", ".aria2", ".!ut", ".bc!"}
IGNORED_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}


def get_downloads_dir() -> Path:
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            class GUID(ctypes.Structure):
                _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]
            folder_id = GUID(0x374DE290, 0x123F, 0x4565, (ctypes.c_ubyte * 8)(0x91, 0x64, 0x39, 0xC4, 0x92, 0x5E, 0x46, 0x7B))
            buf = ctypes.c_wchar_p()
            if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(folder_id), 0, None, ctypes.byref(buf)) == 0:
                path = Path(buf.value)
                ctypes.windll.ole32.CoTaskMemFree(buf)
                return path
        except Exception:
            pass
    return Path.home() / "Downloads"


def get_app_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_path() -> Path:
    return get_app_dir() / "config.json"


def setup_logging() -> logging.Logger:
    logger = logging.getLogger(APP_NAME)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler = RotatingFileHandler(get_app_dir() / "organizer.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


log = setup_logging()


def normalize_extension(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return ""
    return value if value.startswith(".") else f".{value}"


def normalize_categories(raw: dict[str, Any] | None) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for folder, extensions in (raw or {}).items():
        folder = str(folder).strip().replace("\\", "/").strip("/")
        if not folder or not isinstance(extensions, list):
            continue
        clean = sorted({normalize_extension(str(ext)) for ext in extensions if normalize_extension(str(ext))})
        if clean:
            result[folder] = clean
    return result


def default_config() -> dict[str, Any]:
    return {
        "version": CONFIG_VERSION,
        "categories": {k: list(v) for k, v in DEFAULT_CATEGORIES.items()},
        "group_by_year_month": False,
        "duplicate_mode": "duplicates_folder",
        "other_folder": DEFAULT_OTHER_FOLDER,
        "duplicates_folder": DEFAULT_DUPLICATES_FOLDER,
    }


def load_config() -> dict[str, Any]:
    config = default_config()
    path = get_config_path()
    try:
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw.get("categories"), dict):
                config["categories"] = normalize_categories(raw["categories"])
            elif isinstance(raw.get("extra_extensions"), dict):
                for folder, exts in raw["extra_extensions"].items():
                    config["categories"].setdefault(folder, [])
                    config["categories"][folder] = sorted(set(config["categories"][folder]) | set(normalize_extension(str(x)) for x in exts))
            for key in ("group_by_year_month", "duplicate_mode", "other_folder", "duplicates_folder"):
                if key in raw:
                    config[key] = raw[key]
    except (OSError, ValueError, TypeError) as exc:
        log.error("تعذّرت قراءة الإعدادات: %s", exc)
    config["group_by_year_month"] = bool(config.get("group_by_year_month", False))
    config["duplicate_mode"] = config.get("duplicate_mode") if config.get("duplicate_mode") in {"duplicates_folder", "serial"} else "duplicates_folder"
    return config


def save_config(config: dict[str, Any]) -> None:
    path = get_config_path()
    tmp = path.with_suffix(".tmp")
    clean = default_config()
    clean.update(config)
    clean["categories"] = normalize_categories(clean.get("categories"))
    clean["version"] = CONFIG_VERSION
    tmp.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def file_hash(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def unique_path(path: Path) -> Path:
    n = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({n}){path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


class Organizer:
    def __init__(self, root: Path, dry_run: bool = False):
        self.root = root.resolve()
        self.dry_run = dry_run
        self._pending: set[Path] = set()
        self._lock = threading.Lock()
        self._config_lock = threading.RLock()
        self.pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="sorter")
        self.reload_config()

    def reload_config(self) -> None:
        with self._config_lock:
            config = load_config()
            self.config = config
            self.group_by_month = bool(config["group_by_year_month"])
            self.duplicate_mode = config["duplicate_mode"]
            self.other_folder = str(config.get("other_folder") or DEFAULT_OTHER_FOLDER)
            self.duplicates_folder = str(config.get("duplicates_folder") or DEFAULT_DUPLICATES_FOLDER)
            self.categories = normalize_categories(config.get("categories"))
            self.ext_map = {ext: folder for folder, exts in self.categories.items() for ext in exts}

    def should_skip(self, path: Path) -> bool:
        try:
            return path.parent != self.root or path.name.lower() in IGNORED_NAMES or path.name.startswith("~$") or path.name.startswith(".") or path.suffix.lower() in PARTIAL_EXTENSIONS or not path.is_file()
        except OSError:
            return True

    def wait_until_ready(self, path: Path, timeout: int = 900) -> bool:
        deadline = time.monotonic() + timeout
        last_size, stable = -1, 0
        while time.monotonic() < deadline:
            try:
                size = path.stat().st_size
            except OSError:
                return False
            stable = stable + 1 if size == last_size else 0
            last_size = size
            if stable >= 2:
                return True
            time.sleep(1.0)
        log.warning("انتهت مهلة انتظار اكتمال الملف: %s", path.name)
        return False

    def destination_for(self, path: Path) -> Path:
        with self._config_lock:
            folder = self.ext_map.get(path.suffix.lower(), self.other_folder)
            destination = self.root / folder
            if self.group_by_month:
                destination /= datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m")
            return destination

    def resolve_target(self, src: Path, destination: Path) -> Path:
        target = destination / src.name
        if not target.exists():
            return target
        try:
            identical = target.stat().st_size == src.stat().st_size and file_hash(target) == file_hash(src)
        except OSError:
            identical = False
        with self._config_lock:
            mode = self.duplicate_mode
        if identical and mode == "duplicates_folder":
            return unique_path(self.root / self.duplicates_folder / src.name)
        return unique_path(target)

    def process(self, path: Path) -> None:
        try:
            if self.should_skip(path) or not self.wait_until_ready(path):
                return
            target = self.resolve_target(path, self.destination_for(path))
            relative = target.relative_to(self.root)
            if self.dry_run:
                log.info("[معاينة] %s -> %s", path.name, relative)
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            for attempt in range(1, 6):
                try:
                    move(str(path), str(target))
                    log.info("%s -> %s", path.name, relative)
                    return
                except PermissionError:
                    time.sleep(2 * attempt)
                except FileNotFoundError:
                    return
            log.error("فشل نقل الملف بعد عدة محاولات: %s", path.name)
        except Exception:
            log.exception("خطأ غير متوقع أثناء معالجة %s", path)
        finally:
            with self._lock:
                self._pending.discard(path)

    def submit(self, path: Path) -> None:
        if path.parent != self.root or path.suffix.lower() in PARTIAL_EXTENSIONS:
            return
        with self._lock:
            if path in self._pending:
                return
            self._pending.add(path)
        self.pool.submit(self.process, path)

    def sweep(self) -> None:
        try:
            for item in self.root.iterdir():
                if item.is_file():
                    self.submit(item)
        except OSError as exc:
            log.error("تعذّر قراءة المجلد %s: %s", self.root, exc)

    def close(self) -> None:
        self.pool.shutdown(wait=False, cancel_futures=True)


class Handler(FileSystemEventHandler):
    def __init__(self, organizer: Organizer):
        self.org = organizer

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.org.submit(Path(os.fsdecode(event.src_path)))

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.org.submit(Path(os.fsdecode(event.dest_path)))


def startup_script_path() -> Path:
    appdata = os.environ.get("APPDATA", "")
    return Path(appdata) / "Microsoft/Windows/Start Menu/Programs/Startup" / f"{APP_NAME}.vbs"


def install_startup() -> None:
    if sys.platform != "win32":
        raise RuntimeError("التشغيل التلقائي بهذه الطريقة مخصص لويندوز.")
    exe = Path(sys.executable)
    pyw = exe.with_name("pythonw.exe")
    exe = pyw if pyw.exists() else exe
    script = Path(__file__).resolve()
    target = startup_script_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    vbs = f'CreateObject("WScript.Shell").Run """{exe}"" ""{script}""", 0, False\r\n'
    target.write_text(vbs, encoding="utf-8")
    subprocess.Popen([str(exe), str(script)], creationflags=0x00000008 | 0x08000000, close_fds=True)
    print(f"تم تفعيل التشغيل التلقائي: {target}")


def uninstall_startup() -> None:
    target = startup_script_path()
    if target.exists():
        target.unlink()
        print("تم إلغاء التشغيل التلقائي.")
    else:
        print("التشغيل التلقائي غير مثبت.")


def acquire_single_instance() -> socket.socket | None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
        return sock
    except OSError:
        sock.close()
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Downloads Organizer")
    parser.add_argument("--path", type=Path)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    if args.install:
        install_startup(); return
    if args.uninstall:
        uninstall_startup(); return
    root = (args.path or get_downloads_dir()).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"المجلد غير موجود: {root}")
    organizer = Organizer(root, dry_run=args.dry_run)
    if args.once:
        log.info("فرز لمرة واحدة: %s", root)
        organizer.sweep(); organizer.pool.shutdown(wait=True); return
    guard = acquire_single_instance()
    if guard is None:
        raise SystemExit("نسخة أخرى تعمل بالفعل.")
    observer = Observer()
    observer.schedule(Handler(organizer), str(root), recursive=False)
    observer.start()
    log.info("بدء المراقبة: %s", root)
    organizer.sweep()
    try:
        while observer.is_alive():
            observer.join(timeout=1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop(); observer.join(); organizer.close(); guard.close()


if __name__ == "__main__":
    main()
