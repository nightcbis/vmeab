from datetime import datetime, timedelta


def manadsNummer(manad):
    return datetime.strptime(manad, "%B").month


def nuvarandeManad():
    now = datetime.now()
    return int(str(now).split("-")[1])


def nuvarandeAr():
    now = datetime.now()
    return int(str(now).split("-")[0])


def svenskaTillEngelska(svenska):
    engelska = {
        "januari": "january",
        "january": "januari",
        "februari": "february",
        "february": "februari",
        "mars": "march",
        "march": "mars",
        "april": "april",
        "maj": "may",
        "may": "maj",
        "juni": "june",
        "june": "juni",
        "juli": "july",
        "july": "juli",
        "augusti": "august",
        "august": "augusti",
        "september": "september",
        "oktober": "october",
        "october": "oktober",
        "november": "november",
        "december": "december",
        "måndag": "monday",
        "tisdag": "tuesday",
        "onsdag": "wednesday",
        "torsdag": "thursday",
        "fredag": "friday",
        "lördag": "saturday",
        "söndag": "sunday",
        "monday": "måndag",
        "tuesday": "tisdag",
        "wednesday": "onsdag",
        "thursday": "torsdag",
        "friday": "fredag",
        "saturday": "lördag",
        "sunday": "söndag"
    }

    return engelska[svenska]


def dagarTillDatum(datum):
    now = datetime.now()

    # Vi lägger hämtningen till precis innan midnatt för diff-räkningen blir lättare.
    datumDatetime = omvandlaTillDatetime(datum) + timedelta(
        hours=23, minutes=59, seconds=59
    )

    try:
        diff = int(str(datumDatetime - now).split(" ")[0])  # Mer än 1 dag skillnad.
    except:
        diff = 0  # Idag. Så mindre än 1 dag skillnad.

    return diff


def omvandlaTillDatetime(tunna):
    datum = tunna.split(" ")[1]
    manad = svenskaTillEngelska(tunna.split(" ")[2])
    manadNr = manadsNummer(manad)
    ar = 0

    nuManad = nuvarandeManad()
    if nuManad > int(manadNr):
        ar = nuvarandeAr() + 1  # Händer nästa år?
    else:
        ar = nuvarandeAr()  # Händer i år

    datum = str(ar) + " " + datum + " " + manad

    dt = datetime.strptime(datum, "%Y %d %B")

    return dt
