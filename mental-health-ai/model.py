# model.py
import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_seq_len=512):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_seq_len, d_model)
        position = torch.arange(0, max_seq_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return x + self.pe[:x.size(0), :]

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0
        self.d_k = d_model // num_heads
        self.num_heads = num_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attn = torch.softmax(scores, dim=-1)
        return torch.matmul(attn, V)
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        Q = self.W_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        attn = self.scaled_dot_product_attention(Q, K, V, mask)
        attn = attn.transpose(1, 2).contiguous().view(batch_size, -1, self.num_heads * self.d_k)
        return self.W_o(attn)

class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff):
        super(FeedForward, self).__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        return self.linear2(self.relu(self.linear1(x)))

class EncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask):
        attn = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn))
        ff = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff))
        return x

class DecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(DecoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.cross_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, enc_output, src_mask, tgt_mask):
        attn = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn))
        attn2 = self.cross_attn(x, enc_output, enc_output, src_mask)
        x = self.norm2(x + self.dropout(attn2))
        ff = self.feed_forward(x)
        x = self.norm3(x + self.dropout(ff))
        return x

class MentalHealthChatbot(nn.Module):
    def __init__(self, vocab_size, d_model=256, num_heads=8, num_layers=4, d_ff=512, max_seq_len=128, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_seq_len)
        self.encoder_layers = nn.ModuleList([EncoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)])
        self.decoder_layers = nn.ModuleList([DecoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)])
        self.output_proj = nn.Linear(d_model, vocab_size)
        self.crisis_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 3)
        )
        self.dropout = nn.Dropout(dropout)
    
    def create_padding_mask(self, seq, pad_idx=0):
        return (seq != pad_idx).unsqueeze(1).unsqueeze(2)
    
    def create_causal_mask(self, size, device):
        mask = torch.tril(torch.ones(size, size, device=device))
        return mask.unsqueeze(0).unsqueeze(0)
    
    def forward(self, src, tgt, src_mask=None, tgt_mask=None, memory_mask=None):
        src_emb = self.dropout(self.pos_encoding(self.embedding(src) * math.sqrt(self.d_model)))
        tgt_emb = self.dropout(self.pos_encoding(self.embedding(tgt) * math.sqrt(self.d_model)))
        
        enc = src_emb.transpose(0, 1)
        for layer in self.encoder_layers:
            enc = layer(enc.transpose(0, 1), src_mask).transpose(0, 1)
        
        crisis_logits = self.crisis_head(enc.mean(dim=0))
        
        dec = tgt_emb.transpose(0, 1)
        for layer in self.decoder_layers:
            dec = layer(dec.transpose(0, 1), enc.transpose(0, 1), memory_mask, tgt_mask).transpose(0, 1)
        
        output = self.output_proj(dec.transpose(0, 1))
        return {'logits': output, 'crisis_logits': crisis_logits}
    
    def generate(self, src, tokenizer, max_length=50, temperature=1.0, top_k=40):
        self.eval()
        device = src.device
        batch_size = src.size(0)
        src_mask = self.create_padding_mask(src, pad_idx=0)
        
        tgt = torch.full((batch_size, 1), tokenizer.word2idx['<SOS>'], device=device)
        
        for _ in range(max_length):
            tgt_len = tgt.size(1)
            tgt_mask = self.create_causal_mask(tgt_len, device)
            
            with torch.no_grad():
                out = self.forward(src, tgt, src_mask, tgt_mask, src_mask)
            
            logits = out['logits'][:, -1, :] / temperature
            
            if top_k > 0:
                top_k_logits, top_k_indices = torch.topk(logits, top_k)
                probs = torch.softmax(top_k_logits, dim=-1)
                next_token_idx = torch.multinomial(probs, 1)
                next_token = torch.gather(top_k_indices, 1, next_token_idx)
            else:
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)
            
            if next_token.item() == tokenizer.word2idx['<EOS>']:
                break
            
            tgt = torch.cat([tgt, next_token], dim=1)
        
        response = tokenizer.decode(tgt[0].cpu().tolist(), True)
        
        with torch.no_grad():
            crisis_prob = torch.softmax(out['crisis_logits'], dim=-1).cpu()
        
        return {'response': response, 'crisis_probability': crisis_prob}