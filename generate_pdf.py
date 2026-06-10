#!/usr/bin/env python3
"""Convert the Markdown memorial document to PDF with two-column image layout.

Images preserve their original aspect ratio in a 2-column grid.
"""
import os
import re
from fpdf import FPDF
from PIL import Image as PILImage

class MemorialPDF(FPDF):
    """Custom PDF class with two-column image layout (preserving aspect ratio)."""
    
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msyhbd.ttc',
        ]
        self.chinese_font = None
        for fp in font_paths:
            if os.path.exists(fp):
                self.chinese_font = fp
                break
        if self.chinese_font:
            self.add_font('CJK', '', self.chinese_font)
            bold_path = 'C:/Windows/Fonts/msyhbd.ttc'
            if os.path.exists(bold_path):
                self.add_font('CJK', 'B', bold_path)
            else:
                self.add_font('CJK', 'B', self.chinese_font)
        self.set_auto_page_break(True, 20)
        self.set_margins(18, 10, 18)
        self.image_batch = []  # Each element: (resolved_path, original_w, original_h)
    
    def header(self):
        self.set_font('CJK', '', 7.5)
        self.set_text_color(160, 160, 160)
        self.cell(0, 5, '有我——2025届在学院小街2号的这几年', new_x="RIGHT", new_y="TOP", align='C')
        self.ln(7)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('CJK', '', 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, str(self.page_no()), new_x="RIGHT", new_y="TOP", align='C')
    
    def flush_image_batch(self):
        """Render all queued images in a 2-column grid, preserving aspect ratio."""
        if not self.image_batch:
            return
        
        col_width = 75  # mm per column
        col_gap = 6
        total_width = col_width * 2 + col_gap
        start_x = (self.w - total_width) / 2
        
        # Calculate each image's display size preserving aspect ratio
        max_cell_h = 100  # max height per cell
        
        rows = []
        for i in range(0, len(self.image_batch), 2):
            row = []
            for j in range(2):
                idx = i + j
                if idx < len(self.image_batch):
                    img_path, ow, oh = self.image_batch[idx]
                    # Scale to fit col_width wide, preserving ratio
                    ratio = min(col_width / ow, max_cell_h / oh, 1.0)
                    dw = ow * ratio
                    dh = oh * ratio
                    row.append((img_path, dw, dh))
                else:
                    row.append(None)
            rows.append(row)
        
        # Calculate row heights (use max height in each row)
        row_heights = []
        for row in rows:
            max_h = 0
            for item in row:
                if item:
                    max_h = max(max_h, item[2])
            row_heights.append(max_h + 4)  # +4mm gap
        
        total_height_needed = sum(row_heights)
        if self.get_y() + total_height_needed > self.h - 25:
            self.add_page()
        
        for row_idx, row in enumerate(rows):
            rh = row_heights[row_idx]
            if self.get_y() + rh > self.h - 25:
                self.add_page()
            
            y_start = self.get_y()
            max_h_in_row = 0
            
            for col_idx, item in enumerate(row):
                if item:
                    img_path, dw, dh = item
                    x = start_x + col_idx * (col_width + col_gap)
                    # Center vertically within the row
                    y_offset = y_start  # align to top of row
                    try:
                        self.image(img_path, x, y_offset, dw, dh)
                    except Exception:
                        pass
                    max_h_in_row = max(max_h_in_row, dh)
            
            self.ln(max_h_in_row + 4)
        
        self.image_batch = []
    
    def write_heading(self, text, level):
        self.flush_image_batch()
        self.ln(2)
        if level == 1:
            self.set_font('CJK', 'B', 15)
            self.set_text_color(139, 69, 19)
            self.set_draw_color(139, 69, 19)
            self.set_line_width(0.6)
            y = self.get_y()
            self.line(18, y, self.w - 18, y)
            self.ln(4)
        elif level == 2:
            self.set_font('CJK', 'B', 12)
            self.set_text_color(60, 60, 60)
        else:
            self.set_font('CJK', 'B', 11)
            self.set_text_color(80, 80, 80)
        text = text.strip().replace('**', '').replace('*', '')
        if text:
            self.multi_cell(self.w - 36, 7, text)
        if level == 1:
            self.set_draw_color(180, 180, 180)
            self.set_line_width(0.2)
            y = self.get_y() + 1
            self.line(18, y, self.w - 18, y)
            self.ln(3)
        else:
            self.ln(1)
    
    def write_paragraph(self, text):
        self.flush_image_batch()
        text = text.strip()
        if not text:
            self.ln(1.5)
            return
        text = text.replace('**', '').replace('*', '').replace('__', '')
        if text.startswith('>') or text.startswith('re') or text.startswith('\t'):
            self.set_font('CJK', '', 8.5)
            self.set_text_color(100, 100, 100)
            left_save = self.l_margin
            self.set_left_margin(24)
            self.multi_cell(self.w - 42, 4.5, text.lstrip('>\t '))
            self.set_left_margin(left_save)
        else:
            self.set_font('CJK', '', 9.5)
            self.set_text_color(51, 51, 51)
            self.multi_cell(self.w - 36, 5, text)
        self.ln(0.5)
    
    def write_image(self, img_path):
        """Queue an image, reading its original dimensions."""
        if not os.path.isabs(img_path):
            img_path = os.path.join(self.md_dir, img_path)
        if not os.path.exists(img_path):
            alt_path = os.path.join(self.md_dir, 'images', os.path.basename(img_path))
            if os.path.exists(alt_path):
                img_path = alt_path
        if os.path.exists(img_path):
            try:
                with PILImage.open(img_path) as img:
                    w, h = img.size
                self.image_batch.append((img_path, w, h))
            except Exception:
                pass


