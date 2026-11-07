import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


def _inline(text):
    text = escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


@register.filter(name='format_task')
def format_task(value):
    """Tapşırıq şərtini HTML-ə çevirir: ## başlıq, - siyahı, **qalın**, `kod`, ``` kod bloku."""
    html = []
    in_code = False
    in_list = False
    code_lines = []
    para = []

    def close_list():
        nonlocal in_list
        if in_list:
            html.append('</ul>')
            in_list = False

    def flush_para():
        if para:
            html.append('<p>' + '<br>'.join(_inline(p) for p in para) + '</p>')
            para.clear()

    for line in (value or '').split('\n'):
        if line.strip() == '```':
            if in_code:
                html.append('<pre class="task-code"><code>' + escape('\n'.join(code_lines)) + '</code></pre>')
                code_lines = []
                in_code = False
            else:
                flush_para(); close_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        s = line.strip()
        if not s:
            flush_para(); close_list()
        elif s.startswith('## '):
            flush_para(); close_list()
            html.append('<h4 class="task-h">' + _inline(s[3:]) + '</h4>')
        elif s.startswith('- '):
            flush_para()
            if not in_list:
                html.append('<ul class="task-list">')
                in_list = True
            html.append('<li>' + _inline(s[2:]) + '</li>')
        else:
            close_list()
            para.append(s)
    flush_para(); close_list()
    return mark_safe(''.join(html))