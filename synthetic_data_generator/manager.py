from languagemodel import MyModel
from prompts import generation_prompt, categories
from generator import MyGenerator


if __name__ == "__main__":
    #self, max_seq_length, model_name='unsloth/Phi-3-mini-4k-instruct-bnb-4bit', load_in_4bit=True):
    llm_model = MyModel(model_name='unsloth/Phi-3-mini-4k-instruct-bnb-4bit',
                        max_seq_length=2048,
                        load_in_4bit=True)

    model, tokenizer = llm_model.model_tok_init()

    #(self, model, tokenizer, categories, generation_prompt, save_model_name):
    generator = MyGenerator(model=model, 
                            tokenizer=tokenizer, 
                            generation_prompt=generation_prompt, 
                            categories=categories, 
                            save_model_name="./generated_data/train1.jsonl")

    generator.generating()
    generator.save_data()