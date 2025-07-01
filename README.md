# p3db-chat

# Quick Start

1. **Install requirements:**
   ```bash
   pip install openai pandas
   ```

2. **Set your OpenAI API key:**
   - Option 1 (recommended):
     ```bash
     export OPENAI_API_KEY=your-key-here
     ```
   - Option 2: Edit the scripts directly (see comments at the top of each script).

3. **For geneimg.py only:**
   - Set your image folder path:
     ```bash
     export GENEIMG_FOLDER=/path/to/your/images
     ```
   - Or edit `folder_path` in the script.

4. **Run the tools:**
   - For biological question standardization:
     ```bash
     python bioq.py
     ```
   - For gene relationship extraction from images:
     ```bash
     python geneimg.py
     ```

---

## Part 1: Biological Question Standardization and Answering Tool

This Python tool streamlines biological research questions by:
1. Extracting relevant entities (species, protein names).
2. Reformulating the question into standardized templates.
3. Optionally rephrasing the question if the initial reformulation is unsatisfactory.
4. Generating a simple **Yes/No** answer.

It leverages the OpenAI GPT-4o model for natural language processing.

---

## ✨ Features

- **Automatic Entity Extraction**
  - Species (e.g., *Arabidopsis thaliana*)
  - Protein names
- **Standardized Question Templates**
  - Phosphorylation queries
  - Protein-protein interaction queries
  - Kinase prediction
- **Interactive Feedback Loop**
  - Accept or rephrase the reformulated question
- **Simple Yes/No Answering**

---

## 📋 Requirements

- Python 3.7+
- `openai` Python SDK

Install dependencies:

```bash
pip install openai
```

## ⚙️ Configuration

Set your OpenAI API key in the script:

```python
openai.api_key = 'YOUR_API_KEY_HERE'
```

## 🚀 Usage

Run the script:

```bash
python your_script.py
```

You will be prompted:
```
Enter your biological question:
>
```
Example input:
```
Which kinases phosphorylate AtMPK3?
```
### Requirements

## 📝 Example Workflow

1. **Input**
```
In Arabidopsis thaliana, do the kinase CPK27 phosphorylate tonoplast sugar transporter 2?
```


2. **Extracted**
```
Species: Arabidopsis thaliana
ProteinNames: [CPK27, tonoplast sugar transporter 2]
```


3. **Formulated Question**
```
In 'Arabidopsis thaliana', do the kinase 'CPK27' phosphorylate 'tonoplast sugar transporter 2'? Please answer yes or no.
```

4. **Answer**
```
Yes
```


## Part 2: Gene Relationship Extraction Tool

## Overview

This Python tool automatically extracts gene/protein relationships from biological pathway images. It uses the OpenAI GPT API to interpret diagrammatic relationships (arrows and T-bars) between genes, focusing only on gene/protein names and ignoring other terms (e.g., stress, micromolecular).

---

## ✨ Features

- **Automated Image Analysis**
  - Processes images in a specified folder
  - Supports `.png`, `.jpg`, and `.jpeg` formats
- **Gene Relationship Extraction**
  - Identifies activation (arrows) and inhibition (T-bars)
  - Distinguishes direct and indirect interactions (solid/dashed lines)
  - Outputs relationships in a standardized format:
    - `Gene1 -- [directly/indirectly] -- [activates/inhibits] -- Gene2`
- **Batch Processing**
  - Iterates over all images in the folder
- **Clear Output**
  - Prints results for each processed image

---

## 📋 Requirements

- Python 3.7+
- `openai` Python SDK
- `pandas`

Install dependencies:

```bash
pip install openai pandas
```

---

## ⚙️ Configuration

- Place your biological pathway images in the `10_image/` directory (default, or edit `folder_path` in the script).
- Set your OpenAI API key in the script (`openai.api_key = "<your_key>"` for Part 1, `client = openai.OpenAI(api_key="<your_key>")` for Part 2).
- Set your image folder path in the script (`folder_path = "<your_folder>"`).

---

## 🚀 Usage

1. Place your images in the folder specified by `GENEIMG_FOLDER` (or set `folder_path` in the script).
2. Run the script:

```bash
python geneimg.py
```

3. The script will process each image and print extracted gene relationships.

---

## 🖼️ Example (geneimg.py)

Suppose you have an image named `example.png` in your image folder. Run:

```bash
export GENEIMG_FOLDER=$(pwd)
python geneimg.py
```

The script will analyze `example.png` and output the gene relationships it finds.

**Image credit:**
Lin, L., Wu, J., Jiang, M. and Wang, Y., 2021. Plant mitogen-activated protein kinase cascades in environmental stresses. *International Journal of Molecular Sciences*, 22(4), p.1543.

---

## 📝 Notes

- Only gene/protein names are considered; other biological terms are ignored.
- Complexes are not separated unless explicitly depicted in the image.
- The script interprets arrows as activation and T-bars as inhibition, following biological conventions.
- Make sure your OpenAI API key is valid and has sufficient quota.

---

## 📂 Output Format Example

```
IGF-1R -- directly -- activates -- PI3K
GeneA -- indirectly -- inhibits -- GeneB
```

---

## 📧 Contact

For questions or suggestions, please open an issue or contact the maintainer.
