from bs4 import BeautifulSoup, NavigableString

class ChatGPTDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # O ChatGPT envolve toda a resposta (texto + código) nesta div
        containers = soup.find_all('div', class_='markdown')
        if not containers:
            containers = soup.find_all(attrs={"data-assistant-markdown": True})
        if not containers:
            containers = [soup]
            
        parsed_containers = []
        for container in containers:
            # Pula as divs que são apenas controles de UI da OpenAI (como o botão Editar/Copiar)
            # Esses botões ficam em containers marcados com "writing-block-header"
            for ui_header in container.find_all(attrs={"data-testid": "writing-block-header-sticky-container"}):
                ui_header.decompose() # Remove do HTML temporariamente
                
            parsed_containers.append(self._process_node(container).strip())
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element)

        tag = element.name
        
        if tag == 'h1':
            return f"# {self._process_node(element)}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element)}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element)}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element)}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element)}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element)}\n\n"
        elif tag == 'p':
            return f"{self._process_node(element)}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element)}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element)}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element)}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element)
            return f"[{text}]({href})"
        elif tag == 'code':
            # Se já estiver dentro de um bloco pre, ignoramos as crases pois o bloco tratará.
            # Mas pelo nosso mapeamento, os blocos de código são tratados no 'pre' principal.
            return f"`{self._process_node(element)}`"
        elif tag == 'pre':
            # Tratamento de Code Block Específico do ChatGPT
            
            # 1. Encontrar a linguagem
            language = ""
            lang_div = element.find('div', class_='text-token-text-primary')
            if lang_div:
                # Remove o SVG, pega só o texto
                language = lang_div.get_text(strip=True)
            
            # 2. Encontrar o código em si
            code_content = ""
            cm_content = element.find('pre', class_='cm-content')
            if cm_content:
                code_elem = cm_content.find('code')
                if code_elem:
                    # Precisamos extrair preservando quebras de linha
                    # O BeautifulSoup pega o textContent
                    code_content = code_elem.get_text()
            else:
                # Fallback genérico caso a estrutura mude
                code_elem = element.find('code')
                if code_elem:
                    code_content = code_elem.get_text()
                else:
                    code_content = element.get_text()

            # Se a IA encapsulou todo o texto markdown num codeblock 'markdown', nós 'desempacotamos' para evitar scrollbars duplos na IDE
            if language.lower() == 'markdown':
                return f"\n{code_content}\n\n"

            return f"```{language}\n{code_content}\n```\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                # strip() no processamento interno do LI evita quebras de linha excessivas
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            # Cada linha/parágrafo dentro do blockquote deve receber um "> "
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'span' and 'katex-display' in element.get('class', []):
            math_annotation = element.find('annotation', encoding='application/x-tex')
            if math_annotation:
                return f"$$\n{math_annotation.get_text(strip=True)}\n$$\n\n"
            return ""
        elif tag == 'span' and 'result-streaming' in element.get('class', []):
            # Ignora o cursor piscante durante o streaming para não quebrar a lógica de delta
            return ""
        else:
            # Qualquer outra tag (div, span), apenas entra e continua parseando o texto interno
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

class GeminiDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        containers = soup.find_all('message-content')
        if not containers:
            containers = [soup]
            
        parsed_containers = []
        for container in containers:
            parsed_containers.append(self._process_node(container).strip())
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element)

        tag = element.name
        
        if tag in ['button', 'gem-icon-button', 'gem-icon', 'mat-icon', 'gem-popover', 'mat-menu', 'table-block']:
            if tag == 'table-block':
                table = element.find('table')
                if table:
                    return self._process_table(table) + "\n\n"
            return ""

        if tag == 'h1':
            return f"# {self._process_node(element).strip()}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element).strip()}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element).strip()}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element).strip()}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element).strip()}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element).strip()}\n\n"
        elif tag == 'p':
            return f"{self._process_node(element).strip()}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element).strip()}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element).strip()}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element).strip()}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element).strip()
            return f"[{text}]({href})"
        elif tag == 'code-block':
            language = ""
            lang_span = element.find('div', class_='code-block-decoration')
            if lang_span:
                language = lang_span.find('span').get_text(strip=True) if lang_span.find('span') else lang_span.get_text(strip=True)
            
            code_elem = element.find('code', class_='code-container')
            code_content = code_elem.get_text() if code_elem else ""
            
            return f"```{language}\n{code_content}\n```\n\n"
        elif tag == 'code':
            return f"`{self._process_node(element).strip()}`"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        elif tag == 'div' and 'math-block' in element.get('class', []):
            math = element.get('data-math', '')
            return f"$$\n{math}\n$$\n\n"
        else:
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

class ClaudeDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        containers = soup.find_all('div', class_='font-claude-response')
        if not containers:
            containers = [soup]
            
        parsed_containers = []
        for container in containers:
            parsed_containers.append(self._process_node(container).strip())
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element)

        tag = element.name
        
        if tag in ['button', 'svg', 'math']:
            return ""

        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()
            
        if 'sr-only' in classes or 'text-text-500' in classes or element.get('role') == 'status':
            return ""

        if tag == 'h1':
            return f"# {self._process_node(element).strip()}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element).strip()}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element).strip()}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element).strip()}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element).strip()}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element).strip()}\n\n"
        elif tag == 'p':
            return f"{self._process_node(element).strip()}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element).strip()}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element).strip()}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element).strip()}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element).strip()
            return f"[{text}]({href})"
        elif tag == 'pre':
            code_elem = element.find('code')
            if code_elem:
                classes = code_elem.get('class', [])
                language = ""
                for cls in classes:
                    if cls.startswith('language-'):
                        language = cls.replace('language-', '')
                code_content = code_elem.get_text()
                return f"```{language}\n{code_content}\n```\n\n"
            return f"```\n{self._process_node(element).strip()}\n```\n\n"
        elif tag == 'code':
            if element.parent and element.parent.name == 'pre':
                return self._process_node(element)
            return f"`{self._process_node(element).strip()}`"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        elif tag == 'span' and 'katex-display' in element.get('class', []):
            math_annotation = element.find('annotation', encoding='application/x-tex')
            if math_annotation:
                return f"$$\n{math_annotation.get_text(strip=True)}\n$$\n\n"
            return ""
        else:
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

class DeepseekDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        containers = soup.find_all('div', class_='ds-message')
        if not containers:
            containers = [soup]
            
        parsed_containers = []
        for container in containers:
            md_container = container.find('div', class_='ds-markdown')
            if md_container:
                full_markdown += self._process_node(md_container).strip() + "\n\n---\n\n"
            else:
                full_markdown += container.get_text(strip=True) + "\n\n---\n\n"
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element)

        tag = element.name
        
        if tag in ['button', 'svg', 'math', 'style', 'script']:
            return ""

        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()

        if tag == 'div' and 'md-code-block' in classes:
            language = ""
            lang_span = element.find('span', class_='d813de27')
            if not lang_span:
                banner = element.find('div', class_='md-code-block-banner')
                if banner:
                    lang_el = banner.select_one('div > div > span')
                    if lang_el:
                        language = lang_el.get_text(strip=True)
            else:
                language = lang_span.get_text(strip=True)

            pre = element.find('pre')
            if pre:
                code_content = pre.get_text()
                return f"```{language}\n{code_content}\n```\n\n"
            return ""

        if tag == 'div' and 'md-code-block-banner-wrap' in classes:
            return ""

        if tag == 'h1':
            return f"# {self._process_node(element).strip()}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element).strip()}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element).strip()}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element).strip()}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element).strip()}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element).strip()}\n\n"
        elif tag == 'p':
            return f"{self._process_node(element).strip()}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element).strip()}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element).strip()}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element).strip()}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element).strip()
            return f"[{text}]({href})"
        elif tag == 'code':
            return f"`{self._process_node(element).strip()}`"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        elif tag == 'span' and 'katex-display' in classes:
            math_annotation = element.find('annotation', encoding='application/x-tex')
            if math_annotation:
                return f"$$\n{math_annotation.get_text(strip=True)}\n$$\n\n"
            return ""
        else:
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

class QwenDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        containers = soup.find_all('div', class_='qwen-chat-message')
        if not containers:
            containers = [soup]
            
        parsed_containers = []
        for container in containers:
            is_assistant = 'qwen-chat-message-assistant' in container.get('class', [])
            
            if is_assistant:
                md_container = container.find('div', class_='qwen-markdown')
                if md_container:
                    full_markdown += self._process_node(md_container).strip() + "\n\n---\n\n"
            else:
                user_msg = container.find('p', class_='user-message-content')
                if user_msg:
                    full_markdown += user_msg.get_text(strip=True) + "\n\n---\n\n"
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node).replace("\xa0", " ")

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element).replace("\xa0", " ")

        tag = element.name
        
        if tag in ['button', 'svg', 'math', 'style', 'script']:
            return ""

        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()

        if tag == 'pre' and 'qwen-markdown-code' in classes:
            language = ""
            lang_el = element.find('div', class_='qwen-markdown-code-header')
            if lang_el:
                first_div = lang_el.find('div')
                if first_div:
                    language = first_div.get_text(strip=True)
            
            code_lines = []
            view_lines = element.find_all('div', class_='view-line')
            for vl in view_lines:
                code_lines.append(vl.get_text(separator='').replace("\xa0", " "))
                
            code_content = "\n".join(code_lines)
            return f"```{language}\n{code_content}\n```\n\n"

        if tag == 'h1':
            return f"# {self._process_node(element).strip()}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element).strip()}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element).strip()}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element).strip()}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element).strip()}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element).strip()}\n\n"
        elif tag == 'p' or (tag == 'div' and 'qwen-markdown-paragraph' in classes):
            return f"{self._process_node(element).strip()}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element).strip()}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element).strip()}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element).strip()}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element).strip()
            return f"[{text}]({href})"
        elif tag == 'code' or (tag == 'code' and 'qwen-markdown-codespan' in classes):
            return f"`{self._process_node(element).strip()}`"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        elif tag == 'span' and 'katex-display' in classes:
            math_annotation = element.find('annotation', encoding='application/x-tex')
            if math_annotation:
                return f"$$\n{math_annotation.get_text(strip=True)}\n$$\n\n"
            return ""
        else:
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

class KimiDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        containers = soup.find_all('div', class_='chat-content-item')
        if not containers:
            containers = [soup]
            
        parsed_containers = []
        for container in containers:
            is_assistant = 'chat-content-item-assistant' in container.get('class', [])
            
            if is_assistant:
                md_containers = container.find_all('div', class_='markdown-container')
                for md_container in md_containers:
                    if 'toolcall-content-text' not in md_container.get('class', []):
                        full_markdown += self._process_node(md_container).strip() + "\n\n---\n\n"
            else:
                user_msg = container.find('div', class_='user-content')
                if user_msg:
                    full_markdown += user_msg.get_text(strip=True) + "\n\n---\n\n"
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element)

        tag = element.name
        
        if tag in ['button', 'svg', 'math', 'style', 'script', 'header']:
            return ""

        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()

        if tag == 'div' and 'segment-code' in classes:
            language = ""
            lang_span = element.find('span', class_='segment-code-lang')
            if lang_span:
                language = lang_span.get_text(strip=True)

            code_container = element.find('code')
            if code_container:
                code_content = code_container.get_text()
                return f"```{language}\n{code_content}\n```\n\n"
            return ""

        if tag == 'div' and 'sticky-release' in classes:
            return ""

        if tag == 'h1':
            return f"# {self._process_node(element).strip()}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element).strip()}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element).strip()}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element).strip()}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element).strip()}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element).strip()}\n\n"
        elif tag == 'p' or (tag == 'div' and 'paragraph' in classes):
            return f"{self._process_node(element).strip()}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element).strip()}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element).strip()}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element).strip()}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element).strip()
            return f"[{text}]({href})"
        elif tag == 'code' or (tag == 'code' and 'segment-code-inline' in classes):
            return f"`{self._process_node(element).strip()}`"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        else:
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

class DeepAIDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        elements = soup.find_all(['textarea', 'span'])
        
        parsed_containers = []
        for elem in elements:
            classes = elem.get('class', [])
            if not isinstance(classes, list):
                classes = classes.split()
                
            if elem.name == 'textarea' and 'chatbox' in classes:
                full_markdown += elem.get_text(strip=True) + "\n\n---\n\n"
            elif elem.name == 'span' and 'hiddenTextContainer' in classes:
                full_markdown += elem.get_text(strip=True) + "\n\n---\n\n"
                
        return "\n\n---\n\n".join(parsed_containers)

class GrokDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        containers = soup.find_all('div', class_='message-bubble')
        if not containers:
            containers = [soup]
            
        parsed_containers = []
        for container in containers:
            is_user = container.get('data-testid') == 'user-message'
            
            if is_user:
                user_content = container.find('div', class_='response-content-markdown')
                if user_content:
                    full_markdown += user_content.get_text(separator="\n", strip=True) + "\n\n---\n\n"
            else:
                md_container = container.find('div', class_='response-content-markdown')
                if md_container:
                    full_markdown += self._process_node(md_container).strip() + "\n\n---\n\n"
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element)

        tag = element.name
        
        if tag in ['button', 'svg', 'math', 'style', 'script', 'header']:
            return ""

        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()

        if tag == 'div' and element.get('data-testid') == 'code-block':
            language = ""
            lang_span = element.find('span', class_='font-mono')
            if lang_span:
                language = lang_span.get_text(strip=True).lower()
                if language == "plaintext":
                    language = ""

            code_lines = []
            shiki = element.find('div', class_='shiki')
            if shiki:
                code_container = shiki.find('code')
                if code_container:
                    lines = code_container.find_all('span', class_='line')
                    for line in lines:
                        code_lines.append(line.get_text())
            
            code_content = "\n".join(code_lines)
            return f"```{language}\n{code_content}\n```\n\n"

        if tag == 'h1':
            return f"# {self._process_node(element).strip()}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element).strip()}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element).strip()}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element).strip()}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element).strip()}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element).strip()}\n\n"
        elif tag == 'p':
            return f"{self._process_node(element).strip()}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element).strip()}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element).strip()}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element).strip()}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element).strip()
            return f"[{text}]({href})"
        elif tag == 'code' and 'segment-code-inline' not in classes:
            return f"`{self._process_node(element).strip()}`"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        elif tag == 'span' and 'katex-display' in classes:
            math_annotation = element.find('annotation', encoding='application/x-tex')
            if math_annotation:
                return f"$$\n{math_annotation.get_text(strip=True)}\n$$\n\n"
            return ""
        else:
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

