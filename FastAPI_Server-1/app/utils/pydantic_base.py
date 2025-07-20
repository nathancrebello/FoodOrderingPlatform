from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    class Config:
        model_config = ConfigDict(
            populate_by_name=True,
            json_serializers={
                datetime: lambda d: d.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            from_attributes=True,
        )
