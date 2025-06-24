import os
import openai
import pandas as pd
import base64
import argparse

# Configuration
client = openai.OpenAI(api_key="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")
folder_path = "10_image/"

def get_prompt(use_onestep, use_twostep):
    if use_onestep:
        return """Function as the most accurate gene relationship extractor by analyzing the relationships 
provided in the image. Genes are enclosed in circles or ellipses, and their relationships are represented 
by arrows and T-bars. The types of relationships are:

1. Inhibition: Represented by a T-bar, where the gene near the T-bar end is the one being inhibited by 
   the gene at the opposite end. A dashed T-bar represents indirect inhibition.

2. Activation: Represented by an arrow, where the arrowhead indicates the activation target. A dashed 
   arrow represents indirect activation.

As a plant scientist and protein phosphorylation expert, please read the uploaded image.
In this image, for each relationship, please look for the phosphorylation events in this image.  \
Often the protein phosphorylation events are represented by a circle with a letter P inside the circle.  \
Please examine if there is phosphorylation events near the genes. If there is a circle with a letter P near the genes, \
it means this relation involving phosphorylation events. Please analyze the image, and determine if this relation  \
involve phosphorylation event with just YES or NO answer.
    
Important notes:
- For T-bars: The gene at the T-bar end is the target (gene2), and it is inhibited by the gene at the opposite end (gene1).
- For arrows: The base of the arrow is the starting gene (gene1), and the arrowhead points to the target gene (gene2).
- Ensure correct interpretation of the symbols: Arrows indicate activation, while T-bars indicate inhibition.
- Determine if this relation involve phosphorylation event
- Provide the extracted gene relationships in the following format:
  1. Gene1 -- relationship type (directly/indirectly) -- activates/inhibits -- Gene2 -- YES/NO.
  2. Example: IGF-1R -- directly -- activates -- PI3K -- YES.

Please accurately extract each gene relationship without confusing them, considering the direction and type 
of interaction explicitly."""

    elif use_twostep:
        return """Function as the most accurate gene relationship extractor by analyzing the relationships 
provided in the image. Genes are enclosed in circles or ellipses, and their relationships are represented 
by arrows and T-bars. The types of relationships are:

1. Inhibition: Represented by a T-bar, where the gene near the T-bar end is the one being inhibited by 
   the gene at the opposite end. A dashed T-bar represents indirect inhibition.

2. Activation: Represented by an arrow, where the arrowhead indicates the activation target. A dashed 
   arrow represents indirect activation.

Important notes:
- For T-bars: The gene at the T-bar end is the target (gene2), and it is inhibited by the gene at the opposite end (gene1).
- For arrows: The base of the arrow is the starting gene (gene1), and the arrowhead points to the target gene (gene2).
- Ensure correct interpretation of the symbols: Arrows indicate activation, while T-bars indicate inhibition.
- Provide the extracted gene relationships in the following format:
  1. Gene1 -- relationship type (directly/indirectly) -- activates/inhibits -- Gene2.
  2. Example: IGF-1R -- directly -- activates -- PI3K.

Please accurately extract each gene relationship without confusing them, considering the direction and type 
of interaction explicitly."""

def evaluate_image(question, image_path):
    with open(image_path, "rb") as image:
        base64_image = base64.b64encode(image.read()).decode('utf-8')

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        max_tokens=500,
    )

    message = completion.choices[0].message.content.strip()

    return message

def parse_image(image_path, use_onestep, use_twostep):
    message = evaluate_image(get_prompt(use_onestep, use_twostep), image_path)
    print(f"Raw message from API: {message}")
    message_list = message.split("\n\n")
    for x in message_list:
        if "\n" in x:
            message = x
            break
    
    if isinstance(message, str):
        message = message.split(". ")
        if message and message[0] == '':
            message.pop(0)

        for x in range(len(message)):
            if '\n' in message[x]:
                message[x] = message[x][0:message[x].find('\n')]
    else:
        raise ValueError("Expected message to be a string after processing, but got a different type")
    print(f"Processed message segments: {message}")  # Debugging line
    return message

