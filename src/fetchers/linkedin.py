import re
import requests
from typing import Optional
from bs4 import BeautifulSoup
from .base import BaseFetcher
from ..models import ProfileData, Platform

class LinkedInFetcher(BaseFetcher):
    """Fetcher for LinkedIn profiles"""
    
    def can_handle(self, url: str) -> bool:
        return 'linkedin.com' in url.lower()
    
    def extract_profile_data(self, url: str) -> Optional[ProfileData]:
        try:
            # Extract username from URL
            username_match = re.search(r'linkedin\.com/in/([^/]+)', url)
            if not username_match:
                return None
            
            username = username_match.group(1)
            
            # LinkedIn heavily restricts scraping, so we'll do basic extraction
            response = self.session.get(url)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information from meta tags and page structure
            name = None
            bio = None
            location = None
            company = None
            job_title = None
            
            # Try to extract from title tag
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text()
                # LinkedIn titles usually contain name and job title
                if ' | ' in title_text:
                    parts = title_text.split(' | ')
                    name = parts[0].strip()
                    if len(parts) > 1:
                        job_title = parts[1].strip()
            
            # Look for meta tags
            for meta in soup.find_all('meta'):
                property_attr = meta.get('property', '')
                name_attr = meta.get('name', '')
                content = meta.get('content', '')
                
                if property_attr == 'og:title' and not name:
                    if ' | ' in content:
                        name = content.split(' | ')[0].strip()
                elif property_attr == 'og:description':
                    bio = self._clean_text(content)
                elif name_attr == 'description' and not bio:
                    bio = self._clean_text(content)
            
            # Try to extract structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') == 'Person':
                            if not name and data.get('name'):
                                name = data['name']
                            if not job_title and data.get('jobTitle'):
                                job_title = data['jobTitle']
                            if not company and data.get('worksFor', {}).get('name'):
                                company = data['worksFor']['name']
                except:
                    continue
            
            return ProfileData(
                platform=Platform.LINKEDIN,
                handle=username,
                name=name,
                bio=bio,
                location=location,
                company=company,
                job_title=job_title,
                verified=None,  # LinkedIn verification is premium-only
                posts_sample=[],  # Posts require authentication
                additional_data={
                    'scraped_from_web': True,
                    'note': 'Limited data due to LinkedIn anti-scraping measures'
                }
            )
            
        except Exception as e:
            print(f"Error fetching LinkedIn profile: {e}")
            return None
