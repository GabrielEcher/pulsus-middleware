from fastapi import APIRouter
from services.devices_logins import get_devices_logins, request_devices_data, get_merged_devices_info
router = APIRouter(prefix="/devices", tags=["Devices"])

@router.get("")
async def get_devices():
    return await get_merged_devices_info()