def phosphorylation(image_path, relation):
    return evaluate_image('As a plant scientist and protein phosphorylation expert, please read the uploaded image.  \
    In this image, there is a relationship:' + relation + " Please look for the phosphorylation events in this image.  \
    Often the protein phosphorylation events are represented by a circle with a letter P inside the circle.  \
    Please examine if there is phosphorylation events near the genes. If there is a circle with a letter P near the genes, \
    it means this relation involving phosphorylation events. Please analyze the image, and determine if this relation  \
    involve phosphorylation event with just YES or NO answer.", image_path)

def onestep_main():
    output_dir = "onestep"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing image: {filename}")
            message = parse_image(image_path, True, False)

            messageParsed = []

            for x in message:
                if x.strip().isdigit() or not x.strip():
                    continue  # Skip segments like '1' or empty strings

                segment = x.split(' -- ')
                if len(segment) == 5:
                    message1 = segment[0].strip()
                    message1 = message1.rstrip('.')
                    message2 = segment[1].strip()
                    message2 = message2.rstrip('.')
                    message3 = segment[2].strip()
                    message3 = message3.rstrip('.')
                    message4 = segment[3].strip()
                    message4 = message4.rstrip('.')
                    message5 = segment[4].strip()
                    message5 = message5.rstrip('.')
                    if message5 == 'No':
                        message5 = 'NO'
                    if message5 == 'Yes':
                        message5 = 'YES'

                    messageParsed.append([message1, message2, message3, message4, message5])

            if messageParsed:
                df = pd.DataFrame(messageParsed,
                                  columns=["Gene1", "RelationType", "Action", "Gene2", "Phosphorylation"])

                output_filename = filename.split('.')[0] + '.xlsx'
                output_path = os.path.join(output_dir, output_filename)

                with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name='results', index=False)
                print(f"Results saved to: {output_path}")
            else:
                print(f"No valid message segments found for image: {filename}")

def twostep_main():
    output_dir = "twostep"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing image: {filename}")
            message = parse_image(image_path, False, True)

            messageParsed = []

            for x in message:
                if x.strip().isdigit() or not x.strip():
                    continue  # Skip segments like '1' or empty strings

                segment = x.split(' -- ')
                if len(segment) == 4:
                    message1 = segment[0].strip()
                    message1 = message1.rstrip('.')
                    message2 = segment[1].strip()
                    message2 = message2.rstrip('.')
                    message3 = segment[2].strip()
                    message3 = message3.rstrip('.')
                    message4 = segment[3].strip()
                    message4 = message4.rstrip('.')

                    phosphorylation_result = phosphorylation(image_path, x)
                    phosphorylation_result = phosphorylation_result.rstrip('.')
                    if phosphorylation_result == 'No':
                        phosphorylation_result = 'NO'
                    if phosphorylation_result == 'Yes':
                        phosphorylation_result = 'YES'

                    messageParsed.append([message1, message2, message3, message4, phosphorylation_result])

            if messageParsed:
                df = pd.DataFrame(messageParsed,
                                  columns=["Gene1", "RelationType", "Action", "Gene2", "Phosphorylation"])
                output_filename = filename.split('.')[0] + '.xlsx'
                output_path = os.path.join(output_dir, output_filename)
                with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name='twostep', index=False)
                print(f"Finished processing image: {filename}")
            else:
                print(f"No valid message segments found for image: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process images with either one-step or two-step mode.')
    parser.add_argument('--mode', type=str, choices=['onestep', 'twostep'], required=True,
                      help='Choose between onestep or twostep mode')
    
    args = parser.parse_args()

    if args.mode == 'onestep':
        onestep_main()
    elif args.mode == 'twostep':
        twostep_main()