
| Flag | Default | Type | SQLite | Depends | Extracts from the PDF |
| :--- | :---: | :---: | :--- | :---: | :--- |
| `--[no-]DocEmbeddedFile` | ❌ | 🗓️ | `DOCUMENT_EMBEDDED_FILE` | `DocEmbeddedFileInfo` | NOT IMPLENENTED! |
| `--[no-]DocEmbeddedFileInfo` | ❌ | 🗓️ | `DOCUMENT_EMBEDDED_FILE_INFO` | ➖ | Embedded files (attachments). |
| `--[no-]DocumentFont` | ❌ | 👓 | `DOCUMENT_FONT` | `PageFont` | Aggregates font usage across pages. |
| `--[no-]DocumentInfo` | 🟢 | 🗓️ | `DOCUMENT_INFO` | ➖ | General document metadata. |
| `--[no-]DocumentLink` | ❌ | 👓 | `DOCUMENT_LINK` | `PageLink` | Aggregates link usage across pages. |
| `--[no-]DocumentPageLabel` | 🟢 | 🗓️ | `DOCUMENT_PAGE_LABEL` | ➖ | Page labeling definitions. |
| `--[no-]DocumentToC` | 🟢 | 🗓️ | `DOCUMENT_TOC` | ➖ | Table of Contents. |
| `--[no-]DocumentUniqueFont` | ❌ | 👓 | `DOCUMENT_UNIQUE_FONT` | `DocumentFont` | Summarizes unique fonts by base font name. |
| `--[no-]DocumentWordFrequency` | ❌ | 👓 | `DOCUMENT_WORD_FREQUENCY` | `PageWord` | Document global word frequency count. |
| `--[no-]PageAnnotation` | ❌ | 🗓️ | `PAGE_ANNOTATION` | ➖ | Annotations metadata and area image. |
| `--[no-]PageBlock` | 🟢 | 🗓️ | `PAGE_BLOCK` | ➖ | Page `blocks` (Text/Image), and content. |
| `--[no-]PageBlockFTS` | ❌ | 🗓️ | `PAGE_BLOCK_FTS` | `PageBlock` | FTS index for `PAGE_BLOCK`. |
| `--[no-]PageDict` | ❌ | 🗓️ | `PAGE_DICT` | ➖ | Python dictionary representation of page content (stringified). |
| `--[no-]PageDrawings` | ❌ | 🗓️ | `PAGE_DRAWINGS` | ➖ | Page `vector` drawing elements as list of dicts. |
| `--[no-]PageFont` | ❌ | 🗓️ | `PAGE_FONT` | ➖ | Fonts used on each page (xref, name, encoding, etc.). |
| `--[no-]PageHtml` | ❌ | 🗓️ | `PAGE_HTML` | ➖ | HTML representation of each page. Includes virtual column `HTML_LEN`. |
| `--[no-]PageImage` | ❌ | 🗓️ | `PAGE_IMAGE` | ➖ | `Binary` data of images found on pages. |
| `--[no-]PageImageInfo` | ❌ | 🗓️ | `PAGE_IMAGE_INFO` | ➖ | Metadata for images on pages . |
| `--[no-]PageJson` | ❌ | 🗓️ | `PAGE_JSON` | ➖ | Page `JSON` representation. |
| `--[no-]PageLink` | 🟢 | 🗓️ | `PAGE_LINK` | ➖ | Page `Hyperlinks` . |
| `--[no-]PagePhysical2Label` | ❌ | 🗓️ | `PAGE_PHYSICAL2LABEL` | ➖ | Mapping page `physical` (0-indexed) to `logical` labels. |
| `--[no-]PagePixmap` | ❌ | 🗓️ | `PAGE_PIXMAP` | ➖ | Page `raster` image (JPEG format) as a BLOB. |
| `--[no-]PageRawDict` | ❌ | 🗓️ | `PAGE_RAWDICT` | ➖ | Page `dictionary` structure (stringified). |
| `--[no-]PageRawJson` | ❌ | 🗓️ | `PAGE_RAWJSON` | ➖ | Page `JSON` structure content (stringified). |
| `--[no-]PageSvg` | ❌ | 🗓️ | `PAGE_SVG` | ➖ | `SVG` vector image of the page. |
| `--[no-]PageSvgTextAsPath` | ❌ | 🗓️ | `PAGE_SVG_TEXTASPATH` | ➖ | `SVG` vector image with text converted to paths. |
| `--[no-]PageTable` | ❌ | 🗓️ | `PAGE_TABLE` | ➖ | Tables coordinates in the page `x0,y0,x1,y1`. |
| `--[no-]PageTableCsv` | ❌ | 🗓️ | `PAGE_TABLE_CSV` | `PageTable` | Tables data in `CSV` format. |
| `--[no-]PageTableHtml` | ❌ | 🗓️ | `PAGE_TABLE_HTML` | `PageTable` | Tables data in `HTML` format. |
| `--[no-]PageTableJson` | ❌ | 🗓️ | `PAGE_TABLE_JSON` | `PageTable` | Tables data in `JSON` format. |
| `--[no-]PageTableList` | ❌ | 🗓️ | `PAGE_TABLE_LIST` | `PageTable` | Tables data in `List` format. |
| `--[no-]PageTableMarkdown` | ❌ | 🗓️ | `PAGE_TABLE_MARKDOWN` | `PageTable` | Tables data in `Markdown` format. |
| `--[no-]PageTableSql` | ❌ | 🗓️ | `PAGE_TABLE_SQL` | `PageTable` | Tables data in `SQL` format. |
| `--[no-]PageTablePixMap` | ❌ | 🗓️ | `PAGE_TABLE_PIXMAP` | `PageTable` | Tables data in `Pixmap` format. |
| `--[no-]PageText` | ❌ | 🗓️ | `PAGE_TEXT` | ➖ | Page `raw text` from each page. |
| `--[no-]PageWord` | ❌ | 🗓️ | `PAGE_WORD` | ➖ | Page individual words info. |
| `--[no-]PageWordFrequency` | ❌ | 👓 | `PAGE_WORD_FREQUENCY` | `PageWord` | Word frequency count per page. |
| `--[no-]PageXml` | ❌ | 🗓️ | `PAGE_XML` | ➖ | Page data in 'XML' format. |
| `--[no-]PageXHtml` | ❌ | 🗓️ | `PAGE_XHTML` | ➖ | Page data in `XHTML` format. |
---
---

