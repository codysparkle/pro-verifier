import os
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import VerificationReport


class ReportGenerator:
    """Generates verification reports in Markdown and PDF formats"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom styles for PDF generation"""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.darkblue,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="ScoreStyle",
                parent=self.styles["Normal"],
                fontSize=24,
                alignment=1,  # Center alignment
                textColor=colors.darkgreen,
            )
        )

    def generate_markdown_report(
        self, report: VerificationReport, output_path: Optional[str] = None
    ) -> str:
        """Generate a Markdown verification report"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Determine overall trust level
        overall_score = report.trust_score.overall
        trust_level = self._get_trust_level(overall_score)
        trust_emoji = self._get_trust_emoji(overall_score)

        markdown_content = f"""# Social Profile Verification Report {trust_emoji}

**Generated:** {timestamp}
**Profiles Analyzed:** {len(report.profiles_analyzed)}
**Same Person Confidence:** {report.same_person_confidence}%

---

## 🎯 Trust Score: {overall_score}/100 ({trust_level})

| Metric | Score | Assessment |
|--------|-------|------------|
| **Overall Trust** | {report.trust_score.overall}/100 | {self._get_assessment(report.trust_score.overall)} |
| **Reputation** | {report.trust_score.reputation}/100 | {self._get_assessment(report.trust_score.reputation)} |
| **Consistency** | {report.trust_score.consistency}/100 | {self._get_assessment(report.trust_score.consistency)} |
| **Content Quality** | {report.trust_score.content_quality}/100 | {self._get_assessment(report.trust_score.content_quality)} |

---

## 📊 Profile Summary

| Platform | Handle | Name | Verified | Followers |
|----------|--------|------|----------|-----------|
"""

        # Add profile data table
        for profile in report.profiles_analyzed:
            verified_icon = (
                "✅" if profile.verified else "❌" if profile.verified is False else "❔"
            )
            followers = f"{profile.followers:,}" if profile.followers else "N/A"
            name = profile.name or "N/A"

            markdown_content += f"| {profile.platform.value.title()} | {profile.handle} | {name} | {verified_icon} | {followers} |\n"

        markdown_content += "\n---\n\n"

        # Analysis Summary
        markdown_content += f"""## 📝 Analysis Summary

{report.analysis_summary}

---

"""

        # Consistency Analysis
        if report.discrepancies:
            markdown_content += "## ⚠️ Discrepancies Detected\n\n"
            for disc in report.discrepancies:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    disc.severity, "❔"
                )
                platforms_str = ", ".join([p.value.title() for p in disc.platforms])

                markdown_content += f"### {severity_emoji} {disc.field.replace('_', ' ').title()} Mismatch ({disc.severity.upper()})\n\n"
                markdown_content += f"**Platforms:** {platforms_str}\n\n"

                for platform, value in disc.values.items():
                    markdown_content += f"- **{platform.value.title()}:** {value}\n"

                markdown_content += "\n"

        # Red Flags
        if report.red_flags:
            markdown_content += "## 🚩 Red Flags\n\n"
            for flag in report.red_flags:
                markdown_content += f"- {flag}\n"
            markdown_content += "\n"

        # Strengths
        if report.strengths:
            markdown_content += "## ✅ Strengths\n\n"
            for strength in report.strengths:
                markdown_content += f"- {strength}\n"
            markdown_content += "\n"

        # Citations
        if report.citations:
            markdown_content += "## 📚 Citations & Evidence\n\n"
            for i, citation in enumerate(report.citations, 1):
                markdown_content += f"{i}. {citation}\n"
            markdown_content += "\n"

        # Footer
        markdown_content += """---

## ⚡ How to Interpret This Report

- **Trust Score (0-100):** Higher scores indicate more trustworthy and consistent profiles
- **Same Person Confidence:** Likelihood that all profiles belong to the same individual
- **Red Flags:** Concerning patterns that may indicate fake or compromised accounts
- **Strengths:** Positive signals that support authenticity and credibility

