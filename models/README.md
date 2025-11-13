# 🧠 Models Directory

This directory contains the trained machine learning models for PCACR classification.

## 📁 Expected Files

After running `python train_model.py`, this directory will contain:

1. **`pcacr_model.pkl`** (~10-20 MB)
   - Random Forest Classifier trained on clinical data
   - 100 decision trees, max depth 10
   - Trained on 50,000 patient records

2. **`pcacr_scaler.pkl`** (~1 KB)
   - StandardScaler for feature normalization
   - Ensures consistent input scaling

3. **`pcacr_features.pkl`** (~1 KB)
   - List of 17 clinical features used by the model
   - Feature names and order

## 🚀 How to Generate Models

```powershell
# From project root directory
python train_model.py
```

**Time:** 2-5 minutes depending on your CPU  
**Requirements:** Dataset.csv must be in the data/ folder

## ⚠️ Important Notes

- These files are **NOT included in git** (listed in .gitignore)
- Each user must train the model locally
- Models are specific to the dataset version used for training
- Rerun `train_model.py` to update models with new data

## 🔧 Troubleshooting

### Models not loading?
1. Check if all 3 `.pkl` files exist in this directory
2. Verify file sizes are reasonable (not 0 bytes)
3. Try retraining: `python train_model.py`
4. Check for error messages in terminal

### Need to retrain?
```powershell
# Delete old models
Remove-Item models/*.pkl

# Train fresh model
python train_model.py
```

## 📊 Model Performance

Expected metrics after training:
- **Accuracy:** 80-85%
- **Training time:** 2-5 minutes
- **Prediction time:** < 100ms per patient
- **Model size:** ~15MB total
