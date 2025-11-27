import asyncio
import requests
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your categories data
CATEGORIES = [
    {"name": "Home Services", "description": "General household maintenance including cleaning, repairs, and installations."},
    {"name": "Digital Services", "description": "Online-based offerings like web development, graphic design, and digital marketing."},
    {"name": "Health & Wellness", "description": "Services promoting physical and mental health, such as therapy, fitness, and nutrition."},
    {"name": "Beauty & Personal Care", "description": "Hair, skin, and grooming services including salons, spas, and makeup."},
    {"name": "Childcare Services", "description": "Professional care for children including babysitting, tutoring, and early education."},
    {"name": "Pet Services", "description": "Grooming, sitting, training, and veterinary support for pets."},
    {"name": "Elderly Care", "description": "Assistance for seniors including companionship, mobility support, and medical aid."},
    {"name": "Event Services", "description": "Planning, catering, photography, and entertainment for personal or corporate events."},
    {"name": "Education & Tutoring", "description": "Academic support, test prep, and skill-based learning across subjects."},
    {"name": "Transportation Services", "description": "Ridesharing, airport transfers, and logistics."},
    {"name": "Moving & Relocation", "description": "Packing, hauling, and relocation coordination."},
    {"name": "Legal Services", "description": "Legal advice, documentation, and representation."},
    {"name": "Financial Services", "description": "Accounting, tax filing, financial planning, and investment advice."},
    {"name": "Real Estate Services", "description": "Buying, selling, renting, and property management."},
    {"name": "Technical Support", "description": "IT troubleshooting, device setup, and software assistance."},
    {"name": "Automotive Services", "description": "Car repairs, detailing, and maintenance."},
    {"name": "Construction & Renovation", "description": "Building, remodeling, and structural improvements."},
    {"name": "Handyman Services", "description": "Small repairs, installations, and general fix-it tasks."},
    {"name": "Art & Design", "description": "Creative services including illustration, animation, and branding."},
    {"name": "Writing & Translation", "description": "Copywriting, editing, and multilingual translation."},
    {"name": "Marketing & Advertising", "description": "Campaign strategy, branding, and media buying."},
    {"name": "Photography & Videography", "description": "Professional photo and video production."},
    {"name": "Music & Audio Services", "description": "Lessons, production, and sound engineering."},
    {"name": "Fitness & Sports Coaching", "description": "Personal training, sports instruction, and wellness coaching."},
    {"name": "Spiritual & Religious Services", "description": "Counseling, ceremonies, and spiritual guidance."},
    {"name": "Culinary Services", "description": "Personal chefs, catering, and meal prep."},
    {"name": "Fashion & Styling", "description": "Wardrobe consulting, tailoring, and personal shopping."},
    {"name": "Cleaning Services", "description": "Residential, commercial, and specialized cleaning."},
    {"name": "Security Services", "description": "Surveillance, guards, and cybersecurity."},
    {"name": "Courier & Delivery", "description": "Local and long-distance package delivery."},
    {"name": "Administrative Support", "description": "Virtual assistants, scheduling, and office management."},
    {"name": "HR & Recruitment", "description": "Talent sourcing, onboarding, and HR consulting."},
    {"name": "Business Consulting", "description": "Strategy, operations, and growth advisory."},
    {"name": "Product Design & Prototyping", "description": "Industrial design and 3D modeling."},
    {"name": "Data & Analytics", "description": "Data science, visualization, and reporting."},
    {"name": "Blockchain & Crypto Services", "description": "Wallet setup, smart contracts, and consulting."},
    {"name": "AI & Machine Learning Services", "description": "Model training, deployment, and automation."},
    {"name": "Gaming Services", "description": "Game coaching, streaming setup, and development."},
    {"name": "Interior Design", "description": "Space planning, decor, and furniture selection."},
    {"name": "Architecture Services", "description": "Building design, permits, and structural planning."},
    {"name": "Environmental Services", "description": "Sustainability consulting and eco-friendly solutions."},
    {"name": "Utilities & Installation", "description": "Water, gas, and electrical setup."},
    {"name": "Insurance Services", "description": "Policy advice, claims assistance, and brokerage."},
    {"name": "Travel & Tourism", "description": "Trip planning, tour guiding, and booking."},
    {"name": "Public Speaking & Training", "description": "Workshops, seminars, and motivational speaking."},
    {"name": "Crafts & Handmade Goods", "description": "Custom creations and artisanal services."},
    {"name": "Marketplace Support Services", "description": "Dispute resolution, escrow, and identity verification."},
    {"name": "Community Services", "description": "Volunteering, outreach, and social impact."},
    {"name": "Subscription-Based Services", "description": "Recurring offerings like meal kits or coaching plans."},
    {"name": "On-Demand Services", "description": "Instant booking for urgent or short-term needs."}
]

class CategorySeeder:
    def __init__(self, base_url: str = "http://localhost:8000", admin_key: str = "chikara"):
        self.base_url = base_url
        self.admin_key = admin_key
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
    
    def get_existing_categories(self) -> Dict[str, str]:
        """Get all existing categories to check for duplicates"""
        try:
            response = requests.get(
                f"{self.base_url}/admin/categories/categories",
                params={"admin_key": self.admin_key}
            )
            if response.status_code == 200:
                categories = response.json()
                return {cat["name"]: cat.get("description", "") for cat in categories}
            return {}
        except Exception as e:
            logger.error(f"Error fetching existing categories: {e}")
            return {}
    
    def create_category(self, name: str, description: str) -> bool:
        """Create a single category via admin endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/admin/categories/categories",
                params={
                    "name": name,
                    "description": description,
                    "admin_key": self.admin_key
                }
            )
            
            if response.status_code == 200:
                logger.info(f" Created category: {name}")
                self.created_count += 1
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                logger.info(f"  Category already exists: {name}")
                self.skipped_count += 1
                return True
            else:
                logger.error(f" Failed to create category {name}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f" Error creating category {name}: {e}")
            return False
    
    def update_category_description(self, name: str, new_description: str) -> bool:
        """Update category description if different (you'll need to add this endpoint)"""
        # For now, we'll just log that description should be updated
        logger.info(f" Description update needed for {name}")
        return True
    
    def seed_categories(self):
        """Main method to seed all categories"""
        logger.info(" Starting category seeding...")
        
        # Get existing categories
        existing_categories = self.get_existing_categories()
        logger.info(f" Found {len(existing_categories)} existing categories")
        
        # Process each category
        for category in CATEGORIES:
            name = category["name"]
            description = category["description"]
            
            if name in existing_categories:
                # Category exists, check if description needs update
                existing_description = existing_categories[name]
                if existing_description != description:
                    self.update_category_description(name, description)
                    self.updated_count += 1
                else:
                    self.skipped_count += 1
            else:
                # Create new category
                self.create_category(name, description)
            
            # Small delay to avoid overwhelming the server
            import time
            time.sleep(0.1)
        
        # Print summary
        logger.info(" Category seeding completed!")
        logger.info(f" Summary: {self.created_count} created, {self.updated_count} updated, {self.skipped_count} skipped")
    
    def run(self):
        """Run the seeder with error handling"""
        try:
            self.seed_categories()
        except KeyboardInterrupt:
            logger.info("  Seeding interrupted by user")
        except Exception as e:
            logger.error(f" Seeding failed: {e}")

if __name__ == "__main__":
    # You can customize these values
    seeder = CategorySeeder(
        base_url="http://localhost:8000",  
        admin_key="chikara"                
    )
    seeder.run()