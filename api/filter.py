from PIL import ImageEnhance, Image

def apply_filter(image, color, alpha):
    alpha = float(alpha) / 10

    if image.mode == 'RGBA':
        image_rgb, image_alpha = image.convert('RGB'), image.split()[3]
    else:
        image_rgb = image.convert('RGB')

    original = image_rgb.copy()

    if color == 'black and white':
        enhancer = ImageEnhance.Color(image_rgb)
        filtered_image = enhancer.enhance(0)
    else:
        red, green, blue = image_rgb.split()
        if color == 'red':
            green = green.point(lambda i: 0)
            blue = blue.point(lambda i: 0)
        elif color == 'green':
            red = red.point(lambda i: 0)
            blue = blue.point(lambda i: 0)
        elif color == 'blue':
            red = red.point(lambda i: 0)
            green = green.point(lambda i: 0)

        filtered_image = Image.merge("RGB", (red, green, blue))

    result_image = Image.blend(original, filtered_image, alpha)

    if image.mode == 'RGBA':
        result_image = Image.merge("RGBA", (*result_image.split(), image_alpha))

    return result_image