#TODO :

0. **W.I.P** : Create TEST ENVIRONMENT TO TEST ALL FEATURES!!!
   1. **DONE**: Table
   2. **PENDING**: ToC
   3. **PENDING**: Embedding
---   
0. **PENDING** : Telemetry about the do2sqlite usaged.
1. **DONE** Executing SQLite3 FTS5 rebuild.
2. **PENDING**: Stop words must be a external filesystem file loaded in memory.
3. **DONE** :  Table as `CREATE VIEW SELECT (* , ... ) `
4. **PENDING**: Create dependency of `--PageImage` from `--PageImageInfo`.
   1. All fields from `IMAGE` except the image itself, must migrate to `PageImageInfo`
5. **W.I.P**: Add `--DocEmbeddedFile` dependent of `--DocEmbeddedFileInfo`.
6. **DONE** Change `PAGE_NUMBER` to `PAGE_PHYSICAL_NUMBER`.
7. **DONE** Externalize ROWID @ DOCUMENT_TOC
8. **PENDING** Add `--PageOCR` options
9.  **PENDING** Add `--PageStart` and `--PageFinish` flags.
   1.  if a interval is given, study the implications on the default at the `DOCUMENT_*` level.
---
10. **W.I.P** : Add a `--All` flag that turns all options `ON/TRUE`.
11. **PENDING** : PDF password
---

## LLM TODOS :

1.  LLM: n top words ==> LLM explanation : Based on the above list of words and their frequencies in a book, tell me what this book is about?
   https://www.perplexity.ai/search/54729639-8f62-4ef1-bed1-4a2459878df3
