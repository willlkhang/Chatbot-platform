import json
import re

input_file = "./generated_data/train.jsonl"
output_file = "./generated_data/train_c.jsonl"


with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    for line in f_in:
        try:
            data = json.loads(line)
            data['input'] = data['input'].replace('\"', '') #clean /"
            data['input'] = re.sub(r'0{5,}', '', data['input']) #clean repeat character 
            f_out.write(json.dumps(data) + '\n')
        except json.JSONDecodeError:
            continue

print("Done")