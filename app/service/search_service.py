from app.repository.Database.service_repo import ServiceRepository
from app.repository.Database.category_repo import CategoryRepository
from thefuzz import fuzz, process
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db):
        self.service_repo = ServiceRepository(db)
        self.category_repo = CategoryRepository(db)
    
    def fuzzy_search_services(
        self,
        query: Optional[str] = None,
        category_name: Optional[str] = None,
        location: Optional[str] = None,
        max_distance_km: Optional[int] = None,
        min_trust_score: Optional[int] = None,
        max_price: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Advanced fuzzy search for services
        All parameters are optional - search by any combination
        """
        try:
            # Get all active services first
            all_services = self.service_repo.get_active_services(limit=1000)
            
            filtered_services = all_services
            
            # Apply fuzzy matching for service title/description
            if query:
                filtered_services = self._fuzzy_filter_services(filtered_services, query)
            
            # Apply fuzzy matching for category
            if category_name:
                filtered_services = self._fuzzy_filter_by_category(filtered_services, category_name)
            
            # Apply location filtering (with fuzzy matching)
            if location:
                filtered_services = self._fuzzy_filter_by_location(filtered_services, location, max_distance_km)
            
            # Apply trust score filter
            if min_trust_score is not None:
                filtered_services = [s for s in filtered_services if s.trust_points >= min_trust_score]
            
            # Apply price filter
            if max_price is not None:
                filtered_services = [s for s in filtered_services if float(s.base_price) <= max_price]
            
            # Sort by relevance score (if query provided) or trust points
            if query:
                filtered_services.sort(key=lambda s: (
                    -getattr(s, '_search_score', 0),
                    -s.trust_points
                ))
            else:
                filtered_services.sort(key=lambda s: -s.trust_points)
            
            logger.info(f"Fuzzy search completed: query='{query}', results={len(filtered_services)}")
            return filtered_services[:limit]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _fuzzy_filter_services(self, services: List, query: str) -> List:
        """Fuzzy match services by title and description"""
        scored_services = []
        
        for service in services:
            # Calculate scores for title and description
            title_score = fuzz.partial_ratio(query.lower(), service.title.lower())
            desc_score = fuzz.partial_ratio(query.lower(), (service.description or "").lower()) * 0.5
            
            # Combined score (title weighted higher)
            total_score = title_score + desc_score
            
            # Only include if score is above threshold
            if total_score >= 40:
                service._search_score = total_score
                scored_services.append(service)
        
        return scored_services
    
    def _fuzzy_filter_by_category(self, services: List, category_query: str) -> List:
        """Fuzzy match services by category"""
        filtered_services = []
        
        for service in services:
            if service.categories:
                # Check each category assigned to this service
                for category in service.categories:
                    category_score = fuzz.partial_ratio(category_query.lower(), category.name.lower())
                    if category_score >= 60:
                        filtered_services.append(service)
                        break
        
        return filtered_services
    
    def _fuzzy_filter_by_location(self, services: List, location_query: str, max_distance_km: Optional[int]) -> List:
        """Fuzzy match services by location"""
        location_query = location_query.lower()
        scored_services = []
        
        for service in services:
            if service.current_location:
                location_score = fuzz.partial_ratio(location_query, service.current_location.lower())
                
                # Include if location matches reasonably well
                if location_score >= 50:
                    service._location_score = location_score
                    scored_services.append(service)
        
        # Sort by location relevance
        scored_services.sort(key=lambda s: -getattr(s, '_location_score', 0))
        return scored_services
    
    def search_categories_fuzzy(self, query: str, limit: int = 20) -> List:
        """Fuzzy search for categories by name - FIXED VERSION"""
        try:
            all_categories = self.category_repo.get_all(limit=1000)
            
            if not all_categories:
                return []
            
            # Use fuzzy matching to find categories - handle different return formats
            category_names = [cat.name for cat in all_categories]
            matches = process.extract(
                query,
                category_names,
                limit=limit,
                scorer=fuzz.partial_ratio
            )
            
            result_categories = []
            for match in matches:
                # Handle different return formats from process.extract
                if len(match) >= 2:
                    if len(match) == 3:
                        # Format: (name, score, index)
                        match_name, score, _ = match
                    else:
                        # Format: (name, score) 
                        match_name, score = match
                    
                    if score >= 40:
                        category = next((cat for cat in all_categories if cat.name == match_name), None)
                        if category:
                            result_categories.append({
                                "category": category,
                                "match_score": score
                            })
            
            # Sort by match score
            result_categories.sort(key=lambda x: -x["match_score"])
            
            return [item["category"] for item in result_categories]
            
        except Exception as e:
            logger.error(f"Category search error: {e}")
            return []
    
    def autocomplete_services(self, query: str, limit: int = 10) -> List[Dict]:
        """Autocomplete service titles for search suggestions - FIXED VERSION"""
        try:
            all_services = self.service_repo.get_active_services(limit=500)
            
            if not all_services:
                return []
            
            # Extract service titles
            service_titles = [service.title for service in all_services]
            
            # Find best matches
            matches = process.extract(
                query,
                service_titles,
                limit=limit,
                scorer=fuzz.partial_ratio
            )
            
            # Get unique matches above threshold
            unique_matches = []
            seen_titles = set()
            
            for match in matches:
                # Handle different return formats
                if len(match) >= 2:
                    if len(match) == 3:
                        match_title, score, _ = match
                    else:
                        match_title, score = match
                    
                    if score >= 50 and match_title not in seen_titles:
                        seen_titles.add(match_title)
                        unique_matches.append({
                            "title": match_title,
                            "score": score
                        })
            
            return unique_matches[:limit]
            
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            return []
    
    def autocomplete_categories(self, query: str, limit: int = 10) -> List[str]:
        """Simple category autocomplete - returns category names"""
        try:
            categories = self.search_categories_fuzzy(query, limit)
            return [cat.name for cat in categories]
        except Exception as e:
            logger.error(f"Category autocomplete error: {e}")
            return []