import json
import re
from urllib import error, request

from django.conf import settings


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
        price=player.value,
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
