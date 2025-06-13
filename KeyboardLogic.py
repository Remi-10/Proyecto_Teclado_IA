import torch
import torch.nn as nn
import torch.optim as optim
import os
import numpy as np
import pygame
from config import KEYBOARD_WIDTH, KEYBOARD_HEIGHT, TEXT_AREA_HEIGHT, SUGGESTIONS_HEIGHT

class WordCompletionLSTM(nn.Module):
    def __init__(self, vocab_size, embedding_dim=32, hidden_dim=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, x, hidden=None):
        x = self.embedding(x)
        out, hidden = self.lstm(x, hidden)
        out = self.fc(out)
        return out, hidden

class KeyboardLogic:
    def __init__(self):
        pygame.mixer.init()
        self.current_text = ""
        self.selected_key = None
        self.caps_lock = False
        self.sound_click = pygame.mixer.Sound('sounds/click.wav') if pygame.mixer.get_init() else None

        self.max_length = 35  # longitud máxima de palabra
        self.model_path = "word_completion_lstm.pth"
        self._prepare_data()
        self._train_or_load_model()

        self.key_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ñ'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', ';'],
            ['BORRAR', 'ESPACIO', 'MAYUS']
        ]
        self.key_rects = self._init_key_rects()

    def _prepare_data(self):
        print("Cargando palabras y preparando datos...")
        with open('palabras.txt', 'r', encoding='utf-8') as f:
            words = [line.strip().lower() for line in f if line.strip()]
        words = [w for w in words if 2 <= len(w) <= self.max_length]
        self.words = words
        chars = sorted(set(''.join(words)))
        self.char_to_idx = {c: i+1 for i, c in enumerate(chars)} 
        self.char_to_idx['<PAD>'] = 0
        self.idx_to_char = {i: c for c, i in self.char_to_idx.items()}
        self.vocab_size = len(self.char_to_idx)
        print(f"Tamaño del vocabulario de caracteres: {self.vocab_size}")

        # Generar pares (prefijo, palabra)
        self.X, self.y = [], []
        for word in words:
            for i in range(1, len(word)):
                prefix = word[:i]
                # Entrada: prefijo (como índices)
                x_seq = [self.char_to_idx[c] for c in prefix]
                # Salida: palabra completa (como índices)
                y_seq = [self.char_to_idx[c] for c in word]
                self.X.append(x_seq)
                self.y.append(y_seq)
        # Padding
        self.max_seq_len = max(len(seq) for seq in self.y)
        self.X = [seq + [0]*(self.max_seq_len-len(seq)) for seq in self.X]
        self.y = [seq + [0]*(self.max_seq_len-len(seq)) for seq in self.y]
        self.X = torch.tensor(self.X, dtype=torch.long)
        self.y = torch.tensor(self.y, dtype=torch.long)
        print(f"Total de pares prefijo-palabra: {len(self.X)}")

    def _train_or_load_model(self):
        self.model = WordCompletionLSTM(self.vocab_size)
        if os.path.exists(self.model_path):
            print("Cargando modelo entrenado desde archivo...")
            self.model.load_state_dict(torch.load(self.model_path, map_location=torch.device('cpu')))
            self.model.eval()
            print("Modelo cargado correctamente.")
        else:
            print("Entrenando modelo LSTM para autocompletar palabras...")
            optimizer = optim.Adam(self.model.parameters())
            criterion = nn.CrossEntropyLoss(ignore_index=0)
            epochs = 10
            for epoch in range(epochs):
                total_loss = 0
                for x, y in zip(self.X, self.y):
                    x = x.unsqueeze(0)  # batch de 1
                    y = y.unsqueeze(0)
                    optimizer.zero_grad()
                    output, _ = self.model(x)
                    loss = criterion(output.view(-1, self.vocab_size), y.view(-1))
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                print(f"Época {epoch+1}/{epochs} - Pérdida promedio: {total_loss/len(self.X):.4f}")
            print("Entrenamiento finalizado. Guardando modelo...")
            torch.save(self.model.state_dict(), self.model_path)
            print(f"Modelo guardado en '{self.model_path}'.")
            self.model.eval()

    def _init_key_rects(self):
        rects = []
        key_height = KEYBOARD_HEIGHT // len(self.key_layout)
        for row_idx, row in enumerate(self.key_layout):
            row_rects = []
            key_width = KEYBOARD_WIDTH // len(row)
            for col_idx in range(len(row)):
                x = col_idx * key_width
                y = TEXT_AREA_HEIGHT + SUGGESTIONS_HEIGHT + row_idx * key_height
                row_rects.append(pygame.Rect(x, y, key_width, key_height))
            rects.append(row_rects)
        return rects

    def update_selection(self, gaze_pos):
        self.selected_key = None
        for row_idx, row in enumerate(self.key_rects):
            for col_idx, rect in enumerate(row):
                if rect.collidepoint(gaze_pos):
                    self.selected_key = (row_idx, col_idx)
                    return

    def select_key(self, key):
        if self.sound_click:
            self.sound_click.play()
        if key == 'ESPACIO':
            self.current_text += ' '
        elif key == 'BORRAR':
            self.current_text = self.current_text[:-1]
        elif key == 'MAYUS':
            self.caps_lock = not self.caps_lock
        else:
            self.current_text += key.upper() if self.caps_lock else key.lower()

    def get_suggestions(self, n=3):
        if not self.current_text.strip():
            return []
        last_word = self.current_text.split()[-1].lower()
        return self._predict_words(last_word, n)

    def _predict_words(self, prefix, n=3):
        if not prefix or any(c not in self.char_to_idx for c in prefix):
            return []
        with torch.no_grad():
            x = [self.char_to_idx[c] for c in prefix]
            x = x + [0]*(self.max_seq_len-len(x))
            x = torch.tensor(x, dtype=torch.long).unsqueeze(0)
            output, _ = self.model(x)
            output = torch.softmax(output, dim=2)
            pred_indices = output.argmax(dim=2).squeeze().tolist()
            pred_word = ''.join([self.idx_to_char[idx] for idx in pred_indices if idx != 0])
            # Solo sugerir palabras reales que empiecen con el prefijo
            valid_words = [w for w in self.words if w.startswith(prefix)]
            suggestions = []
            if pred_word in valid_words and pred_word not in suggestions:
                suggestions.append(pred_word)
            for w in valid_words:
                if w not in suggestions:
                    suggestions.append(w)
                if len(suggestions) >= n:
                    break
            return suggestions[:n]

    def select_suggestion(self, suggestion):
        if suggestion:
            words = self.current_text.split()
            self.current_text = ' '.join(words[:-1]) + " " + suggestion + " "
            if self.sound_click:
                self.sound_click.play()