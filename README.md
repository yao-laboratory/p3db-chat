# p3db-chat

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
