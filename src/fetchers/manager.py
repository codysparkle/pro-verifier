from typing import List, Optional

from ..models import ProfileData
from .github import GitHubFetcher
from .instagram import InstagramFetcher
from .linkedin import LinkedInFetcher
from .twitter import TwitterFetcher


class FetcherManager:
    """Manages all profile fetchers and routes URLs to appropriate handlers"""

    def __init__(self):
        self.fetchers = [
            GitHubFetcher(),
            TwitterFetcher(),
            LinkedInFetcher(),
            InstagramFetcher(),
        ]

    def fetch_profile(self, url: str) -> Optional[ProfileData]:
        """Fetch profile data from a URL using the appropriate fetcher"""
        for fetcher in self.fetchers:
            if fetcher.can_handle(url):
                try:
                    return fetcher.extract_profile_data(url)
                except Exception as e:
                    print(
                        f"Error fetching {url} with {fetcher.__class__.__name__}: {e}"
                    )
                    return None

        print(f"No fetcher available for URL: {url}")
        return None

    def fetch_multiple_profiles(self, urls: List[str]) -> List[ProfileData]:
        """Fetch data from multiple profile URLs"""
        profiles = []
        for url in urls:
            profile = self.fetch_profile(url)
            if profile:
                profiles.append(profile)
            else:
                print(f"Failed to fetch profile from: {url}")

        return profiles
