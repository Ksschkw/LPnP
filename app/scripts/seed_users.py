import requests
import logging
import random
import time
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expanded test users with Nigerian phone numbers
TEST_USERS = [
    {"name": "Rob Lucci", "phone": "+2347012345001", "email": "rob.lucci@example.com"},
    {"name": "Oka Kosi", "phone": "+2347012345002", "email": "oka.kosi@example.com"},
    {"name": "Sun Nika", "phone": "+2347012345003", "email": "sun.nika@example.com"},
    {"name": "Hito Hito", "phone": "+2347012345004", "email": "hito.hito@example.com"},
    {"name": "No Mi", "phone": "+2347012345005", "email": "no.mi@example.com"},
    {"name": "Datte Bayo", "phone": "+2347012345006", "email": "datte.bayo@example.com"},
    {"name": "King Chi", "phone": "+2347012345007", "email": "king.chi@example.com"},
    {"name": "Amarachi Umunake", "phone": "+2347012345008", "email": "amarachi.umunake@example.com"},
    {"name": "Chinedu Blessing", "phone": "+2347012345009", "email": "chinedu.blessing@example.com"},
    {"name": "Kelechi Fugbara", "phone": "+2347012345010", "email": "kelechi.fugbara@example.com"},
    {"name": "Anita Igwe", "phone": "+2347012345011", "email": "anita.igwe@example.com"},
    {"name": "Emeka Nwankwo", "phone": "+2347012345012", "email": "emeka.nwankwo@example.com"},
    {"name": "Fatima Bello", "phone": "+2347012345013", "email": "fatima.bello@example.com"},
    {"name": "Samuel Johnson", "phone": "+2347012345014", "email": "samuel.johnson@example.com"},
    {"name": "Grace Okoro", "phone": "+2347012345015", "email": "grace.okoro@example.com"}
]

