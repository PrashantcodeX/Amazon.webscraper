def parse_int(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        length = len(s)
        start = 0
        while start < length and not s[start].isdigit():
            start += 1

        end = start + 1
        while end < length and s[end].isdigit():
            end += 1

        return int(s[start:end + 1])


def parse_float(s: str) -> float:
    try:
        return float(s)
    except ValueError:
        length = len(s)
        start = 0
        while start < length and not s[start].isdigit():
            start += 1

        end = start + 1
        dot = False
        while end < length and (s[end].isdigit() or s[end] == '.'):
            if dot and s[end] == '.':
                break
            elif s[end] == '.':
                dot = True
            end += 1

        return float(s[start:end + 1])
