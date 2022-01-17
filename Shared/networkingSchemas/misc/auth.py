from Shared.networkingSchemas.base import CustomBaseModel


class BackendUserModel(CustomBaseModel):
    user_name: str
    allowed_scopes: list[str]
    has_write_permission: bool
    has_read_permission: bool
    disabled: bool

    class Config:
        orm_mode = True


class Token(CustomBaseModel):
    access_token: str
    token_type: str


class BungieRegistrationInput(CustomBaseModel):
    code: str
    state: str


class BungieTokenInput(CustomBaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    membership_id: str
    state: str


class BungieTokenOutput(CustomBaseModel):
    bungie_name: str
