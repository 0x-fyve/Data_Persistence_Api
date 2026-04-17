def get_age_group(age):
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"


def get_top_country(countries):
    if not countries:
        return None, None

    top = max(countries, key=lambda x: x["probability"])
    return top["country_id"], top["probability"] 