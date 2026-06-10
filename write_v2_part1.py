import re

with open('index_v1_backup.html', 'r', encoding='utf-8') as f:
    v1 = f.read()

lines = v1.split('\n')

def get_lines(start, end):
    return '\n'.join(lines[start-1:end])

# 提取关键块
css1_content = get_lines(15, 600)  # 主 CSS
tools_html = get_lines(895, 1039)  # 工具区 HTML
css2_content = get_lines(1080, 1209)  # 工具区 CSS
notes_data = get_lines(1213, 1255)  # TOP_NOTES + renderTopNotes
api_keys = get_lines(1599, 1601)   # API keys
form_funcs = get_lines(1346, 1498) # getFormData 等函数
audit_func = get_lines(1609, 1690) # runAudit

print(f"css1={len(css1_content)}, tools={len(tools_html)}, css2={len(css2_content)}, notes={len(notes_data)}, keys={len(api_keys)}, funcs={len(form_funcs)}, audit={len(audit_func)}")
