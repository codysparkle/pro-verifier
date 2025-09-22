# Social Profile Verification Tool 🔍

A powerful AI-powered tool that analyzes and cross-verifies social media profiles across multiple platforms using Google Gemini API. Generate comprehensive trust reports with reputation scoring, consistency analysis, and fraud detection.

## Features ✨

- **Multi-Platform Support**: GitHub, LinkedIn, Twitter/X, Instagram
- **AI-Powered Analysis**: Uses Google Gemini for intelligent profile comparison
- **Trust Scoring**: Comprehensive 0-100 scoring across multiple dimensions
- **Fraud Detection**: Identifies discrepancies and suspicious patterns
- **Report Generation**: Beautiful Markdown and PDF reports
- **Extensible Architecture**: Easy to add new platforms

## Installation 🚀

1. **Clone the repository:**
```bash
git clone <repository-url>
cd ProVerifer
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Get a Gemini API key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

## Quick Start 🏃‍♂️

### Command Line Usage

**Basic verification:**
```bash
python main.py --profiles '{"profiles": ["https://github.com/username", "https://linkedin.com/in/username"]}'
```

**From JSON file:**
```bash
# Create profiles.json
echo '{"profiles": ["https://github.com/octocat", "https://twitter.com/github"]}' > profiles.json

python main.py --profiles profiles.json
```

**Advanced options:**
```bash
python main.py \
  --profiles profiles.json \
  --output-dir ./my_reports \
  --format pdf \
  --user-id john_doe
```

### Sample JSON Input

```json
{
  "profiles": [
    "https://github.com/octocat",
    "https://linkedin.com/in/octocat",
    "https://twitter.com/github",
    "https://instagram.com/github"
  ]
}
```

## CLI Options 📋

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--profiles` | `-p` | JSON string or file path with profile URLs | Required |
| `--output-dir` | `-o` | Output directory for reports | `./reports` |
| `--format` | `-f` | Output format: `markdown`, `pdf`, or `both` | `both` |
| `--user-id` | `-u` | Optional user identifier for file naming | None |

## Report Output 📊

The tool generates comprehensive reports with:

### Trust Score Breakdown
- **Overall Trust** (0-100): Combined reliability assessment
- **Reputation** (0-100): Follower quality, verification badges, mentions
- **Consistency** (0-100): Cross-platform data alignment
- **Content Quality** (0-100): Authenticity and spam likelihood

### Analysis Sections
- **Profile Summary**: Key metrics across all platforms
- **Discrepancy Detection**: Conflicting information between profiles  
- **Red Flags**: Suspicious patterns and potential fraud indicators
- **Strengths**: Positive credibility signals
- **Citations**: Evidence and examples from profile data

## Architecture 🏗️

```
ProVerifer/
├── src/
│   ├── fetchers/          # Platform-specific data extraction
│   │   ├── base.py        # Base fetcher class
│   │   ├── github.py      # GitHub API integration
│   │   ├── linkedin.py    # LinkedIn scraper
│   │   ├── twitter.py     # Twitter/X scraper
│   │   ├── instagram.py   # Instagram scraper
│   │   └── manager.py     # Fetcher orchestration
│   ├── models.py          # Pydantic data models
│   ├── analyzer.py        # Gemini AI integration
│   ├── report_generator.py # Markdown/PDF generation
│   └── cli.py            # Command-line interface
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── .env                 # Environment variables
```

## Supported Platforms 🌐

| Platform | Data Available | API/Scraping | Verification Status |
|----------|----------------|---------------|-------------------|
| **GitHub** | ✅ Full | API | N/A |
| **LinkedIn** | ⚠️ Limited | Scraping | Premium only |
| **Twitter/X** | ⚠️ Limited | Scraping | Available |
| **Instagram** | ⚠️ Limited | Scraping | Available |

*Note: Some platforms have anti-scraping measures. For production use, consider official APIs where available.*

## Adding New Platforms 🔧

1. Create a new fetcher in `src/fetchers/`:
```python
from .base import BaseFetcher
from ..models import ProfileData, Platform

class CustomFetcher(BaseFetcher):
    def can_handle(self, url: str) -> bool:
        return 'custom.com' in url.lower()
    
    def extract_profile_data(self, url: str) -> ProfileData:
        # Implementation here
        pass
```

2. Add to `Platform` enum in `models.py`:
```python
class Platform(str, Enum):
    CUSTOM = "custom"
```

3. Register in `FetcherManager`:
```python
self.fetchers = [
    # ... existing fetchers
    CustomFetcher(),
]
```

## Limitations ⚠️

- **Rate Limits**: Respect platform rate limiting and terms of service
- **Data Availability**: Some platforms restrict public data access
- **Anti-Scraping**: LinkedIn and Instagram have strong anti-bot measures
- **API Costs**: Gemini API usage incurs costs based on token consumption

## Best Practices 💡

1. **API Keys**: Never commit API keys to version control
2. **Rate Limiting**: Add delays between requests for large batches
3. **Error Handling**: Always handle network failures gracefully  
4. **Data Privacy**: Only analyze publicly available information
5. **Legal Compliance**: Respect platform terms of service and local laws

## Troubleshooting 🔧

### Common Issues

**"No fetcher available for URL"**
- Ensure URL format is correct (e.g., `https://github.com/username`)
- Check if platform is supported

**"Error fetching profile"**
- Profile may be private or deleted
- Platform may be blocking requests
- Check internet connection

**"Gemini API error"**
- Verify `GEMINI_API_KEY` in `.env` file
- Check API quota and billing
- Ensure stable internet connection

### Debug Mode
```bash
# Add verbose logging
export PYTHONPATH=/path/to/ProVerifer/src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from src.cli import verify_profiles
verify_profiles()
" --profiles 'your-json-here'
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Security 🔒

- Never log or expose API keys
- Only process publicly available profile data
- Sanitize all user inputs
- Use HTTPS for all external requests

## Roadmap 🗺️

- [ ] **Enhanced Platform Support**: TikTok, YouTube, Medium
- [ ] **Real-time Monitoring**: Track profile changes over time
- [ ] **Batch Processing**: Handle large CSV files efficiently
- [ ] **Web Interface**: Browser-based UI for non-technical users
- [ ] **API Server**: REST API for integration with other tools
- [ ] **Machine Learning**: Custom fraud detection models

---

**Made with ❤️ for secure profile verification**
