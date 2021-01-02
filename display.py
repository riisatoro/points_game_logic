from types import EMPTY, SYSTEM, RED, BLUE

def display_ascii_field(field, colors):
    chars = {
        colors[0]: "&",
        colors[1]: "#",
        EMPTY: "○",
        SYSTEM: ".",

        "CAPTURED": "©",
        "EMPTY_CAPTURED": ".",
    }

    for row in field:
        for i in range(3):
            for col in row:
                if i == 0:
                    # display top lines
                    pass
                elif i == 1:
                    # display side lines and point
                    if col.captured:
                        if col.color == EMPTY:
                            print(chars["EMPTY_CAPTURED"], end=" ")
                        else:
                            print(chars["CAPTURED"], end=" ")
                    else:
                        print(chars[col.color], end=" ")
                else:
                    # display lines below
                    pass
        print("")