2. LLM: GLiNER2
3. LLM: SQLite3 Vector Embeddings.
4. LLM: Create. PDF/TXT/MARKDOWN summary documento about the PDF scanned giving hot points about the scanned document.
5. LLM: NER / VERBS / PRONOUNS / Ontology / Top Modelling / Entity Linking / KG / Classification / Tagging
6. Corpus analisys.
---

# doc2sqlite

**doc2sqlite** is a command-line tool that extracts comprehensive metadata, text, images, tables, and structural information from PDF documents and stores them directly into a SQLite database. It leverages `PyMuPDF` for high-performance PDF parsing and allows users to select specific extraction modules via command-line flags or configuration files.

## Features

- **Granular Extraction**: Extract document-level info (metadata, TOC, fonts) and page-level content (text, blocks, words, images, tables, SVGs, HTML, XML).
- **SQLite Integration**: Directly persists extracted data into SQLite tables, supporting full-text search (FTS) and binary blob storage (for images).
- **Flexible Configuration**: Supports command-line arguments, YAML configuration files, and default settings with dependency handling.
- **Rich Data Types**: Handles text, JSON, XML, HTML, SVG, and binary image data.
- **Table Extraction**: Extracts tables with support for Pandas DataFrames, CSV, Markdown, and HTML formats.

## Installation

Install the package via pip:

```bash
pip install doc2sqlite
```

*Note: Requires `PyMuPDF`, `pandas`, `pyyaml`, and `sqlite3` (standard library).*

## Quick Start

### Basic Usage

Extract all default enabled information (Document Info, Page Labels, TOC, Blocks, Links) from a PDF:

```bash
doc2sqlite -i input.pdf
```

This creates a SQLite database named `output.db` (default) in the current directory.

### Selective Extraction

Enable specific extraction modules using flags. For example, to extract text, images, and tables:

```bash
doc2sqlite -i input.pdf --PageText --PageImage --PageTable
```

### Using a Configuration File

For complex projects, use a YAML configuration file to define extraction parameters:

1. Create a `config.yaml`:
   ```yaml
   DocumentInfo: true
   PageText: true
   PageTable: true
   PageImageInfo: true
   ```
2. Run the tool with the config file:
   ```bash
   doc2sqlite -i input.pdf -c config.yaml
   ```

### Output Database

By default, the output database is named `output.db`. You can query it using any SQLite client:

```sql
SELECT * FROM DocumentInfo;
SELECT * FROM PageText WHERE page_number = 1;
```

## Command-Line Arguments

### Global Options

| Flag | Description |
|------|-------------|
| `-i`, `--InputPdf` | **Required**. Path to the input PDF file. |
| `-c`, `--ConfigFile` | Path to a YAML configuration file. |
| `-l`, `--log` | Path to the log file (default: `doc2sqlite.log`). |

### Extraction Flags

All extraction flags are boolean optional. If not specified, they default to the values defined in the schema.

#### Document-Level Exactions
| Flag | Description | Dependency |
|------|-------------|------------|
| `--DocumentInfo` | Extract document metadata, permissions, and info. | None |
| `--DocumentPageLabel` | Extract page label definitions. | None |
| `--DocumentToC` | Extract table of contents and destinations. | None |
| `--DocEmbeddedFileInfo` | Extract embedded file information. | None |
| `--DocumentFont` | Extract all fonts used in the document. | `--PageFont` |
| `--DocumentUniqueFont` | Extract unique fonts in the document. | `--DocumentFont` |
| `--DocumentLink` | Extract all links in the document. | `--PageLink` |
| `--DocumentWordFrequency` | Calculate word frequency across the document. | `--PageWord` |

