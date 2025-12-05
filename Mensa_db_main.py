import MensaHTWGWebScrapping
import datetime

def main():
    currentDate = datetime.datetime.today().weekday()
    if currentDate != 5 and currentDate != 6:
        MensaHTWGWebScrapping.webScrappingUni()
    elif currentDate == 5:
        print("Heute ist es Samstag, deswegen werden die Daten nicht übertragen")
    elif currentDate == 6:
        print("Heute ist es Sonntag, deswegen werden die Daten nicht übertragen")

if __name__ == "__main__":
    main()
