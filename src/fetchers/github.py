import re
import requests
from typing import Optional
from .base import BaseFetcher
from ..models import ProfileData, Platform

class GitHubFetcher(BaseFetcher):
    """Fetcher for GitHub profiles"""
    
    def can_handle(self, url: str) -> bool:
        return 'github.com' in url.lower()
    
    def extract_profile_data(self, url: str) -> Optional[ProfileData]:
        try:
            # Extract username from URL
            username_match = re.search(r'github\.com/([^/]+)', url)
            if not username_match:
                return None
            
            username = username_match.group(1)
            
            # Use GitHub API for reliable data
            api_url = f"https://api.github.com/users/{username}"
            response = self.session.get(api_url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Get recent repositories for content analysis
            repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
            repos_response = self.session.get(repos_url)
            repos_data = repos_response.json() if repos_response.status_code == 200 else []
            
            # Extract recent commit messages or repo descriptions
            posts_sample = []
            for repo in repos_data:
                if repo.get('description'):
                    posts_sample.append(f"Repo: {repo['name']} - {repo['description']}")
                
                # Get recent commits
                commits_url = f"https://api.github.com/repos/{username}/{repo['name']}/commits?per_page=3"
                commits_response = self.session.get(commits_url)
                if commits_response.status_code == 200:
                    commits = commits_response.json()
                    for commit in commits:
                        if commit.get('commit', {}).get('message'):
                            posts_sample.append(f"Commit: {commit['commit']['message']}")
            
            return ProfileData(
                platform=Platform.GITHUB,
                handle=data.get('login', username),
                name=self._clean_text(data.get('name')),
                bio=self._clean_text(data.get('bio')),
                location=self._clean_text(data.get('location')),
                followers=data.get('followers'),
                following=data.get('following'),
                verified=None,  # GitHub doesn't have verification badges
                posts_sample=posts_sample[:10],  # Limit to 10 samples
                profile_image_url=data.get('avatar_url'),
                website=data.get('blog'),
                joined_date=data.get('created_at'),
                company=self._clean_text(data.get('company')),
                email=data.get('email'),
                additional_data={
                    'public_repos': data.get('public_repos', 0),
                    'public_gists': data.get('public_gists', 0),
                    'hireable': data.get('hireable'),
                    'twitter_username': data.get('twitter_username'),
                }
            )
            
        except Exception as e:
            print(f"Error fetching GitHub profile: {e}")
            return None
