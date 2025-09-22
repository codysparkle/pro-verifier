import os
import json
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
from .models import ProfileData, VerificationReport, TrustScore, Discrepancy, Platform

load_dotenv()

class GeminiAnalyzer:
    """Analyzes profile data using Google Gemini API"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_profiles(self, profiles: List[ProfileData]) -> VerificationReport:
        """Analyze multiple profiles and generate verification report"""
        
        # Prepare data for Gemini
        profiles_json = []
        for profile in profiles:
            profiles_json.append(profile.model_dump())
        
        prompt = self._build_analysis_prompt(profiles_json)
        
        try:
            response = self.model.generate_content(prompt)
            analysis_result = self._parse_gemini_response(response.text, profiles)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error analyzing profiles with Gemini: {e}")
            # Return fallback analysis
            return self._create_fallback_report(profiles)
    
    def _build_analysis_prompt(self, profiles_data: List[dict]) -> str:
        """Build structured prompt for Gemini analysis"""
        
        prompt = """You are a social profile verification system designed to analyze and cross-verify user profiles across multiple platforms.

TASK: Analyze the following normalized profile data and provide a comprehensive verification report.

ANALYSIS GOALS:
1. Determine if all profiles likely belong to the same person/organization (confidence: 0-100)
2. Identify discrepancies between profiles (name, bio, location, job title, etc.)
3. Assess reputation signals (follower quality, engagement, credibility indicators)
4. Calculate trust scores across multiple dimensions
5. Detect potential red flags (inconsistencies, suspicious activity, fake profiles)
6. Highlight strengths and positive signals
7. Provide reasoning with specific citations from the data

PROFILE DATA:
```json
""" + json.dumps(profiles_data, indent=2) + """
```

Please provide your analysis in the following JSON format (ensure valid JSON syntax):

```json
{
  "same_person_confidence": [0-100 integer],
  "trust_score": {
    "overall": [0-100 integer],
    "reputation": [0-100 integer],
    "consistency": [0-100 integer],
    "content_quality": [0-100 integer]
  },
  "consistency_score": [0-100 integer],
  "discrepancies": [
    {
      "field": "name/bio/location/job_title/etc",
      "platforms": ["platform1", "platform2"],
      "values": {
        "platform1": "value1",
        "platform2": "value2"
      },
      "severity": "low/medium/high"
    }
  ],
  "red_flags": [
    "List of concerning findings with specific examples"
  ],
  "strengths": [
    "List of positive signals and credibility indicators"
  ],
  "citations": [
    "Specific examples from the data that support your analysis"
  ],
  "analysis_summary": "Detailed summary of your findings and reasoning"
}
```

ANALYSIS GUIDELINES:
- Be thorough but concise
- Focus on factual observations from the provided data
- Consider platform-specific norms (GitHub for technical profiles, LinkedIn for professional, etc.)
- Look for patterns that suggest authenticity vs. fabrication
- Consider follower counts, verification status, content quality, and cross-platform consistency
- Highlight both positive and negative indicators
- Provide specific examples and citations from the data"""

        return prompt
    
    def _parse_gemini_response(self, response_text: str, profiles: List[ProfileData]) -> VerificationReport:
        """Parse Gemini's JSON response into VerificationReport"""
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                # Parse discrepancies
                discrepancies = []
                for disc in data.get('discrepancies', []):
                    discrepancies.append(Discrepancy(
                        field=disc['field'],
                        platforms=[Platform(p) for p in disc['platforms']],
                        values={Platform(k): v for k, v in disc['values'].items()},
                        severity=disc['severity']
                    ))
                
                # Create trust score
                trust_data = data.get('trust_score', {})
                trust_score = TrustScore(
                    overall=trust_data.get('overall', 50),
                    reputation=trust_data.get('reputation', 50),
                    consistency=trust_data.get('consistency', 50),
                    content_quality=trust_data.get('content_quality', 50)
                )
                
                return VerificationReport(
                    trust_score=trust_score,
                    profiles_analyzed=profiles,
                    consistency_score=data.get('consistency_score', 50),
                    discrepancies=discrepancies,
                    red_flags=data.get('red_flags', []),
                    strengths=data.get('strengths', []),
                    citations=data.get('citations', []),
                    analysis_summary=data.get('analysis_summary', ''),
                    same_person_confidence=data.get('same_person_confidence', 50)
                )
            
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
        
        return self._create_fallback_report(profiles)
    
    def _create_fallback_report(self, profiles: List[ProfileData]) -> VerificationReport:
        """Create a basic fallback report when Gemini analysis fails"""
        
        trust_score = TrustScore(
            overall=50,
            reputation=50,
            consistency=50,
            content_quality=50
        )
        
        # Basic consistency check
        names = [p.name for p in profiles if p.name]
        consistency = 80 if len(set(names)) <= 1 else 30
        
        return VerificationReport(
            trust_score=trust_score,
            profiles_analyzed=profiles,
            consistency_score=consistency,
            discrepancies=[],
            red_flags=["Analysis unavailable - using fallback assessment"],
            strengths=["Multiple platforms present"],
            citations=[],
            analysis_summary="Fallback analysis due to API error. Manual review recommended.",
            same_person_confidence=50
        )