#### Page-Level Exactions
| Flag | Description | Dependency |
|------|-------------|------------|
| `--PagePhysical2Label` | Map physical page numbers to labels. | None |
| `--PageFont` | Extract fonts used on each page. | None |
| `--PageBlock` | Extract text blocks with coordinates and types. | None |
| `--PageBlockFTS` | Enable Full-Text Search on blocks. | `--PageBlock` |
| `--PageLink` | Extract hyperlinks on each page. | None |
| `--PageText` | Extract raw text from each page. | None |
| `--PageHtml` | Extract HTML representation of the page. | None |
| `--PageXHtml` | Extract XHTML representation. | None |
| `--PageXml` | Extract XML representation. | None |
| `--PageDict` | Extract page content as a dictionary string. | None |
| `--PageRawDict` | Extract raw dictionary structure. | None |
| `--PageJson` | Extract page content as JSON string. | None |
| `--PageRawJson` | Extract raw JSON structure. | None |
| `--PageSvg` | Extract SVG vector image of the page. | None |
| `--PageSvgTextAsPath` | Extract SVG with text converted to paths. | None |
| `--PagePixmap` | Extract page as JPEG/PNG image blob. | None |
| `--PageDrawings` | Extract vector drawing elements. | None |
| `--PageWord` | Extract individual words with coordinates. | None |
| `--PageWordFrequency` | Calculate word frequency per page. | `--PageWord` |
| `--PageTable` | Extract tables with Pandas support. | None |
| `--PageImageInfo` | Extract image metadata (size, resolution, etc.). | None |
| `--PageImage` | Extract full image binaries. | None |
| `--PageAnnotation` | Extract annotations and their pixel data. | None |

## Configuration Schema

The tool uses a priority resolution system:
1. **Command Line Arguments** (Highest Priority)
2. **YAML Config File**
3. **Default Schema Values**

### Dependencies
Some flags require other flags to be enabled. For example:
- `--DocumentFont` requires `--PageFont`.
- `--PageBlockFTS` requires `--PageBlock`.

If a dependent flag is disabled, the tool will raise a `ValueError`.

## Output Database Structure

The SQLite database contains tables named after the extraction classes:
- `DocumentInfo`: General PDF metadata.
- `DocumentPageLabel`: Page labeling rules.
- `DocumentToC`: Table of contents entries.
- `PageText`, `PageHtml`, `PageXml`, etc.: Page-specific content.
- `PageImage`: Binary image data and metadata.
- `PageTable`: Table data in multiple formats (CSV, JSON, Markdown, HTML).

## Logging

Logs are written to both the console (INFO level and above) and a file named `doc2sqlite.log` (DEBUG level and above). You can change the log file path using the `-l` flag.

## Example Queries

### Get Document Metadata
```sql
SELECT name, page_count, permissions FROM DocumentInfo;
```

### Search for Text in Page 1
```sql
SELECT text FROM PageText WHERE page_number = 1 AND text LIKE '%keyword%';
```

### Extract Tables from Page 2
```sql
SELECT page_number, table_index, csv_data FROM PageTable WHERE page_number = 2;
```

## Dependencies

- Python 3.9+
- PyMuPDF
- Pandas
- Tabulate
- Pandas
- PyYAML
- SQLite3 (built-in)


### Database Schema & Table Reference

All extracted data is stored in a single SQLite database file (default: `DBs/MAIN.db`). The schema is divided into **Document-Level** tables (metadata, TOC), **Page-Level** tables (content, images, annotations), and **Views** (aggregated statistics and FTS indexes).

Below is the reference for each table/view, including the required command-line flags to generate them.

#### 1. Document-Level Data

These tables contain metadata about the PDF document as a whole.

| Table Name | Description | Required Flags |
| :--- | :--- | :--- |
| **DOCUMENT_INFO** | General document metadata: filename, page count, encryption status, permissions, XMP metadata, form fonts, etc. | `--DocumentInfo` (Default: `True`) |
| **DOCUMENT_PAGE_LABEL** | Page labeling definitions (e.g., roman numerals for front matter, Arabic for body). | `--DocumentPageLabel` (Default: `True`) |
| **DOCUMENT_TOC** | Table of Contents entries with hierarchy levels, titles, destinations, and link types. | `--DocumentToC` (Default: `True`) |
| **DOCUMENT_EMBEDDED_FILE_INFO** | Information about files embedded within the PDF (attachments). | `--DocEmbeddedFileInfo` (Default: `False`) |

#### 2. Page-Level Data

These tables store data extracted from individual pages. Each row corresponds to a specific element on a page.

