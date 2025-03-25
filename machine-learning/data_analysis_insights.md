# Data Analysis and Visualization Report

## Dataset Structure and Preprocessing
- **Dataset**: The chest X-ray dataset contains 5840 images, split into 4672 training and 1168 validation images.
- **Classes**: 
  - NORMAL: 1575 images (27%)
  - PNEUMONIA: 4265 images (73%)
- **Preprocessing**: Images are assumed to be preprocessed (resized, normalized) for model training. No significant noise was observed in sample images.

## Exploratory Data Analysis (EDA)
- **Class Distribution**: The dataset is imbalanced, with 27% NORMAL and 73% PNEUMONIA images (see `class_distribution.png`). This imbalance likely contributes to the CNN's bias toward predicting PNEUMONIA.
- **Sample Images**: Visualized one NORMAL and one PNEUMONIA X-ray (see `sample_images.png`). NORMAL images show clear lung fields, while PNEUMONIA images exhibit opacities indicating infection.

## Performance Analysis (CNN)
- **Metrics**: 100% recall, 81.16% accuracy, 79.50% precision, 88.58% F1-score (threshold 0.05).
- **Confusion Matrix**: High false positives (NORMAL as PNEUMONIA) due to imbalance, but no false negatives (see `cnn_cm.png`). Note: The confusion matrix currently uses simulated data; actual FP/FN counts may differ with real validation data.
- **ROC & Precision-Recall**: High recall but lower precision due to FPs (see `roc_curve.png`, `pr_curve.png`). Note: These curves use simulated data.

## Future Improvements
- **Address Imbalance**: Use techniques like oversampling NORMAL, undersampling PNEUMONIA, or applying class weights during training to reduce false positives.
- **Threshold Tuning**: Adjust the CNN threshold (currently 0.05) to balance precision and recall.
- **Data Augmentation**: Apply more augmentation (e.g., rotation, flipping) to increase dataset diversity.
- **Real Validation Data**: Use actual validation data instead of simulated predictions to generate accurate confusion matrices, ROC, and Precision-Recall curves.

## Visualizations
- Sample Images: `sample_images.png`
- Class Distribution: `class_distribution.png`
- Confusion Matrix (CNN): `cnn_cm.png`
- ROC Curve (CNN): `roc_curve.png`
- Precision-Recall Curve (CNN): `pr_curve.png`