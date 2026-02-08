"""通知ドメインの値オブジェクト定義。

通知チャネルの種別を定義する。
ジョブドメインとは独立した関心事として管理する。
"""

from enum import Enum


class NotificationChannel(Enum):
    """通知チャネルを表す列挙型。

    ジョブ完了・失敗時にどのチャネルで通知するかを指定する。
    """

    NONE = "NONE"
    EMAIL = "EMAIL"
    DISCORD = "DISCORD"
