import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

class ArticleDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer(text, truncation=True, padding='max_length', max_length=512, return_tensors='pt')
        return {key: tensor.squeeze() for key, tensor in encoding.items()}, torch.tensor(label)

def classify_texts(df):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=6)
    
    texts = df['processed_summary'].tolist()
    labels = df['label'].tolist()

    train_texts, val_texts, train_labels, val_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

    train_dataset = ArticleDataset(train_texts, train_labels, tokenizer)
    val_dataset = ArticleDataset(val_texts, val_labels, tokenizer)

    train_dataloader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=8, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
    class_weights = compute_class_weight('balanced', classes=np.unique(train_labels), y=train_labels)
    class_weights = torch.tensor(class_weights, dtype=torch.float)

    model.train()
    for epoch in range(3):
        total_loss = 0
        for batch in train_dataloader:
            inputs, labels = batch
            optimizer.zero_grad()
            outputs = model(**inputs, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()
            optimizer.step()
        
        avg_train_loss = total_loss / len(train_dataloader)
        print(f"Epoch {epoch + 1}, Training loss: {avg_train_loss}")

        val_loss = 0
        predictions, true_labels = [], []
        with torch.no_grad():
            for batch in val_dataloader:
                inputs, labels = batch
                outputs = model(**inputs, labels=labels)
                loss = outputs.loss
                val_loss += loss.item()
                logits = outputs.logits
                predictions.extend(torch.argmax(logits, dim=1).tolist())
                true_labels.extend(labels.tolist())
        avg_val_loss = val_loss / len(val_dataloader)
        val_accuracy = sum([p == t for p, t in zip(predictions, true_labels)]) / len(true_labels)
        print(f"Epoch {epoch + 1}, Validation loss: {avg_val_loss}")
        print(f"Epoch {epoch + 1}, Validation Accuracy: {val_accuracy}")
        print(f"Epoch {epoch + 1}, Classification Report:\n{classification_report(true_labels, predictions, target_names=['Cognition', 'Dopamine', 'Mémoire', 'Apprentissage', 'Olfaction', 'Autre'])}")
