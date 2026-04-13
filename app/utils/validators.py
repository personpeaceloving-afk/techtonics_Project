def validate_list(data):
    if not isinstance(data, list):
        raise ValueError("Invalid response format")