def parse_and_generate(md_file, pdf_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    pdf = MemorialPDF()
    pdf.md_dir = os.path.dirname(os.path.abspath(md_file))
    pdf.set_title('有我——2025届在学院小街2号的这几年')
    pdf.set_author('北京八中2025届')
    
    pdf.add_page()
    
    # Title
    pdf.ln(50)
    pdf.set_font('CJK', 'B', 26)
    pdf.set_text_color(139, 69, 19)
    pdf.cell(0, 12, '有我', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    pdf.set_font('CJK', '', 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 9, '2025届在学院小街2号的这几年', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(6)
    pdf.set_font('CJK', '', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 7, '北京八中', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(20)
    pdf.set_draw_color(139, 69, 19)
    pdf.set_line_width(0.5)
    y = pdf.get_y()
    pdf.line(60, y, pdf.w - 60, y)
    pdf.ln(15)
    
    # Content
    skip_section = True
    for line in lines:
        stripped = line.rstrip()
        if '不要修改这以上的内容哦~' in stripped:
            skip_section = False
            continue
        if '不要修改已有的tag哦' in stripped:
            continue
        if skip_section:
            continue
        if 'https://i.y.qq.com/' in stripped:
            continue
        if re.match(r'^#{1,3}\s*$', stripped):
            continue
        
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', stripped)
        if heading_match:
            pdf.write_heading(heading_match.group(2), len(heading_match.group(1)))
            continue
        
        img_match = re.match(r'!\[(.*?)\]\((.+?)\)', stripped)
        if img_match:
            pdf.write_image(img_match.group(2))
            continue
        
        if re.match(r'^---+$', stripped):
            pdf.flush_image_batch()
            pdf.ln(1)
            y = pdf.get_y()
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.line(18, y, pdf.w - 18, y)
            pdf.ln(3)
            continue
        
        if stripped:
            pdf.write_paragraph(stripped)
        else:
            pdf.ln(1.5)
    
    pdf.flush_image_batch()
    
    pdf.output(pdf_file)
    print(f'PDF generated: {pdf_file}')
    print(f'Total pages: {pdf.page_no()}')


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    md_file = os.path.join(project_dir, '有我——2025届在学院小街2号的这几年.md')
    pdf_file = os.path.join(project_dir, '有我——2025届在学院小街2号的这几年.pdf')
    parse_and_generate(md_file, pdf_file)