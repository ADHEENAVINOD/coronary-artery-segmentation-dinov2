% TO DO:
% 1) Check all the %TOEDIT lines in this file and in frontespizio.tex



\documentclass[12pt,openany,oneside]{book} 
% Use options 'twoside,openright' if the number of pages is high.
% Use option 'oneside,openany' if the number of pages is low and you want to print it single-sided.

\usepackage{geometry}
% Adjust page margins to center content on the page
\geometry{
  left=4cm,
  right=4cm,
  top=4cm,
  bottom=4cm,
  bindingoffset=0cm,
}
\usepackage{cite}

\usepackage{graphicx}
\graphicspath{{./images/}}

\usepackage{amsmath}
\usepackage{amsfonts}

\usepackage{setspace}
\onehalfspacing

\usepackage{url}

\usepackage{multirow}

% You may want to define some useful keywords that you are going to use several times in the manuscript and are subject to modifications.
\usepackage{xspace}
\newcommand{\dataname}{XXX\xspace}   %% Acronym of the dataset
\newcommand{\methname}{XXX\xspace}   %% Acronym of the method

\newcommand{\figref}[1]{Fig.~\ref{#1}}
\newcommand{\tabref}[1]{Table~\ref{#1}}

\makeatletter
\DeclareRobustCommand\onedot{\futurelet\@let@token\@onedot}
\def\@onedot{\ifx\@let@token.\else.\null\fi\xspace}

\def\eg{\emph{e.g}\onedot} \def\Eg{\emph{E.g}\onedot}
\def\ie{\emph{i.e}\onedot} \def\Ie{\emph{I.e}\onedot}
\def\cf{\emph{c.f}\onedot} \def\Cf{\emph{C.f}\onedot}
\def\etc{\emph{etc}\onedot} \def\vs{\emph{vs}\onedot}
\def\wrt{w.r.t\onedot} \def\dof{d.o.f\onedot}
\def\etal{\emph{et al}\onedot}
\makeatother

\usepackage{xcolor}
\newcommand{\outline}[1]{\textcolor{blue}{Outline: #1}}
\newcommand{\fs}[1]{\textcolor{red}{[FRANZ: #1]}}
\newcommand{\my}[1]{\textcolor{red}{[CV: #1]}}  %\TOEDIT adjust this command to use your name and initials

\usepackage{array,booktabs}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}p{#1}}



\begin{document}


\frontmatter

\include{frontespizio}

% You can put acknowledgment here (optional)


\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}
Coronary artery disease (CAD) resulting from luminal narrowing by atherosclerotic plaque remains the leading cause of mortality worldwide. In forensic pathology and clinical post-mortem examinations, determining the precise degree of coronary artery stenosis provides vital diagnostic evidence regarding the mechanism of death. However, standard histological evaluation relies predominantly on qualitative visual estimation or manual digital tracing, which suffer from substantial inter-observer variability, labor intensity, and poor throughput across gigapixel whole-slide images (WSIs).
While deep learning methods have achieved remarkable success in computational pathology, conventional segmentation networks optimized via pixel-wise objective functions (such as Cross-Entropy or standard Dice loss) frequently predict anatomically invalid shapes. Because pixel-wise losses treat spatial coordinates independently, models frequently introduce disconnected boundaries, broken arterial wall rings, and isolated false-positive islands. In vascular morphometry, even a single-pixel discontinuity along the circular Tunica Media boundary breaks the closed vessel contour, corrupting downstream area integration and clinical stenosis quantification.
To address these fundamental limitations, this thesis presents an automated, topology-preserving semantic segmentation framework tailored for microscopic coronary histopathology. The proposed methodology leverages transfer learning from a self-supervised Vision Transformer foundation model (\texttt{DINOv2-Small}) frozen as a robust multi-scale feature extractor. To enforce strict anatomical continuity without non-differentiable graph matching, we integrate a continuous, differentiable soft-skeletonization objective based on Centerline Dice (\texttt{clDice}). This topological regularizer penalizes breaks along the medial skeletons of both the outer muscular boundary (Tunica Media) and the residual blood flow channel (Lumen). Furthermore, to overcome the severe memory and I/O bottlenecks inherent to gigapixel slide processing, an offline patch caching pipeline was engineered, reducing active RAM consumption from over 16~GB to under 100~MB and accelerating training from six hours to under two minutes per epoch.
Experimental validation on annotated post-mortem coronary artery histopathology slides demonstrates that incorporating the continuous topological prior improves average segmentation accuracy from $57.33\%$ to $64.17\%$ (+6.84\%) and increases mean Intersection-over-Union (mIoU) from $0.300$ to $0.381$ over the baseline. Crucially, qualitative overlays confirm that the framework preserves continuous, nested concentric tissue rings (Media, Intima, Lumen), eliminating broken wall contours and reducing stenosis measurement error from $14.8\%$ to $4.2\%$.
\vspace{1.5cm}
\noindent\textbf{Keywords:} Computational Pathology, Coronary Artery Stenosis, Topological Deep Learning, clDice Loss, Self-Supervised Learning, Vision Transformers, Histology Segmentation.



\chapter{Introduction}
\label{ch:Introduction}

Coronary artery disease (CAD) resulting from atherosclerotic plaque accumulation in the epicardial coronary arteries remains the single leading cause of mortality worldwide, accounting for over nine million deaths each year according to the World Health Organization. In clinical forensic medicine and post-mortem pathology, evaluating the patency of the coronary tree is a core diagnostic task to determine the medical cause of death, especially in cases of sudden unexpected cardiac death (SCD).
Microscopic histopathological evaluation of coronary cross-sections provides the clinical gold standard for assessing luminal stenosis, plaque morphology, and vascular remodeling. However, current routine practice relies primarily on qualitative visual estimation ("eyeballing") under a light microscope or laborious manual tracing using digital pathology software. While deep learning has made major strides in digital pathology, standard semantic segmentation networks trained with pixel-wise loss functions (such as Cross-Entropy or standard Dice) frequently predict broken boundaries, disconnected arterial walls, and anatomically impossible shapes.
This thesis presents a topology-preserving deep learning framework that pairs self-supervised Vision Transformers with continuous centerline loss constraints to achieve accurate, continuous segmentation of coronary artery histopathology, enabling automated and objective stenosis quantification.

\section{Cardiovascular Pathology and Coronary Anatomy}
\label{sec:clinical_background}
The human heart relies on three main epicardial coronary arteries for oxygenated blood delivery: the Left Anterior Descending (LAD) artery, the Left Circumflex (LCx) artery, and the Right Coronary Artery (RCA). Under normal physiological conditions, cross-sections of these vessels display a distinct, concentric trilaminar histological architecture:
\begin{enumerate}
    \item \textbf{Tunica Intima:} The innermost layer, lined by endothelial cells on the luminal side and bounded externally by the Internal Elastic Lamina (IEL). In healthy individuals, it is an extremely thin, single-cell layer.
    \item \textbf{Tunica Media:} The intermediate muscular tunic, composed of circumferentially organized smooth muscle cells, elastic fibers, and proteoglycan extracellular matrix. It provides the mechanical strength to resist pulsatile arterial pressure.
    \item \textbf{Tunica Adventitia:} The outermost connective tissue sheath containing collagen fibers, fibroblasts, adipose tissue, and nutritive microvessels (\textit{vasa vasorum}).
\end{enumerate}
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.50\linewidth]{fig3_4_coronary_stenosis_geometry.png}
    \caption{Histological anatomy and geometric concentricity of the coronary vessel wall. Atherosclerotic plaque accumulation within the Tunica Intima causes progressive luminal narrowing (stenosis).}
    \label{fig:intro_geometry}
\end{figure}
Atherogenesis is a chronic inflammatory process initiated by endothelial injury and subendothelial retention of low-density lipoproteins (LDL). Macrophages ingest these oxidized lipids, transforming into foam cells that form early fatty streaks. Over decades, smooth muscle cell proliferation, extracellular lipid pools, and dystrophic calcification lead to mature atheromatous plaque within the Tunica Intima (Fig.~\ref{fig:intro_geometry}). As the plaque expands inward, it obstructs the lumen, restricting coronary blood flow and increasing the risk of acute thrombotic occlusion.
\subsection{Forensic Autopsy Practice}
In forensic pathology, post-mortem cardiovascular examinations are essential to determine whether death was caused by acute myocardial infarction, fatal ischemic arrhythmia, or non-cardiac causes. During an autopsy, coronary arteries are sectioned perpendicularly at $3\,\text{mm}$ intervals. Segments with visible narrowing or calcification are sampled, formalin-fixed, embedded in paraffin, cut at $4\,\mu\text{m}$ thickness, and stained with Hematoxylin and Eosin (H\&E) or Movat's Pentachrome stain for microscopic assessment.


\section{Limitations of Manual Pathological Evaluation}
\label{sec:manual_limitations}
Despite the diagnostic importance of coronary histomorphometry, manual evaluation in forensic and clinical laboratories faces three major limitations:
\begin{enumerate}
    \item \textbf{High Inter-Observer Variability:} In standard practice, pathologists estimate the percentage of luminal stenosis visually under the microscope. Multiple studies have shown that visual estimation carries high subjective variability, often varying by $\pm 15\%$ to $20\%$ between different pathologists. A borderline case estimated at $65\%$ (moderate) by one examiner may be categorized as $75\%$ (severe/critical) by another, directly impacting forensic cause-of-death conclusions.
    \item \textbf{High Labor Cost and Low Throughput:} Accurate quantitative morphometry requires manually delineating the borders of the vessel caliber and the residual lumen in software like QuPath. Manually tracing complex, multi-layered histological images can take 20 to 30 minutes per slide, making exhaustive manual tracing impractical in busy autopsy departments.
    \item \textbf{Histological Artifacts:} Routine post-mortem specimens often contain technical artifacts, such as microtome blade chatter, tears across hard calcified plaques, and post-mortem blood clotting in the lumen. Pathologists must manually interpret and filter these artifacts, creating a strong need for robust automated methods that can handle real-world histological variations.
\end{enumerate}

\section{Computational Pathology and the Topological Challenge}
\label{sec:topological_challenge}
The advent of digital Whole-Slide Imaging (WSI) and deep learning has enabled automated analysis of digital histology slides. Fully Convolutional Networks (such as U-Net) and Vision Transformers have been widely used for cellular detection and tumor grading.
However, standard segmentation models face a fundamental theoretical limitation when applied to coronary arteries: \textbf{pixel-wise loss functions do not preserve spatial topology}.
\subsection{Failure of Pixel-Wise Objectives}
Standard loss functions (such as categorical Cross-Entropy and soft Dice) evaluate segmentation quality by calculating individual pixel misclassifications:
\begin{equation}
    \mathcal{L}_{\text{CE}} = - \frac{1}{|\Omega|} \sum_{(u,v) \in \Omega} \sum_{k=0}^{K-1} \mathbf{Y}(u, v, k) \log(\mathbf{P}(u, v, k)).
\end{equation}
Because these losses treat every pixel independently, they penalize an interior pixel error the same as an error that breaks a thin, critical boundary ring. 
In coronary histology, the Tunica Media forms a continuous circular ring. If a neural network misclassifies just a 2-pixel gap along a 500-pixel circular wall, Cross-Entropy incurs an insignificant penalty ($<0.001\%$). However, this small gap breaks the closed loop, turning a closed boundary into an open curve. Downstream algorithms that measure the internal vessel area fail, leading to invalid stenosis calculations.
\subsection{Memory and I/O Bottlenecks in Gigapixel Slides}
Digital whole-slide images scanned at $40\times$ resolution routinely measure $80,000 \times 60,000$ pixels. Loading and processing these gigabyte-scale images on the fly during neural network training creates severe memory spikes and I/O bottlenecks. An effective computational framework must therefore combine topology-aware learning with an optimized data pipeline capable of running efficiently on standard hardware.

\section{Research Objectives and Hypotheses}
\label{sec:objectives}
The main goal of this thesis is to develop and validate an automated, topology-preserving deep learning pipeline for multi-class coronary artery segmentation and objective stenosis quantification. We formulate three specific research hypotheses:
\begin{enumerate}
    \item \textbf{Hypothesis 1 ($H_1$) -- Self-Supervised Feature Representation:} Features extracted from a frozen self-supervised Vision Transformer foundation model (\texttt{DINOv2-Small}) provide richer histological representations than standard convolutional networks trained from scratch on small autopsy cohorts.
    \item \textbf{Hypothesis 2 ($H_2$) -- Topological Continuity Preservation:} Incorporating continuous soft-skeletonization loss (\texttt{clDice}) into the training objective significantly reduces boundary breaks in the annular Tunica Media and Lumen layers compared to standard Cross-Entropy baselines.
    \item \textbf{Hypothesis 3 ($H_3$) -- Diagnostic Stenosis Accuracy:} Automated stenosis calculations derived from topology-preserving segmentations exhibit strong correlation ($R^2 > 0.90$) and diagnostic concordance with expert pathologist ground truth across clinical autopsy slides.
\end{enumerate}

\section{Key Contributions of the Thesis}
\label{sec:contributions}
The principal contributions of this work are:
\begin{enumerate}
    \item \textbf{Hybrid Foundation Model Architecture:} We pair a frozen pre-trained \texttt{DINOv2-Small} Vision Transformer backbone with a lightweight 3-layer convolutional decoding head, avoiding overfitting on small histopathology datasets while reducing GPU memory requirements.
    \item \textbf{Continuous Topological clDice Regularization:} We integrate a differentiable soft-skeletonization loss using 2D min-max spatial pooling layers, enforcing loop closure on the Tunica Media and Lumen boundaries without expensive persistent homology calculations.
    \item \textbf{High-Throughput Patch Caching Pipeline:} We engineer an offline disk-caching architecture in PyTorch that reduces active RAM consumption from over $16\,\text{GB}$ to under $100\,\text{MB}$ and speeds up training by $193\times$ (from $5.8$ hours to $1.8$ minutes per epoch).
    \item \textbf{Quantitative and Clinical Validation:} We benchmark our approach against standard U-Net and DeepLabv3+ baselines, demonstrating a $+6.84\%$ improvement in test accuracy ($57.33\% \to 64.17\%$), a reduction in stenosis measurement error from $14.8\%$ to $4.2\%$, and a $91.3\%$ four-tier clinical diagnostic agreement with pathologists.
\end{enumerate}





\chapter{Related Work}
\label{ch:related_work}

This chapter presents the research papers that were studied during this project and that helped in deciding the methods used in our work. Four papers were mainly considered, focusing on different techniques related to medical image segmentation. Some of the ideas from these papers were used in our approach, such as the pre-trained DINOv2 backbone, clDice loss for maintaining the topology of the segmented structures, and lazy loading for working with large medical image datasets. In the following sections, these papers are discussed in terms of their methods, results, and the parts that were useful for our project.

\section{Topology Preserving Compositionality for Robust Medical Image Segmentation}


In this work, Santhirasekaram et al. \cite{santhirasekaram2023topology} focus on maintaining anatomical shape connectivity in medical image segmentation. In standard clinical segmentation models like U-Net \cite{ronneberger2015u}, training usually relies on pixel-level overlap or cross-entropy losses. The main issue with this approach is that when scans have noise, motion blur, or artifacts, the model often predicts broken borders or isolated holes inside ring-like organs, creating shapes that are biologically impossible.
To address this, earlier methods applied persistent homology to detect and penalize broken topological loops in cardiac images \cite{clough2020topological}. Santhirasekaram et al. \cite{santhirasekaram2023topology} took this concept further by restricting the network's latent space to a dictionary of learned anatomical shape templates. Instead of generating masks pixel by pixel without geometric rules, the network builds the segmentation from these base shapes, using Persistent Homology as an explicit prior to ensure the assembled loops stay closed during backpropagation.
Testing on the ACDC cardiac MRI dataset and multi-organ CT benchmarks showed that this shape-composition strategy remained remarkably robust against image perturbations, keeping heart chamber boundaries continuous where standard baselines failed. This relates closely to my work on coronary arteries, as both problems involve segmenting circular anatomical walls that must stay closed. However, while their persistent homology calculations require heavy GPU computations during training, my approach achieves topological continuity for coronary artery rings using a lighter centerline Dice (clDice) loss, paired with a frozen DINOv2 backbone and offline patch caching for fast training.

\section{ Topograph: An Efficient Graph-Based Framework for Strictly Topology Preserving Image Segmentation }

In this work, Lux et al. \cite{lux2025topograph} address the heavy computational cost typically required to train topology-preserving segmentation networks. While persistent homology methods \cite{hu2019topology} can prevent structural defects in standard architectures like V-Net \cite{milletari2016v} by matching Betti numbers across filtration steps, computing persistence barcodes and pairing critical points for every batch is notoriously slow, making large-scale training impractically expensive.
To resolve this bottleneck, Lux et al. \cite{lux2025topograph} introduced Topograph, an alternative framework grounded in graph theory rather than global persistence calculations. Their method constructs a spatial component graph that captures the adjacency and structural layout of both the predicted segmentation and the ground-truth mask. By analyzing local graph neighborhoods, the algorithm efficiently identifies topologically critical regions—such as broken paths, false bridges, or disconnected components—and applies localized loss penalties directly during backpropagation. Evaluated across 2D and 3D medical benchmarks on binary and multi-class segmentation tasks, Topograph matched state-of-the-art segmentation accuracy while running up to five times faster than persistent homology baselines \cite{hu2019topology}.
Computational efficiency and structural continuity are equally central to my coronary artery segmentation pipeline. However, my work approaches this challenge through a different architectural strategy. Instead of generating online component graphs on convolutional networks \cite{milletari2016v}, I enforce continuity across concentric coronary tissue layers (Media, Intima, and Lumen) using a soft morphological centerline loss (clDice). Combined with a frozen self-supervised DINOv2 backbone and an offline patch caching pipeline, this setup avoids heavy loss computations altogether and allows full training on histology slides in under two minutes on standard hardware.

\section{clDice - A Novel Topology-Preserving Loss Function for Tubular Structure Segmentation}
In this work, Suprosanna Shit et al. \cite{shit2021cldice} address the fundamental failure of standard segmentation losses when applied to tubular and network-like anatomical structures, such as blood vessels and neurons. Standard pixel-wise objectives (like Cross-Entropy or Dice) evaluate predictions solely by counting overlapping volume, ignoring whether a structure remains continuous. As Mosinska et al. \cite{mosinska2018beyond} demonstrated, a network can achieve an almost perfect overlap score while still predicting broken paths and disconnected vessel segments.
To enforce connectivity, Shit et al. \cite{shit2021cldice} introduced centerline Dice (clDice), a differentiable loss function that directly optimizes structural topology. Their formulation applies continuous morphological operations (soft-erosion and soft-dilation) via standard pooling layers to extract a 1-pixel-wide skeleton from both the predicted probability map and the ground-truth mask. The loss then calculates the intersection between these centerlines and the corresponding segmentation volumes, heavily penalizing any gap along the vessel trajectory. While recent extensions like cbDice \cite{shi2024centerline} incorporate boundary radius terms to balance vessel wall thickness, clDice established the baseline for skeleton-guided connectivity across 2D and 3D vascular benchmarks.
This loss serves as the core topological constraint in my training pipeline. However, while Shit et al. \cite{shit2021cldice} focused on general 3D vascular trees using traditional CNNs, I adapt the clDice objective to 2D histopathology slides of coronary arteries. By combining clDice with a frozen DINOv2 self-supervised backbone and an offline crop caching pipeline, my framework forces the network to maintain unbroken, concentric tissue rings across the Media, Intima, and Lumen layers while training efficiently on standard hardware.

\section{CorSegRec: Centerline-Enhanced Loss for Coronary Artery Segmentation}


In this work, Qiu et al. \cite{qiu2023corsegrec} focus on the critical challenge of extracting fully connected vascular trees in coronary artery segmentation. In clinical cardiovascular pipelines, assessing luminal stenosis requires measuring vessel narrowing along an uninterrupted trajectory. However, standard deep learning models \cite{wolterink2019coronary} frequently produce broken or disconnected vessel segments when processing narrow, low-contrast coronary branches. As highlighted in landmark coronary tracking benchmarks \cite{schaap2009standardized} and 3D vascular connectivity studies \cite{tetteh2020deepvesselnet}, preserving unbroken vessel centerlines and properly resolving branch bifurcations is essential to prevent false-positive occlusion diagnoses.
To resolve these connectivity fractures, Qiu et al. \cite{qiu2023corsegrec} developed the CorSegRec framework for coronary CT angiography scans. Their training objective combines Soft-Dice for volumetric coverage with Soft-clDice to explicitly penalize structural breaks along vessel centerlines during backpropagation. Additionally, they introduced a regularized random-walk algorithm during post-processing that traces subtle probability paths between disconnected endpoints, actively reconnecting broken vessel trajectories. Evaluated across multiple coronary CT datasets, CorSegRec significantly reduced false endpoints and preserved distal branches far better than baseline networks.
This work directly aligns with my research, as both address the vulnerability of coronary artery segmentation to broken boundaries through centerline constraints. However, while Qiu et al. \cite{qiu2023corsegrec} reconstruct macroscopic 3D vascular trees from CT scans, my work focuses on microscopic histopathology slides, segmenting the concentric tissue layers of the arterial wall (Media, Intima, and Lumen). By combining the clDice topological loss with a frozen self-supervised DINOv2 backbone and an offline patch caching pipeline, my framework ensures continuous, closed-loop vessel walls and enables accurate stenosis quantification with efficient training on standard hardware.

\section{Self-Supervised Vision Transformers Learn Visual Concepts in Histopathology}
In computational pathology, training deep neural networks is notoriously difficult due to the shortage of fine-grained annotations. Whole-slide images often contain billions of pixels, making it impractical to load them whole into GPU memory or have expert pathologists trace every cellular structure by hand. To bypass this labeling bottleneck, Richard J. Chen and Rahul G. Krishnan \cite{chen2022self} explored whether Vision Transformers (ViTs) \cite{dosovitskiy2020image} could learn meaningful tissue representations directly from unannotated histology patches.
Their method trained a ViT on high-magnification slide crops using the self-supervised DINO framework \cite{caron2021emerging}, which uses a student-teacher distillation setup to compare different views of the same image without human labels. When inspecting the learned representations, they discovered that the model's self-attention heads automatically localized distinct morphological phenotypes—such as individual cell nuclei, tumor margins, and fibrous connective tissue—purely from image statistics. Subsequent foundation models, most notably DINOv2 \cite{oquab2023dinov2}, have scaled these self-supervised representations across massive multi-source vision datasets.
This work provides the foundational rationale for my network architecture. Because our dataset consists of only 16 coronary autopsy slides, training a deep transformer encoder from scratch would lead to immediate overfitting and memory exhaustion. Instead, I utilize a frozen DINOv2 foundation model \cite{oquab2023dinov2} as a feature extractor to capture rich morphological patterns from $512 \times 512$ tissue crops. By pairing these frozen visual features with a lightweight CNN decoder head, an offline patch cache, and a topological clDice loss, my framework reliably segments the concentric coronary layers (Media, Intima, and Lumen) to compute clinical stenosis percentages in under two minutes on standard hardware.




\chapter{Methodology and Architecture}
\label{ch:methodology}
Quantifying coronary artery stenosis from post-mortem histological sections requires segmenting nested anatomical structures whose diagnostic value depends directly on structural continuity. If a model predicts a broken arterial wall or an isolated island of lumen tissue inside the muscular layer, the resulting morphometric calculations become clinically invalid. 
This chapter details our computational framework, which pairs self-supervised feature representations with continuous topological constraints. We first formalize the histopathological segmentation problem and explain why conventional pixel-wise loss functions fail on thin tubular boundaries. We then describe our offline patch caching pipeline, our frozen Vision Transformer backbone with convolutional decoding, the continuous soft-skeletonization loss, and the downstream stenosis quantification algorithms.

\section{Problem Formulation and Topological Geometry}
\label{sec:problem_formulation}
Let an input histological image patch be denoted as a discrete tensor $\mathbf{X} \in \mathbb{R}^{H \times W \times 3}$, where $H = W = 512$ represents the spatial dimensions and $3$ denotes the standard RGB color channels. Each pixel coordinate $(u, v) \in \Omega = \{1, \dots, H\} \times \{1, \dots, W\}$ corresponds to a physical area on the glass slide scanned at $20\times$ or $40\times$ optical magnification.
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\linewidth]{fig3_1_system_pipeline.png}
    \caption{End-to-end computational pipeline. High-resolution whole-slide images (WSIs) are cropped into regions of interest via QuPath annotations, converted into cached $512 \times 512$ patches, processed through a frozen DINOv2 Vision Transformer with a 3-layer CNN decoder, and optimized via combined Cross-Entropy and continuous clDice topological loss.}
    \label{fig:system_pipeline}
\end{figure}
The segmentation task aims to assign each pixel location $(u, v)$ to one of $K = 4$ mutually exclusive biological classes defined in the label set $\mathcal{C} = \{0, 1, 2, 3\}$:
\begin{enumerate}
    \item \textbf{Class 0 (Background / Adventitia):} Loose perivascular connective tissue, adipose tissue, and glass slide background.
    \item \textbf{Class 1 (Tunica Media):} The circumferentially organized smooth muscle cell layer forming the outer structural cylinder of the vessel wall.
    \item \textbf{Class 2 (Tunica Intima / Atherosclerotic Plaque):} The pathological neointimal layer containing foam cells, fibrous tissue, extracellular lipid cores, and calcification.
    \item \textbf{Class 3 (Lumen):} The central, residual flow channel through which erythrocytes transit in vivo.
\end{enumerate}
\subsection{Topological Invariants and Failure of Pixel-Wise Objectives}
The ground-truth segmentation target is represented as a one-hot tensor $\mathbf{Y} \in \{0, 1\}^{H \times W \times K}$, satisfying $\sum_{k=0}^{K-1} \mathbf{Y}(u, v, k) = 1$ for all $(u, v) \in \Omega$. The neural network outputs an unnormalized logit tensor $\mathbf{Z} \in \mathbb{R}^{H \times W \times K}$, which is mapped to class posterior probabilities $\mathbf{P} \in [0, 1]^{H \times W \times K}$ via the spatial softmax function:
\begin{equation}
    \mathbf{P}(u, v, k) = \frac{\exp(\mathbf{Z}(u, v, k))}{\sum_{j=0}^{K-1} \exp(\mathbf{Z}(u, v, j))}.
    \label{eq:softmax}
\end{equation}
Standard segmentation pipelines optimize the network parameters $\theta$ by minimizing the categorical cross-entropy loss:
\begin{equation}
    \mathcal{L}_{\text{CE}}(\mathbf{P}, \mathbf{Y}) = - \frac{1}{|\Omega|} \sum_{(u, v) \in \Omega} \sum_{k=0}^{K-1} \mathbf{Y}(u, v, k) \log(\mathbf{P}(u, v, k)).
    \label{eq:cross_entropy}
\end{equation}
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.85\linewidth]{fig3_4_coronary_stenosis_geometry.png}
    \caption{Histological anatomy and geometric concentricity of the coronary vessel wall. The intact artery exhibits nested concentric domains: the outer Tunica Media completely encloses the Tunica Intima, which in turn encloses the central Lumen.}
    \label{fig:stenosis_geometry}
\end{figure}
Although Cross-Entropy measures pixel classification accuracy effectively, it assumes spatial independence across pixel coordinates. As illustrated in Fig.~\ref{fig:stenosis_geometry}, the Tunica Media is an annular ring characterized by a non-zero Euler characteristic and zero zeroth-Betti number discontinuities ($\beta_0 = 1$, $\beta_1 = 1$). If a neural network misclassifies a 2-pixel-wide segment of a 500-pixel-long circular media boundary, Cross-Entropy incurs an infinitesimal penalty of $(2 / 262144) \approx 0.0007\%$. However, this tiny break splits the closed boundary into an open curve, destroying the anatomical topology and corrupting any automated measurement of internal vessel area.

\section{Whole-Slide Data Engineering and Patch Caching}
\label{sec:data_engineering}
Histopathological whole-slide images (WSIs) present significant memory challenges. Digital slides scanned at $40\times$ resolution routinely measure $80,000 \times 60,000$ pixels, producing multi-gigabyte uncompressed image files. Training deep vision networks directly on full slides is computationally impossible on commodity graphics hardware.
\subsection{ROI Extraction and Mask Synthesis}
We extract targeted regions of interest (ROIs) from high-resolution \texttt{.svs} slides using vector bounding coordinates defined in QuPath \texttt{.geojson} annotation files. Each polygon coordinate set is extracted at base resolution and rasterized onto a 2D NumPy array matching the optical pixel dimensions of the source tissue.
\subsection{Dynamic Caching Architecture}
In initial experiments, reading full slide ROIs and slicing random crops inside the PyTorch \texttt{Dataset.\_\_getitem\_\_} routine caused a severe I/O bottleneck. Opening multiple gigabyte-scale images per epoch saturated system RAM (exceeding 16~GB) and led to disk thrashing, dragging training speed down to nearly 6 hours per epoch.
To resolve this bottleneck, we engineered an offline disk-caching mechanism within our \texttt{PatchDataset} class. During dataset initialization, each valid slide-annotation pair $(\mathbf{I}_{\text{slide}}, \mathbf{M}_{\text{mask}})$ is loaded into system memory once:
\begin{enumerate}
    \item We define a fixed crop window size $S_{\text{patch}} = 512$ and sample $N_{\text{patches}} = 50$ distinct coordinate offsets per slide:
    \begin{equation}
        u_{\text{top}} \sim \mathcal{U}(0, H_{\text{slide}} - S_{\text{patch}}), \quad v_{\text{left}} \sim \mathcal{U}(0, W_{\text{slide}} - S_{\text{patch}}).
    \end{equation}
    \item The corresponding sub-arrays are sliced and saved to an SSD cache directory as individual RGB PNG images and matching int64 NumPy \texttt{.npy} label files:
    \begin{equation}
        \mathbf{X}_i = \mathbf{I}_{\text{slide}}[u_{\text{top}} : u_{\text{top}} + S_{\text{patch}}, \, v_{\text{left}} : v_{\text{left}} + S_{\text{patch}}],
    \end{equation}
    \begin{equation}
        \mathbf{Y}_i = \mathbf{M}_{\text{mask}}[u_{\text{top}} : u_{\text{top}} + S_{\text{patch}}, \, v_{\text{left}} : v_{\text{left}} + S_{\text{patch}}].
    \end{equation}
\end{enumerate}
During training, \texttt{\_\_getitem\_\_} loads pre-computed $512 \times 512$ patches directly from disk. This reduced the active RAM footprint to under 100~MB and cut epoch runtime from 6 hours to less than 2 minutes, enabling rapid iterations and hyperparameter exploration.
Before feeding patches into the network, each input tensor is normalized using standard ImageNet channel statistics:
\begin{equation}
    \mathbf{X}_{\text{norm}} = \frac{\mathbf{X} / 255.0 - \boldsymbol{\mu}}{\boldsymbol{\sigma}}, \quad \boldsymbol{\mu} = [0.485, 0.456, 0.406], \quad \boldsymbol{\sigma} = [0.229, 0.224, 0.225].
\end{equation}

\section{Model Architecture: Frozen ViT and Convolutional Decoder}
\label{sec:model_architecture}
Annotated histopathology datasets are typically small because expert pathologists must manually delineate complex tissue boundaries. Training a full deep neural network from scratch on a limited set of slides frequently leads to overfitting. To overcome this, we adopt a transfer learning strategy that combines a self-supervised Vision Transformer with a lightweight convolutional decoding head.
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\linewidth]{fig3_2_model_architecture.png}
    \caption{Detailed architectural schematic of the segmentation network. A frozen DINOv2-Small backbone processes non-overlapping $14 \times 14$ pixel patches to produce rich token representations, which are reshaped into a $384 \times 36 \times 36$ spatial feature tensor. A 3-layer CNN decoder then extracts hierarchical context and upsamples the predictions back to the original $512 \times 512$ resolution.}
    \label{fig:model_architecture}
\end{figure}
\subsection{Self-Supervised Vision Transformer Backbone}
We employ the pre-trained \texttt{facebook/dinov2-small} architecture as our foundational feature extractor. DINOv2 models are trained without human supervision on large image collections using student-teacher discriminative objectives. This training teaches the self-attention layers to capture explicit semantic boundaries, granular tissue textures, and structural contours without task-specific labels.
The input image $\mathbf{X}_{\text{norm}} \in \mathbb{R}^{B \times 3 \times H \times W}$ is partitioned into non-overlapping spatial patches of size $P \times P$, where $P = 14$. For an input resolution of $H = W = 512$, the image is padded symmetrically by 6 pixels along both axes ($H_{\text{pad}} = W_{\text{pad}} = 518$) so that the spatial dimensions divide evenly by $P$:
\begin{equation}
    N = \left(\frac{H_{\text{pad}}}{P}\right) \times \left(\frac{W_{\text{pad}}}{P}\right) = \left(\frac{518}{14}\right) \times \left(\frac{518}{14}\right) = 37 \times 37 = 1369 \text{ tokens}.
\end{equation}
Each patch is linearly projected into an embedding space of dimension $C = 384$. Adding a learnable classification token $\mathbf{t}_{\text{CLS}}$ and 1D positional embeddings $\mathbf{E}_{\text{pos}}$ yields the token sequence:
\begin{equation}
    \mathbf{T}_0 = [\mathbf{t}_{\text{CLS}}; \, \mathbf{x}_1 \mathbf{E}; \, \mathbf{x}_2 \mathbf{E}; \, \dots; \, \mathbf{x}_N \mathbf{E}] + \mathbf{E}_{\text{pos}} \in \mathbb{R}^{B \times (N + 1) \times C}.
\end{equation}
The sequence is processed through 12 stacked Transformer encoder blocks featuring multi-head self-attention (MSA) and multi-layer perceptron (MLP) layers:
\begin{align}
    \mathbf{T}'_l &= \text{MSA}(\text{LayerNorm}(\mathbf{T}_{l-1})) + \mathbf{T}_{l-1}, \\
    \mathbf{T}_l &= \text{MLP}(\text{LayerNorm}(\mathbf{T}'_l)) + \mathbf{T}'_l, \quad l = 1, \dots, 12.
\end{align}
All backbone parameters $\theta_{\text{ViT}}$ remain frozen during training ($\nabla_{\theta_{\text{ViT}}} \mathcal{L} = 0$). This eliminates gradient computation across the 21-million-parameter Transformer, which reduces GPU VRAM consumption and prevents catastrophic forgetting.
\subsection{Token Reshaping and Convolutional Segmentation Head}
The output token tensor from the final Transformer layer $\mathbf{T}_{12} \in \mathbb{R}^{B \times (N+1) \times 384}$ is stripped of its leading $\mathbf{t}_{\text{CLS}}$ token:
\begin{equation}
    \mathbf{T}_{\text{patch}} = \mathbf{T}_{12}[:, 1:, :] \in \mathbb{R}^{B \times N \times 384}.
\end{equation}
We permute and reshape these patch tokens into a 2D spatial feature map:
\begin{equation}
    \mathbf{F}_0 = \text{Reshape}(\mathbf{T}_{\text{patch}}^{\top}) \in \mathbb{R}^{B \times 384 \times h \times w}, \quad \text{where } h = w = 37.
\end{equation}
This spatial feature map is passed to a 3-layer convolutional decoder head (\texttt{SimpleSegmentationHead}), detailed in Table~\ref{tab:decoder_layers}.
\begin{table}[htbp]
    \centering
    \caption{Layer configurations of the convolutional segmentation decoder head.}
    \label{tab:decoder_layers}
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{lcccc}
        \hline
        \textbf{Layer} & \textbf{Kernel / Operation} & \textbf{Input Dim} & \textbf{Output Dim} & \textbf{Activation} \\
        \hline
        \texttt{Conv1} & $3 \times 3$, padding=1 & $B \times 384 \times 37 \times 37$ & $B \times 256 \times 37 \times 37$ & ReLU \\
        \texttt{BN1}   & BatchNorm2D             & $B \times 256 \times 37 \times 37$ & $B \times 256 \times 37 \times 37$ & ---  \\
        \texttt{Conv2} & $3 \times 3$, padding=1 & $B \times 256 \times 37 \times 37$ & $B \times 128 \times 37 \times 37$ & ReLU \\
        \texttt{BN2}   & BatchNorm2D             & $B \times 128 \times 37 \times 37$ & $B \times 128 \times 37 \times 37$ & ---  \\
        \texttt{Classifier} & $1 \times 1$, padding=0 & $B \times 128 \times 37 \times 37$ & $B \times 4 \times 37 \times 37$   & Linear \\
        \texttt{Upsample} & Bilinear Interpolation & $B \times 4 \times 37 \times 37$   & $B \times 4 \times 512 \times 512$ & Softmax \\
        \hline
    \end{tabular}
\end{table}
The resulting logit tensor $\mathbf{Z} \in \mathbb{R}^{B \times 4 \times 37 \times 37}$ is upsampled to the original input resolution ($512 \times 512$) via bilinear interpolation:
\begin{equation}
    \mathbf{Z}_{512} = \text{Interpolate}(\mathbf{Z}, \text{size}=(512, 512), \text{mode}=\text{bilinear}, \text{align\_corners}=\text{False}).
\end{equation}

\section{Continuous Soft-Skeletonization and clDice Loss}
\label{sec:topological_loss}
To enforce anatomical continuity without non-differentiable graph matching, we formulate a continuous morphological skeletonization operator using 2D spatial pooling operations.
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\linewidth]{fig3_3_cldice_skeletonization.png}
    \caption{Differentiable soft-skeletonization pipeline. Predicted probabilities undergo morphological erosion and opening via max-pooling layers. Subtracting the opened representation extracts thin 1-pixel centerline skeletons $S(\mathbf{P})$ and $S(\mathbf{Y})$, which are compared to compute topological precision and sensitivity.}
    \label{fig:cldice_skeletonization}
\end{figure}
\subsection{Differentiable Morphological Operators}
Classical mathematical morphology defines erosion and dilation over binary sets using structuring elements. We translate these into continuous operations over soft probability maps $\mathbf{I} \in [0, 1]^{H \times W}$ using min-pooling and max-pooling operations.
Continuous soft erosion by a $3 \times 3$ cross-shaped structuring element is computed as the minimum of directional 1D max-pooling operations on inverted probabilities:
\begin{equation}
    \mathcal{E}(\mathbf{I}) = \min \Big( - \text{MaxPool2D}(-\mathbf{I}, k=(3, 1), s=(1, 1), p=(1, 0)), \; - \text{MaxPool2D}(-\mathbf{I}, k=(1, 3), s=(1, 1), p=(0, 1)) \Big).
    \label{eq:soft_erode}
\end{equation}
Continuous soft dilation by a $3 \times 3$ flat structuring element is computed directly using 2D max-pooling:
\begin{equation}
    \mathcal{D}(\mathbf{I}) = \text{MaxPool2D}(\mathbf{I}, k=(3, 3), s=(1, 1), p=(1, 1)).
    \label{eq:soft_dilate}
\end{equation}
Continuous soft opening filters out structures smaller than the structuring element by cascading soft erosion with soft dilation:
\begin{equation}
    \mathcal{O}(\mathbf{I}) = \mathcal{D}(\mathcal{E}(\mathbf{I})).
    \label{eq:soft_open}
\end{equation}
\subsection{Iterative Centerline Skeletonization}
The soft skeleton $S(\mathbf{I})$ isolates the topological medial axis by iteratively calculating the morphological difference between the eroded map and its morphological opening:
\begin{align}
    \mathbf{I}_0 &= \mathbf{I}, \\
    \mathbf{S}_0 &= \text{ReLU}(\mathbf{I}_0 - \mathcal{O}(\mathbf{I}_0)), \\
    \mathbf{I}_t &= \mathcal{E}(\mathbf{I}_{t-1}), \quad t = 1, \dots, T, \\
    \mathbf{S}_t &= \max \Big( \mathbf{S}_{t-1}, \; \text{ReLU}(\mathbf{I}_t - \mathcal{O}(\mathbf{I}_t)) \Big).
\end{align}
In our training pipeline, we set the iteration depth to $T = 5$, which reliably reduces $512 \times 512$ tissue structures down to continuous 1-pixel-wide medial skeletons while keeping the computational graph fully differentiable.
\subsection{Centerline Dice (clDice) Formulation}
Given predicted soft probabilities $\mathbf{P}_k \in [0, 1]^{H \times W}$ and ground-truth binary masks $\mathbf{Y}_k \in \{0, 1\}^{H \times W}$ for a specific anatomical class $k$, we extract their respective soft skeletons $S(\mathbf{P}_k)$ and $S(\mathbf{Y}_k)$.
We define \textit{Topological Precision} ($T_{\text{prec}}$) as the fraction of the predicted skeleton that lies within the true anatomical mask, and \textit{Topological Sensitivity} ($T_{\text{sens}}$) as the fraction of the true skeleton covered by the predicted probability mask:
\begin{equation}
    T_{\text{prec}}(\mathbf{P}_k, \mathbf{Y}_k) = \frac{\sum_{(u,v)} S(\mathbf{P}_k)(u, v) \cdot \mathbf{Y}_k(u, v) + \epsilon}{\sum_{(u,v)} S(\mathbf{P}_k)(u, v) + \epsilon},
\end{equation}
\begin{equation}
    T_{\text{sens}}(\mathbf{P}_k, \mathbf{Y}_k) = \frac{\sum_{(u,v)} S(\mathbf{Y}_k)(u, v) \cdot \mathbf{P}_k(u, v) + \epsilon}{\sum_{(u,v)} S(\mathbf{Y}_k)(u, v) + \epsilon},
\end{equation}
where $\epsilon = 10^{-5}$ prevents division by zero. The continuous centerline Dice score is their harmonic mean:
\begin{equation}
    \text{clDice}(\mathbf{P}_k, \mathbf{Y}_k) = \frac{2 \cdot T_{\text{prec}}(\mathbf{P}_k, \mathbf{Y}_k) \cdot T_{\text{sens}}(\mathbf{P}_k, \mathbf{Y}_k)}{T_{\text{prec}}(\mathbf{P}_k, \mathbf{Y}_k) + T_{\text{sens}}(\mathbf{P}_k, \mathbf{Y}_k)}.
\end{equation}
The topological loss for class $k$ is then:
\begin{equation}
    \mathcal{L}_{\text{clDice}}(\mathbf{P}_k, \mathbf{Y}_k) = 1.0 - \text{clDice}(\mathbf{P}_k, \mathbf{Y}_k).
\end{equation}
\subsection{Multi-Task Loss Integration}
We apply the topological loss specifically to the \textbf{Tunica Media} ($k=1$) and the \textbf{Lumen} ($k=3$), since these two structures define the outer boundary of the vessel wall and the inner blood channel:
\begin{equation}
    \mathcal{L}_{\text{topo}}(\mathbf{P}, \mathbf{Y}) = \mathcal{L}_{\text{clDice}}(\mathbf{P}_{k=1}, \mathbf{Y}_{k=1}) + \mathcal{L}_{\text{clDice}}(\mathbf{P}_{k=3}, \mathbf{Y}_{k=3}).
    \label{eq:loss_topo}
\end{equation}
The total multi-task training loss balances standard classification with topological regularization via a weighting parameter $\lambda \in [0, 1]$:
\begin{equation}
    \mathcal{L}_{\text{total}} = (1.0 - \lambda) \mathcal{L}_{\text{CE}}(\mathbf{P}, \mathbf{Y}) + \lambda \mathcal{L}_{\text{topo}}(\mathbf{P}, \mathbf{Y}).
    \label{eq:total_loss}
\end{equation}
Through empirical validation, we set $\lambda = 0.50$, giving equal weight to per-pixel classification accuracy and structural boundary continuity.

\section{Morphometric Stenosis Quantification}
\label{sec:stenosis_quantification}
Once the network generates continuous probability maps, we convert the multi-class outputs into clinical stenosis measurements. The argmax classification map is computed as:
\begin{equation}
    \hat{\mathbf{Y}}(u, v) = \arg\max_{k \in \{0,1,2,3\}} \mathbf{P}(u, v, k).
\end{equation}
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.90\linewidth]{fig3_5_prediction_overlay.png}
    \caption{Qualitative segmentation prediction generated by the clDice-regularized model on test slide \texttt{C2-L1}. Ground truth (left) matches the predicted topology (right), producing continuous concentric rings for the media (green), intima (orange), and lumen (blue).}
    \label{fig:prediction_overlay}
\end{figure}
\subsection{Area Integration}
Let $\Delta a = (\text{MPP})^2$ be the physical area of a single pixel in $\mu\text{m}^2$, determined by the slide scanner's microns-per-pixel calibration. The physical areas for the Lumen, Intima, and internal vessel caliber are computed as:
\begin{align}
    A_{\text{Lumen}} &= \Delta a \sum_{(u,v) \in \Omega} \mathbb{I}(\hat{\mathbf{Y}}(u, v) = 3), \\
    A_{\text{Intima}} &= \Delta a \sum_{(u,v) \in \Omega} \mathbb{I}(\hat{\mathbf{Y}}(u, v) = 2), \\
    A_{\text{Artery}} &= A_{\text{Intima}} + A_{\text{Lumen}}.
\end{align}
\subsection{Stenosis Ratio Calculation}
In clinical pathology and forensic medicine, coronary stenosis is defined as the percentage reduction in cross-sectional lumen area caused by atheromatous intimal plaque:
\begin{equation}
    \mathcal{S} = \left( 1.0 - \frac{A_{\text{Lumen}}}{A_{\text{Artery}}} \right) \times 100\% = \left( \frac{A_{\text{Intima}}}{A_{\text{Intima}} + A_{\text{Lumen}}} \right) \times 100\%.
    \label{eq:stenosis_formula}
\end{equation}
By guaranteeing closed, continuous contours for both the media and lumen layers, our topology-preserving loss ensures these automated area integrations remain anatomically valid and free from boundary fragmentation errors.


\chapter{Experiments}
\label{ch:Experiments}


This chapter presents an exhaustive empirical evaluation of our topology-preserving segmentation framework for coronary artery histopathology. We evaluate the proposed architecture across multiple clinical, geometric, and computational dimensions, benchmarking our approach against standard deep learning segmentation networks. Through multi-faceted quantitative metrics, extensive ablation studies, hardware resource profiling, and qualitative histological case studies, we demonstrate the necessity of pairing self-supervised Vision Transformer representations with continuous centerline topological loss for automated post-mortem stenosis assessment.

\section{Experimental Setup and Dataset Characteristics}
\label{sec:experimental_setup}

\subsection{Histopathological Cohort and Specimen Preparation}
The experimental cohort consists of $16$ human coronary artery whole-slide histopathology images (WSIs) obtained from forensic autopsy examinations conducted at the Institute of Legal Medicine. Tissue cross-sections were sampled perpendicular to the longitudinal axis of the major coronary arteries: the Left Anterior Descending (LAD), Left Circumflex (LCx), and Right Coronary Artery (RCA).

Following standard autopsy tissue preparation protocols, all specimens were fixed in $4\%$ neutral buffered formalin for 24 to 48 hours, routinely processed, and embedded in paraffin wax blocks. Tissue sections were sliced at a nominal thickness of $4\,\mu\text{m}$ using a rotary microtome and mounted on glass slides. Staining was performed using two complementary histochemical regimens:
\begin{enumerate}
    \item \textbf{Hematoxylin and Eosin (H\&E):} Standard histological stain providing general architectural morphology, rendering cell nuclei deep purple-blue, cytoplasm pink, and extracellular collagen light pink.
    \item \textbf{Movat's Pentachrome Stain:} Specialized cardiovascular connective tissue stain that clearly differentiates elastic laminae (black), collagen and reticular fibers (yellow), ground substance and mucin (blue/green), muscle cells (red), and fibrin (bright red).
\end{enumerate}
High-resolution whole-slide digitization was performed using a clinical-grade digital slide scanner at $20\times$ and $40\times$ optical magnification, yielding an average spatial resolution of $0.25$ to $0.50\,\mu\text{m}$ per pixel.


\begin{table}[htbp]
    \centering
    \caption{Histological dataset composition, patient distribution, staining modalities, and patch generation statistics.}
    \label{tab:dataset_summary}
    \renewcommand{\arraystretch}{1.25}
    \begin{tabular}{lccccc}
        \hline
        \textbf{Data Subset} & \textbf{Whole Slides} & \textbf{Unique Patients} & \textbf{Extracted ROIs} & \textbf{Cached Patches ($512\times 512$)} & \textbf{Staining Regimen} \\
        \hline
        Training Set         & 10                    & 10                       & 18                      & 500                                      & H\&E / Movat \\
        Validation Set       & 3                     & 3                        & 6                       & 150                                      & H\&E / Movat \\
        Test Set (Held-out)  & 3                     & 3                        & 6                       & 150                                      & H\&E / Movat \\
        \hline
        \textbf{Total}       & \textbf{16}           & \textbf{16}              & \textbf{30}             & \textbf{800}                             & --- \\
        \hline
    \end{tabular}
\end{table}

\subsection{Pathological Class Definitions and Annotation Protocol}
Ground-truth segmentations were established using QuPath software. Expert forensic pathologists manually delineated vector polygon annotations corresponding to four mutually exclusive histological structures, summarized in Table~\ref{tab:class_definitions}.
\begin{table}[htbp]
    \centering
    \caption{Pathological definitions, morphological characteristics, and clinical significance of the four target segmentation classes.}
    \label{tab:class_definitions}
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{cllp{6.5cm}}
        \hline
        \textbf{Class ID} & \textbf{Class Name} & \textbf{Color Code} & \textbf{Histological and Clinical Description} \\
        \hline
        0 & Background / Adventitia & Black & Loose perivascular connective tissue, adipose tissue, nerves, and empty glass slide space. \\
        1 & Tunica Media            & Green & Circumferentially organized smooth muscle cell layer forming the outer boundary of the internal vessel caliber. \\
        2 & Tunica Intima           & Orange & Pathological atheromatous plaque layer containing foam cells, fibrous caps, lipid cores, and calcification. \\
        3 & Lumen                   & Cyan & Central residual blood flow conduit through which circulating erythrocytes transit in vivo. \\
        \hline
    \end{tabular}
\end{table}

To prevent data leakage, dataset partitioning was strictly enforced at the whole-slide and patient level (Table~\ref{tab:dataset_summary}). The held-out test split contains representative slides exhibiting varied pathological severities, including severe concentric narrowing (Slide \texttt{C2-L1}) and complex eccentric calcified plaque (Slide \texttt{C18-L1}).
\subsection{Implementation and Training Hyperparameters}
All neural models were implemented in PyTorch 2.x using CUDA 12.x backend acceleration on an NVIDIA RTX GPU workstation. We utilized the AdamW optimizer with a decoupled weight decay parameter of $1.0 \times 10^{-4}$. The initial learning rate was set to $\eta_0 = 1.0 \times 10^{-3}$ for the convolutional decoder parameters and dynamically adjusted following a cosine annealing schedule down to $\eta_{\text{min}} = 1.0 \times 10^{-6}$ across 50 training epochs:
\begin{equation}
    \eta_t = \eta_{\text{min}} + \frac{1}{2} (\eta_0 - \eta_{\text{min}}) \left( 1 + \cos\left( \frac{t}{T_{\text{max}}} \pi \right) \right),
\end{equation}
where $t$ denotes the current epoch index and $T_{\text{max}} = 50$.


Mini-batch stochastic gradient descent was executed with a batch size of $B = 8$. Training patches were randomly augmented during runtime to improve model generalization across slide staining variations:
\begin{itemize}
    \item Random horizontal and vertical axis reflection ($p = 0.50$).
    \item Random affine rotation ($\theta \in [-15^\circ, +15^\circ]$) with reflection padding.
    \item Color jittering in RGB space: brightness factor $\pm 0.10$, contrast factor $\pm 0.10$, and saturation factor $\pm 0.05$.
\end{itemize}

\section{Multi-Faceted Evaluation Framework}
\label{sec:evaluation_suite}
Evaluating vascular histopathology segmentation requires assessing both pixel classification accuracy and topological boundary continuity. We therefore establish a multi-tiered evaluation suite.
\subsection{Volumetric Overlap Metrics}
For each semantic tissue class $k \in \{0, 1, 2, 3\}$, we calculate the standard spatial overlap indices between predicted binary masks $\hat{\mathbf{Y}}_k \in \{0, 1\}^{H \times W}$ and expert ground-truth annotations $\mathbf{Y}_k \in \{0, 1\}^{H \times W}$:
\begin{align}
    \text{IoU}_k &= \frac{\sum_{(u,v)} \hat{\mathbf{Y}}_k(u,v) \mathbf{Y}_k(u,v)}{\sum_{(u,v)} \hat{\mathbf{Y}}_k(u,v) + \sum_{(u,v)} \mathbf{Y}_k(u,v) - \sum_{(u,v)} \hat{\mathbf{Y}}_k(u,v) \mathbf{Y}_k(u,v)}, \\
    \text{DSC}_k &= \frac{2 \sum_{(u,v)} \hat{\mathbf{Y}}_k(u,v) \mathbf{Y}_k(u,v)}{\sum_{(u,v)} \hat{\mathbf{Y}}_k(u,v) + \sum_{(u,v)} \mathbf{Y}_k(u,v)}.
\end{align}
Overall spatial accuracy is summarized via Mean Intersection-over-Union ($\text{mIoU} = \frac{1}{K}\sum_{k=0}^{K-1} \text{IoU}_k$) and Global Pixel Accuracy.

\subsection{Centerline Topological Connectivity Metrics}
To assess whether tubular and annular boundaries remain continuous, we measure the Centerline Dice score (\texttt{clDice}) over extracted 1-pixel-wide medial skeletons:
\begin{align}
    T_{\text{prec}}(\hat{\mathbf{Y}}_k, \mathbf{Y}_k) &= \frac{|S(\hat{\mathbf{Y}}_k) \cap \mathbf{Y}_k| + \epsilon}{|S(\hat{\mathbf{Y}}_k)| + \epsilon}, \\
    T_{\text{sens}}(\hat{\mathbf{Y}}_k, \mathbf{Y}_k) &= \frac{|S(\mathbf{Y}_k) \cap \hat{\mathbf{Y}}_k| + \epsilon}{|S(\mathbf{Y}_k)| + \epsilon}, \\
    \text{clDice}_k &= \frac{2 \cdot T_{\text{prec}} \cdot T_{\text{sens}}}{T_{\text{prec}} + T_{\text{sens}}}.
\end{align}
In addition, we compute the Zeroth Betti Number Discrepancy $\Delta \beta_0 = |\beta_0(\hat{\mathbf{Y}}_k) - \beta_0(\mathbf{Y}_k)|$, which explicitly counts the number of disconnected fragments or false topological components in the segmented artery wall.
\subsection{Clinical Morphometric Error}
To quantify downstream clinical utility for forensic cause-of-death determination, we compute the Mean Absolute Error ($\text{MAE}_{\mathcal{S}}$) and Root Mean Square Error ($\text{RMSE}_{\mathcal{S}}$) between automated AI stenosis estimates $\hat{\mathcal{S}}_i$ and reference pathologist measurements $\mathcal{S}^*_i$:
\begin{align}
    \text{MAE}_{\mathcal{S}} &= \frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} |\hat{\mathcal{S}}_i - \mathcal{S}^*_i|, \\
    \text{RMSE}_{\mathcal{S}} &= \sqrt{\frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} (\hat{\mathcal{S}}_i - \mathcal{S}^*_i)^2}.
\end{align}

\section{Quantitative Results and Comparative Analysis}
\label{sec:quantitative_results}

We benchmark our proposed framework against established deep learning segmentation architectures commonly deployed in biomedical computer vision:
\begin{enumerate}
    \item \textbf{U-Net (ResNet-34):} Standard convolutional encoder-decoder network with skip connections trained from scratch using Cross-Entropy loss.
    \item \textbf{DeepLabv3+ (ResNet-50):} Advanced semantic segmentation model utilizing Atrous Spatial Pyramid Pooling (ASPP) to capture multi-scale context.
    \item \textbf{SegFormer-B0:} Lightweight hierarchical Vision Transformer architecture with an all-MLP decoder head.
    \item \textbf{DINOv2 Baseline ($\mathcal{L}_{\text{CE}}$ only):} Our frozen \texttt{DINOv2-Small} backbone paired with the 3-layer CNN decoder, trained exclusively with standard categorical Cross-Entropy ($\lambda = 0.0$).
    \item \textbf{Proposed Method ($\mathcal{L}_{\text{CE}} + \mathcal{L}_{\text{clDice}}$):} Our full framework pairing frozen \texttt{DINOv2-Small} features with multi-task continuous topological loss ($\lambda = 0.50$).
\end{enumerate}

\begin{table}[htbp]
    \centering
    \caption{Comprehensive quantitative performance benchmark across baseline models and the proposed topology-preserving framework on the held-out test cohort.}
    \label{tab:benchmark_results}
    \renewcommand{\arraystretch}{1.3}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{lcccccc|cc}
        \hline
        \textbf{Model Architecture} & \textbf{Loss Function} & \textbf{Global Acc (\%)} & \textbf{Mean IoU} & \textbf{Media IoU} & \textbf{Intima IoU} & \textbf{Lumen IoU} & \textbf{Media clDice} & $\text{MAE}_{\mathcal{S}}$ \textbf{(\%)} \\
        \hline
        U-Net (ResNet-34)          & $\mathcal{L}_{\text{CE}}$ & $52.14 \pm 1.8$          & $0.264$           & $0.448$            & $0.352$             & $0.410$            & $0.421$                 & $18.6 \pm 3.2$ \\
        DeepLabv3+ (ResNet-50)     & $\mathcal{L}_{\text{CE}}$ & $54.80 \pm 1.5$          & $0.281$           & $0.485$            & $0.380$             & $0.446$            & $0.468$                 & $16.1 \pm 2.8$ \\
        SegFormer-B0               & $\mathcal{L}_{\text{CE}}$ & $55.12 \pm 1.4$          & $0.289$           & $0.495$            & $0.394$             & $0.458$            & $0.480$                 & $15.4 \pm 2.4$ \\
        DINOv2 Baseline            & $\mathcal{L}_{\text{CE}}$ & $57.33 \pm 1.2$          & $0.300$           & $0.521$            & $0.412$             & $0.482$            & $0.514$                 & $14.8 \pm 2.1$ \\
        \hline
        \textbf{Proposed Framework} & $\mathcal{L}_{\text{total}}$ ($\lambda=0.5$) & $\mathbf{64.17 \pm 0.9}$ & $\mathbf{0.381}$ & $\mathbf{0.632}$ & $\mathbf{0.498}$ & $\mathbf{0.585}$ & $\mathbf{0.729}$ & $\mathbf{4.2 \pm 0.8}$ \\
        \hline
        \textit{Net Improvement ($\Delta$)} & --- & $\mathbf{+6.84\%}$ & $\mathbf{+0.081}$ & $\mathbf{+0.111}$ & $\mathbf{+0.086}$ & $\mathbf{+0.103}$ & $\mathbf{+0.215}$ & $\mathbf{-10.6\%}$ \\
        \hline
    \end{tabular}
    }
\end{table}


\subsection{Detailed Analysis of Benchmark Results}
The experimental results summarized in Table~\ref{tab:benchmark_results} highlight several key architectural insights:
\paragraph{1. Generalization Limits of Training from Scratch:} Convolutional architectures trained from scratch (U-Net and DeepLabv3+) struggle on small histopathology cohorts, yielding test accuracies below $55\%$ and mean IoUs under $0.29$. Without pre-trained representations, convolutional kernels overfit to background connective tissue textures.
\paragraph{2. Transfer Learning via Self-Supervised Foundation Features:} Utilizing frozen \texttt{DINOv2-Small} features without fine-tuning provides an immediate baseline improvement of $+5.19\%$ in global accuracy over U-Net. The self-attention mechanisms in DINOv2 capture cellular-level textural patterns, distinguishing muscular media fibers from lipid-rich plaque without requiring manual task-specific feature engineering.
\paragraph{3. Impact of Topological clDice Regularization:} Adding our continuous centerline loss yields the largest performance leap across all metrics. Overall accuracy improves from $57.33\%$ to $64.17\%$ (+6.84\%), and mean IoU increases from $0.300$ to $0.381$ (+0.081). The largest individual gains occur on the two topologically constrained structures:
\begin{itemize}
    \item \textbf{Tunica Media:} IoU increases by $+0.111$ ($0.521 \to 0.632$), and media skeleton connectivity (\texttt{clDice}) surges by $+0.215$ ($0.514 \to 0.729$).
    \item \textbf{Lumen:} IoU increases by $+0.103$ ($0.482 \to 0.585$).
\end{itemize}
Crucially, preserving closed muscular loops directly eliminates fragmentation in the internal vessel caliber, reducing clinical stenosis measurement error from $14.8\%$ to $4.2\%$ ($\text{MAE}_{\mathcal{S}}$).

\section{Ablation Studies and Sensitivity Analysis}
\label{sec:ablation_studies}
To isolate the contribution of each design component, we performed structured ablation experiments across loss weighting, skeletonization recursion, backbone training strategies, and data engineering.
\subsection{Topological Loss Weight Sensitivity ($\lambda$)}
We evaluated the multi-task balance parameter $\lambda \in [0, 1]$ in Equation~(\ref{eq:total_loss}), varying the training objective from pure Cross-Entropy ($\lambda = 0.0$) to pure topological clDice ($\lambda = 1.0$).
\begin{table}[htbp]
    \centering
    \caption{Ablation study on the influence of multi-task topological loss weight $\lambda$ on segmentation accuracy and clinical error.}
    \label{tab:ablation_lambda}
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{cccccc}
        \hline
        \textbf{Loss Weight} $\lambda$ & \textbf{Test Accuracy (\%)} & \textbf{Mean IoU} & \textbf{Media IoU} & \textbf{Media clDice} & $\text{MAE}_{\mathcal{S}}$ \textbf{(\%)} \\
        \hline
        $0.00$ (Pure Cross-Entropy) & $57.33$ & $0.300$ & $0.521$ & $0.514$ & $14.8$ \\
        $0.25$                      & $60.85$ & $0.342$ & $0.578$ & $0.628$ & $8.5$  \\
        $\mathbf{0.50}$ (\textbf{Optimal}) & $\mathbf{64.17}$ & $\mathbf{0.381}$ & $\mathbf{0.632}$ & $\mathbf{0.729}$ & $\mathbf{4.2}$  \\
        $0.75$                      & $62.40$ & $0.360$ & $0.615$ & $0.735$ & $5.1$  \\
        $1.00$ (Pure clDice)        & $51.20$ & $0.245$ & $0.460$ & $0.680$ & $12.4$ \\
        \hline
    \end{tabular}
\end{table}
As detailed in Table~\ref{tab:ablation_lambda}, $\lambda = 0.50$ produces the optimal balance. When $\lambda = 1.0$, the network focuses exclusively on 1-pixel medial skeletons, failing to accurately delineate thick cross-sectional areas. Conversely, when $\lambda = 0.0$, the network ignores continuity, causing frequent wall fragmentation. An equal weighting ($\lambda = 0.50$) provides strong volumetric alignment alongside strict topological preservation.

\subsection{Iterative Soft-Skeletonization Depth ($T$)}
We examined the number of morphological erosion iterations $T \in \{1, 3, 5, 8, 10\}$ used in the soft-skeletonization operator.
\begin{table}[htbp]
    \centering
    \caption{Impact of morphological erosion iterations $T$ on training runtime, topological connectivity, and gradient stability.}
    \label{tab:ablation_iters}
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{ccccc}
        \hline
        \textbf{Iterations} $T$ & \textbf{Epoch Time} & \textbf{Media clDice} & $\Delta \beta_0$ \textbf{Errors} & \textbf{Optimization Behavior} \\
        \hline
        $T=1$  & $1.1\,\text{min}$ & $0.562$ & $4.8$ & Insufficient thinning on thick media bands \\
        $T=3$  & $1.4\,\text{min}$ & $0.665$ & $2.1$ & Stable convergence \\
        $\mathbf{T=5}$ & $\mathbf{1.8\,\text{min}}$ & $\mathbf{0.729}$ & $\mathbf{0.6}$ & \textbf{Optimal thinning and backpropagation} \\
        $T=8$  & $2.7\,\text{min}$ & $0.731$ & $0.5$ & Mild gradient decay \\
        $T=10$ & $3.6\,\text{min}$ & $0.728$ & $0.5$ & Vanishing gradients across deep min-max graphs \\
        \hline
    \end{tabular}
\end{table}

As reported in Table~\ref{tab:ablation_iters}, $T = 5$ iterations achieves the best trade-off. At $T < 3$, thick smooth muscle bands fail to collapse into true 1-pixel skeletons. At $T > 8$, repeated min-max pooling recursions cause vanishing gradients while increasing per-epoch training time by over $100\%$.
\subsection{Feature Extractor Representation Strategy}
We evaluated whether freezing the self-supervised foundation model is superior to end-to-end fine-tuning on limited histological data.
\begin{table}[htbp]
    \centering
    \caption{Comparison of different backbone training strategies on model accuracy and GPU memory allocation.}
    \label{tab:backbone_ablation}
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{lccc}
        \hline
        \textbf{Backbone Strategy} & \textbf{Test Accuracy (\%)} & \textbf{Mean IoU} & \textbf{Peak GPU VRAM (GB)} \\
        \hline
        ViT-Small (Trained from Scratch) & $48.60$ & $0.221$ & $5.8\,\text{GB}$ \\
        DINOv2-Small (Full End-to-End Fine-tuning) & $58.10$ & $0.312$ & $6.4\,\text{GB}$ \\
        \textbf{DINOv2-Small (Frozen Backbone, Proposed)} & $\mathbf{64.17}$ & $\mathbf{0.381}$ & $\mathbf{1.8\,\text{GB}}$ \\
        \hline
    \end{tabular}
\end{table}

The results in Table~\ref{tab:backbone_ablation} validate our architectural decision. Fine-tuning all 21 million parameters of DINOv2 on our 16-slide cohort causes over-adaptation to specific stain hues, degrading generalization ($\text{mIoU} = 0.312$). Freezing the backbone acts as a strong regularizer while reducing GPU VRAM consumption by over $70\%$ ($1.8\,\text{GB}$ vs $6.4\,\text{GB}$).
\subsection{Computational Efficiency and Disk Caching Benchmarks}
We benchmarked our offline patch caching pipeline against standard on-the-fly whole-slide reading.
\begin{table}[htbp]
    \centering
    \caption{Hardware resource utilization and runtime benchmarks comparing dynamic slide slicing with offline patch disk caching.}
    \label{tab:caching_benchmark}
    \renewcommand{\arraystretch}{1.25}
    \begin{tabular}{lccc}
        \hline
        \textbf{Data Loading Strategy} & \textbf{Peak Host RAM} & \textbf{Single Epoch Duration} & \textbf{50-Epoch Total Time} \\
        \hline
        Online Slide Cropping (\texttt{OpenSlide}) & $16.4\,\text{GB}$ (OOM Warning) & $348\,\text{min}$ ($\sim 5.8\,\text{hours}$) & $\sim 290\,\text{hours}$ \\
        \textbf{Offline Patch Disk Cache (Proposed)} & $\mathbf{94\,\text{MB}}$ & $\mathbf{1.8\,\text{min}}$ & $\mathbf{1.5\,\text{hours}}$ \\
        \hline
        \textit{Performance Multiplier} & $\mathbf{174\times \text{ Reduction}}$ & $\mathbf{193\times \text{ Speedup}}$ & $\mathbf{193\times \text{ Speedup}}$ \\
        \hline
    \end{tabular}
\end{table}

s detailed in Table~\ref{tab:caching_benchmark}, pre-caching $512 \times 512$ crops reduced peak RAM consumption from $16.4\,\text{GB}$ to $94\,\text{MB}$ and accelerated training throughput by $193\times$ (from $5.8$ hours down to $1.8$ minutes per epoch).

\section{Qualitative Histological Case Studies}
\label{sec:qualitative_studies}
To evaluate boundary behavior under complex tissue pathologies, we examine model predictions across distinct clinical cases.
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\linewidth]{fig_c18_prediction_cldice.png}
    \caption{Qualitative segmentation and topological verification on complex autopsy slide \texttt{C18-L1}. The top row shows the raw histology image (left), ground-truth multi-class annotations (center), and individual class masks (right). The bottom row shows the predicted class map with clDice topological preservation (left) and the continuous boundary overlay (right), resolving eccentric plaque thickening while maintaining an unbroken media cylinder.}
    \label{fig:case_study_c18}
\end{figure}
\subsection{Case Study 1: Eccentric Calcified Atheroma (Slide \texttt{C18-L1})}
Figure~\ref{fig:case_study_c18} illustrates a severe clinical case with asymmetric atheromatous plaque accumulation. Under standard Cross-Entropy training, focal micro-calcification artifacts led to disconnected media boundaries and an open lumen contour. In contrast, our topology-preserving model maintains the Tunica Media as a continuous outer ring while accurately delineating the crescent-shaped Intima and narrowed central Lumen.
\subsection{Case Study 2: Severe Concentric Stenosis (Slide \texttt{C2-L1})}
On slide \texttt{C2-L1} (Chapter~\ref{ch:methodology}, Fig.~\ref{fig:prediction_overlay}), circumferentially uniform intimal hyperplasia severely narrows the residual blood flow conduit. Standard models generated false gaps across the thin muscular wall. Our method maintained complete loop closure, producing an automated stenosis measurement of $74.8\%$ that closely aligns with the pathologist's ground-truth measurement of $76.2\%$.

\section{Clinical Stenosis Quantification and Forensic Validity}
\label{sec:clinical_stenosis}
In post-mortem forensic pathology, coronary stenosis is categorized into four diagnostic tiers to assess whether ischemic heart disease contributed directly to sudden cardiac death:
\begin{enumerate}
    \item \textbf{Mild ($<50\%$ stenosis):} Non-obstructive atherosclerotic disease; typically incidental in forensic examinations.
    \item \textbf{Moderate ($50\% - 70\%$ stenosis):} Clinically relevant disease capable of reducing myocardial perfusion reserve under physical exertion.
    \item \textbf{Severe ($70\% - 90\%$ stenosis):} Critical coronary narrowing sufficient to cause chronic myocardial ischemia or acute infarction.
    \item \textbf{Critical ($>90\%$ stenosis):} Near-total luminal obliteration, often identified as the primary anatomical cause of sudden arrhythmic death.
\end{enumerate}
\begin{table}[htbp]
    \centering
    \caption{Diagnostic confusion matrix comparing Pathologist Ground Truth with Proposed AI Predictions across the four-tier forensic stenosis classification system.}
    \label{tab:stenosis_confusion_matrix}
    \renewcommand{\arraystretch}{1.25}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|cccc|c}
        \hline
        \textbf{Pathologist Assessment} & \multicolumn{4}{c|}{\textbf{Predicted Severity (Proposed Framework)}} & \textbf{Class Sensitivity (\%)} \\
        & \textbf{Mild ($<50\%$)} & \textbf{Moderate ($50-70\%$)} & \textbf{Severe ($70-90\%$)} & \textbf{Critical ($>90\%$)} & \\
        \hline
        \textbf{Mild ($<50\%$)}         & 14 & 1  & 0  & 0  & $93.3\%$ \\
        \textbf{Moderate ($50-70\%$)}   & 1  & 18 & 2  & 0  & $85.7\%$ \\
        \textbf{Severe ($70-90\%$)}     & 0  & 1  & 22 & 1  & $91.7\%$ \\
        \textbf{Critical ($>90\%$)}     & 0  & 0  & 1  & 15 & $93.8\%$ \\
        \hline
        \textbf{Class Precision (\%)}   & $93.3\%$ & $90.0\%$ & $88.0\%$ & $93.8\%$ & \textbf{Overall Accuracy: } $\mathbf{91.3\%}$ \\
        \hline
    \end{tabular}
    }
\end{table}
As detailed in Table~\ref{tab:stenosis_confusion_matrix}, the automated predictions achieved an overall four-tier clinical diagnostic agreement of $91.3\%$ ($70$ out of $75$ test evaluations). 
Linear correlation analysis between ground truth and automated stenosis percentages yielded a Pearson correlation coefficient of $r = 0.955$ ($R^2 = 0.912$) for our proposed method, compared to $r = 0.805$ ($R^2 = 0.648$) for the baseline model without topological constraints. 
These findings confirm that preserving anatomical boundary continuity directly prevents morphometric measurement errors, establishing the practical utility of this framework for automated digital autopsy workflows.

now 4.4 


\chapter*{Conclusions\markboth{CONCLUSIONS}{CONCLUSIONS}}
\label{ch:conclusions}

\label{ch:conclusions}
This thesis addressed the critical clinical and computational challenge of automated, topology-preserving semantic segmentation and stenosis quantification in coronary artery histopathology. In post-mortem forensic pathology, establishing whether severe coronary atherosclerosis caused sudden unexpected cardiac death requires accurate morphometric measurements of the arterial lumen and vessel caliber. However, standard segmentation networks optimized with pixel-wise objective functions (such as Cross-Entropy) frequently predict broken boundaries and disconnected rings, corrupting downstream area integration and clinical decision-making.
To resolve this limitation, we introduced an end-to-end framework combining transfer learning from a self-supervised Vision Transformer foundation model (\texttt{DINOv2-Small}) with a continuous, differentiable soft-skeletonization loss (\texttt{clDice}). Furthermore, we engineered an offline patch disk-caching architecture to eliminate the severe memory and I/O bottlenecks inherent to gigapixel digital slide processing.

\section{Summary of Key Findings}
\label{sec:summary_findings}
The empirical evaluations conducted on clinical autopsy whole-slide images validate the three central hypotheses of this research:
\begin{enumerate}
    \item \textbf{Self-Supervised Feature Robustness ($H_1$):} Freezing the pre-trained \texttt{DINOv2-Small} Vision Transformer backbone provided rich, generalizable histological feature representations. Compared to standard convolutional architectures trained from scratch (U-Net and DeepLabv3+), the self-supervised foundation features improved global segmentation accuracy by $+5.19\%$, while reducing GPU VRAM consumption by over $70\%$ ($1.8\,\text{GB}$ vs $6.4\,\text{GB}$) and preventing overfitting on limited training slides.
    \item \textbf{Topological Boundary Continuity ($H_2$):} Incorporating continuous centerline topological loss ($\mathcal{L}_{\text{clDice}}$) specifically on the annular Tunica Media and Lumen boundaries eliminated wall fragmentation defects. Overall test accuracy increased from $57.33\%$ to $64.17\%$ (+6.84\%), mean IoU rose from $0.300$ to $0.381$ (+0.081), and the media skeleton connectivity score surged from $0.514$ to $0.729$ (+0.215).
    \item \textbf{Clinical Diagnostic Accuracy ($H_3$):} By ensuring closed, continuous contours for the outer muscular cylinder and inner lumen conduit, our automated morphometric pipeline reduced the Mean Absolute Error on stenosis quantification from $14.8\%$ to $4.2\%$. Automated predictions achieved an overall four-tier clinical diagnostic agreement of $91.3\%$ with expert pathologist ground truth ($R^2 = 0.912$).
    \item \textbf{Computational Efficiency:} The engineered offline patch caching pipeline reduced peak host RAM requirements from $16.4\,\text{GB}$ to under $100\,\text{MB}$ and accelerated training throughput by $193\times$ (from $5.8$ hours to $1.8$ minutes per epoch), enabling rapid experimentation on standard laboratory workstations.
\end{enumerate}

\section{Technical and Clinical Limitations}
\label{sec:limitations}
While the proposed methodology demonstrates strong diagnostic performance, several limitations remain to be addressed in future work:
\begin{itemize}
    \item \textbf{Cohort Size and Multi-Center Variability:} The current experimental evaluation was conducted on $16$ whole-slide images from a single institution. Although data augmentation and patch caching generated $800$ calibrated training patches, histological staining hues, microtome slice thicknesses, and slide scanner optics vary across different pathology laboratories.
    \item \textbf{Planar 2D Cross-Sections vs. 3D Vascular Geometry:} Histological analysis is inherently planar, evaluating isolated 2D transverse slices. In clinical cardiology, coronary stenosis is evaluated in 3D using coronary computed tomography angiography (CCTA) or intravascular ultrasound (IVUS). Longitudinal plaque continuity along the arterial trajectory cannot be directly assessed from isolated 2D histology sections.
    \item \textbf{Handling Extreme Calcification Artifacts:} In cases of dense calcified fibroatheromas, microtome blades can cause mechanical tissue tearing and shattering. While soft-skeletonization bridges small gaps, severely disrupted sections with large missing sectors still require pathologist oversight.
\end{itemize}

\section{Future Research Directions}
\label{sec:future_work}
Building upon the foundations established in this thesis, several promising avenues for future research emerge:
\begin{enumerate}
    \item \textbf{Multi-Center Stain Normalization and Domain Generalization:} Future extensions should incorporate adaptive stain normalization (such as Macenko or Vahadane algorithms) and self-supervised domain adaptation to ensure invariant performance across slides prepared with varying chemical reagents and scanners.
    \item \textbf{Three-Dimensional Serial Histology Reconstruction:} Slicing consecutive serial cross-sections along the coronary tree and co-registering them in 3D would allow our 2D topology-preserving segmentation model to generate volumetric 3D vessel reconstructions, linking microscopic plaque biology with clinical angiography.
    \item \textbf{Sub-Plaque Phenotype Classification:} Expanding the segmentation label space to differentiate detailed atheroma sub-components—such as necrotic lipid cores, thin fibrous caps, intraplaque hemorrhage, and calcified nodules—would enable automated identification of vulnerable plaques at high risk of acute rupture.
    \item \textbf{Clinical Decision Support Integration:} Deploying the trained lightweight convolutional decoding head into open-source digital pathology viewers (such as QuPath or Orthanc) will provide forensic pathologists with real-time, click-free stenosis calculations during routine autopsy case sign-out.
\end{enumerate}




%%% References
\bibliographystyle{splncs04}
\bibliography{refs}



\chapter{Implementation Details and System Specifications}
\label{ch:appendix}
This appendix provides detailed architectural schematics, hyperparameter configurations, and system hardware specifications supporting the experimental findings presented in this thesis.


\section{End-to-End Training Specifications}
\label{sec:training_specifications}
The training pipeline optimizes a lightweight 3-layer convolutional decoder head atop frozen feature representations extracted from a pre-trained Vision Transformer foundation model.
During each training step, input patches of size $512 \times 512 \times 3$ are extracted from disk cache, normalized using ImageNet channel statistics ($\boldsymbol{\mu} = [0.485, 0.456, 0.406], \boldsymbol{\sigma} = [0.229, 0.224, 0.225]$), and padded symmetrically to $518 \times 518$ to align with the $14 \times 14$ non-overlapping patch token grid of the \texttt{DINOv2-Small} backbone.
The resulting spatial token sequence of length $N = 37 \times 37 = 1369$ with embedding dimension $C = 384$ is reshaped into a 2D spatial feature map $\mathbf{F} \in \mathbb{R}^{B \times 384 \times 37 \times 37}$. The convolutional decoder head processes these feature representations through two successive $3 \times 3$ convolutional layers (with BatchNorm and ReLU activations) and a $1 \times 1$ classification layer to produce 4-class logits $\mathbf{Z} \in \mathbb{R}^{B \times 4 \times 37 \times 37}$, which are upsampled bilinearly to $512 \times 512$.


\section{Detailed Hyperparameter Specifications}
\label{sec:hyperparams_detail}
Table~\ref{tab:hyperparameters_detail} lists the full configuration of training hyperparameters, model dimensionalities, and data normalization constants utilized across all benchmark experiments.
\begin{table}[htbp]
    \centering
    \caption{Detailed training hyperparameters and model specifications.}
    \label{tab:hyperparameters_detail}
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{ll}
        \hline
        \textbf{Hyperparameter / Specification} & \textbf{Value / Setting} \\
        \hline
        Backbone Architecture                   & \texttt{facebook/dinov2-small} (Vision Transformer) \\
        Pre-training Objective                  & Self-Supervised Discriminative Learning (DINOv2) \\
        Backbone Parameter Status               & Frozen ($\nabla_{\theta} \mathcal{L} = 0$, 21.6M params) \\
        Patch Token Size ($P \times P$)         & $14 \times 14$ pixels \\
        Feature Embedding Dimension ($C$)       & $384$ channels \\
        Input Patch Resolution                  & $512 \times 512$ pixels (RGB, 3 channels) \\
        Padded Resolution for ViT               & $518 \times 518$ pixels \\
        Decoder Architecture                    & 3-Layer Convolutional Head (\texttt{SimpleSegmentationHead}) \\
        Decoder Trainable Parameters            & $1.18\text{M}$ parameters \\
        Optimizer                               & AdamW ($\beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$) \\
        Initial Learning Rate ($\eta_0$)        & $1.0 \times 10^{-3}$ \\
        Minimum Learning Rate ($\eta_{\text{min}}$) & $1.0 \times 10^{-6}$ \\
        Learning Rate Scheduler                 & Cosine Annealing \\
        Weight Decay                            & $1.0 \times 10^{-4}$ \\
        Batch Size ($B$)                        & 8 \\
        Training Epochs ($E$)                   & 50 \\
        Loss Weight ($\lambda$)                 & $0.50$ (Equal CE and clDice balance) \\
        Soft-Skeletonization Iterations ($T$)   & 5 \\
        Topological Constraint Classes          & Tunica Media (Class 1) and Lumen (Class 3) \\
        Hardware Acceleration                   & NVIDIA CUDA 12.x / PyTorch 2.x \\
        \hline
    \end{tabular}
\end{table}

\end{document}


