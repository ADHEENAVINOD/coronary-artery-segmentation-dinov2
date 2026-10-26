# 📝 Summary of the Two Key Papers for My Thesis

This document summarizes the **two main papers** that define your thesis:
1.  **Paper 1 (External Reference)**: *Topology Preserving Compositionality for Robust Medical Image Segmentation* (Santhirasekaram et al., CVPRW 2023).
2.  **Paper 2 (Our Internal Manuscript)**: The medical journal paper written by your professor/team detailing the clinical dataset and stenosis formulas.

---

## 1. Paper 1: Santhirasekaram et al. (CVPRW 2023)
*   **Official Title**: *Topology Preserving Compositionality for Robust Medical Image Segmentation*
*   **What it is about**: A machine learning method that forces AI models to output anatomically correct shapes, preventing broken loops or scattered pixels in medical images.
*   **Their Methods**:
    1.  Uses a **compositional dictionary** in the latent space (building the segmentation by combining pre-learned standard anatomical shapes).
    2.  Uses **Persistent Homology** (a branch of math) to check if the loops and holes in the segmentation match the true anatomy, penalizing the AI during training if they are broken.
*   **How it relates to your project**:
    *   **The similarity**: Both projects share the same core goal—to stop standard AI models from predicting broken artery walls (Media) or blood channels (Lumen) by adding "topological rules."
    *   **Your improvement**: Their Persistent Homology calculations are very slow and heavy. In your project, you use **clDice loss** (centerline skeletonization) which is lightweight, much faster to train (takes 2 minutes instead of hours), and specifically designed for blood vessel loops.

---

## 2. Paper 2: Our Medical Journal Manuscript (The Baseline Paper)
*   **Official Title**: The manuscript written by your professor/team for the medical journal.
*   **What it is about**: A clinical research study demonstrating how to segment coronary artery tissue layers (Lumen, Intima, Media) from H&E histopathology slides to calculate artery blockage (stenosis) objectively.
*   **Their Methods**:
    1.  Uses a clinical database of **103 high-quality ROIs** extracted from whole-slide autopsy images.
    2.  Segments the slides into 4 classes (Background, Media, Intima, Lumen) to measure plaque buildup.
    3.  Uses the mathematical formula for stenosis calculation:
        $$S_p = \left[ 1 - \left( \frac{\text{Residual Lumen}}{\text{Residual Lumen} + \text{Tunica intima}} \right) \right] \times 100$$
*   **How it relates to your project**:
    *   **The similarity**: This manuscript is the **foundation of your entire thesis**. You use their dataset, their classes, and their exact stenosis formula to calculate the artery blockages.
    *   **Your improvement**: The manuscript originally proposed using a standard SegFormer model. In your project, you **upgraded the system** by implementing **DINOv2 features + clDice topological constraints**, which ensures the predicted vessel loops never fragment and are anatomically perfect.
