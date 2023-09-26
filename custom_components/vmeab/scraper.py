import requests
from bs4 import BeautifulSoup


def vmeab_scrape(StreetName, City):
    URL = "https://www.vmeab.se/tjanster/avfall--atervinning/min-sophamtning/"
    HOSTURL = "https://www.vmeab.se"

    # Vi skapar en session för att kunna skicka vidare cookies vi får ifrån VMEAB i våran post.
    vmeab = requests.Session()

    page = vmeab.get(URL)

    # För att kunna söka i sidan så använder vi BeautifulSoup
    soup = BeautifulSoup(page.content, "html.parser")

    # Hittar formen för sökningen. Vi måste plocka ur en dold nyckel där med mera.
    form = soup.find(id="wasteDisposalNextPickupForm")

    # VMEAB har skapat en dold input som innehåller en nyckel som vi måste skicka i våran post.
    # Detta är för att hämta den.
    __RequestVerificationToken = form.find(type="hidden")["value"]

    # Ifall att de ändrar var API't ligger så hämtar vi den här varje gång.
    formAction = form["action"]
    formURL = HOSTURL + formAction

    # Detta är våran data för våran post
    data = {
        "__RequestVerificationToken": __RequestVerificationToken,
        "StreetAddress": StreetName,
        "City": City,
    }

    # Nu har vi all info för att göra våran request i form av en post
    post = vmeab.post(formURL, data=data, cookies=vmeab.cookies)

    # Använder BeautifulSoup för att kunna söka i resultatet.
    soup = BeautifulSoup(post.content, "html.parser")

    # Varje tunna ligger som en egen div med class waste-disposal-search-result-item
    allaTunnor = soup.find_all("div", class_="waste-disposal-search-result-item")

    tunnor = {}  # Använder json för att spara sakerna i.

    for tunna in allaTunnor:
        soup = BeautifulSoup(tunna.prettify(), "html.parser")

        # Lägger in varje träff som ett nytt inlägg i form av json
        tunnor[soup.find("h4").get_text().strip().split(",")[0]] = (
            soup.find("p").get_text().strip().split(": ")[1]
        )

    return tunnor  # Retrun i form av json


# print(vmeab_scrape("Flundregatan 29", "Västervik"))
