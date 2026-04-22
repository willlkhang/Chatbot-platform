from unsloth import FastLanguageModel
import torch
import json
import random

#model_name = 'unsloth/Phi-3-mini-4k-instruct-bnb-4bit'

class MyModel():
    def __init__(self, max_seq_length, model_name='unsloth/Phi-3-mini-4k-instruct-bnb-4bit', load_in_4bit=True):
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.load_in_4bit = load_in_4bit

    def model_tok_init(self):
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = self.model_name,
            max_seq_length = self.max_seq_length,
            dtype = None,
            load_in_4bit = self.load_in_4bit
        )

        return model, tokenizer