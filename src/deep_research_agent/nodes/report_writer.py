USER_PROMPT_TEMPLATE = """
User question:
{query}

Report outline:
{outline_json}

Approved evidence:
{evidence_json}

Write the report using only the approved evidence.
"""