class UserSeeder:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.created_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        self.created_users = []
    
    def create_user(self, user_data: Dict) -> bool:
        """Create a single user - let the API handle duplicate checking"""
        try:
            payload = {
                "name": user_data["name"],
                "phone": user_data["phone"],
                "email": user_data["email"],
                "password": "password123"
            }
            
            response = requests.post(
                f"{self.base_url}/users/",
                json=payload
            )
            
            if response.status_code == 201:
                user_info = response.json()
                logger.info(f"Created user: {user_data['name']} ({user_data['phone']})")
                self.created_count += 1
                
                self.created_users.append({
                    "name": user_data["name"],
                    "phone": user_data["phone"],
                    "email": user_data["email"],
                    "password": "password123",
                    "user_id": user_info.get("id", "unknown")
                })
                return True
                
            elif response.status_code == 400:
                logger.info(f"User already exists: {user_data['name']} ({user_data['phone']})")
                self.skipped_count += 1
                return True
            else:
                logger.error(f"Failed to create user {user_data['name']}: {response.status_code} - {response.text}")
                self.failed_count += 1
                return False
                
        except Exception as e:
            logger.error(f"Error creating user {user_data['name']}: {e}")
            self.failed_count += 1
            return False
    
    def login_user(self, phone: str, password: str) -> str:
        """Login as a user and get JWT token"""
        try:
            response = requests.post(
                f"{self.base_url}/users/login",
                json={"phone": phone, "password": password}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                logger.error(f"Login failed for {phone}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Login error for {phone}: {e}")
            return None
    
    def create_services_for_user(self, token: str, user_name: str):
        """Create 2-10 services for a user"""
        try:
            services = self.generate_services(user_name)
            num_services = random.randint(2, 10)  # 2-10 services per user
            services_to_create = services[:num_services]
            
            headers = {"Authorization": f"Bearer {token}"}
            created_count = 0
            
            for service_data in services_to_create:
                response = requests.post(
                    f"{self.base_url}/services/",
                    json=service_data,
                    headers=headers
                )
                if response.status_code == 201:
                    created_count += 1
                    logger.info(f"   Created service: {service_data['title']}")
                time.sleep(0.2)  # Small delay between service creation
            
            logger.info(f"   Created {created_count} services for {user_name}")
            return created_count
            
        except Exception as e:
            logger.error(f"Service creation error for {user_name}: {e}")
            return 0
    
    def generate_services(self, user_name: str) -> List[Dict]:
        """Generate realistic service data"""
        service_templates = [
            {
                "title": f"Professional {random.choice(['Web Development', 'Mobile App Development', 'Software Consulting'])}",
                "description": f"Expert {random.choice(['web', 'mobile', 'software'])} development services with modern technologies and best practices.",
                "base_price": random.randint(50000, 300000),
                "category_name": "Digital Services",
                "service_radius_km": random.randint(10, 100),
                "current_location": random.choice(["Lagos", "Abuja", "Port Harcourt", "Ibadan"]),
                "hourly_rate": random.randint(5000, 15000)
            },
            {
                "title": f"Expert {random.choice(['Mathematics Tutoring', 'English Lessons', 'Science Coaching'])}",
                "description": f"Professional educational services for {random.choice(['students', 'professionals', 'beginners'])} of all levels.",
                "base_price": random.randint(10000, 50000),
                "category_name": "Education & Tutoring", 
                "service_radius_km": random.randint(5, 50),
                "current_location": random.choice(["Lagos", "Abuja", "Enugu", "Benin City"]),
                "hourly_rate": random.randint(2000, 8000)
            },
            {
                "title": f"Quality {random.choice(['Home Cleaning', 'Office Cleaning', 'Deep Cleaning'])}",
                "description": f"Thorough and reliable cleaning services for {random.choice(['residential', 'commercial', 'industrial'])} spaces.",
                "base_price": random.randint(8000, 25000),
                "category_name": "Cleaning Services",
                "service_radius_km": random.randint(5, 30),
                "current_location": random.choice(["Lagos", "Abuja", "Kano", "Kaduna"]),
                "hourly_rate": random.randint(1500, 4000)
            },
            {
                "title": f"Professional {random.choice(['Graphic Design', 'UI/UX Design', 'Brand Identity'])}",
                "description": f"Creative design services for {random.choice(['businesses', 'startups', 'individuals'])} looking to enhance their visual identity.",
                "base_price": random.randint(20000, 100000),
                "category_name": "Art & Design",
                "service_radius_km": random.randint(5, 100),
                "current_location": random.choice(["Lagos", "Abuja", "Port Harcourt"]),
                "hourly_rate": random.randint(3000, 10000)
            },
            {
                "title": f"Expert {random.choice(['Fitness Training', 'Yoga Instruction', 'Sports Coaching'])}",
                "description": f"Professional fitness and wellness services to help you achieve your {random.choice(['health', 'fitness', 'sports'])} goals.",
                "base_price": random.randint(15000, 60000),
                "category_name": "Fitness & Sports Coaching",
                "service_radius_km": random.randint(5, 40),
                "current_location": random.choice(["Lagos", "Abuja", "Ibadan", "Warri"]),
                "hourly_rate": random.randint(2500, 7000)
            },
            {
                "title": f"Professional {random.choice(['Car Repair', 'Vehicle Maintenance', 'Auto Diagnostics'])}",
                "description": f"Reliable automotive services for all types of vehicles with {random.choice(['quick', 'thorough', 'affordable'])} service.",
                "base_price": random.randint(10000, 80000),
                "category_name": "Automotive Services",
                "service_radius_km": random.randint(5, 25),
                "current_location": random.choice(["Lagos", "Abuja", "Port Harcourt", "Kano"]),
                "hourly_rate": random.randint(2000, 6000)
            },
            {
                "title": f"Quality {random.choice(['Handyman Services', 'Home Repairs', 'Installation Services'])}",
                "description": f"Skilled handyman services for {random.choice(['home', 'office', 'commercial'])} repair and maintenance needs.",
                "base_price": random.randint(5000, 30000),
                "category_name": "Handyman Services",
                "service_radius_km": random.randint(5, 35),
                "current_location": random.choice(["Lagos", "Abuja", "Benin City", "Uyo"]),
                "hourly_rate": random.randint(1500, 4500)
            },
            {
                "title": f"Professional {random.choice(['Photography', 'Videography', 'Content Creation'])}",
                "description": f"High-quality visual content creation for {random.choice(['events', 'businesses', 'personal'])} use.",
                "base_price": random.randint(25000, 120000),
                "category_name": "Photography & Videography",
                "service_radius_km": random.randint(10, 80),
                "current_location": random.choice(["Lagos", "Abuja", "Port Harcourt", "Calabar"]),
                "hourly_rate": random.randint(4000, 12000)
            }
        ]
        
        # Shuffle and return services
        random.shuffle(service_templates)
        return service_templates
    
    def seed_users(self):
        """Main method to seed all users"""
        logger.info("Starting user seeding...")
        logger.info("Creating test users with Nigerian phone numbers...")
        
        # First pass: Create all users
        for user_data in TEST_USERS:
            if self.create_user(user_data):
                time.sleep(0.3)  # Small delay between user creation
        
        # Second pass: Create services for created users
        logger.info("Creating services for users...")
        service_stats = []
        
        for user_data in self.created_users:
            token = self.login_user(user_data["phone"], user_data["password"])
            if token:
                services_created = self.create_services_for_user(token, user_data["name"])
                service_stats.append((user_data["name"], services_created))
                time.sleep(0.5)  # Delay between users
        
        # Print summary
        logger.info("User seeding completed!")
        logger.info(f"Summary: {self.created_count} created, {self.skipped_count} skipped, {self.failed_count} failed")
        
        # Print service creation stats
        if service_stats:
            logger.info("Service creation summary:")
            for name, count in service_stats:
                logger.info(f"   {name}: {count} services")
        
        # Print user credentials
        if self.created_users:
            logger.info("Created Users (Login Credentials):")
            logger.info("=" * 60)
            for user in self.created_users:
                logger.info(f"Name: {user['name']}")
                logger.info(f"Phone: {user['phone']}")
                logger.info(f"Password: {user['password']}")
                logger.info(f"Email: {user['email']}")
                logger.info("-" * 40)
    
    def run(self):
        """Run the seeder with error handling"""
        try:
            self.seed_users()
        except KeyboardInterrupt:
            logger.info("Seeding interrupted by user")
        except Exception as e:
            logger.error(f"Seeding failed: {e}")

if __name__ == "__main__":
    seeder = UserSeeder(base_url="http://localhost:8000")
    seeder.run()