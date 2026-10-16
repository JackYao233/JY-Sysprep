from dataclasses import dataclass
from typing import Optional


@dataclass
class SysprepConfig:
    test_only: bool = True
    mode: str = "audit"
    completion_action: str = "shutdown"
    computer_name: str = "*"
    time_zone: str = "China Standard Time"
    input_locale: str = "zh-CN"
    system_locale: str = "zh-CN"
    ui_language: str = "zh-CN"
    user_locale: str = "zh-CN"
    hide_eula: bool = True
    hide_wireless: bool = True
    hide_online_accounts: bool = False
    hide_local_account_screen: bool = False
    protect_your_pc: int = 3
    owner: str = ""
    organization: str = ""
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None
    auto_logon: bool = False
    auto_logon_count: int = 1

    def uses_local_account(self):
        return bool(self.admin_username and self.admin_password)
