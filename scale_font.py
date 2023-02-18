import json
import os


def scale_font(base_font_name, scaled_font_name, scale):
    """Scaled the passed in font by the passed in scale.

    Args:
        base_font_name: file name of the base font
        scaled_font_name: file name of the scaled fount
        scale: integer scale value

    Returns:
        none
    """
    with open(base_font_name) as file_obj:
        original_font = json.load(file_obj)
    scaled_font = original_font
    scaled_font['name'] = os.path.splitext(scaled_font_name)[0]
    scaled_font['lineHeight'] = original_font['lineHeight'] * scale
    scaled_font['description'] = f'{os.path.splitext(base_font_name)[0]} scaled to {scale}'
    for char_val, definition in original_font['glyphs'].items():
        scaled_definition = []
        for row in definition['pixels']:
            scaled_row = []
            for col in row:
                scaled_col = [col] * scale
                scaled_row.extend(scaled_col)
            scaled_definition.extend([scaled_row] * scale)
        scaled_font['glyphs'][char_val]['offset'] *= scale
        scaled_font['glyphs'][char_val]['pixels'] = scaled_definition
    with open(scaled_font_name, 'w') as file_obj:
        json.dump(scaled_font, file_obj, indent=4)
    return 0


def main():
    """Main entry point.

    Returns:
        0 on success (always)
    """
    scale_font('pixel-font-7x5.json', 'pixel-font-14x10.json', 2)
    return 0


if __name__ == "__main__":
    exit(main())