from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import sys
import requests
import os
import json

# load the environment variables
load_dotenv()

# classes used to extract the bus lines
CLASSES = ["table4", "table5"]

# get the current time in HH:MM format
NOW = datetime.now().time().strftime("%H:%M")

# dictionary containing the route information
INFO = {
        0: {
            "URL": os.getenv("INFO_0_URL"),
            "Departure": os.getenv("INFO_0_DEPARTURE"),
            "Destination": os.getenv("INFO_0_DESTINATION"),
            "Time-to-Arrive": int(os.getenv("INFO_0_TIME_TO_ARRIVE")),
            "buses": json.loads(os.getenv("INFO_0_BUSES"))
        },
        
        1: {
            "URL": os.getenv("INFO_1_URL"),
            "Departure": os.getenv("INFO_1_DEPARTURE"),
            "Destination": os.getenv("INFO_1_DESTINATION"),
            "Time-to-Arrive": int(os.getenv("INFO_1_TIME_TO_ARRIVE")),
            "buses": json.loads(os.getenv("INFO_1_BUSES"))
        }
}

# function to get the route information
def getRouteInfo(arg1: int) -> tuple:
    url = INFO[arg1]["URL"]
    departure = INFO[arg1]["Departure"]
    destination = INFO[arg1]["Destination"]
    TTA = INFO[arg1]["Time-to-Arrive"]
    buses = INFO[arg1]["buses"]

    return url, departure, destination, TTA, buses


# function to extract the bus line, track and arrival time
def getBusInfo(card: BeautifulSoup) -> tuple:
    busLine = card.find_all("b")[0].text
    time = card.find_all("b")[2].text
    
    track = card.find_all("i")[0].text
    if "Schedulato" in track: track = "schedulato"
    elif "Tempo Reale" in track: track = "tempo reale"
    else: "N/A"

    return busLine, track, time


# function to calculate the arrival time, the time difference and the early arrival
def getTimes(time: str, TTA: int) -> tuple:
    arrival = datetime.strptime(time, "%H:%M").time().strftime("%H:%M")
    
    # get the time difference in minutes between the current time and the arrival time
    delta = datetime.strptime(arrival, "%H:%M") - datetime.strptime(NOW, "%H:%M")
    delta = int(delta.total_seconds() // 60)
    
    # calculate the time difference between the arrival time and the time-to-arrive
    early = delta - TTA

    return arrival, delta, early 


def getRunInfo(early: int) -> str:
    if early < -3: return "🔵"      # You arrive more than 3 minutes after the bus has passed
    elif early <= 0: return "🔴"    # You arrive while the bus is passing or it may have already passed
    elif early <= 2: return "🟠"    # You arrive 1-2 minutes before the bus passes
    elif early <= 4: return "🟡"    # You arrive 3-4 minutes before the bus passes
    else: return "🟢"               # You arrive more than 5 minutes before the bus passes



def main(arg1: int):
    url, departure, destination, TTA, buses = getRouteInfo(arg1)
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    cards = soup.find_all(class_=CLASSES)

    print(f"{departure} ➜ {destination}\n")
    noBus = True    # flag to check if there are no buses for the destination

    # extract cards containing the bus of interest
    for card in cards:
        if card.find("b").text in buses:
            noBus = False
            busLine, track, time = getBusInfo(card)
            arrival, delta, early = getTimes(time, TTA)
            info = getRunInfo(early)

            print(f"🚍 Linea {busLine}")
            print(f"🚏 In arrivo alle {arrival}, {track}")
            print(f"{info} Alla fermata tra {delta} minuti\n")

    if noBus:
        print("🚫 Nessun autobus trovato per questa destinazione.")


arg1 = int(sys.argv[1])
main(arg1)