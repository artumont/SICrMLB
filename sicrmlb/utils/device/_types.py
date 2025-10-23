from pydantic import BaseModel


class DeviceMetrics(BaseModel):
    height: int
    width: int
