def construct_options(options, zero = None) -> str:
    result = ""
    count = 0
    for option in options:
        count += 1
        result += f"[{count}] {option}\n"
    if zero is not None:
        result += f"[0] {zero}"
    return result