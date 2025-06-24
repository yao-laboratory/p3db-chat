import os
import openai
import pandas as pd
import base64
import argparse
import re  # Added for regex-based filtering

# Configuration
client = openai.OpenAI(api_key="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")
folder_path = "10_image/"

def save_metrics_to_file(output_dir, filename, relationship_accuracy, long_error_rate):
    """Save accuracy metrics to both a text file and a CSV file."""
    txt_file_path = os.path.join(output_dir, "metrics_summary.txt")
    csv_file_path = os.path.join(output_dir, "metrics_summary.csv")
    
    # Save to TXT file
    with open(txt_file_path, "a") as txt_file:
        txt_file.write(f"Image: {filename}\n")
        txt_file.write(f"Relationship Accuracy: {relationship_accuracy:.2%}\n")
        txt_file.write(f"Long-Error-Rate: {long_error_rate:.2%}\n")
        txt_file.write("-" * 40 + "\n")
    
    # Save to CSV file
    metrics_data = {
        "Image": [filename],
        "Relationship Accuracy": [relationship_accuracy],
        "Long-Error-Rate": [long_error_rate]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    
    if not os.path.exists(csv_file_path):
        metrics_df.to_csv(csv_file_path, index=False)
    else:
        metrics_df.to_csv(csv_file_path, mode="a", header=False, index=False)


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
    """Processes the image using OpenAI API."""
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

    return completion.choices[0].message.content.strip()

def parse_image(image_path, use_onestep, use_twostep):
    """Extracts relationships from the image using AI analysis."""
    message = evaluate_image(get_prompt(use_onestep, use_twostep), image_path)
    
    # Debugging line
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

        # Filtering out unwanted elements
        message = [x.split("\n")[0] for x in message if not x.strip().isdigit() and x.strip()]
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

def calculate_metrics(pred_df, ground_truth_path, output_dir, filename):
    """Compare predicted relationships with ground truth and calculate accuracy metrics."""
    
    # Check if the ground truth file exists
    if not os.path.exists(ground_truth_path):
        print(f"Warning: Ground truth file '{ground_truth_path}' not found. Skipping evaluation.")
        return None, None

    # Load the ground truth file
    ground_truth_df = pd.read_excel(ground_truth_path)

    # Validate required columns in the ground truth file
    expected_columns = ['Gene1', 'RelationType', 'Action', 'Gene2']
    missing_columns = [col for col in expected_columns if col not in ground_truth_df.columns]

    if missing_columns:
        print(f"Warning: The ground truth file '{ground_truth_path}' is missing columns: {missing_columns}")
        return None, None  # Exit without calculating metrics

    # Initialize sets for comparisons
    ground_truth_gene_pairs = set()
    ground_truth_details = set()

    # Populate ground truth sets
    for _, row in ground_truth_df.iterrows():
        gene1 = row['Gene1']
        gene2 = row['Gene2']
        ground_truth_gene_pairs.add(frozenset([gene1, gene2]))
        ground_truth_details.add((frozenset([gene1, gene2]), row['RelationType'], row['Action']))

    # Initialize accuracy counters
    correct_relationships = 0
    fully_correct = 0

    # Compare predictions with ground truth
    for _, pred_row in pred_df.iterrows():
        gene1_pred = pred_row['Gene1']
        gene2_pred = pred_row['Gene2']
        rel_type_pred = pred_row['RelationType']
        action_pred = pred_row['Action']
        
        gene_pair_pred = frozenset([gene1_pred, gene2_pred])
        details_pred = (gene_pair_pred, rel_type_pred, action_pred)

        if gene_pair_pred in ground_truth_gene_pairs:
            correct_relationships += 1
            if details_pred in ground_truth_details:
                fully_correct += 1

    # Calculate accuracy metrics
    total_predictions = len(pred_df)
    relationship_accuracy = correct_relationships / total_predictions if total_predictions > 0 else 0
    long_error_rate = (correct_relationships - fully_correct) / correct_relationships if correct_relationships > 0 else 0

    # Save metrics to files
    save_metrics_to_file(output_dir, filename, relationship_accuracy, long_error_rate)

    return relationship_accuracy, long_error_rate

def onestep_main(ground_truth_dir=None):
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
                    continue

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

                # Calculate metrics if ground truth exists
                relationship_accuracy, long_error_rate = None, None
                if ground_truth_dir:
                    base_name = os.path.splitext(filename)[0]
                    ground_truth_path = os.path.join(ground_truth_dir, f"{base_name}.xlsx")
                    relationship_accuracy, long_error_rate = calculate_metrics(df, ground_truth_path)

                with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name='results', index=False)
                    if relationship_accuracy is not None and long_error_rate is not None:
                        metrics_df = pd.DataFrame({
                            'Metric': ['Relationship Accuracy', 'Long-Error-Rate'],
                            'Value': [relationship_accuracy, long_error_rate]
                        })
                        metrics_df.to_excel(writer, sheet_name='metrics', index=False)
                print(f"Results saved to: {output_path}")
            else:
                print(f"No valid message segments found for image: {filename}")

