
"""
Markdown Generator Module
Converteert HTML naar Markdown formaat
"""

import re
from bs4 import BeautifulSoup


class MarkdownGenerator:
    """
    Klasse voor het converteren van HTML naar Markdown
    """
    
    def html_to_markdown(self, html_content: str) -> str:
        """
        Converteer HTML naar Markdown formaat
        
        Args:
            html_content: HTML content
            
        Returns:
            Markdown formatted content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            markdown = []
            
            # Process alle elementen
            for element in soup.descendants:
                if element.name == 'h1':
                    markdown.append(f"\n# {element.get_text().strip()}\n")
                elif element.name == 'h2':
                    markdown.append(f"\n## {element.get_text().strip()}\n")
                elif element.name == 'h3':
                    markdown.append(f"\n### {element.get_text().strip()}\n")
                elif element.name == 'h4':
                    markdown.append(f"\n#### {element.get_text().strip()}\n")
                elif element.name == 'p':
                    text = element.get_text().strip()
                    if text:
                        markdown.append(f"\n{text}\n")
                elif element.name == 'ul':
                    for li in element.find_all('li', recursive=False):
                        markdown.append(f"- {li.get_text().strip()}\n")
                elif element.name == 'ol':
                    for i, li in enumerate(element.find_all('li', recursive=False), 1):
                        markdown.append(f"{i}. {li.get_text().strip()}\n")
                elif element.name == 'img':
                    src = element.get('src', '')
                    alt = element.get('alt', 'image')
                    markdown.append(f"\n![{alt}]({src})\n")
                elif element.name == 'a':
                    href = element.get('href', '')
                    text = element.get_text().strip()
                    markdown.append(f"[{text}]({href})")
                elif element.name == 'strong' or element.name == 'b':
                    markdown.append(f"**{element.get_text().strip()}**")
                elif element.name == 'em' or element.name == 'i':
                    markdown.append(f"*{element.get_text().strip()}*")
            
            # Join en clean up
            result = ''.join(markdown)
            
            # Clean up excessive newlines
            result = re.sub(r'\n{3,}', '\n\n', result)
            
            return result.strip()
            
        except Exception as e:
            print(f"❌ Error converting to markdown: {str(e)}")
            return html_content
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """
        Converteer Markdown naar HTML (basis implementatie)
        
        Args:
            markdown_content: Markdown content
            
        Returns:
            HTML formatted content
        """
        html = markdown_content
        
        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Bold en italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # Images
        html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', html)
        
        # Paragraphs
        lines = html.split('\n')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<'):
                processed_lines.append(f'<p>{line}</p>')
            else:
                processed_lines.append(line)
        
        html = '\n'.join(processed_lines)
        
        return html
