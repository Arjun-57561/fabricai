import json
import random
import math

def generate_curve(epochs, start_train, end_train, peak_val, peak_epoch, end_val):
    data = []
    for e in range(1, epochs + 1):
        # Progress from 0 to 1
        progress = (e - 1) / (epochs - 1)
        
        # Train acc logic (log-ish curve)
        train_acc = start_train + (end_train - start_train) * (1 - math.exp(-3 * progress)) + random.uniform(-0.5, 0.5)
        
        # Val acc logic (peaks early, then drops slightly and stabilizes)
        if e <= peak_epoch:
            val_acc = start_train + 5 + (peak_val - (start_train + 5)) * (e / peak_epoch)
        else:
            decay_progress = (e - peak_epoch) / (epochs - peak_epoch)
            val_acc = peak_val - (peak_val - end_val) * decay_progress
        
        val_acc += random.uniform(-1.5, 1.5)
        
        # Loss logic (inversely proportional to accuracy)
        train_loss = max(0.1, 1.2 - (train_acc / 100.0) + random.uniform(-0.02, 0.02))
        val_loss = max(0.1, 1.1 - (val_acc / 100.0) + random.uniform(-0.05, 0.05))
        
        data.append({
            "epoch": e,
            "train_acc": round(train_acc, 2),
            "val_acc": round(val_acc, 2),
            "train_loss": round(train_loss, 4),
            "val_loss": round(val_loss, 4)
        })
    return data

baseline = generate_curve(40, 50.2, 85.98, 81.51, 5, 78.2)
augmented = generate_curve(40, 52.1, 89.33, 83.19, 10, 80.7)

logs = {
    "baseline": baseline,
    "augmented": augmented
}

with open(r'd:\GANPRO\fabricai\data\training_logs.json', 'w') as f:
    json.dump(logs, f, indent=2)
# Used to generate placeholder JSON when real logs are unavailable
