import uuid

def generate_sku(product, variant):
    parts = []

    # Category
    if product.category and product.category.category_name:
        parts.append(product.category.category_name[:3].upper())

    # Product type
    if product.product_type:
        parts.append(product.product_type[:3].upper())

    # Color (ignore HEX)
    if variant.color and not variant.color.startswith('#'):
        parts.append(variant.color[:3].upper())

    # Size
    if variant.size:
        parts.append(variant.size.upper())

    # Random part (safer length)
    random_part = uuid.uuid4().hex[:6].upper()

    return 'OUT-' + '-'.join(parts) + '-' + random_part