| Table Name | Description | Required Flags |
| :--- | :--- | :--- |
| **PAGE_PHYSICAL2LABEL** | Mapping of physical page numbers (0-indexed) to logical page labels. | `--PagePhysical2Label` (Default: `False`) |
| **PAGE_TEXT** | Raw text extracted from each page. Includes a virtual column `TXT_LEN`. | `--PageText` (Default: `False`) |
| **PAGE_BLOCK** | Text blocks with bounding boxes, block types (Text/Image), and content. Includes virtual columns for lowercase text and length. | `--PageBlock` (Default: `True`) |
| **PAGE_BLOCK_FTS** | **Virtual Table (FTS5)**. Full-text search index for `PAGE_BLOCK`. Enables fast keyword search across all page blocks. | `--PageBlockFTS` (Default: `False`) |
| **PAGE_HTML** | HTML representation of each page. Includes virtual column `HTML_LEN`. | `--PageHtml` (Default: `False`) |
| **PAGE_XHTML** | XHTML representation of each page. Includes virtual column `XHTML_LEN`. | `--PageXHtml` (Default: `False`) |
| **PAGE_XML** | XML representation of each page. Includes virtual column `XML_LEN`. | `--PageXml` (Default: `False`) |
| **PAGE_DICT** | Python dictionary representation of page content (stringified). | `--PageDict` (Default: `False`) |
| **PAGE_RAWDICT** | Raw dictionary structure of page content (stringified). | `--PageRawDict` (Default: `False`) |
| **PAGE_JSON** | JSON representation of page content (stringified). | `--PageJson` (Default: `False`) |
| **PAGE_RAWJSON** | Raw JSON structure of page content (stringified). | `--PageRawJson` (Default: `False`) |
| **PAGE_SVG** | SVG vector image of the page. Includes virtual column `SVG_LEN`. | `--PageSvg` (Default: `False`) |
| **PAGE_SVG_TEXTASPATH** | SVG vector image with text converted to paths. Includes virtual column `SVG_TEXTASPATH_LEN`. | `--PageSvgTextAsPath` (Default: `False`) |
| **PAGE_PIXMAP** | Rasterized image of the page (JPEG format) stored as a BLOB. | `--PagePixmap` (Default: `False`) |
| **PAGE_FONT** | Fonts used on each page (xref, name, encoding, etc.). | `--PageFont` (Default: `False`) |
| **PAGE_LINK** | Hyperlinks found on each page, including source rect, destination URI, and link type. | `--PageLink` (Default: `True`) |
| **PAGE_WORD** | Individual words with coordinates, block/line/word indices, and stopword detection. Includes virtual columns for alphanumeric cleaning and lowercasing. | `--PageWord` (Default: `False`) |
| **PAGE_TABLE** | Tables extracted from pages. Stores data in multiple formats: `TO_EXTRACT` (list), `TO_JSON`, `TO_MARKDOWN`, `TO_HTML`, `TO_CSV`, and `TO_IMAGE` (BLOB). | `--PageTable` (Default: `False`) |
| **PAGE_IMAGE** | Full binary data of images found on pages, plus metadata (width, height, colorspace, filters). | `--PageImage` (Default: `False`) |
| **PAGE_IMAGE_INFO** | Metadata for images on pages (bbox, resolution, hash/digest, transform matrix) without storing the binary image data. | `--PageImageInfo` (Default: `False`) |
| **PAGE_ANNOTATION** | Annotations (comments, highlights, stamps) with metadata and a thumbnail image (BLOB) of the annotation area. | `--PageAnnotation` (Default: `False`) |
| **PAGE_DRAWINGS** | Vector drawing elements extracted from the page (stringified list of dicts). | `--PageDrawings` (Default: `False`) |

#### 3. Aggregated Views

These are SQLite Views that provide aggregated statistics based on the page-level tables. They do not store data but compute it dynamically.

