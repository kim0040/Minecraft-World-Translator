"""User-visible PomiTranslate safety copy. Surfaces must include these sentences."""

PRODUCT_NAME = "PomiTranslate"
SUBTITLE = "World Translator for Minecraft"

UNOFFICIAL_NOTICE = (
    "NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT."
)
BACKUP_WARNING = "Back up your world before translating. PomiTranslate writes to the world files you select."
API_WARNING = (
    "Text you choose to translate is sent to the API provider you select and may incur charges."
)

FIRST_LAUNCH = "\n".join(
    [
        f"{PRODUCT_NAME}",
        SUBTITLE,
        UNOFFICIAL_NOTICE,
        BACKUP_WARNING,
        API_WARNING,
    ]
)

PRE_TRANSLATE = "\n".join(
    [
        f"{PRODUCT_NAME} is ready to translate this world.",
        SUBTITLE,
        UNOFFICIAL_NOTICE,
        BACKUP_WARNING,
        API_WARNING,
    ]
)

ABOUT = "\n".join(
    [
        PRODUCT_NAME,
        SUBTITLE,
        UNOFFICIAL_NOTICE,
        BACKUP_WARNING,
        API_WARNING,
        "PomiTranslate has no purchase, subscription, or in-app payment.",
    ]
)


def payload() -> dict[str, str]:
    return {
        "productName": PRODUCT_NAME,
        "subtitle": SUBTITLE,
        "firstLaunch": FIRST_LAUNCH,
        "preTranslate": PRE_TRANSLATE,
        "about": ABOUT,
        "unofficialNotice": UNOFFICIAL_NOTICE,
        "backupWarning": BACKUP_WARNING,
        "apiWarning": API_WARNING,
    }
