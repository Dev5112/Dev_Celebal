from faker import Faker
from faker.providers import BaseProvider
import random

class EcommerceProvider(BaseProvider):
    def product_category(self) -> str:
        return random.choice(['Electronics', 'Clothing', 'Home', 'Books'])
    
    def product_subcategory(self, category: str) -> str:
        subcategories = {
            'Electronics': ['Smartphones', 'Laptops', 'Audio', 'Accessories'],
            'Clothing': ['Shirts', 'Pants', 'Shoes', 'Outerwear'],
            'Home': ['Furniture', 'Decor', 'Kitchen', 'Bedding'],
            'Books': ['Fiction', 'Non-Fiction', 'Sci-Fi', 'Biography']
        }
        return random.choice(subcategories.get(category, ['Other']))
    
    def customer_type(self) -> str:
        return random.choices(
            ['REGULAR', 'PREMIUM', 'VIP'],
            weights=[0.70, 0.20, 0.10],
            k=1
        )[0]
    
    def order_status(self) -> str:
        return random.choices(
            ['PLACED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED'],
            weights=[0.10, 0.20, 0.60, 0.05, 0.05],
            k=1
        )[0]
    
    def region_code(self) -> str:
        return random.choice(['US-EAST', 'US-WEST', 'EU', 'APAC'])

def get_faker(seed: int = 42) -> Faker:
    """Returns a configured Faker instance."""
    fake = Faker()
    fake.add_provider(EcommerceProvider)
    Faker.seed(seed)
    random.seed(seed)
    return fake
