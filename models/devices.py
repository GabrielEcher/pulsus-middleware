from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, RootModel


class User(BaseModel):
    first_name: str
    last_name: Any
    identifier: str
    email: Any
    exchange_user_name: Any


class Devices(BaseModel):
    id: int
    identifier: str
    status: str
    manufacturer: str
    model: str
    platform: str
    os_version: str
    serial_number: str
    mac_address: str
    updated_at: str
    activated_at: str
    last_contact_at: str
    group: str
    group_pin: str
    group_name: str
    telephone_number_by_sms: Any
    wifi: bool
    bluetooth: bool
    gps: bool
    battery_level: int
    is_charging: bool
    total_memory: int
    available_memory: int
    total_storage: int
    available_storage: int
    default_launcher: bool
    battery_temperature: int
    ssid: str
    frequency: int
    ip_address: str
    gateway: str
    imeis: Optional[List[Any]] = None
    custom_fields: Any
    user: User


class Model(BaseModel):
    RootModel: List[Devices]
