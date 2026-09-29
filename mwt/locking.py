"""Cross-process world write lock shared by the CLI and desktop sidecar."""

from __future__ import annotations

import json
import os
import socket
import time
import uuid
from pathlib import Path


class WorldWriteLocked(RuntimeError):
    pass


class MinecraftWorldInUse(RuntimeError):
    pass


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class WorldWriteLock:
    def __init__(self, world_dir: Path) -> None:
        self.world_dir = world_dir.resolve()
        self.path = self.world_dir / ".pomi-translate" / "write.lock"
        self.token = uuid.uuid4().hex
        self.acquired = False

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "version": 1,
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "createdAt": time.time(),
            "token": self.token,
        }
        encoded = json.dumps(document).encode("utf-8")
        for attempt in range(2):
            try:
                descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                if attempt or not self._remove_stale_lock():
                    raise WorldWriteLocked("Another PomiTranslate write operation is using this world")
                continue
            try:
                os.write(descriptor, encoded)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            self.acquired = True
            return
        raise WorldWriteLocked("Could not acquire the world write lock")

    def _remove_stale_lock(self) -> bool:
        try:
            existing = json.loads(self.path.read_text(encoding="utf-8"))
            same_host = existing.get("host") == socket.gethostname()
            pid = int(existing.get("pid", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return False
        if not same_host or _pid_is_alive(pid):
            return False
        try:
            self.path.unlink()
        except OSError:
            return False
        return True

    def release(self) -> None:
        if not self.acquired:
            return
        try:
            existing = json.loads(self.path.read_text(encoding="utf-8"))
            if existing.get("token") == self.token:
                self.path.unlink(missing_ok=True)
        except (OSError, json.JSONDecodeError):
            pass
        self.acquired = False


class MinecraftSessionLocks:
    """Hold existing Java Edition session.lock files for the full write operation."""

    def __init__(self, world_dir: Path) -> None:
        self.world_dir = world_dir.resolve()
        self._handles: list[object] = []

    def _world_roots(self) -> list[Path]:
        if (self.world_dir / "level.dat").is_file():
            return [self.world_dir]
        try:
            return sorted(
                path for path in self.world_dir.iterdir()
                if path.is_dir() and (path / "level.dat").is_file()
            )
        except OSError:
            return []

    def acquire(self) -> None:
        try:
            for root in self._world_roots():
                session_path = root / "session.lock"
                if not session_path.is_file():
                    continue
                handle = session_path.open("r+b")
                try:
                    if os.name == "nt":
                        import msvcrt

                        handle.seek(0)
                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (OSError, BlockingIOError):
                    handle.close()
                    raise MinecraftWorldInUse(f"Minecraft or a server is using {root.name}")
                self._handles.append(handle)
        except Exception:
            self.release()
            raise

    def release(self) -> None:
        for handle in reversed(self._handles):
            try:
                if os.name == "nt":
                    import msvcrt

                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                handle.close()
            except OSError:
                pass
        self._handles.clear()


def world_is_in_use(world_dir: Path) -> bool:
    guard = MinecraftSessionLocks(world_dir)
    try:
        guard.acquire()
    except (MinecraftWorldInUse, OSError):
        return True
    finally:
        guard.release()
    return False
