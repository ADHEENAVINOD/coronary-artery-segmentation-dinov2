# 📚 Literature Comparison: My Project vs. Key Research Papers

This document provides a detailed comparative analysis between your thesis project and the 10 key research papers in your literature review.

---

## 🌟 Overview: My Project Baseline

*   **Goal**: Coronary artery layer segmentation (Lumen, Intima, Media) to quantify stenosis.
*   **Methodology**: Frozen **DINOv2** self-supervised backbone (Hugging Face) + 3-layer CNN decoder head + **clDice Loss** (topological constraint).
*   **Performance Optimization**: Lazy-loading and offline patch caching (GPU/CPU-friendly, under 2-minute training).
*   **Result**: **+6.84% accuracy boost** (64.17% total) on test slides with fully continuous loops.

---

## 🔬 Comparative Analysis of the 10 Papers

### 1. "clDice -- A Novel Topology-Preserving Loss Function..." (Shit et al., 2020)
*   **Their Methods**: Introduced soft-skeletonization algorithms (`soft_erode` and `soft_dilate`) to calculate centerline Dice overlap. Tested on U-Net and V-Net.
*   **Their Results**: Significant improvement in centerline connectivity metrics on vascular datasets, though overall volumetric Dice scores remained similar.
*   **Similarity**: You use the exact same mathematical formulation of clDice loss to enforce the loop structures of the coronary arteries.
*   **Contrast / Difference**: They tested on 3D angiographies and neural networks (vascular trees), whereas your project applies it specifically to **2D histopathological tissue slices** of coronary arteries.

---

### 2. "cbDice: Centerline Boundary Dice..." (Shi et al., 2024)
*   **Their Methods**: Expanded clDice by incorporating boundary-aware radius parameters into the skeleton to handle vessels of varying thicknesses.
*   **Their Results**: Improved boundary accuracy on micro-vessels, preventing thin capillaries from vanishing during prediction.
*   **Similarity**: Both are centerline-based losses focused on preserving vessel continuity.
*   **Contrast / Difference**: Their model is more geometrically complex (requires radius estimates), while your project uses the standard clDice loss which is faster to compute and sufficient for the large, relatively uniform coronary artery layers.

---

### 3. "Towards General Purpose Vision Foundation Models..." (Ouyang et al., 2023)
*   **Their Methods**: Evaluated DINOv2 (pre-trained on natural images) as a frozen feature extractor on radiology benchmarks (CT/MRI organ segmentation).
*   **Their Results**: Showed that DINOv2 features generalize well to medical scans without fine-tuning, matching or beating models trained from scratch.
*   **Similarity**: You also freeze the DINOv2 backbone and only train a small segmentation head, utilizing its pre-trained visual knowledge.
*   **Contrast / Difference**: They tested on radiology scans (CT/MRI), while your project proves that DINOv2 generalizes to **microscopic histopathology slides** (H&E staining).

---

### 4. "DINOv2 based Self Supervised Learning..." (He et al., 2024)
*   **Their Methods**: Combined DINOv2 with few-shot learning techniques to segment organs with very few labeled samples (1 to 5 images).
*   **Their Results**: Achieved competitive accuracy with minimal labels, proving the robustness of DINOv2 feature descriptors.
*   **Similarity**: Both projects handle very small datasets (you trained on 16 slides).
*   **Contrast / Difference**: They focused on few-shot logic, whereas you used standard supervised learning but solved the data bottleneck using **lazy-loading and offline caching**.

---

### 5. "A Topological Loss Function... Using Persistent Homology" (Clough et al., 2020)
*   **Their Methods**: Used Persistent Homology (a math concept from Topological Data Analysis) to compute barcodes of loops and holes and align them.
*   **Their Results**: Enforced correct loop topology on cardiac MRI ventricles (ensuring the heart chamber has exactly one hole).
*   **Similarity**: Both enforce structural correctness (loop preservation).
*   **Contrast / Difference**: Their method is mathematically complex and very slow to compute during backpropagation. Your clDice method is **morphological-based**, making it much faster to train on standard CPUs.

---

### 6. "Topology-Preserving Deep Image Segmentation" (Hu et al., 2019)
*   **Their Methods**: Introduced a loss based on Betti numbers (counting connected components and holes) to match prediction and target topology.
*   **Their Results**: Reduced broken connections in road networks and cell membranes.
*   **Similarity**: Both aim to eliminate topological violations (broken rings).
*   **Contrast / Difference**: They enforce topology on structural contours (boundaries), while you apply topological loss to **filled artery tissue layers** (Media and Lumen).

---

### 7. "Beyond the Pixel-Wise Loss for Topology-Aware Delineation" (Mosinska et al., 2018)
*   **Their Methods**: Incorporated linear features and path detectors into the loss function instead of standard cross-entropy.
*   **Their Results**: Better delineation of thin filaments (dendrites and blood vessels).
*   **Similarity**: Both reject standard pixel-wise cross-entropy because it fragments vessels.
*   **Contrast / Difference**: They use pathway detectors for thin lines, while you use clDice for **thick circular layers** (artery walls).

---

### 8. "Emerging Properties in Self-Supervised Vision Transformers" (Caron et al., 2021)
*   **Their Methods**: Introduced DINO, showing that self-supervised ViT training automatically segments foreground objects in its attention maps.
*   **Their Results**: Vision transformers learned high-quality scene layouts without ever seeing a label.
*   **Similarity**: DINOv2 (which you use) is the direct successor to this model.
*   **Contrast / Difference**: This is a general computer vision paper on natural images (dogs, cars, landscapes), while your project applies this "emerging property" specifically to **medical histology structures**.

---

### 9. "Hierarchical Topology Learning for Coronary Artery Segmentation" (Gupta et al., 2023)
*   **Their Methods**: Used a hierarchical tree-structure model to trace the branches of the coronary artery tree from clinical scans.
*   **Their Results**: High accuracy in 3D vascular tracing, preventing false endpoints.
*   **Similarity**: Both target coronary arteries.
*   **Contrast / Difference**: They trace 3D blood vessel trees in angiography scans, while you segment **cross-sectional layers** in 2D tissue slides.

---

### 10. "Deep Learning for Vascular Structure Segmentation: A Review" (Review Paper, 2022)
*   **Their Methods**: A comprehensive review of various CNNs (U-Net, SegNet) used to segment blood vessels.
*   **Their Results**: Summarized that U-Net remains dominant, but boundary errors and structural continuity remain the biggest unresolved challenges.
*   **Similarity**: You address the exact challenge raised by this review: **vascular continuity**.
*   **Contrast / Difference**: While they review general U-Nets, your project provides a concrete solution by combining **DINOv2 features with clDice loss**.
