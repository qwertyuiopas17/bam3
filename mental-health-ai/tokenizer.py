import re
import pickle
from collections import Counter

class MentalHealthTokenizer:
    def __init__(self):
        self.pad_token = '<PAD>'
        self.sos_token = '<SOS>'
        self.eos_token = '<EOS>'
        self.unk_token = '<UNK>'
        self.crisis_token = '<CRISIS>'
        self.support_token = '<SUPPORT>'
        self.word2idx = {}
        self.idx2word = {}
        self.vocab_size = 0
    
    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s\'\-\u0964\?]', ' ', text)
        tokens = re.findall(r'\w+|\u0964|\?|\.', text)
        return tokens
    
    def build_vocabulary(self, texts, min_freq=1):
        self.word2idx = {
            self.pad_token: 0,
            self.sos_token: 1,
            self.eos_token: 2,
            self.unk_token: 3,
            self.crisis_token: 4,
            self.support_token: 5
        }
        
        word_freq = Counter()
        for text in texts:
            tokens = self.preprocess_text(text)
            word_freq.update(tokens)
        
        for word, freq in word_freq.most_common():
            if freq >= min_freq and word not in self.word2idx:
                self.word2idx[word] = len(self.word2idx)
        
        self.idx2word = {idx: word for word, idx in self.word2idx.items()}
        self.vocab_size = len(self.word2idx)
        print(f"Vocabulary size: {self.vocab_size}")
    
    def encode(self, text, max_length=None):
        tokens = self.preprocess_text(text)
        token_ids = [self.word2idx[self.sos_token]]
        
        for token in tokens:
            token_ids.append(self.word2idx.get(token, self.word2idx[self.unk_token]))
        
        token_ids.append(self.word2idx[self.eos_token])
        
        if max_length:
            if len(token_ids) > max_length:
                token_ids = token_ids[:max_length-1] + [self.word2idx[self.eos_token]]
            else:
                token_ids.extend([self.word2idx[self.pad_token]] * (max_length - len(token_ids)))
        
        return token_ids
    
    def decode(self, token_ids, skip_special_tokens=True):
        tokens = []
        for idx in token_ids:
            token = self.idx2word.get(idx, self.unk_token)
            if skip_special_tokens and token in [self.pad_token, self.sos_token, self.eos_token]:
                continue
            tokens.append(token)
        return ' '.join(tokens)
    
    def save(self, filepath="mental_health_tokenizer.pkl"):
        with open(filepath, 'wb') as f:
            pickle.dump({
                'word2idx': self.word2idx,
                'idx2word': self.idx2word,
                'vocab_size': self.vocab_size
            }, f)
        print(f"Tokenizer saved to {filepath}")
    
    def load(self, filepath="mental_health_tokenizer.pkl"):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.word2idx = data['word2idx']
        self.idx2word = data['idx2word']
        self.vocab_size = data['vocab_size']
        print(f"Tokenizer loaded from {filepath}")