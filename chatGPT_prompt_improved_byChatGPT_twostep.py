import os
import openai
import pandas as pd
import base64
import re

'''
1. only consider the protein/gene name, other words, such as "xxx stress", "micromolecular" wont be consider
2. wont seperate complex,if the complex was considered seperately, it's still correct. eg picture1, LLG1/LLG2
'''

client = openai.OpenAI(api_key="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")
folder_path = "10_image/"
first_prompt = """Function as the most accurate gene relationship extractor by analyzing the relationships 
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


def main():
    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing image: {filename}")
            message = parseImage(image_path)

            messageParsed = []

            for x in message:
                # Filter out segments that are not useful
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

                    phosphorylation = Phosphorylation(image_path, x)
                    phosphorylation = phosphorylation.rstrip('.')
                    if phosphorylation == 'No':
                        phosphorylation = 'NO'
                    if phosphorylation == 'Yes':
                        phosphorylation = 'YES'
                    messageParsed.append([message1, message2, message3, message4, phosphorylation])
                else:
                    print(f"Unexpected format in message segment: {segment}")

            if messageParsed:  # Only create the DataFrame if there is something to parse
                df = pd.DataFrame(messageParsed,
                                  columns=["Gene1", "RelationType", "Action", "Gene2", "Phosphorylation"])
                with pd.ExcelWriter('repeat_10/10_'+filename.split('.')[0] + '_results.xlsx', engine='openpyxl', mode='w') as writer:
                    # Write the main DataFrame to the first sheet
                    df.to_excel(writer, sheet_name='twostep', index=False)
                # df.to_csv('repeat_10/'+filename.split('.')[0] + '_results.csv', index=False)
                print(f"Finished processing image: {filename}")
            else:
                print(f"No valid message segments found for image: {filename}")


def evaluateImage(question, imagePath):
    with open(imagePath, "rb") as image:
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


def parseImage(imagePath):
    message = evaluateImage(first_prompt, imagePath)

    print(f"Raw message from API: {message}")  # Debugging line

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


def Phosphorylation(imagePath, relation):
    message = evaluateImage('As a plant scientist and protein phosphorylation expert, please read the uploaded image.  \
    In this image, there is a relationship:' + relation + " Please look for the phosphorylation events in this image.  \
    Often the protein phosphorylation events are represented by a circle with a letter P inside the circle.  \
    Please examine if there is phosphorylation events near the genes. If there is a circle with a letter P near the genes, \
    it means this relation involving phosphorylation events. Please analyze the image, and determine if this relation  \
    involve phosphorylation event with just YES or NO answer.", imagePath)

    return message


main()