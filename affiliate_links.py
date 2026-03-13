from config import AFFILIATE_TAG, AMAZON_DOMAIN

def generate_affiliate_link(asin):
    return f"{AMAZON_DOMAIN}/dp/{asin}?tag={AFFILIATE_TAG}"
