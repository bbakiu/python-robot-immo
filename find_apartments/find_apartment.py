import requests
import logging
import os
import logging
from hashlib import sha3_512
from pymongo import MongoClient
import telegram
import re
from tinydb import TinyDB, Query

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
SECRET = os.environ['SECRET_KEY']
IMMO_SEARCH_URL =  os.environ['IMMO_SEARCH_URL']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = telegram.Bot(token=BOT_TOKEN)
tinydb = TinyDB('db.json')

def add_to_database(hash_obj):
    existing = check_if_exists_in_database(hash_obj)
    if (len(existing) == 0):
        tinydb.insert(hash_obj)

def check_if_exists_in_database(hash_obj):
    Apartment = Query()
    db_obj = tinydb.search(Apartment.hash == hash_obj['hash'])
    return db_obj
    
def get_all_hashes_in_database():
    hashes = tinydb.all()
    return hashes

def push_notification(text):
    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

def get_immoscout_data(apartment):
    title = re.sub('[^a-zA-Z0-9.\d\s]+', '', apartment['title'])
    address = re.sub('[^a-zA-Z0-9.\d\s]+', '', apartment['address']['description']['text'])
    size = apartment['livingSpace']
    price_warm = apartment['calculatedPrice']['value']
    text = f"Apartment: {title} - Address: {address} - Size:{size} m2 - Price (warm): {price_warm} EUR -  - [https://www.immobilienscout24.de/expose/{apartment['@id']}](https://www.immobilienscout24.de/expose/{apartment['@id']})"
    return text

def search_immobilienscout(q):
    if verify_secret(q):
        logger.info("Searching Immoscout")
        try:
            apartments = requests.post(IMMO_SEARCH_URL).json()['searchResponseModel']['resultlist.resultlist']['resultlistEntries'][0]['resultlistEntry']
        except:
            logger.warn("Could not read any listed appartement")
            apartments = []
        
        unseen_apartments = []
        seen_apartments = get_all_hashes_in_database()

        # public_companies = ["WBM", "HOWOGE", "GESOBAU", "GEWOBAG", "STADT UND LAND", "WOBEGE"]

        if not type(apartments) is list:
            apartments = [apartments]

        for apartment in apartments:
            hash_obj = {"hash": apartment['@id']}
            
            if not hash_obj in seen_apartments:
                unseen_apartments.append(apartment)

        for unseen_apartment in unseen_apartments:
            apartment = unseen_apartment['resultlist.realEstate']
            text = get_immoscout_data(apartment)
            
            # If you are interested only in public companies uncomment the next 2 line.
            # is_public = False
            
            # if 'realtorCompanyName' in apartment:
            #     company = apartment['realtorCompanyName'].upper()
            #     for c in public_companies:
            #         if company.find(c) != -1:
            #             is_public = True
            
            # if is_public:
                # push_notification(data)
            
            # If you are interested only in public companies comment out the next line.
            push_notification(text)
            add_to_database({"hash": apartment['@id']})

        return {
            'status' : 'SUCESS',
        }
    else:
        return {
            'status' : 'SUCCESS'
        }

def verify_secret(q):
    return True