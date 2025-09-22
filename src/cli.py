#!/usr/bin/env python3
import click
import json
import os
import sys
from typing import List
from .models import VerificationRequest
from .fetchers.manager import FetcherManager
from .analyzer import GeminiAnalyzer
from .report_generator import ReportGenerator

@click.command()
@click.option('--profiles', '-p', help='JSON string of profile URLs or path to JSON file')
@click.option('--output-dir', '-o', default='./reports', help='Output directory for reports')
@click.option('--format', '-f', type=click.Choice(['markdown', 'pdf', 'both']), default='both', 
              help='Output format (markdown, pdf, or both)')
@click.option('--user-id', '-u', help='Optional user identifier')
def verify_profiles(profiles: str, output_dir: str, format: str, user_id: str):
    """Social Profile Verification Tool
    
    Analyze social media profiles across platforms and generate trust reports.
    
    Examples:
    
    \b
    # From JSON string
    python -m src.cli --profiles '{"profiles": ["https://github.com/username", "https://linkedin.com/in/username"]}'
    
    \b  
    # From JSON file
    python -m src.cli --profiles profiles.json
    
    \b
    # Specify output format
    python -m src.cli --profiles profiles.json --format pdf --output-dir ./my_reports
    """
    
    try:
        # Parse profiles input
        profile_urls = _parse_profiles_input(profiles)
        if not profile_urls:
            click.echo("❌ No valid profile URLs found. Please provide profiles in JSON format.", err=True)
            sys.exit(1)
        
        click.echo(f"🔍 Starting verification for {len(profile_urls)} profiles...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        fetcher_manager = FetcherManager()
        analyzer = GeminiAnalyzer()
        report_generator = ReportGenerator()
        
        # Step 1: Fetch profile data
        click.echo("📥 Fetching profile data...")
        profiles_data = fetcher_manager.fetch_multiple_profiles(profile_urls)
        
        if not profiles_data:
            click.echo("❌ Failed to fetch any profile data. Please check the URLs.", err=True)
            sys.exit(1)
        
        click.echo(f"✅ Successfully fetched data from {len(profiles_data)} profiles")
        
        # Step 2: Analyze with Gemini
        click.echo("🤖 Analyzing profiles with Gemini AI...")
        verification_report = analyzer.analyze_profiles(profiles_data)
        
        # Step 3: Generate reports
        timestamp = _get_timestamp()
        user_suffix = f"_{user_id}" if user_id else ""
        
        reports_generated = []
        
        if format in ['markdown', 'both']:
            markdown_path = os.path.join(output_dir, f"verification_report{user_suffix}_{timestamp}.md")
            click.echo(f"📝 Generating Markdown report: {markdown_path}")
            report_generator.generate_markdown_report(verification_report, markdown_path)
            reports_generated.append(markdown_path)
        
        if format in ['pdf', 'both']:
            pdf_path = os.path.join(output_dir, f"verification_report{user_suffix}_{timestamp}.pdf")
            click.echo(f"📄 Generating PDF report: {pdf_path}")
            report_generator.generate_pdf_report(verification_report, pdf_path)
            reports_generated.append(pdf_path)
        
        # Display summary
        _display_summary(verification_report, reports_generated)
        
    except Exception as e:
        click.echo(f"❌ Error during verification: {str(e)}", err=True)
        sys.exit(1)

def _parse_profiles_input(profiles_input: str) -> List[str]:
    """Parse profiles input from JSON string or file path"""
    if not profiles_input:
        return []
    
    try:
        # Try to parse as JSON string first
        if profiles_input.startswith('{'):
            data = json.loads(profiles_input)
        else:
            # Try to read as file path
            with open(profiles_input, 'r') as f:
                data = json.load(f)
        
        if isinstance(data, dict) and 'profiles' in data:
            return data['profiles']
        elif isinstance(data, list):
            return data
        else:
            return []
            
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        # Try to treat as single URL
        if profiles_input.startswith('http'):
            return [profiles_input]
        return []

def _get_timestamp() -> str:
    """Get current timestamp for file naming"""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _display_summary(report, report_paths: List[str]):
    """Display verification summary"""
    click.echo("\n" + "="*60)
    click.echo("🎯 VERIFICATION SUMMARY")
    click.echo("="*60)
    
    # Trust score with color coding
    overall_score = report.trust_score.overall
    if overall_score >= 80:
        score_color = 'green'
        emoji = '🟢'
    elif overall_score >= 60:
        score_color = 'yellow'
        emoji = '🟡'
    elif overall_score >= 40:
        score_color = 'red'
        emoji = '🟠'
    else:
        score_color = 'red'
        emoji = '🔴'
    
    click.echo(f"\n{emoji} Overall Trust Score: ", nl=False)
    click.secho(f"{overall_score}/100", fg=score_color, bold=True)
    
    click.echo(f"🤝 Same Person Confidence: {report.same_person_confidence}%")
    click.echo(f"📊 Profiles Analyzed: {len(report.profiles_analyzed)}")
    
    # Show platforms
    platforms = [p.platform.value.title() for p in report.profiles_analyzed]
    click.echo(f"🌐 Platforms: {', '.join(platforms)}")
    
    # Red flags count
    if report.red_flags:
        click.echo(f"🚩 Red Flags: {len(report.red_flags)}")
    
    # Strengths count
    if report.strengths:
        click.echo(f"✅ Strengths: {len(report.strengths)}")
    
    # Reports generated
    click.echo(f"\n📋 Reports Generated:")
    for path in report_paths:
        click.echo(f"   • {path}")
    
    # Quick analysis preview
    if report.analysis_summary:
        click.echo(f"\n📝 Quick Analysis:")
        summary_preview = report.analysis_summary[:200] + "..." if len(report.analysis_summary) > 200 else report.analysis_summary
        click.echo(f"   {summary_preview}")
    
    click.echo("\n" + "="*60)
    click.echo("✨ Verification complete! Check the generated reports for detailed analysis.")

if __name__ == '__main__':
    verify_profiles()