def twostep_main(ground_truth_dir=None):
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
                    continue

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

                # Calculate metrics if ground truth exists
                relationship_accuracy, long_error_rate = None, None
                if ground_truth_dir:
                    base_name = os.path.splitext(filename)[0]
                    ground_truth_path = os.path.join(ground_truth_dir, f"{base_name}.xlsx")
                    relationship_accuracy, long_error_rate = calculate_metrics(df, ground_truth_path)

                with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name='twostep', index=False)
                    if relationship_accuracy is not None and long_error_rate is not None:
                        metrics_df = pd.DataFrame({
                            'Metric': ['Relationship Accuracy', 'Long-Error-Rate'],
                            'Value': [relationship_accuracy, long_error_rate]
                        })
                        metrics_df.to_excel(writer, sheet_name='metrics', index=False)
                print(f"Finished processing image: {filename}")
            else:
                print(f"No valid message segments found for image: {filename}")


def process_images(use_onestep, use_twostep, output_dir, ground_truth_dir=None):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing image: {filename}")
            
            message = parse_image(image_path, use_onestep, use_twostep)
            messageParsed = []

            for x in message:
                if x.strip().isdigit() or not x.strip():
                    continue

                segment = x.split(' -- ')
                if len(segment) == 5:
                    messageParsed.append([segment[0].strip(), segment[1].strip(), segment[2].strip(), segment[3].strip(), segment[4].strip()])

            if messageParsed:
                df = pd.DataFrame(messageParsed, columns=["Gene1", "RelationType", "Action", "Gene2", "Phosphorylation"])
                output_filename = filename.split('.')[0] + '.xlsx'
                output_path = os.path.join(output_dir, output_filename)

                # Calculate metrics if ground truth exists
                relationship_accuracy, long_error_rate = None, None
                if ground_truth_dir:
                    base_name = os.path.splitext(filename)[0]
                    ground_truth_path = os.path.join(ground_truth_dir, f"{base_name}.xlsx")
                    relationship_accuracy, long_error_rate = calculate_metrics(df, ground_truth_path, output_dir, filename)

                with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name='results', index=False)

                print(f"Results saved to: {output_path}")
            else:
                print(f"No valid message segments found for image: {filename}")


def onestep_main(ground_truth_dir=None):
    process_images(use_onestep=True, use_twostep=False, output_dir="onestep", ground_truth_dir=ground_truth_dir)


def twostep_main(ground_truth_dir=None):
    process_images(use_onestep=False, use_twostep=True, output_dir="twostep", ground_truth_dir=ground_truth_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process images with either one-step or two-step mode.')
    parser.add_argument('--mode', type=str, choices=['onestep', 'twostep'], required=True,
                        help='Choose between onestep or twostep mode')
    parser.add_argument('--ground_truth_dir', type=str, help='Directory containing ground truth Excel files')

    args = parser.parse_args()

    if args.mode == 'onestep':
        onestep_main(args.ground_truth_dir)
    elif args.mode == 'twostep':
        twostep_main(args.ground_truth_dir)