*This report was generated using automated analysis. Manual verification is recommended for high-stakes decisions.*
"""

        # Save to file if path provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

        return markdown_content

    def generate_pdf_report(self, report: VerificationReport, output_path: str) -> None:
        """Generate a PDF verification report"""

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Build story (content)
        story = []

        # Title
        title = Paragraph(
            "Social Profile Verification Report", self.styles["CustomTitle"]
        )
        story.append(title)
        story.append(Spacer(1, 20))

        # Metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta_data = [
            ["Generated:", timestamp],
            ["Profiles Analyzed:", str(len(report.profiles_analyzed))],
            ["Same Person Confidence:", f"{report.same_person_confidence}%"],
        ]

        meta_table = Table(meta_data, colWidths=[2 * inch, 3 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(meta_table)
        story.append(Spacer(1, 20))

        # Trust Score Section
        story.append(Paragraph("Trust Score", self.styles["SectionHeader"]))

        overall_score = report.trust_score.overall
        trust_level = self._get_trust_level(overall_score)

        score_para = Paragraph(f"{overall_score}/100", self.styles["ScoreStyle"])
        story.append(score_para)

        level_para = Paragraph(f"<b>{trust_level}</b>", self.styles["Normal"])
        story.append(level_para)
        story.append(Spacer(1, 15))

        # Trust Score Breakdown
        trust_data = [
            ["Metric", "Score", "Assessment"],
            [
                "Overall Trust",
                f"{report.trust_score.overall}/100",
                self._get_assessment(report.trust_score.overall),
            ],
            [
                "Reputation",
                f"{report.trust_score.reputation}/100",
                self._get_assessment(report.trust_score.reputation),
            ],
            [
                "Consistency",
                f"{report.trust_score.consistency}/100",
                self._get_assessment(report.trust_score.consistency),
            ],
            [
                "Content Quality",
                f"{report.trust_score.content_quality}/100",
                self._get_assessment(report.trust_score.content_quality),
            ],
        ]

        trust_table = Table(trust_data, colWidths=[1.5 * inch, 1 * inch, 2 * inch])
        trust_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(trust_table)
        story.append(Spacer(1, 20))

        # Profile Summary
        story.append(Paragraph("Profile Summary", self.styles["SectionHeader"]))

        profile_data = [["Platform", "Handle", "Name", "Verified", "Followers"]]
        for profile in report.profiles_analyzed:
            verified_text = (
                "Yes"
                if profile.verified
                else "No"
                if profile.verified is False
                else "Unknown"
            )
            followers = f"{profile.followers:,}" if profile.followers else "N/A"
            name = profile.name or "N/A"

            profile_data.append(
                [
                    profile.platform.value.title(),
                    profile.handle,
                    name,
                    verified_text,
                    followers,
                ]
            )

        profile_table = Table(
            profile_data,
            colWidths=[1 * inch, 1.5 * inch, 1.5 * inch, 0.8 * inch, 0.7 * inch],
        )
        profile_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(profile_table)
        story.append(Spacer(1, 15))

        # Analysis Summary
        if report.analysis_summary:
            story.append(Paragraph("Analysis Summary", self.styles["SectionHeader"]))
            summary_para = Paragraph(report.analysis_summary, self.styles["Normal"])
            story.append(summary_para)
            story.append(Spacer(1, 15))

        # Red Flags
        if report.red_flags:
            story.append(Paragraph("Red Flags", self.styles["SectionHeader"]))
            for flag in report.red_flags:
                flag_para = Paragraph(f"• {flag}", self.styles["Normal"])
                story.append(flag_para)
            story.append(Spacer(1, 10))

        # Strengths
        if report.strengths:
            story.append(Paragraph("Strengths", self.styles["SectionHeader"]))
            for strength in report.strengths:
                strength_para = Paragraph(f"• {strength}", self.styles["Normal"])
                story.append(strength_para)
            story.append(Spacer(1, 10))

        # Build PDF
        doc.build(story)

    def _get_trust_level(self, score: int) -> str:
        """Get trust level description based on score"""
        if score >= 80:
            return "High Trust"
        elif score >= 60:
            return "Moderate Trust"
        elif score >= 40:
            return "Low Trust"
        else:
            return "Very Low Trust"

    def _get_trust_emoji(self, score: int) -> str:
        """Get emoji based on trust score"""
        if score >= 80:
            return "🟢"
        elif score >= 60:
            return "🟡"
        elif score >= 40:
            return "🟠"
        else:
            return "🔴"

    def _get_assessment(self, score: int) -> str:
        """Get assessment text based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
