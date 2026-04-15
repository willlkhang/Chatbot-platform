import random
import json
import os

class MyGenerator():
    def __init__(self, model, tokenizer, categories, generation_prompt, save_model_name):
        self.model = model
        self.tokenizer = tokenizer
        self.categories = categories
        self.generation_prompt = generation_prompt
        self.data = []
        self.save_model_name = save_model_name
    
    def generating(self):
        print(f"Start generating training data for {len(self.categories)} categories")

        for cat, keywords in self.categories.items():
            print(f"--> Generating data for: {cat}...")
            for i in range(2): #this depends deeply on prompt sending to llm model
                messages = [
                    {"role": "user", "content": self.generation_prompt.format(category=cat, keywords=keywords)}
                ]

                inputs = self.tokenizer.apply_chat_template(
                    messages, 
                    tokenize=True, 
                    add_generation_prompt=True, 
                    return_tensors="pt"
                ).to("cuda")

                outputs = self.model.generate(
                    inputs, 
                    max_new_tokens=2048,
                    temperature=0.9, # High temperature = more creativity/variety
                    use_cache=True
                )

                #decode output
                decoded_text = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

                if "assistant" in decoded_text:
                    raw_response = decoded_text.split("assistant")[-1].strip()
                else:
                    raw_response = decoded_text

                lines = raw_response.split("\n")

                count = 0
                for line in lines:
                    line = line.strip()
                    # Remove bullets, numbers, and garbage
                    clean_line = line.lstrip("- ").lstrip("* ").lstrip("1234567890. ").strip()
                    
                    # Keep only valid-looking lines
                    if len(clean_line) > 10 and not clean_line.startswith("Here is") and not clean_line.startswith("Sure"):
                        self.data.append({"input": clean_line, "output": cat})
                        count += 1
                
                print(f"Batch {i+1}: Generated {count} examples")
        print(f"Shuffling and saving {len(self.data)} examples...")
        return random.shuffle(self.data)
    
    def save_data(self):
        dir = os.path.dirname(self.save_model_name)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
            print(f"Created directory: {dir}")
            
        with open(self.save_model_name, "w", encoding='utf-8') as f:
            for entry in self.data:
                json.dump(entry, f)
                f.write("\n")
        print("Generating training data. Done")