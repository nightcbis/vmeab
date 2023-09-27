from datetime import datetime


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
    }

    return engelska[svenska]


def dagarTillDatum(datum):
    now = datetime.now()
    datumDatetime = omvandlaTillDatetime(datum)

    diff = int(str(datumDatetime - now).split(" ")[0]) + 1
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
