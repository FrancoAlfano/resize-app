from PIL import Image
from filter import apply_filter
import io


def process_image(data, output_size, is_exact=False, filter=None, alpha=None):
    image = Image.open(io.BytesIO(data))
    if not is_exact:
        original_aspect_ratio = image.width / image.height
        target_width, target_height = output_size
        target_aspect_ratio = target_width / target_height

        if target_aspect_ratio > original_aspect_ratio:
            new_height = target_height
            new_width = int(new_height * original_aspect_ratio)
        else:
            new_width = target_width
            new_height = int(new_width / original_aspect_ratio)

        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    else:
        resized_image = image.resize(output_size, Image.LANCZOS)

    if filter != 'none':
        resized_image = apply_filter(resized_image, filter, alpha)

    buffer = io.BytesIO()
    format = image.format if image.format else 'JPEG'
    resized_image.save(buffer, format)

    return buffer.getvalue()