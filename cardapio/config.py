from pydantic_settings import BaseSettings, SettingsConfigDict


class CardapioSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CARDAPIO_",
        env_file=".env",
        extra="ignore",
    )

    admin_token: str = ""
    db_path: str = "data/cardapio.sqlite"
    public_base_url: str = "http://127.0.0.1:8001"
    pix_key: str = ""
    pix_name: str = ""
    operator_name: str = "Cardápio Pix"
    trial_days: int = 14
    default_price_cents: int = 3900
    cookie_secure: bool = False

    @property
    def public_base(self) -> str:
        return self.public_base_url.rstrip("/")
