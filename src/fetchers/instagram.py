import re
import requests
from typing import Optional
from bs4 import BeautifulSoup
from .base import BaseFetcher
from ..models import ProfileData, Platform

class InstagramFetcher(BaseFetcher):
    """Fetcher for Instagram profiles"""
    
    def can_handle(self, url: str) -> bool:
        return 'instagram.com' in url.lower()
    
    def extract_profile_data(self, url: str) -> Optional[ProfileData]:
        try:
            # Extract username from URL
            username_match = re.search(r'instagram\.com/([^/]+)', url)
            if not username_match:
                return None
            
            username = username_match.group(1)
            
            response = self.session.get(url)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic profile information
            name = None
            bio = None
            followers = None
            following = None
            verified = False
            posts_count = None
            
            # Try to extract from meta tags
            for meta in soup.find_all('meta'):
                property_attr = meta.get('property', '')
                name_attr = meta.get('name', '')
                content = meta.get('content', '')
                
                if property_attr == 'og:title':
                    # Instagram titles usually contain name and handle
                    if ' (@' in content:
                        name = content.split(' (@')[0].strip()
                elif property_attr == 'og:description':
                    bio = self._clean_text(content)
                elif name_attr == 'description' and not bio:
                    bio = self._clean_text(content)
            
            # Try to extract structured data from script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        import json
                        # Extract JSON data from Instagram's shared data
                        json_str = script.string
                        start = json_str.find('{')
                        end = json_str.rfind('}') + 1
                        if start >= 0 and end > start:
                            data = json.loads(json_str[start:end])
                            
                            # Navigate through Instagram's data structure
                            entry_data = data.get('entry_data', {})
                            profile_page = entry_data.get('ProfilePage', [{}])[0]
                            graphql = profile_page.get('graphql', {})
                            user = graphql.get('user', {})
                            
                            if user:
                                if not name:
                                    name = user.get('full_name')
                                if not bio:
                                    bio = user.get('biography')
                                followers = user.get('edge_followed_by', {}).get('count')
                                following = user.get('edge_follow', {}).get('count')
                                verified = user.get('is_verified', False)
                                posts_count = user.get('edge_owner_to_timeline_media', {}).get('count')
                    except:
                        continue
            
            # Look for verification badge
            if soup.find('span', {'aria-label': 'Verified'}):
                verified = True
            
            return ProfileData(
                platform=Platform.INSTAGRAM,
                handle=f"@{username}",
                name=name,
                bio=bio,
                followers=followers,
                following=following,
                verified=verified,
                posts_sample=[],  # Posts require more complex extraction
                additional_data={
                    'posts_count': posts_count,
                    'scraped_from_web': True,
                    'note': 'Limited data due to Instagram restrictions'
                }
            )
            
        except Exception as e:
            print(f"Error fetching Instagram profile: {e}")
            return None
