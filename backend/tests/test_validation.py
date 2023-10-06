from services.validation import validate_photo, infer_image


def test_infer_image(get_spoofing_image):
    predictions = infer_image(get_spoofing_image)
    assert 0 <= predictions <= 1


def test_validate_photo(get_spoofing_image):
    is_valid = validate_photo(get_spoofing_image)
    assert type(is_valid) == bool
