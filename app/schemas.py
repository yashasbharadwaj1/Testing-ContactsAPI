
from pydantic import BaseModel, ConfigDict


class ContactBase(BaseModel):
    name: str
    email: str
    phone: str


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class Contact(ContactBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
