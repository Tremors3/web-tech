# Execute the script with:
#     python manage.py runscript initdb

from django.db import IntegrityError, transaction
from django.utils import timezone
from random import choice, randint
from datetime import datetime
import logging


logger = logging.getLogger('custom')


# Note: The 'apps' directory has already been added to PYTHONPATH in 'settings.py'.
# Therefore, import app modules directly using:
#     from app_name.models import ...       # Correct
# Do NOT include the 'apps' prefix in imports:
#     from apps.app_name.models import ...  # Incorrect - causes model duplication errors


from accounts.models import (
    User, Role, Seller, Buyer, Private, Shopkeeper
)

from auctions.models import (
    Category, Auction, Offer, WinnerOffer
)

from favorites.models import (
    FavoriteAuction, RecentlyViewedAuction
)

from inbox.models import (
    Notification
)

from reviews.models import (
    Review
)

from wallet.models import (
    Wallet, Transaction
)


class ManageDB():
    
    _models = list(reversed([
        # Accounts
        User, Role, Seller, Buyer, Private, Shopkeeper,
        # Auctions
        Category, Auction, Offer, WinnerOffer,
        # Favourites
        FavoriteAuction, RecentlyViewedAuction,
        # Inbox
        Notification,
        # Reviews
        Review,
        # Wallet
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
                Buyer.objects.create(role=role, shipping_address="Via Libertà 123")
            else:
                Seller.objects.create(role=role, collection_address="Corso Italia 45")

            # Aggiunga portafoglio digitale
            Wallet.objects.create(user=user, balance_cents=randint(0, 1000 * 100))

        logger.info("Sample users created.")
    
    @staticmethod
    @transaction.atomic
    def erase_db():
        for model in ManageDB._models:
            model.objects.all().delete()
        logging.info("Database erased succesfully.")
    
    @staticmethod
    @transaction.atomic
    def init_db():
        ManageDB._insert_data()
        logging.info("Database initialized succesfully.")
    
    @staticmethod
    @transaction.atomic
    def build_db():
        ManageDB.erase_db()
        ManageDB.init_db()
        logging.info("Database built succesfully.")


def run(*args):
    # runscript entry point
    ManageDB.build_db()


if __name__ == '__main__':
    run()