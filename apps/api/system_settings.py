import json
from dataclasses import asdict, dataclass
from threading import Lock

from database import DATA_DIR

DEFAULT_PASSWORD = "123qwe"
DEFAULT_EDGE_TTS_RATE = 1.0
SETTINGS_FILE = DATA_DIR / "system_settings.json"


@dataclass(frozen=True)
class SystemSettings:
    default_password: str = DEFAULT_PASSWORD
    edge_tts_rate: float = DEFAULT_EDGE_TTS_RATE


class SystemSettingsManager:
    _instance = None
    _instance_lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._settings = None
                    cls._instance._settings_lock = Lock()
        return cls._instance

    def get(self) -> SystemSettings:
        if self._settings is None:
            with self._settings_lock:
                if self._settings is None:
                    self._settings = self._load()
        return self._settings

    def update(self, default_password: str, edge_tts_rate: float) -> SystemSettings:
        settings = self._normalize(default_password, edge_tts_rate)
        with self._settings_lock:
            self._write(settings)
            self._settings = settings
        return settings

    def _load(self) -> SystemSettings:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not SETTINGS_FILE.exists():
            settings = SystemSettings()
            self._write(settings)
            return settings

        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        default_password = payload.get("default_password", DEFAULT_PASSWORD)
        edge_tts_rate = payload.get("edge_tts_rate", DEFAULT_EDGE_TTS_RATE)
        return self._normalize(default_password, edge_tts_rate)

    def _write(self, settings: SystemSettings) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _normalize(self, default_password: str, edge_tts_rate: float) -> SystemSettings:
        password = default_password.strip()
        if not password:
            raise ValueError("默认密码不能为空")

        rate = float(edge_tts_rate)
        if rate < 0 or rate > 1:
            raise ValueError("edge-tts 音频语速必须在 0 到 1 之间")

        return SystemSettings(default_password=password, edge_tts_rate=rate)


_manager = SystemSettingsManager()


def get_system_settings() -> SystemSettings:
    return _manager.get()


def update_system_settings(default_password: str, edge_tts_rate: float) -> SystemSettings:
    return _manager.update(default_password, edge_tts_rate)


def get_edge_tts_rate_string() -> str:
    percent = round((get_system_settings().edge_tts_rate - 1) * 100)
    return f"{percent:+d}%"
