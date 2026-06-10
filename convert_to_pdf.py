import markdown
import weasyprint
import re
import os

def fix_image_paths(md_content, md_dir, images_dir):
    """Fix image paths to point to the correct images directory."""
    def replace_path(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        # Check if the path already has a directory prefix
        if '/' not in img_path and '\\' not in img_path:
            # This is a bare filename, check if it exists in images/
            full_path = os.path.join(images_dir, img_path)
            if os.path.exists(full_path):
                return f'![{alt_text}]({full_path})'
            # Also try with the md directory
            full_path_md = os.path.join(md_dir, img_path)
            if os.path.exists(full_path_md):
                return f'![{alt_text}]({full_path_md})'
        return match.group(0)
    
    return re.sub(r'!\[(.*?)\]\(([^)]+)\)', replace_path, md_content)

def convert_md_to_pdf(md_file, pdf_output):
    """Convert a Markdown file to PDF using WeasyPrint."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    md_dir = os.path.dirname(os.path.abspath(md_file))
    images_dir = os.path.join(md_dir, 'images')
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Fix image paths
    md_content = fix_image_paths(md_content, md_dir, images_dir)
    
    # Remove the music embed links (QQ music URLs) as they won't work in PDF
    # Also remove the formatting instructions at the top
    lines = md_content.split('\n')
    filtered_lines = []
    for line in lines:
        # Remove QQ music embed URLs
        if 'https://i.y.qq.com/' in line:
            continue
        # Remove the formatting instruction section
        if line.strip() == '#+空格 添加tag和话题 可多级标题（多级标题就是敲多个#然后再空格）':
            continue
        if '如果手机版往下滑太慢的话' in line:
            continue
        if '电脑添加音乐鼠标放在这行前面' in line:
            continue
        if '手机添加音乐键盘上方最左侧可以找到酷狗音乐' in line:
            continue
        if '可以直接上传照片' in line:
            continue
        if '记得给自己写的加楼号' in line:
            continue
        if '回复楼主在前面加一个' in line:
            continue
        if '不要删已有的楼哦' in line:
            continue
        if '如果想要匿名可以在' in line:
            continue
        if '找到自己后面有一个小三角点一下就不会有微信昵称了' in line:
            continue
        if '备份区' in line:
            continue
        if '1111 00:00 http' in line:
            continue
        if '希望大家在这里玩得开心' in line:
            continue
        if '回忆永不散场～' in line:
            continue
        if 'thx@皙的帮助' in line:
            continue
        if 'thx 24届备忘录' in line:
            continue
        if 'thx 友校备忘录' in line:
            continue
        if '不要修改这以上的内容哦~' in line:
            continue
        if '不要修改已有的tag哦' in line:
            continue
        filtered_lines.append(line)
    
    md_content = '\n'.join(filtered_lines)
    
    # Remove empty headings
    md_content = re.sub(r'^##\s*$', '', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^#\s*$', '', md_content, flags=re.MULTILINE)
    
    # Convert Markdown to HTML
    extensions = ['extra', 'codehilite', 'toc']
    html_body = markdown.markdown(md_content, extensions=extensions)
    
    # Create a styled HTML document
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
@page {{
    size: A4;
    margin: 2.5cm 2cm;
}}
body {{
    font-family: 'Microsoft YaHei', 'SimSun', 'Noto Sans CJK SC', sans-serif;
    font-size: 12pt;
    line-height: 1.8;
    color: #333;
}}
h1 {{
    font-size: 24pt;
    color: #1a1a1a;
    border-bottom: 2px solid #8B4513;
    padding-bottom: 8px;
    margin-top: 40px;
    page-break-before: always;
}}
h1:first-of-type {{
    page-break-before: avoid;
}}
h2 {{
    font-size: 20pt;
    color: #2a2a2a;
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
    margin-top: 30px;
}}
strong {{
    color: #8B4513;
}}
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 15px auto;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}
blockquote {{
    border-left: 4px solid #8B4513;
    padding-left: 15px;
    margin: 10px 0;
    color: #555;
    background: #f9f9f9;
    padding: 10px 15px;
    border-radius: 0 4px 4px 0;
}}
p {{
    margin: 8px 0;
    text-indent: 0;
}}
a {{
    color: #0066cc;
    text-decoration: none;
}}
hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}}
ul, ol {{
    padding-left: 25px;
}}
code {{
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11pt;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    # Generate PDF
    weasyprint.HTML(string=html_template).write_pdf(pdf_output)
    print(f"PDF generated successfully: {pdf_output}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    md_file = os.path.join(project_dir, '有我——2025届在学院小街2号的这几年.md')
    pdf_output = os.path.join(project_dir, '有我——2025届在学院小街2号的这几年.pdf')
    convert_md_to_pdf(md_file, pdf_output)