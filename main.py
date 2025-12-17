import discord
import requests
import calendar
import datetime
import json
import os
from dotenv import load_dotenv


load_dotenv()

CM_FRACTALS = ["kinfall", "nightmare", "sunqua_peak", "silent_surf", "lonely_tower"]
ANNOYING_FRACTALS = ["aquatic_ruins", "sirens_reef", "deepstone", "twilight_oasis"]


def load_data(category: str) -> dict:
    """
    Loads the provided data category into a dict.

    :param category: The category to load. Corresponds to a json file in data/.
    :type category: str
    :return: The loaded data.
    :rtype: dict
    """

    base_folder = os.path.dirname(__file__)
    with open(os.path.join(base_folder, "data", category + ".json"), "r") as datafile:
        return json.load(datafile)


DAILY_FRACTALS = load_data("dailies")["dailies"]
FRACTALS = load_data("fractals")["fractal_details"]
DAILY_INSTABILITIES = load_data("instabilities")["instabilities"]
INSTABILITIES = load_data("instabilities")["instability_details"]


def main():
    hook = discord.SyncWebhook.from_url(
        "https://discord.com/api/webhooks/1450618571905564783/ao40XXQcOcQ1if_XRG3-vR7bvDplFAfKPNVI19h-LSfepZVRr5Z2deCR_DseiDZsWF5q"
    )

    msg = build_daily_message("1342934440778928148")
    hook.send(content=msg)


def build_daily_message(role_id: str) -> str:
    daily_msg = f"<@&{role_id}> Daily Fractal Poke!"

    daily_joke = fetchJoke()
    daily_msg += f"\n\n**Joke of the day:**\n{daily_joke}"

    cms_that_are_daily, fractals_with_npng, daily_annoying = get_daily_info()
    daily_msg += "\n\n**Fractals:**"
    if any(cms_that_are_daily):
        daily_msg += f"\n{enunciate(cms_that_are_daily)} {'are' if len(cms_that_are_daily) > 1 else 'is'} daily today!"
    else:
        daily_msg += "\nNo CMs are daily today."
    if any(daily_annoying):
        daily_msg += f"\nUnfortunatly, {enunciate(daily_annoying)} {'are' if len(daily_annoying) > 1 else 'is'}{' also' if any(cms_that_are_daily) else ''} daily."
    if any(fractals_with_npng):
        daily_msg += f"\n{enunciate(fractals_with_npng)} {'have' if len(fractals_with_npng) > 1 else 'has'} No Pain, No Gain."
    else:
        daily_msg += "\nNo fractals have No Pain, No Gain today!"
    daily_msg += "\nReact with ✅ if you can make it today or ❌ if you skip."

    return daily_msg


def fetchJoke() -> str:
    api = requests.get(
        "https://icanhazdadjoke.com", headers={"Accept": "application/json"}
    )  # Make request to the api
    content = api.json()  # transform JSON into a python object
    return content["joke"]


def get_daily_info():
    daily_index = get_daily_index()

    daily_fractals = get_daily_fractals(daily_index)
    daily_instabs = get_daily_instabilities(
        daily_index, list(set(daily_fractals + CM_FRACTALS))
    )

    cms_that_are_daily = [
        get_full_fractal_name(cm) for cm in CM_FRACTALS if cm in daily_fractals
    ]
    fractals_with_npng = [
        get_full_fractal_name(frac)
        for frac, instabs in daily_instabs.items()
        if "No Pain, No Gain" in instabs
    ]
    daily_annoying = [
        get_full_fractal_name(frac)
        for frac in daily_fractals
        if frac in ANNOYING_FRACTALS
    ]

    return cms_that_are_daily, fractals_with_npng, daily_annoying


def get_daily_fractals(daily_index: int) -> list[str]:
    """
    Gets the list of daily fractals.

    :param daily_index: The index of the daily fractals. A number between 0 and 14.
    :type daily_index: int
    :return: Description
    :rtype: list[str]
    """

    return DAILY_FRACTALS[daily_index % 15]


def get_daily_instabilities(daily_index: int, daily_fractals: list[str]):
    daily_instabs: dict[str, list[str]] = {}

    for fractal_name in daily_fractals:
        t4_scale = str(FRACTALS[fractal_name]["scales"][-1])
        instabs = DAILY_INSTABILITIES[t4_scale][daily_index]
        instabs = [INSTABILITIES[instab]["name"]["en"] for instab in instabs]
        daily_instabs[fractal_name] = instabs

    return daily_instabs


def get_daily_index() -> int:
    """
    Gets the corresponding date in the daily index as a number modulo 15.

    :return: Index of the daily rotation
    :rtype: int
    """

    now = datetime.datetime.now()
    year_start = datetime.date(now.year, 1, 1)

    time_passed: datetime.timedelta = now.date() - year_start
    total_days_passed = time_passed.days

    # Adjusting for leap year.
    # This index is the same for both leap and non leap years.
    #  This means it will skip the index value 59 (February 29) in non leap years.
    is_leap_year: bool = calendar.isleap(now.year)
    if not is_leap_year and total_days_passed > 58:
        total_days_passed += 1

    return total_days_passed + 1


def get_full_fractal_name(fractal: str) -> str:
    return FRACTALS[fractal]["name"]["en"]


def enunciate(list: list[str]) -> str:
    """Turns a list ['a', 'b', 'c'] into a string 'a, b and c'"""

    if len(list) == 1:
        return list[0]

    string = ", ".join(list[:-1])
    string += f" and {list[-1]}"

    return string


if __name__ == "__main__":
    main()
