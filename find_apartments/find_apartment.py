import requests
import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
IMMO_SEARCH_URL = 'https://www.immobilienscout24.de/Suche/radius/wohnung-mieten?centerofsearchaddress=Berlin;;;1276003001;Berlin;&numberofrooms=2.0-&price=-800.0&livingspace=50.0-&geocoordinates=52.51051;13.43068;5.0&enteredFrom=one_step_search'

def get_immoscout_data(apartment):
    title = re.sub('[^a-zA-Z0-9.\d\s]+', '', apartment['title'])
    address = re.sub('[^a-zA-Z0-9.\d\s]+', '', apartment['address']['description']['text'])
    size = apartment['livingSpace']
    price_warm = apartment['calculatedPrice']['value']
    text = f"Apartment: {title} - Address: {address} - Size:{size} m2 - Price (warm): {price_warm} EUR -  - [https://www.immobilienscout24.de/expose/{apartment['@id']}](https://www.immobilienscout24.de/expose/{apartment['@id']})"
    return text

def search_immobilienscout(q):
    if verify_secret(q):
        seen_apartments = []
        unseen_apartments = []
        logger.info("Searching Immoscout")
        try:
            apartments = requests.post(IMMO_SEARCH_URL).json()['searchResponseModel']['resultlist.resultlist']['resultlistEntries'][0]['resultlistEntry']
        except:
            logger.warn("Could not read any listed appartement")
            apartments = []

        if not type(apartments) is list:
            apartments = [apartments]

        for apartment in apartments:
            # hash_id = sha3_512(apartment['@id'].encode('utf-8')).hexdigest()
            hash_obj = {"hash": apartment['@id']}
            if not apartment['@id'] in seen_apartments:
                unseen_apartments.append(apartment)
                seen_apartments.append(hash_obj)

        for unseen_apartment in unseen_apartments:
            apartment = unseen_apartment['resultlist.realEstate']
            text = get_immoscout_data(apartment)
            
            logger.info(text)
            # push_notification(text)
            # add_to_database({"hash": apartment['@id']})

        return {
            'status' : 'SUCCESS'
        }
    else:
        return {
            'status' : 'SUCCESS'
        }

def verify_secret(q):
    return True