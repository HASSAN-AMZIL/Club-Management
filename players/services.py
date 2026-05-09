import json
import re
from io import BytesIO
from pathlib import Path
from urllib import error, request

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .utils import format_money


SCOUTING_REPORT_PROMPT = """You are a professional football scout analyst.

Write a short scouting report for the following player based ONLY on the data provided.

Rules:
- Keep it 3 to 5 lines maximum
- Be professional and realistic
- Mention strengths and weaknesses
- Mention playing style
- Do NOT add any invented facts
- Include club context

----------------------------------------

PLAYER DATA:

Name: {name}
Age: {age}
Position: {position}
Club: {club_name}
Price: {price}

Stats:
- Overall: {overall}
- Form: {form}
- Pace: {pace}
- Shooting: {shooting}
- Passing: {passing}
- Defense: {defense}
- Dribbling: {dribbling}

----------------------------------------

OUTPUT FORMAT:

Start directly with the report (no titles)."""


class ScoutingReportError(Exception):
    """Raised when a scouting report cannot be generated."""


def build_scouting_report_prompt(player, stats):
    return SCOUTING_REPORT_PROMPT.format(
        name=player.name,
        age=player.age,
        position=player.position,
        club_name=player.club.name,
        price=format_money(player.value),
        overall=stats.overall,
        form=stats.form,
        pace=stats.pace,
        shooting=stats.shooting,
        passing=stats.passing,
        defense=stats.defense,
        dribbling=stats.dribbling,
    )


def generate_scouting_report(player, stats):
    prompt = build_scouting_report_prompt(player, stats)
    payload = {
        'model': settings.OLLAMA_MODEL,
        'messages': [
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        'stream': False,
        'think': False,
    }

    api_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    request_body = json.dumps(payload).encode('utf-8')
    ollama_request = request.Request(
        api_url,
        data=request_body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with request.urlopen(ollama_request, timeout=settings.OLLAMA_TIMEOUT_SECONDS) as response:
            response_data = json.loads(response.read().decode('utf-8'))
    except error.HTTPError as exc:
        raise ScoutingReportError('Ollama returned an error while generating the report.') from exc
    except error.URLError as exc:
        raise ScoutingReportError('Ollama is not available. Please make sure it is running locally.') from exc
    except TimeoutError as exc:
        raise ScoutingReportError('Ollama took too long to generate the report. Please try again.') from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ScoutingReportError('Ollama returned an invalid response.') from exc

    report = response_data.get('message', {}).get('content', '')
    report = strip_thinking_output(report)

    if not report:
        raise ScoutingReportError('Ollama did not return a report.')

    return report


def strip_thinking_output(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE).strip()


def build_player_report_pdf(player, scouting_report=''):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
        pageCompression=0,
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name='ReportTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=30,
            textColor=colors.HexColor('#111827'),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#65A30D'),
            spaceBefore=14,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name='Body',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#111827'),
        )
    )

    story = []
    image_path = _resolve_player_image_path(player)

    title_block = [
        Paragraph(player.name, styles['ReportTitle']),
        Paragraph(f'{player.position} | Age {player.age} | {player.club.name}', styles['Body']),
        Paragraph(f'Market value: {format_money(player.value)}', styles['Body']),
    ]

    if image_path is not None:
        header = Table(
            [[Image(str(image_path), width=1.15 * inch, height=1.15 * inch), title_block]],
            colWidths=[1.35 * inch, 5.05 * inch],
        )
        header.setStyle(
            TableStyle(
                [
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ]
            )
        )
        story.append(header)
    else:
        story.extend(title_block)

    story.append(Spacer(1, 14))
    story.append(Paragraph('Player Details', styles['SectionTitle']))
    story.append(_details_table(
        [
            ('Name', player.name),
            ('Age', player.age),
            ('Position', player.position),
            ('Value', format_money(player.value)),
            ('Join Date', player.join_date),
            ('Club', player.club.name),
        ]
    ))

    story.append(Paragraph('Club Information', styles['SectionTitle']))
    league = getattr(player.club, 'league', None)
    story.append(_details_table(
        [
            ('Club', player.club.name),
            ('League', league.name if league else '-'),
            ('Country / City', f'{player.club.country}, {player.club.city}'),
            ('Budget', format_money(player.club.budget)),
        ]
    ))

    stats = getattr(player, 'stats', None)
    if stats is not None:
        story.append(Paragraph('Stats', styles['SectionTitle']))
        story.append(_details_table(
            [
                ('Overall', stats.overall),
                ('Form', stats.form),
                ('Pace', stats.pace),
                ('Shooting', stats.shooting),
                ('Passing', stats.passing),
                ('Defense', stats.defense),
                ('Dribbling', stats.dribbling),
            ]
        ))

    scouting_report = scouting_report.strip()
    if scouting_report:
        story.append(
            KeepTogether(
                [
                    Paragraph('AI Scouting Report', styles['SectionTitle']),
                    Paragraph(_escape_pdf_text(scouting_report), styles['Body']),
                ]
            )
        )

    doc.build(story)
    return buffer.getvalue()


def _details_table(rows):
    data = [[str(label), str(value)] for label, value in rows]
    table = Table(data, colWidths=[1.55 * inch, 4.85 * inch])
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111827')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEADING', (0, 0), (-1, -1), 13),
                ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#D1D5DB')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _resolve_player_image_path(player):
    image_url = player.image_url.strip()

    if not image_url or '://' in image_url:
        return None

    image_path = Path(settings.BASE_DIR) / 'source' / 'players' / image_url

    if image_path.is_file():
        return image_path

    return None


def _escape_pdf_text(text):
    return (
        text.replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('\n', '<br/>')
    )
