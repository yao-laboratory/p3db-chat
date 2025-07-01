# Gene Relationship Extraction Tool

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
- Set your OpenAI API key in the script (`client = openai.OpenAI(api_key=...)`).

---

## 🚀 Usage

1. Ensure your images are in the `10_image/` folder.
2. Run the script:

```bash
python chatGPT_prompt_improved_byChatGPT_twostep.py
```

3. The script will process each image and print extracted gene relationships.

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
