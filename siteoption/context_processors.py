from siteoption.constants import SITE_NAME
from siteoption.utils.functions import get_option


def site_options(request):
    """Add site options (e.g. SiteName) to template context."""
    return {
        "site_name": get_option(SITE_NAME, default="siteName"),
    }
