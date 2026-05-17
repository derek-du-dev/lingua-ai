from fastapi import APIRouter, Depends

from auth import require_admin
from models import User
from schemas import SystemSettingsPublic, SystemSettingsUpdate
from system_settings import SystemSettings, get_system_settings, update_system_settings

router = APIRouter(prefix="/system-settings", tags=["system-settings"])


def to_system_settings_public(settings: SystemSettings) -> SystemSettingsPublic:
    return SystemSettingsPublic(
        default_password=settings.default_password,
        edge_tts_rate=settings.edge_tts_rate,
    )


@router.get("/", response_model=SystemSettingsPublic, include_in_schema=False)
@router.get("", response_model=SystemSettingsPublic)
def read_system_settings(_admin: User = Depends(require_admin)) -> SystemSettingsPublic:
    return to_system_settings_public(get_system_settings())


@router.put("", response_model=SystemSettingsPublic)
def save_system_settings(
    payload: SystemSettingsUpdate,
    _admin: User = Depends(require_admin),
) -> SystemSettingsPublic:
    settings = update_system_settings(payload.default_password, payload.edge_tts_rate)
    return to_system_settings_public(settings)
