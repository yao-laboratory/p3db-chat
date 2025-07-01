import openai
import re
import sys
import os

# --- Configuration ---
# Set your OpenAI API key here, or set the environment variable OPENAI_API_KEY
openai.api_key = os.getenv('OPENAI_API_KEY', '')

if not openai.api_key:
    print("ERROR: Please set your OpenAI API key in bioq.py or as the environment variable OPENAI_API_KEY.")
    sys.exit(1)

def extract_and_format(user_question):
    prompt = f"""
You are a helpful assistant trained to standardize biological research questions.

Instructions:
1. Extract:
   - Species: If not explicitly mentioned, infer it from context (e.g., for plant proteins, default to "Arabidopsis thaliana").
   - ProteinNames: Extract all relevant protein names as a list.
2. Reformulate the user's question using one of the following templates:
   (1) In '{{Species}}', for protein, '{{ProteinName}}', can it be phosphorylated? Please answer yes or no.
   (2) In '{{Species}}', do the proteins '{{ProteinName1}}' and '{{ProteinName2}}' form a protein-protein interaction (PPI)? Please answer yes or no.
   (3) In '{{Species}}', do the kinase ‘{{ProteinName1}}’ phosphorylate '{{ProteinName2}}’? Please answer yes or no.
   (4) In '{{Species}}', what's the potential kinase for protein '{{ProteinName}}'? Please list them without other sentences.
   (5) In '{{Species}}', what's protein-protein interaction partners for protein '{{ProteinName}}'? Please list them without other sentences.
   (6) The question is outside of our current scope.

User question: "{user_question}"

Respond in this format:

Species: <species>
ProteinNames: [<protein1>, <protein2>, ...]
Formulated question: <reformulated question>
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # ✅ Updated to GPT-4o
        messages=[
            {"role": "system", "content": "You are an assistant trained to reformat biological questions into standardized templates."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def extract_parts(result_text):
    species_match = re.search(r"Species:\s*(.*)", result_text)
    proteins_match = re.search(r"ProteinNames:\s*\[(.*)\]", result_text)
    question_match = re.search(r"Formulated question:\s*(.*)", result_text)

    species = species_match.group(1).strip() if species_match else "Unknown"
    proteins = [p.strip() for p in proteins_match.group(1).split(",")] if proteins_match else []
    question = question_match.group(1).strip() if question_match else None

    return species, proteins, question

def rephrase_formulated_question(user_question, species, proteins):
    prompt = f"""
The user said the previous reformulated question was incorrect. Using the extracted information below, try a better reformulation using the correct format.

Species: {species}
ProteinNames: {proteins}
User question: "{user_question}"

Only respond with:

Formulated question: <new reformulated question>
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # ✅ Updated to GPT-4o
        messages=[
            {"role": "system", "content": "You are an assistant improving reformulated biological questions."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content'].strip()

def answer_reformulated_question(formulated_question):
    prompt = f"""
Answer the following biological question with only "Yes" or "No". Do not add any explanation.

Question: {formulated_question}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # ✅ Updated to GPT-4o
        messages=[
            {"role": "system", "content": "You are a biology assistant answering protein-related questions with a simple yes or no."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content'].strip()

# --- MAIN ---
if __name__ == "__main__":
    user_question = input("Enter your biological question:\n> ")

    # Step 1: Initial extraction
    result = extract_and_format(user_question)
    species, proteins, formulated_question = extract_parts(result)

    # Show extracted details
    print(f"\nSpecies: {species}")
    print(f"ProteinNames: {proteins}")
    print(f"Formulated question: {formulated_question}")

    # Step 2: Exit if out of scope
    if "outside of our current scope" in formulated_question.lower():
        print("\nThe question is outside of our current scope. Exiting.")
        sys.exit()

    # Step 3: User feedback loop
    while True:
        feedback = input("\nIs this formulated question good or bad? (good/bad): ").strip().lower()

        if feedback == "good":
            answer = answer_reformulated_question(formulated_question)
            print("\nAnswer:", answer)
            break

        elif feedback == "bad":
            print("\nTrying a better formulation...\n")
            reformulated = rephrase_formulated_question(user_question, species, proteins)
            match = re.search(r"Formulated question:\s*(.*)", reformulated)
            if match:
                formulated_question = match.group(1).strip()
                print(f"New Formulated question: {formulated_question}")
            else:
                print("Couldn't generate a better question.")
                break

        else:
            print("Please type only 'good' or 'bad'.")