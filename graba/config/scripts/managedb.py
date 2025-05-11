from django.db import IntegrityError, transaction
from django.utils import timezone
from random import choice, randint
from datetime import datetime
import logging


logger = logging.getLogger('custom')


from apps.accounts.models import (
    User, Role, Seller, Buyer, Private, Shopkeeper
)

from apps.auctions.models import (
    Category, Auction, Offer, WinnerOffer
)

from apps.favorites.models import (
    FavoriteAuction, RecentlyViewedAuction
)

from apps.inbox.models import (
    Notification
)

from apps.reviews.models import (
    Review
)

from apps.wallet.models import (
    Wallet, Transaction
)


class ManageDB():
    
    _models = list(reversed([
        User, Role, Seller, Buyer, Private, Shopkeeper, 
        Category, Auction, Offer, WinnerOffer,
        FavoriteAuction, RecentlyViewedAuction,
        Notification,
        Review,
        Wallet, Transaction,
    ]))
    
    @staticmethod
    @transaction.atomic
    def _insert_data():
        logger.info("Inserting sample data...")
        
        user_dict = {
            'firstname': ['Roberto', 'Giorgia', 'Francesco', 'Laura', 'Pietro'],
            'lastname': ['Corazza', 'Panini', 'Corbezzoli', 'Dimele', 'Dipesche'],
            'email': { 'domain': ['gmail', 'yahoo'], 'tld': ['com', 'it'] },
            'bio': ['Tech enthusiast', 'Art lover', 'Traveler', 'Seller of fine goods']
        }
        
        for i in range(10):
            fname = choice(user_dict['firstname'])
            lname = choice(user_dict['lastname'])
            domain = choice(user_dict['email']['domain'])
            tld = choice(user_dict['email']['tld'])
            email = f"{fname.lower()}.{lname.lower()}{randint(1, 100)}@{domain}.{tld}"

            user = User.objects.create_user(
                username=f"{fname}{lname}{randint(100, 999)}",
                email=email,
                password="TestPassword123!",
                bio=choice(user_dict['bio']),
                legal_type=choice(['PRIVATE', 'SHOPKEEPER']),
            )
            
            # Aggiunta ruoli e profili
            role_type = choice(['BUYER', 'SELLER'])
            role = Role.objects.create(user=user, type=role_type)

            if user.legal_type == 'PRIVATE':
                Private.objects.create(user=user, first_name=fname, last_name=lname, fiscal_code=f"FSC{randint(1000,9999)}CODE")
            else:
                Shopkeeper.objects.create(user=user, business_name=f"{lname} Store", iva_number=str(randint(10000000000,99999999999)), headquarters_address="Via Roma 1")

            if role.type == 'BUYER':
                Buyer.objects.create(user=role, shipping_address="Via Libertà 123")
            else:
                Seller.objects.create(user=role, collection_address="Corso Italia 45")

        logger.info("Sample users created.")
    
    @staticmethod
    @transaction.atomic
    def erase_db():
        for model in ManageDB._models:
            model.objects.all().delete()
        logging.DEBUG("Database erased succesfully.")
    
    @staticmethod
    @transaction.atomic
    def init_db():
        ManageDB._insert_data()
        logging.DEBUG("Database initialized succesfully.")
    
    @staticmethod
    @transaction.atomic
    def build_db():
        ManageDB.erase_db()
        ManageDB.init_db()
        logging.DEBUG("Database built succesfully.")


def run(*args):
    ManageDB.build_db()


if __name__ == '__main__':
    ManageDB.build_db()