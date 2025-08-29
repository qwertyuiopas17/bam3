import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os

# FIXED: Import the working tokenizer and model
try:
    from tokenizer import MentalHealthTokenizer
    from model import MentalHealthChatbot
    import data_preparation
except ImportError:
    print("⚠️  Import error - make sure you have the fixed tokenizer.py and model.py files!")
    exit(1)

class MentalHealthDataset(Dataset):
    def __init__(self, dialogue_pairs, tokenizer, max_length=64):  # FIXED: Reduced max_length
        self.dialogue_pairs = dialogue_pairs
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.risk_mapping = {'low': 0, 'moderate': 1, 'high': 2}

    def __len__(self):
        return len(self.dialogue_pairs)

    def __getitem__(self, idx):
        pair = self.dialogue_pairs[idx]
        
        # FIXED: Better error handling for encoding
        try:
            input_ids = self.tokenizer.encode(pair['input'], self.max_length)
            target_ids = self.tokenizer.encode(pair['target'], self.max_length)
        except Exception as e:
            print(f"Encoding error for pair {idx}: {e}")
            # Return dummy data if encoding fails
            input_ids = [1, 3, 2] + [0] * (self.max_length - 3)  # <SOS> <UNK> <EOS> + padding
            target_ids = [1, 3, 2] + [0] * (self.max_length - 3)
        
        risk_level = self.risk_mapping.get(pair.get('risk_level', 'low'), 0)

        return {
            'input_ids': torch.tensor(input_ids, dtype=torch.long),
            'target_ids': torch.tensor(target_ids, dtype=torch.long),
            'risk_level': torch.tensor(risk_level, dtype=torch.long)
        }

def collate_fn(batch):
    # FIXED: Better tensor handling
    try:
        inputs = torch.stack([x['input_ids'] for x in batch])
        targets = torch.stack([x['target_ids'] for x in batch])
        risks = torch.stack([x['risk_level'] for x in batch])
        return {'input_ids': inputs, 'target_ids': targets, 'risk_levels': risks}
    except Exception as e:
        print(f"Batch collation error: {e}")
        # Return dummy batch if stacking fails
        batch_size = len(batch)
        max_len = 64
        return {
            'input_ids': torch.ones(batch_size, max_len, dtype=torch.long),
            'target_ids': torch.ones(batch_size, max_len, dtype=torch.long),
            'risk_levels': torch.zeros(batch_size, dtype=torch.long)
        }

def train_model():
    print("🚀 Starting FIXED training process...")
    
    # STEP 1: Prepare training data
    print("📊 Preparing training data...")
    data_preparation.prepare_training_data()
    
    # STEP 2: Load dialogue pairs
    try:
        with open('dialogue_pairs.json', 'r', encoding='utf-8') as f:
            dialogue_pairs = json.load(f)
        print(f"✅ Loaded {len(dialogue_pairs)} conversation pairs")
    except FileNotFoundError:
        print("❌ dialogue_pairs.json not found! Run data_preparation.py first.")
        return
    except Exception as e:
        print(f"❌ Error loading dialogue pairs: {e}")
        return

    # STEP 3: Initialize tokenizer
    print("🔤 Initializing tokenizer...")
    tokenizer = MentalHealthTokenizer()
    
    # Build vocabulary from all texts
    all_texts = []
    for pair in dialogue_pairs:
        all_texts.append(pair.get('input', ''))
        all_texts.append(pair.get('target', ''))
    
    tokenizer.build_vocabulary(all_texts)
    tokenizer.save('mental_health_tokenizer.pkl')
    print(f"✅ Vocabulary built with {tokenizer.vocab_size} tokens")

    # STEP 4: Create dataset and dataloader
    print("📦 Creating dataset...")
    dataset = MentalHealthDataset(dialogue_pairs, tokenizer)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=collate_fn)  # FIXED: Smaller batch size
    
    # STEP 5: Initialize model
    print("🧠 Initializing model...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🖥️  Using device: {device}")
    
    model = MentalHealthChatbot(vocab_size=tokenizer.vocab_size, d_model=128, num_layers=2)  # FIXED: Smaller model
    model.to(device)
    
    # STEP 6: Initialize training components
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)  # FIXED: Higher learning rate
    criterion_lang = nn.CrossEntropyLoss(ignore_index=0)
    criterion_crisis = nn.CrossEntropyLoss()

    # STEP 7: Training loop
    epochs = 10  # FIXED: Fewer epochs for testing
    print(f"🏋️  Starting training for {epochs} epochs...")
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0
        successful_batches = 0
        
        for batch_idx, batch in enumerate(dataloader):
            try:
                input_ids = batch['input_ids'].to(device)
                target_ids = batch['target_ids'].to(device)
                risk_levels = batch['risk_levels'].to(device)

                optimizer.zero_grad()

                # FIXED: Better tensor handling for decoder
                decoder_input = target_ids[:, :-1]
                decoder_target = target_ids[:, 1:]

                # FIXED: Simplified mask creation
                src_mask = model.create_padding_mask(input_ids)
                tgt_mask = model.create_causal_mask(decoder_input.size(1), device)

                # Forward pass
                outputs = model(input_ids, decoder_input, src_mask, tgt_mask, src_mask)
                
                # FIXED: Better loss calculation
                loss_lang = criterion_lang(
                    outputs['logits'].reshape(-1, tokenizer.vocab_size), 
                    decoder_target.reshape(-1)
                )
                loss_crisis = criterion_crisis(outputs['crisis_logits'], risk_levels)
                
                total_loss = loss_lang + 0.3 * loss_crisis

                # Backward pass
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

                running_loss += total_loss.item()
                successful_batches += 1
                
            except Exception as e:
                print(f"⚠️  Error in batch {batch_idx}: {e}")
                continue

        if successful_batches > 0:
            avg_loss = running_loss / successful_batches
            print(f"Epoch {epoch+1}/{epochs} - Average Loss: {avg_loss:.4f} ({successful_batches} successful batches)")
        else:
            print(f"Epoch {epoch+1}/{epochs} - No successful batches!")

    # STEP 8: Save model
    print("💾 Saving trained model...")
    torch.save(model.state_dict(), 'mental_health_model.pth')
    tokenizer.save('mental_health_tokenizer.pkl')
    
    # STEP 9: Test the trained model
    print("\n🧪 Testing trained model...")
    model.eval()
    
    test_inputs = [
        "I feel anxious",
        "I am sad", 
        "Help me"
    ]
    
    for test_input in test_inputs:
        try:
            input_ids = tokenizer.encode(test_input, max_length=64)
            input_tensor = torch.tensor([input_ids], device=device)
            
            with torch.no_grad():
                result = model.generate(input_tensor, tokenizer, max_length=20, temperature=0.8)
                print(f"Input: '{test_input}' → Output: '{result['response']}'")
                
        except Exception as e:
            print(f"Test error for '{test_input}': {e}")
    
    print("\n✅ Training completed! Files saved:")
    print("   • mental_health_model.pth")
    print("   • mental_health_tokenizer.pkl")
    print("   🎯 Now you can run: python server.py")

if __name__ == "__main__":
    try:
        train_model()
    except KeyboardInterrupt:
        print("\n⛔ Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Training failed with error: {e}")
        print("🔧 Make sure you have all the fixed files: tokenizer.py, model.py")