| View Name | Description | Required Flags |
| :--- | :--- | :--- |
| **DOCUMENT_FONT** | Aggregates font usage across pages (count of pages where each font appears). | `--DocumentFont` (Requires `--PageFont`) |
| **DOCUMENT_UNIQUE_FONT** | Summarizes unique fonts by base font name and total page coverage. | `--DocumentUniqueFont` (Requires `--DocumentFont`) |
| **DOCUMENT_LINK** | Aggregates link statistics, counting how many pages link to each URI. | `--DocumentLink` (Requires `--PageLink`) |
| **DOCUMENT_WORD_FREQUENCY** | Global word frequency count for the entire document, excluding stopwords if configured. | `--DocumentWordFrequency` (Requires `--PageWord`) |
| **PAGE_WORD_FREQUENCY** | Word frequency count per page. | `--PageWordFrequency` (Requires `--PageWord`) |

### `Link` Destination Kinds

```python
"LINK_NONE",  # 0 – No destination. Indicates a dummy link.
"LINK_GOTO",  # 1 – Points to a place in this document.
# - PyMuPDF treats any external link that contains a colon and does not start with 'file:' as LINK_URI.
"LINK_URI",  # 2 – Points to a URI – typically a resource specified with internet syntax.
# - PyMuPDF treats any external link that starts with 'file:' or doesn’t contain a colon, as LINK_LAUNCH.
"LINK_LAUNCH",  # 3 – Launch (open) another file (of any “executable” type).
"LINK_NAMED",  # 4 – points to a named location.
"LINK_GOTOR",  # 5 – Points to a place in another PDF document.
```

### Query Examples

#### Search for Text (Using FTS)
If `--PageBlockFTS` is enabled, you can search for keywords efficiently:

> NOTE: Sometimes the following command needs to be executed before:
> ```sql
> INSERT INTO PAGE_BLOCK_FTS(PAGE_BLOCK_FTS) VALUES('rebuild')
> ```


```sql
    SELECT S.PAGE_NUMBER
         , S.BLOCK_NO
         , highlight(PAGE_BLOCK_FTS, 0, '<<', '>>') 
        AS HIGHLIGHTED_TEXT
      FROM PAGE_BLOCK_FTS T
INNER JOIN PAGE_BLOCK S ON T.ROWID = S.ROWID
     WHERE T.BLOCK_TEXT MATCH 'keyword'
```

```sql
    SELECT T.RANK
         , T.ROWID
         , S.PAGE_NUMBER
         , S.BLOCK_NO 
         , S.TEXT_LEN
         , highlight( PAGE_BLOCK_FTS, 0, '<<<', '>>>')
        AS HIGHLIGHTED
         , T.BLOCK_TEXT
      FROM PAGE_BLOCK_FTS T
INNER JOIN PAGE_BLOCK S
        ON T.ROWID = S.ROWID
     WHERE T.BLOCK_TEXT MATCH 'resume OR interview OR question'
  ORDER BY T.RANK ASC
```

#### Extract Tables as CSV
If `--PageTable` is enabled, you can retrieve the CSV string directly:

```sql
SELECT 
    PAGE_NUMBER, 
    TABLE_, 
    TO_CSV 
FROM PAGE_TABLE 
WHERE PAGE_NUMBER = 5;
```

#### Get Document Metadata
```sql
SELECT 
    NAME, 
    PAGE_COUNT, 
    IS_ENCRYPTED, 
    METADATA 
FROM DOCUMENT_INFO;
```

#### Analyze Word Frequency
If `--PageWord` and `--DocumentWordFrequency` are enabled:

```sql
SELECT 
    LOWERED_ALPHANUM, 
    FREQ 
FROM DOCUMENT_WORD_FREQUENCY 
WHERE STOPWORD = 0 
ORDER BY FREQ DESC 
LIMIT 10;
```

### Notes on Storage

*   **Binary Data**: Images (`PAGE_IMAGE`, `PAGE_ANNOTATION`, `PAGE_TABLE.TO_IMAGE`) and Page Pixmaps (`PAGE_PIXMAP`) are stored as BLOBs. This can significantly increase the database size.
*   **Virtual Columns**: Many tables use `GENERATED ALWAYS AS` virtual columns (e.g., `lower(TEXT)`, `length(TEXT)`) to optimize queries without storing redundant data.
*   **FTS5**: The `PAGE_BLOCK_FTS` table is a virtual table using SQLite's FTS5 module. It mirrors content from `PAGE_BLOCK` for fast full-text search capabilities.


