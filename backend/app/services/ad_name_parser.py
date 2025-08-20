import re
from datetime import date, datetime
from typing import Dict, Optional, Any
from loguru import logger

class AdNameParser:
    """
    Advanced parser for extracting structured data from Meta Ads ad names
    Based on House of Noa's specific naming convention patterns
    """
    
    def __init__(self):
        # Define known colors (expanded list)
        self.colors = [
            'fog', 'biscuit', 'multi', 'black', 'white', 'grey', 'gray', 'blue', 
            'green', 'red', 'pink', 'purple', 'yellow', 'orange', 'brown', 'beige', 
            'cream', 'navy', 'sage', 'charcoal', 'ivory', 'stone', 'sand', 'dust',
            'rose', 'mint', 'slate', 'pearl', 'amber', 'coral', 'teal', 'lavender'
        ]
        
        # Define known products/patterns
        self.products = [
            'folklore', 'checks', 'multi', 'arden', 'wisp', 'botanical', 'stripe',
            'solid', 'marble', 'geometric', 'floral', 'abstract', 'vintage', 'modern'
        ]
        
        # Define known categories
        self.categories = [
            'tumbling mat', 'bath', 'standing mat', 'play mat', 'playmat', 'play furniture', 'multi',
            'desk mat', 'floor mat', 'yoga mat', 'exercise mat', 'kitchen mat', 'door mat'
        ]
        
        # Define content types
        self.content_types = [
            'whitelist', 'brand', 'ugc', 'brand ugc', 'influencer', 'user generated',
            'organic', 'testimonial', 'review'
        ]
        
        # Define formats
        self.formats = [
            'video', 'image', 'collection', 'carousel', 'story', 'reel', 'static',
            'animated', 'gif', 'slideshow'
        ]
        
        # Define known handles/creators
        self.handles = [
            'brookeknuth', 'hon', 'sydnee', 'taylor', 'madison', 'emma', 'olivia',
            'house of noa', 'houseofnoa', 'noa'
        ]
    
    def parse_ad_name(self, ad_name: str, campaign_name: str = "") -> Dict[str, Any]:
        """
        Parse ad name using House of Noa's naming convention
        
        Expected format: "Date - Category - Product - Color - Content Type - Handle - Format - Ad Name"
        Example: "7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist"
        """
        
        result = {
            'launch_date': None,
            'days_live': 0,
            'category': '',
            'product': '',
            'color': '',
            'content_type': '',
            'handle': '',
            'format': '',
            'ad_name_clean': ad_name,  # Store original as fallback
            'campaign_optimization': 'Standard'  # Default
        }
        
        try:
            # First, try to parse the structured format
            if ' - ' in ad_name:
                parts = [part.strip() for part in ad_name.split(' - ')]
                
                if len(parts) >= 7:  # Minimum expected parts
                    # Parse each component
                    result.update(self._parse_structured_format(parts))
                else:
                    # Fallback to pattern-based parsing
                    result.update(self._parse_fallback_patterns(ad_name))
            else:
                # No structured format, use pattern-based parsing
                result.update(self._parse_fallback_patterns(ad_name))
            
            # Calculate days live if we have a launch date
            if result['launch_date']:
                today = date.today()
                result['days_live'] = (today - result['launch_date']).days
            
            # Determine campaign optimization from campaign name
            result['campaign_optimization'] = self._parse_campaign_optimization(campaign_name)
            
            logger.debug(f"Parsed ad name: {ad_name[:50]}... -> {result}")
            
        except Exception as e:
            logger.warning(f"Error parsing ad name '{ad_name}': {e}")
            # Return defaults with original ad name
            result['ad_name_clean'] = ad_name
        
        return result
    
    def _parse_structured_format(self, parts: list) -> Dict[str, Any]:
        """
        Parse the structured format: Date - Category - Product - Color - Content Type - Handle - Format - Ad Name
        """
        result = {}
        
        try:
            # Part 0: Launch Date
            if len(parts) > 0:
                result['launch_date'] = self._parse_date(parts[0])
            
            # Part 1: Category
            if len(parts) > 1:
                result['category'] = self._normalize_category(parts[1])
            
            # Part 2: Product
            if len(parts) > 2:
                result['product'] = parts[2].title()
            
            # Part 3: Color
            if len(parts) > 3:
                result['color'] = parts[3].title()
            
            # Part 4: Content Type
            if len(parts) > 4:
                result['content_type'] = self._normalize_content_type(parts[4])
            
            # Part 5: Handle
            if len(parts) > 5:
                result['handle'] = self._normalize_handle(parts[5])
            
            # Part 6: Format
            if len(parts) > 6:
                result['format'] = self._normalize_format(parts[6])
            
            # Part 7+: Ad Name (everything after format)
            if len(parts) > 7:
                result['ad_name_clean'] = ' - '.join(parts[7:])
            elif len(parts) > 6:
                # If no separate ad name, use the format as part of the name
                result['ad_name_clean'] = parts[6]
            
        except Exception as e:
            logger.warning(f"Error parsing structured format: {e}")
        
        return result
    
    def _parse_fallback_patterns(self, ad_name: str) -> Dict[str, Any]:
        """
        Parse ad name using pattern matching when structured format isn't available
        """
        result = {}
        ad_lower = ad_name.lower()
        
        # Try to extract date from beginning
        date_match = re.match(r'^(\d{1,2}/\d{1,2}/\d{4})', ad_name)
        if date_match:
            result['launch_date'] = self._parse_date(date_match.group(1))
        
        # Extract category
        result['category'] = self._extract_category_from_text(ad_lower)
        
        # Extract product
        result['product'] = self._extract_product_from_text(ad_lower)
        
        # Extract color
        result['color'] = self._extract_color_from_text(ad_lower)
        
        # Extract content type
        result['content_type'] = self._extract_content_type_from_text(ad_lower)
        
        # Extract format
        result['format'] = self._extract_format_from_text(ad_lower)
        
        # Extract handle
        result['handle'] = self._extract_handle_from_text(ad_lower)
        
        # Clean ad name (remove extracted parts)
        result['ad_name_clean'] = self._clean_ad_name(ad_name)
        
        return result
    
    def _parse_date(self, date_string: str) -> Optional[date]:
        """
        Parse date from string in various formats
        """
        date_string = date_string.strip()
        
        # Try different date formats - include 2-digit years
        formats = [
            '%m/%d/%Y',    # 8/8/2024
            '%m/%d/%y',    # 8/8/24 
            '%d/%m/%Y',    # 8/8/2024 (EU format)
            '%d/%m/%y',    # 8/8/24 (EU format)
            '%Y-%m-%d',    # 2024-08-08
            '%m-%d-%Y',    # 8-8-2024
            '%m-%d-%y'     # 8-8-24
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_string}")
        return None
    
    def _normalize_category(self, category: str) -> str:
        """
        Normalize category name to standard format
        """
        category_lower = category.lower().strip()
        
        if 'tumbling' in category_lower:
            return 'Tumbling Mat'
        elif 'bath' in category_lower:
            return 'Bath'
        elif 'standing' in category_lower or 'desk' in category_lower:
            return 'Standing Mat'
        elif 'play furniture' in category_lower:
            return 'Play Furniture'
        elif category_lower == 'playmat':
            return 'Playmat'
        elif 'play' in category_lower and 'mat' in category_lower:
            return 'Play Mat'
        elif category_lower == 'multi':
            return 'Multi'
        elif 'mat' in category_lower:
            return 'Mat'
        else:
            return category.title()
    
    def _normalize_content_type(self, content_type: str) -> str:
        """
        Normalize content type to standard format
        """
        content_lower = content_type.lower().strip()
        
        if 'whitelist' in content_lower:
            return 'Whitelist'
        elif 'brand ugc' in content_lower:
            return 'Brand UGC'
        elif 'brand' in content_lower:
            return 'Brand'
        elif 'ugc' in content_lower:
            return 'UGC'
        elif 'influencer' in content_lower:
            return 'Influencer'
        else:
            return content_type.title()
    
    def _normalize_handle(self, handle: str) -> str:
        """
        Normalize handle/creator name
        """
        handle_lower = handle.lower().strip()
        
        if handle_lower in ['hon', 'house of noa', 'houseofnoa']:
            return 'HoN'
        elif 'brookeknuth' in handle_lower or 'brooke' in handle_lower:
            return 'BrookeKnuth'
        else:
            return handle
    
    def _normalize_format(self, format_str: str) -> str:
        """
        Normalize format to standard format
        """
        format_lower = format_str.lower().strip()
        
        if 'video' in format_lower:
            return 'Video'
        elif 'carousel' in format_lower:
            return 'Carousel'
        elif 'collection' in format_lower:
            return 'Collection'
        elif 'static' in format_lower:
            return 'Static'
        elif 'gif' in format_lower:
            return 'GIF'
        elif 'image' in format_lower:
            return 'Image'
        else:
            return format_str.title()
    
    def _extract_category_from_text(self, text: str) -> str:
        """
        Extract category from free text using pattern matching
        """
        for category in self.categories:
            if category in text:
                return self._normalize_category(category)
        return ''
    
    def _extract_product_from_text(self, text: str) -> str:
        """
        Extract product from free text
        """
        for product in self.products:
            if product in text:
                return product.title()
        return ''
    
    def _extract_color_from_text(self, text: str) -> str:
        """
        Extract color from free text
        """
        for color in self.colors:
            if f' {color} ' in f' {text} ' or text.startswith(color) or text.endswith(color):
                return color.title()
        return ''
    
    def _extract_content_type_from_text(self, text: str) -> str:
        """
        Extract content type from free text
        """
        if 'whitelist' in text:
            return 'Whitelist'
        elif 'brand ugc' in text:
            return 'Brand UGC'
        elif 'brand' in text:
            return 'Brand'
        elif 'ugc' in text:
            return 'UGC'
        return ''
    
    def _extract_format_from_text(self, text: str) -> str:
        """
        Extract format from free text
        """
        # Check for specific formats in order of specificity
        if 'carousel' in text:
            return 'Carousel'
        elif 'collection' in text:
            return 'Collection'
        elif 'static' in text:
            return 'Static'
        elif 'gif' in text:
            return 'GIF'
        elif 'video' in text:
            return 'Video'
        elif 'image' in text:
            return 'Image'
        
        # Fallback to checking all formats
        for fmt in self.formats:
            if fmt in text:
                return self._normalize_format(fmt)
        return ''
    
    def _extract_handle_from_text(self, text: str) -> str:
        """
        Extract handle from free text
        """
        for handle in self.handles:
            if handle in text:
                return self._normalize_handle(handle)
        return ''
    
    def _clean_ad_name(self, ad_name: str) -> str:
        """
        Clean the ad name by removing date prefix and other extracted elements
        """
        # Remove date prefix
        cleaned = re.sub(r'^\d{1,2}/\d{1,2}/\d{4}\s*-?\s*', '', ad_name)
        
        # Remove common prefixes that might have been extracted
        prefixes_to_remove = [
            r'^(tumbling mat|bath|standing mat|play mat)\s*-?\s*',
            r'^(folklore|checks|multi|arden|wisp)\s*-?\s*',
            r'^(fog|biscuit|multi)\s*-?\s*',
            r'^(whitelist|brand|ugc|brand ugc)\s*-?\s*',
            r'^(hon|brookeknuth|sydnee)\s*-?\s*',
            r'^(video|image|collection|carousel)\s*-?\s*'
        ]
        
        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _parse_campaign_optimization(self, campaign_name: str) -> str:
        """
        Determine campaign optimization type from campaign name
        """
        if not campaign_name:
            return 'Standard'
        
        campaign_lower = campaign_name.lower()
        
        # Only detect as incremental if the word "incrementality" is present
        # Not just "incremental" which could be part of other words
        if 'incrementality' in campaign_lower:
            return 'Incremental'
        else:
            return 'Standard'
    
    def validate_parsing(self, ad_name: str, campaign_name: str = "", expected: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse and optionally validate against expected results
        """
        result = self.parse_ad_name(ad_name, campaign_name)
        
        if expected:
            validation_result = {'passed': True, 'errors': []}
            
            for key, expected_value in expected.items():
                if key in result:
                    if key == 'launch_date' and isinstance(expected_value, str):
                        # Convert expected string date to date object for comparison
                        try:
                            expected_date = self._parse_date(expected_value)
                            if result[key] != expected_date:
                                validation_result['passed'] = False
                                validation_result['errors'].append(f"{key}: expected {expected_date}, got {result[key]}")
                        except:
                            validation_result['passed'] = False
                            validation_result['errors'].append(f"{key}: could not parse expected date {expected_value}")
                    elif result[key] != expected_value:
                        validation_result['passed'] = False
                        validation_result['errors'].append(f"{key}: expected {expected_value}, got {result[key]}")
                else:
                    validation_result['passed'] = False
                    validation_result['errors'].append(f"Missing key: {key}")
            
            result['validation'] = validation_result
        
        return result