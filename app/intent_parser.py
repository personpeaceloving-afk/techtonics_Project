def parse_intent(user_input):
    user_input = user_input.lower()

    if "get" in user_input:
        return "test_get_part.py"

    elif "post" in user_input:
        return "test_edge_cases.py"

    elif "put" in user_input:
        return "test_filters.py"

    elif "patch" in user_input:
        return "test_parts_crud.py"

    elif "delete" in user_input:
        return "test_delete_part.py"

    elif "all" in user_input:
        return "ALL"

    return None