---

### Full-Text Search (FTS5) Query Explanation

SEE MORE : https://www.sqlite.org/fts5.html

The `doc2sqlite` package enables high-performance text search using SQLite's FTS5 virtual table. Below is an explanation of the standard query used to search within extracted page blocks.

#### The Query

```sql
    SELECT T.RANK
         , T.ROWID
         , S.PAGE_NUMBER
         , S.BLOCK_NO 
         , S.TEXT_LEN
         , highlight(PAGE_BLOCK_FTS, 0, '<<<', '>>>') AS HIGHLIGHTED
         , T.BLOCK_TEXT
      FROM PAGE_BLOCK_FTS T
INNER JOIN PAGE_BLOCK S 
        ON T.ROWID = S.ROWID
     WHERE T.BLOCK_TEXT MATCH 'resume OR interview OR question'
  ORDER BY T.RANK ASC
```

#### Column Explanation

| Column | Source | Description |
| :--- | :--- | :--- |
| **RANK** | `PAGE_BLOCK_FTS` | A numerical score representing the relevance of the match. **Lower values indicate higher relevance.** The ordering is typically ascending (`ASC`) so the most relevant results appear first. |
| **ROWID** | `PAGE_BLOCK_FTS` | The internal row identifier of the FTS table. This is used to join back to the original `PAGE_BLOCK` table to retrieve structured metadata. |
| **PAGE_NUMBER** | `PAGE_BLOCK` | The physical page number (0-indexed) in the PDF where the matching text block is located. |
| **BLOCK_NO** | `PAGE_BLOCK` | The unique identifier of the text block within that page. Useful for referencing specific layout elements. |
| **TEXT_LEN** | `PAGE_BLOCK` | The character length of the text block. Helpful for filtering out trivial fragments or identifying large paragraphs. |
| **HIGHLIGHTED** | `FTS5 Function` | The text block with matched terms wrapped in the specified markers (`<<<` and `>>>`). This allows UI components to visually emphasize keywords. Note: The `highlight` function may return `NULL` if the match occurs in a term not fully present in the stored text (e.g., due to normalization) or if the row is not in the content table. |
| **BLOCK_TEXT** | `PAGE_BLOCK_FTS` | The raw text content of the matching block as indexed by FTS. |

#### How SQLite3 FTS5 RANK Works

The `RANK` column is generated by the FTS5 engine based on the **BM25 (Best Matching 25)** statistical model. It is not an arbitrary count but a weighted score calculated as follows:

1.  **Term Frequency (TF)**: How often the search terms appear in the specific document (block).
2.  **Inverse Document Frequency (IDF)**: How rare the search terms are across the entire corpus. Rare words score higher than common words (e.g., "interview" may score higher than "the" if "the" were in the query).
3.  **Document Length Normalization**: Longer documents are penalized slightly to prevent them from dominating results simply due to size.
4.  **Proximity**: If multiple terms are used, their closeness together in the text increases the relevance score.

**Important Note on Ordering:**
In SQLite FTS5, a **lower rank value means higher relevance**. Therefore, queries should always use `ORDER BY RANK ASC` to show the best matches first. A rank of `0.0` is the ideal perfect match, while negative values indicate increasing relevance relative to other results.

#### Example Usage in Python

```python
import sqlite3

def search_pdf(db_path, query_terms):
    conn = sqlite3.connect(db_path)
    # Construct the MATCH clause safely
    # Note: For complex boolean logic, ensure terms are escaped or use parameterized 
    # approaches if available in your specific SQLite build, though FTS MATCH 
    # strings are often constructed directly.
    match_clause = " OR ".join(query_terms)
    
    sql = """
            SELECT T.RANK
                , S.PAGE_NUMBER
                , S.BLOCK_NO
                , highlight(PAGE_BLOCK_FTS, 0, '<<', '>>') AS HIGHLIGHTED
              FROM PAGE_BLOCK_FTS T
        INNER JOIN PAGE_BLOCK S 
                ON T.ROWID = S.ROWID
            WHERE T.BLOCK_TEXT MATCH ?
          ORDER BY T.RANK ASC
    """
    
    cursor = conn.execute(sql, (match_clause,))
    results = cursor.fetchall()
    conn.close()
    return results
```