class ChatXDOMParser:
    def __init__(self):
        pass

    def parse_html_to_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        containers = soup.find_all(lambda tag: tag.name == 'div' and 'markdown' in tag.get('class', []))
        if not containers:
            return ""
            
        parsed_containers = []
        for container in containers:
            classes = container.get('class', [])
            if not isinstance(classes, list):
                classes = classes.split()
                
            is_assistant = 'system_write' in classes
            
            if not is_assistant:
                full_markdown += container.get_text(separator="\n", strip=True) + "\n\n---\n\n"
            else:
                parsed_containers.append(self._process_node(container).strip())
            
        return "\n\n---\n\n".join(parsed_containers)

    def _process_node(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        markdown = ""
        for child in node.children:
            markdown += self._process_element(child)

        return markdown

    def _process_element(self, element) -> str:
        if isinstance(element, NavigableString):
            return str(element)

        tag = element.name
        
        if tag in ['button', 'svg', 'math', 'style', 'script', 'header']:
            return ""

        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()

        if tag == 'pre':
            code_node = element.find('code')
            if code_node:
                lang_classes = code_node.get('class', [])
                if isinstance(lang_classes, str):
                    lang_classes = lang_classes.split()
                
                language = ""
                for c in lang_classes:
                    if c.startswith('language-'):
                        language = c.replace('language-', '')
                        break
                
                code_content = code_node.get_text()
                return f"```{language}\n{code_content}\n```\n\n"
            else:
                return f"```\n{element.get_text()}\n```\n\n"

        if tag == 'h1':
            return f"# {self._process_node(element).strip()}\n\n"
        elif tag == 'h2':
            return f"## {self._process_node(element).strip()}\n\n"
        elif tag == 'h3':
            return f"### {self._process_node(element).strip()}\n\n"
        elif tag == 'h4':
            return f"#### {self._process_node(element).strip()}\n\n"
        elif tag == 'h5':
            return f"##### {self._process_node(element).strip()}\n\n"
        elif tag == 'h6':
            return f"###### {self._process_node(element).strip()}\n\n"
        elif tag == 'p':
            return f"{self._process_node(element).strip()}\n\n"
        elif tag == 'strong' or tag == 'b':
            return f"**{self._process_node(element).strip()}**"
        elif tag == 'em' or tag == 'i':
            return f"*{self._process_node(element).strip()}*"
        elif tag == 's' or tag == 'del':
            return f"~~{self._process_node(element).strip()}~~"
        elif tag == 'a':
            href = element.get('href', '')
            text = self._process_node(element).strip()
            return f"[{text}]({href})"
        elif tag == 'code':
            return f"`{self._process_node(element).strip()}`"
        elif tag == 'table':
            return self._process_table(element) + "\n\n"
        elif tag == 'ul':
            result = ""
            for li in element.find_all('li', recursive=False):
                result += f"- {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'ol':
            result = ""
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result += f"{i}. {self._process_node(li).strip()}\n"
            return result + "\n"
        elif tag == 'blockquote':
            result = ""
            content = self._process_node(element).strip()
            for line in content.split('\n'):
                if line.strip():
                    result += f"> {line.strip()}\n"
            return result + "\n"
        elif tag == 'span' and 'katex-display' in classes:
            math_annotation = element.find('annotation', encoding='application/x-tex')
            if math_annotation:
                return f"$$\n{math_annotation.get_text(strip=True)}\n$$\n\n"
            return ""
        elif 'math-inline' in classes or 'math-display' in classes:
            return self._process_node(element)
        else:
            return self._process_node(element)

    def _process_table(self, table_elem) -> str:
        rows = []
        for tr in table_elem.find_all('tr'):
            cols = [self._process_node(c).strip().replace("\n", " ") for c in tr.find_all(['th', 'td'])]
            rows.append("| " + " | ".join(cols) + " |")
            if tr.find('th'):
                rows.append("|" + "|".join(["---"] * len(cols)) + "|")
        return "\n".join(rows)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Teste rápido se rodar diretamente
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        
        if 'gemini' in filepath.lower():
            parser = GeminiDOMParser()
        elif 'claude' in filepath.lower():
            parser = ClaudeDOMParser()
        elif 'deepseek' in filepath.lower():
            parser = DeepseekDOMParser()
        elif 'qwen' in filepath.lower():
            parser = QwenDOMParser()
        elif 'kimi' in filepath.lower():
            parser = KimiDOMParser()
        elif 'deepai' in filepath.lower():
            parser = DeepAIDOMParser()
        elif 'grok' in filepath.lower():
            parser = GrokDOMParser()
        elif 'chatx' in filepath.lower():
            parser = ChatXDOMParser()
        else:
            parser = ChatGPTDOMParser()
            
        print(parser.parse_html_to_markdown(html))
