from abc import ABC, abstractmethod
from typing import Optional
import re
import requests
from bs4 import BeautifulSoup
from ..models import ProfileData, Platform

class BaseFetcher(ABC):
    """Base class for all profile fetchers"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this fetcher can handle the given URL"""
        pass
    
    @abstractmethod
    def extract_profile_data(self, url: str) -> Optional[ProfileData]:
        """Extract profile data from the given URL"""
        pass
    
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean and normalize text"""
        if not text:
            return None
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text (e.g., '1.2K followers' -> 1200)"""
        if not text:
            return None
        
        text = text.lower().replace(',', '')
        
        # Handle K, M suffixes
        multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                try:
                    number = float(re.findall(r'\d+\.?\d*', text)[0])
                    return int(number * multiplier)
                except (IndexError, ValueError):
                    continue
        
        # Extract plain number
        try:
            return int(re.findall(r'\d+', text)[0])
        except (IndexError, ValueError):
            return None