---


## System Requirements

*   **Python**: 3.9 or higher.
*   **Operating System**: Linux, macOS, or Windows.
*   **System Libraries**: `PyMuPDF` relies on system-level PDF rendering libraries.
    *   **Linux**: You may need to install `libfontconfig1`, `libfreetype6`, and `libssl`.
        ```bash
        # Ubuntu/Debian
        sudo apt-get install libfontconfig1 libfreetype6 libssl1.1
        # CentOS/RHEL
        sudo yum install fontconfig freetype openssl
        ```
    *   **macOS**: Usually works out-of-the-box via Homebrew installations of Python.
    *   **Windows**: Pre-built wheels are provided; no extra system libraries are typically required.

---

## Performance Tips

Processing large PDFs (100+ pages) or extracting high-resolution images (`--PagePixmap`, `--PageImage`) can consume significant RAM.

*   **Selective Extraction**: Only enable the flags you need. Extracting `--PageSvg` or `--PagePixmap` for every page dramatically increases processing time and database size.
*   **Chunking**: For very large documents, consider splitting the PDF into smaller chunks using external tools before processing, or process pages in batches if you extend the script.
*   **Database Size**: Binary blobs (images) are stored directly in the SQLite database. If database size becomes an issue, consider disabling `--PageImage` and `--PagePixmap` and relying on `--PageImageInfo` for metadata only.


---
## Using Configuration Files

For reproducible workflows, use a YAML configuration file. Create a file named `config.yaml`:

```yaml
# Global Settings
InputPdf: "report_2023.pdf"

# Document Level Exactions
DocumentInfo: true
DocumentToC: true
DocumentPageLabel: true

# Page Level Exactions (Enable only what you need)
PageText: true
PageTable: true
PageImageInfo: true

# Disable heavy extractions to save space
PagePixmap: false
PageSvg: false
PageImage: false

# Enable Full-Text Search
PageBlock: true
PageBlockFTS: true
```

---


## Troubleshooting

Address the most common errors users encounter with PyMuPDF and SQLite.

**Q: I get a `ModuleNotFoundError: No module named 'pymupdf'` or installation fails.**
A: Ensure you are using a supported Python version. If installation fails due to system library issues on Linux, refer to the **System Requirements** section above to install missing fonts or SSL libraries.

**Q: The database file is huge.**
A: Check which binary extraction flags are enabled. `--PageImage`, `--PagePixmap`, and `--PageAnnotation` store raw binary data in the SQLite BLOB columns. Disable these if you only need text or metadata.

**Q: `sqlite3.OperationalError: database is locked`**
A: Ensure no other process (like a database browser or another instance of the script) has the database file open. The script creates a new database or overwrites the existing one by dropping tables.

**Q: Some text looks garbled or missing.**
A: PDFs are layout-based, not semantic-based. Text extraction depends on how the PDF was generated. If the PDF contains scanned images rather than text layers, `doc2sqlite` will not extract text. You would need an OCR (Optical Character Recognition) tool before or after extraction.


---

## License

This project is licensed under the [MIT License](LICENSE).

## Citation

If you use `doc2sqlite` in your research or projects, please cite it as:

```bibtex
@software{doc2sqlite,
  author = {Your Name},
  title = {doc2sqlite: PDF to SQLite Extraction Tool},
  year = {2024},
  url = {https://github.com/yourusername/doc2sqlite}
}
```

---


### 6. Contributing / Issue Reporting
Encourage community involvement and bug reporting.

```markdown
## Contributing

Contributions are welcome! 
Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Reporting Issues
Found a bug or have a feature request? Please open an issue on GitHub with:
1. The version of `doc2sqlite` you are using.
2. The operating system and Python version.
3. The command or configuration file used.
4. Any error logs or stack traces.
```
