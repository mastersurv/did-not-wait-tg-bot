from keyboards.inline.client import time_intervals

database_time_intervals = {
    1: "с 9:00 до 21:00",
    2: "с 9:00 до 13:00",
    3: "с 13:00 до 17:00",
    4: "с 17:00 до 21:00",
    5: "с 9:00 до 13:00, с 13:00 до 17:00",
    6: "с 9:00 до 13:00, с 17:00 до 21:00",
    7: "с 13:00 до 17:00, с 17:00 до 21:00",
}


def get_interval_from_choices(choices: list[str]) -> int:
    if len(choices) == 1:
        if choices[0] == time_intervals[0]:
            return 2
        if choices[0] == time_intervals[1]:
            return 3
        if choices[0] == time_intervals[2]:
            return 4
    if len(choices) == 2:
        if time_intervals[0] in choices and time_intervals[1] in choices:
            return 5
        if time_intervals[0] in choices and time_intervals[2] in choices:
            return 6
        if time_intervals[1] in choices and time_intervals[2] in choices:
            return 7
    return 1