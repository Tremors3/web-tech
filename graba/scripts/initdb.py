# Execute the script with:
#     python manage.py runscript initdb

from django.db import IntegrityError, transaction
from django.utils import timezone
from random import choice, randint
from datetime import datetime, timedelta
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
        
        auctions_dict = {
            'title': [
                "Sneakers Running Uomo Nike Air Zoom Pegasus 40",
                "Cuffie Bluetooth Noise Cancelling Sony WH-1000XM5",
                "Set Pentole Antiaderenti 10 Pezzi – Acciaio Inox",
                "Divano 3 Posti in Tessuto con Chaise Longue – Grigio Antracite",
                "Zaino Outdoor Impermeabile da 40L – Trekking & Escursionismo",
                "Orologio Smartwatch Amazfit GTR 4 – GPS & Monitoraggio Salute",
                "LEGO Star Wars – Millennium Falcon (Set da Costruzione)",
                "Crema Viso Idratante Bio – Aloe Vera & Acido Ialuronico",
                "Alimento Secco per Cani – Royal Canin Maxi Adult 15kg",
                "Giacca Invernale Donna con Cappuccio – Piumino Termico"
            ],
            'image_url': [
                'https://picsum.photos/200',
                'https://picsum.photos/300',
                'https://picsum.photos/300/200',
                'https://picsum.photos/200/300'
            ],
            'description': [
                "Scarpe da corsa leggere e reattive, ideali per allenamenti intensi e lunghe distanze.",
                "Cuffie wireless con cancellazione attiva del rumore, audio ad alta fedeltà e autonomia di 30 ore.",
                "Set completo di pentole antiaderenti, perfette per cucinare ogni giorno con stile e praticità.",
                "Divano moderno con chaise longue, rivestito in tessuto resistente e facile da pulire.",
                "Zaino tecnico da escursionismo, con schienale traspirante e copertura antipioggia inclusa.",
                "Smartwatch con monitoraggio della salute, GPS integrato e oltre 120 modalità sportive.",
                "Set LEGO dettagliato del celebre Millennium Falcon, ideale per appassionati di Star Wars.",
                "Crema viso naturale, idratante e lenitiva, adatta anche alle pelli più sensibili.",
                "Crocchette di alta qualità per cani adulti di taglia grande, con formula bilanciata e digeribile.",
                "Giacca invernale calda e leggera, perfetta per affrontare il freddo con stile."
            ],
            'technical_details': [
                "Peso: 280g | Suola: Gomma con tecnologia Zoom Air | Tomaia: Mesh traspirante | Drop: 10mm",
                "Driver da 30mm | Autonomia: fino a 30 ore | Bluetooth 5.2 | Ricarica rapida USB-C",
                "Materiale: Acciaio inox + rivestimento antiaderente | Compatibile con induzione | Manici ergonomici in silicone",
                "Dimensioni: 230x95x160 cm | Tessuto: poliestere 100% | Struttura: legno massello | Cuscini sfoderabili",
                "Capacità: 40L | Materiale: nylon ripstop impermeabile | Tasche: 6 | Peso: 950g",
                "Display AMOLED 1.43” | Autonomia: fino a 14 giorni | Sensori: SpO2, battito, GPS | Impermeabilità: 5 ATM",
                "Numero pezzi: 1353 | Età consigliata: 9+ anni | Include minifigure originali | Dimensioni costruzione: 44 x 32 cm",
                "Formato: 50 ml | Ingredienti principali: Aloe Vera, Acido Ialuronico, Vitamina E | pH dermatologicamente testato",
                "Peso netto: 15 kg | Tipo: secco | Composizione: proteine 26%, grassi 17% | Adatto a cani >25 kg",
                "Materiale esterno: poliestere impermeabile | Imbottitura: piuma sintetica | Tasche: 4 | Chiusura: zip con patta antivento"
            ]
        }
        
        categories = {
            "Electronics & Technology": [
                "Computers & Accessories",
                "Mobile Phones & Tablets",
                "Smart Home Devices",
                "Cameras & Photography",
                "Audio & Headphones",
                "Wearables (Smartwatches, Fitness Trackers)"
            ],
            "Home & Living": [
                "Furniture",
                "Kitchen & Dining",
                "Home Decor",
                "Bedding & Bath",
                "Tools & DIY",
                "Lighting"
            ],
            "Fashion & Apparel": [
                "Men’s Clothing",
                "Women’s Clothing",
                "Kids & Baby Clothing",
                "Shoes",
                "Bags & Accessories",
                "Jewelry & Watches"
            ],
            "Grocery & Food": [
                "Beverages",
                "Fresh Produce",
                "Snacks",
                "Organic & Health Foods",
                "Pantry Staples"
            ],
            "Sports & Outdoors": [
                "Fitness Equipment",
                "Camping & Hiking",
                "Bicycles & Accessories",
                "Team Sports Gear",
                "Outdoor Clothing"
            ],
            "Health & Beauty": [
                "Skincare",
                "Haircare",
                "Cosmetics & Makeup",
                "Vitamins & Supplements",
                "Personal Care"
            ],
            "Baby & Kids": [
                "Toys",
                "Baby Gear (strollers, car seats)",
                "Educational Materials",
                "Diapers & Wipes",
                "Kids Furniture"
            ],
            "Pets": [
                "Pet Food",
                "Toys & Accessories",
                "Grooming",
                "Pet Health Products"
            ],
            "Books, Media & Entertainment": [
                "Books & eBooks",
                "Movies & TV",
                "Music",
                "Video Games",
                "Board Games"
            ],
            "Automotive": [
                "Car Accessories",
                "Motorbike Gear",
                "Tools & Equipment",
                "Oils & Fluids"
            ],
            "Gifts & Hobbies": [
                "Crafts & DIY Kits",
                "Collectibles",
                "Stationery",
                "Seasonal Gifts",
                "Party Supplies"
            ]
        }
        
        # Aggiunta delle categorie
        for parent_name, childs in categories.items():
            parent = Category.objects.create(name=parent_name, level=1)
            for child_name in childs:
                Category.objects.create(name=child_name, level=2, parent=parent)
        
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
                buyer = Buyer.objects.create(role=role, shipping_address="Via Libertà 123")
            else:
                seller = Seller.objects.create(role=role, collection_address="Corso Italia 45")

            # Aggiunga portafoglio digitale
            Wallet.objects.create(user=user, balance_cents=randint(0, 1000 * 100))
            
            # Aggiunta delle aste
            if role.type == 'SELLER':
                for j in range(randint(0, 3)):
                    title = choice(auctions_dict['title'])
                    image = choice(auctions_dict['image_url'])
                    descr = choice(auctions_dict['description'])
                    techn = choice(auctions_dict['technical_details'])
                    
                    start_date = timezone.now()
                    duration_days = choice([7, 14, 30])
                    end_date = start_date + timedelta(days=duration_days)
                    
                    markup_percentage = randint(50, 150) # range da 50% a 150%
                    min_price_cents = randint(10 * 100, 500 * 100) # range da 10 e 500 euro
                    buy_now_price_cents = min_price_cents + (min_price_cents * markup_percentage) // 100
                    
                    category_name = choice(categories[ choice(list(categories.keys())) ])
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