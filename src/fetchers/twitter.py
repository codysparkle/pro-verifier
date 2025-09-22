import re
from typing import Optional

from bs4 import BeautifulSoup

from ..models import Platform, ProfileData
from .base import BaseFetcher


class TwitterFetcher(BaseFetcher):
    """Fetcher for Twitter/X profiles"""

    def can_handle(self, url: str) -> bool:
        return any(domain in url.lower() for domain in ["twitter.com", "x.com"])

    def extract_profile_data(self, url: str) -> Optional[ProfileData]:
        try:
            # Extract username from URL
            username_match = re.search(r"(?:twitter\.com|x\.com)/([^/]+)", url)
            if not username_match:
                return None

            username = username_match.group(1)

            # Note: Twitter API requires authentication, so we'll use web scraping
            # In production, you'd want to use the official Twitter API v2
            response = self.session.get(url)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract basic profile information
            name = None
            bio = None
            followers = None
            following = None
            verified = False
            location = None
            website = None
            posts_sample = []

            # Try to extract name from title or meta tags
            title_tag = soup.find("title")
            if title_tag:
                title_text = title_tag.get_text()
                if " (@" in title_text:
                    name = title_text.split(" (@")[0].strip()

            # Look for meta tags with profile information
            for meta in soup.find_all("meta"):
                property_attr = meta.get("property", "")
                name_attr = meta.get("name", "")
                content = meta.get("content", "")

                if property_attr == "og:title" and not name:
                    if " (@" in content:
                        name = content.split(" (@")[0].strip()
                elif property_attr == "og:description":
                    bio = self._clean_text(content)
                elif name_attr == "description" and not bio:
                    bio = self._clean_text(content)

            # Try to extract tweet text as samples
            tweet_elements = soup.find_all(
                ["div", "span"], string=re.compile(r".{10,}")
            )
            for element in tweet_elements[:5]:  # Limit to first 5
                text = self._clean_text(element.get_text())
                if text and len(text) > 10 and len(text) < 280:
                    posts_sample.append(text)

            # Look for verified badge indicators
            if soup.find("svg", {"aria-label": "Verified account"}):
                verified = True

            return ProfileData(
                platform=Platform.TWITTER,
                handle=f"@{username}",
                name=name,
                bio=bio,
                location=location,
                followers=followers,
                following=following,
                verified=verified,
                posts_sample=posts_sample,
                website=website,
                additional_data={
                    "scraped_from_web": True,
                    "note": "Limited data due to Twitter API restrictions",
                },
            )

        except Exception as e:
            print(f"Error fetching Twitter profile: {e}")
            return None
