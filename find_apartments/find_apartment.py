import requests
import logging
import os
import logging
from hashlib import sha3_512
from pymongo import MongoClient
import telegram
import re

DB_NAME = os.environ["DB_NAME"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
COLLECTION_NAME = os.environ["COLLECTION_NAME"]

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
SECRET = os.environ['SECRET']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = telegram.Bot(token=BOT_TOKEN)
IMMO_SEARCH_URL = 'https://www.immobilienscout24.de/Suche/radius/wohnung-mieten?centerofsearchaddress=Berlin;;;1276003001;Berlin;&numberofrooms=2.0-&price=-800.0&livingspace=50.0-&geocoordinates=52.51051;13.43068;5.0&enteredFrom=one_step_search'

def get_db_collection():
    client = MongoClient(
        "mongodb+srv://%s:%s@cluster0.s7mly.mongodb.net/%s?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE" % (DB_USERNAME, DB_PASSWORD, DB_NAME))
    db = client[DB_NAME]
    hashes = db[COLLECTION_NAME]
    return hashes

def add_to_database(hash_obj):
    hashes = get_db_collection()
    
    hash_id = hashes.insert_one(hash_obj).inserted_id
    logger.info(hash_id)

def add_many_to_database(hash_objs):
    hashes = get_db_collection()

    hashes.insert_many(hash_objs)

def check_if_exists_in_database(hash_obj):
    hashes = get_db_collection()

    db_obj = hashes.find_one(hash_obj)
    return db_obj
    
def get_all_hashes_in_database():
    hashes = get_db_collection()

    db_objs = hashes.find().sort("_id", -1).limit(20)
    hashes_in_db = []
    for db_obj in db_objs:
        hashes_in_db.append(db_obj["hash"])
    return hashes_in_db

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
            if not apartment['@id'] in seen_apartments:
                unseen_apartments.append(apartment)
                seen_apartments.append(hash_obj)

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