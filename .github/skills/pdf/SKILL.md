---
name: pdf
description: Use esta skill sempre que o usuario quiser fazer qualquer operacao com arquivos PDF. Isso inclui leitura ou extracao de texto/tabelas de PDFs, combinacao/mescla de varios PDFs em um so, divisao de PDFs, rotacao de paginas, adicao de marca d'agua, criacao de novos PDFs, preenchimento de formularios PDF, criptografia/descriptografia de PDFs, extracao de imagens e OCR em PDFs digitalizados para torna-los pesquisaveis. Se o usuario mencionar um arquivo .pdf ou pedir para gerar um, use esta skill.
license: Proprietaria. Consulte LICENSE.txt para os termos completos
---

# Guia de Processamento de PDF

## Visao Geral

Este guia cobre operacoes essenciais de processamento de PDF usando bibliotecas Python e ferramentas de linha de comando. Para recursos avancados, bibliotecas JavaScript e exemplos detalhados, consulte REFERENCE.md. Se precisar preencher um formulario PDF, leia FORMS.md e siga as instrucoes.

## Inicio Rapido

```python
from pypdf import PdfReader, PdfWriter

# Ler um PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extrair texto
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Bibliotecas Python

### pypdf - Operacoes Basicas

#### Mesclar PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Dividir PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extrair Metadados
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotacionar Paginas
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotaciona 90 graus no sentido horario
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Extracao de Texto e Tabelas

#### Extrair Texto com Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extrair Tabelas
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Tabela {j+1} na pagina {i+1}:")
            for row in table:
                print(row)
```

#### Extracao Avancada de Tabelas
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Verifica se a tabela nao esta vazia
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combina todas as tabelas
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Criacao de PDFs

#### Criacao Basica de PDF
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Adicionar texto
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Adicionar uma linha
c.line(100, height - 140, 400, height - 140)

# Salvar
c.save()
```

#### Criar PDF com Multiplas Paginas
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Adicionar conteudo
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Pagina 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Gerar PDF
doc.build(story)
```

#### Subscritos e Sobrescritos

**IMPORTANTE**: Nunca use caracteres Unicode de subscrito/sobrescrito (₀₁₂₃₄₅₆₇₈₉, ⁰¹²³⁴⁵⁶⁷⁸⁹) em PDFs com ReportLab. As fontes padrao nao incluem esses glifos, e eles podem aparecer como blocos pretos.

Em vez disso, use as tags XML do ReportLab em objetos Paragraph:
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Subscritos: usar tag <sub>
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# Sobrescritos: usar tag <super>
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

Para texto desenhado diretamente no canvas (sem Paragraph), ajuste manualmente tamanho e posicao da fonte em vez de usar Unicode subscrito/sobrescrito.

## Ferramentas de Linha de Comando

### pdftotext (poppler-utils)
```bash
# Extrair texto
pdftotext input.pdf output.txt

# Extrair texto preservando layout
pdftotext -layout input.pdf output.txt

# Extrair paginas especificas
pdftotext -f 1 -l 5 input.pdf output.txt  # Paginas 1-5
```

### qpdf
```bash
# Mesclar PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Dividir paginas
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotacionar paginas
qpdf input.pdf output.pdf --rotate=+90:1  # Rotaciona a pagina 1 em 90 graus

# Remover senha
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Mesclar
pdftk file1.pdf file2.pdf cat output merged.pdf

# Dividir
pdftk input.pdf burst

# Rotacionar
pdftk input.pdf rotate 1east output rotated.pdf
```

## Tarefas Comuns

### Extrair Texto de PDFs Digitalizados
```python
# Requer: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Converter PDF em imagens
images = convert_from_path('scanned.pdf')

# OCR em cada pagina
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Adicionar Marca d'Agua
```python
from pypdf import PdfReader, PdfWriter

# Criar marca d'agua (ou carregar existente)
watermark = PdfReader("watermark.pdf").pages[0]

# Aplicar em todas as paginas
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extrair Imagens
```bash
# Usando pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# Isso extrai todas as imagens como output_prefix-000.jpg, output_prefix-001.jpg etc.
```

### Protecao por Senha
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Adicionar senha
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Referencia Rapida

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Mesclar PDFs | pypdf | `writer.add_page(page)` |
| Dividir PDFs | pypdf | Uma pagina por arquivo |
| Extrair texto | pdfplumber | `page.extract_text()` |
| Extrair tabelas | pdfplumber | `page.extract_tables()` |
| Criar PDFs | reportlab | Canvas ou Platypus |
| Mesclar via terminal | qpdf | `qpdf --empty --pages ...` |
| OCR em PDFs digitalizados | pytesseract | Converter para imagem primeiro |
| Preencher formularios PDF | pdf-lib ou pypdf (ver FORMS.md) | Ver FORMS.md |

## Proximos Passos

- Para uso avancado de pypdfium2, veja REFERENCE.md
- Para bibliotecas JavaScript (pdf-lib), veja REFERENCE.md
- Se precisar preencher formulario PDF, siga FORMS.md
- Para guias de troubleshooting, veja REFERENCE.md
