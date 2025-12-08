# Execute the script with:
#     python manage.py runscript initdb

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.conf import settings

from random import choice, randint
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import logging
import json
import os


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
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.updateMocks()
    
    def updateMocks(self):
        self.user_mocks: Dict[str, Any] = ManageDB.read_json_file(self.base_dir / "data" / "mocks" / "users.json")
        self.auction_mocks: Dict[str, Any] = ManageDB.read_json_file(self.base_dir / "data" / "mocks" / "auctions.json")
        self.category_mocks: Dict[str, Any] = ManageDB.read_json_file(self.base_dir / "data" / "mocks" / "categories.json")
    
    @staticmethod
    def read_json_file(file_path: str) -> dict:
        if not os.path.isfile(file_path):
            logger.warning(f"Error file not found \'{file_path}\'")
            return {}
        try:
            with open(file=file_path, mode='r', encoding='utf-8') as fd:
                return json.load(fd)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Error reading the JSON file \'{file_path}\': {e}")
            return {}
    
    @transaction.atomic
    def init_table_category(self):
        # Adding the categories
        for parent_name, childs in self.category_mocks.items():
            parent = Category.objects.create(name=parent_name, level=1)
            for child_name in childs:
                Category.objects.create(name=child_name, level=2, parent=parent)
    
    @transaction.atomic
    def init_table_wallet(self, user: User):
        # Aggiunga portafoglio digitale
        Wallet.objects.create(user=user, balance_cents=randint(0, 1000 * 100))
    
    @transaction.atomic
    def init_table_auction(self, min_: int, max_: int, seller: Seller):
        if min_ < 0 or max_ < 0 or max_ < min_: return
        
        for j in range(randint(min_, max_)):
            title = choice(self.auction_mocks['title'])
            image = choice(self.auction_mocks['image_url'])
            descr = choice(self.auction_mocks['description'])
            techn = choice(self.auction_mocks['technical_details'])
            
            start_date = timezone.now()
            duration_days = choice([7, 14, 30])
            end_date = start_date + timedelta(days=duration_days)
            
            markup_percentage = randint(50, 150) # range da 50% a 150%
            min_price_cents = randint(10 * 100, 500 * 100) # range da 10 e 500 euro
            buy_now_price_cents = min_price_cents + (min_price_cents * markup_percentage) // 100
            
            category_name = choice(self.category_mocks[ choice(list(self.category_mocks.keys())) ])
            category = Category.objects.get(name=category_name)
            
            auction = Auction.objects.create(
                title=title,
                image_url=image,
                description=descr,
                technical_details=techn,
                start_date=start_date,
                end_date=end_date,
                min_price_cents=min_price_cents,
                
                seller=seller,
                category=category
            )
            
            if j % 2 == 0:
                auction.buy_now_price_cents = buy_now_price_cents
                auction.save()
    
    @transaction.atomic
    def init_table_user(self, amount: int = 30):
        if amount < 0 or amount > 100: return
        
        # Adding the users
        for _ in range(amount):
            first_name = choice(self.user_mocks['firstname'])
            last_name = choice(self.user_mocks['lastname'])
            email_domain = choice(self.user_mocks['email']['domain'])
            email_tld = choice(self.user_mocks['email']['tld'])
            email = f"{first_name.lower()}.{last_name.lower()}{randint(1, 100)}@{email_domain}.{email_tld}"
            bio = choice(self.user_mocks['bio'])
            password_clear = "TestPassword123"
            username = f"{first_name}{last_name}{randint(100, 999)}"
            legal_type = choice(['PRIVATE', 'SHOPKEEPER'])

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password_clear,
                bio=bio,
                legal_type=legal_type,
            )
            
            # Adding user's role
            role_type = choice(['BUYER', 'SELLER'])
            role = Role.objects.create(
                user=user,
                type=role_type
            )
            
            # Adding Role specific table 
            address = choice(self.user_mocks['addresses'])
            if role.type == 'BUYER':
                buyer = Buyer.objects.create(
                    role=role,
                    shipping_address=address
                )
            else:
                seller = Seller.objects.create(
                    role=role,
                    collection_address=address
                )

            # Adding user's legal type
            if user.legal_type == 'PRIVATE':
                Private.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    fiscal_code=f"FSC{randint(1000,9999)}CODE"
                )
            else:
                Shopkeeper.objects.create(
                    user=user,
                    business_name=f"{last_name} Store",
                    iva_number=str(randint(10000000000,99999999999)),
                    headquarters_address=address
                )

            # Adding digital wallet
            self.init_table_wallet(user=user)
        
            # Adding user's auctions
            if role.type == 'SELLER':
                self.init_table_auction(0, 20, seller)
                print(seller)

        logger.info("Sample data created.")
    
    @transaction.atomic
    def erase_db(self):
        for model in ManageDB._models:
            model.objects.all().delete()
    
    @transaction.atomic
    def init_db(self):
        self.init_table_category()
        self.init_table_user()
    
    @transaction.atomic
    def rebuild_db(self):
        self.erase_db()
        self.init_db()


def run(*args):
    # runscript entry point
    mdb = ManageDB(settings.BASE_DIR)
    mdb.rebuild_db()


if __name__ == '__main__':
    run()