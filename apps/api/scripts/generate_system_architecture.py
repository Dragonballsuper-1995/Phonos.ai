"""
generate_system_architecture.py
================================
Generates high-resolution, sleek dark-themed System Architecture Diagram matching
modern GitHub Dark / Obsidian UI aesthetic with high-visibility arrows and typography.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(12, 13.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background canvas: Deep Obsidian / GitHub Dark
    bg_color = '#0D1117'
    box_bg = '#161B22'
    border_color = '#30363D'
    box_border = '#388BFD'
    accent_blue = '#58A6FF'
    text_title = '#FFFFFF'
    text_sub = '#8B949E'
    arrow_color = '#58A6FF'

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Outer container border
    outer = patches.FancyBboxPatch(
        (2.5, 2.5), 95, 95,
        boxstyle='round,pad=0,rounding_size=1.5',
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.8
    )
    ax.add_patch(outer)

    def draw_box(x, y, w, h, title, subtitle='', highlight=False):
        edge = '#58A6FF' if highlight else '#30363D'
        fill = '#1C2128' if highlight else box_bg
        bx = patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle='round,pad=0.2,rounding_size=0.8',
            facecolor=fill,
            edgecolor=edge,
            linewidth=1.6
        )
        ax.add_patch(bx)
        if subtitle:
            ax.text(x, y + h*0.15, title, ha='center', va='center', fontsize=11, fontweight='bold', color=text_title, family='sans-serif')
            ax.text(x, y - h*0.20, subtitle, ha='center', va='center', fontsize=8.8, color=text_sub, family='sans-serif')
        else:
            ax.text(x, y, title, ha='center', va='center', fontsize=10.8, fontweight='bold', color=text_title, family='sans-serif')

    def draw_straight_arrow(x1, y1, x2, y2):
        ax.annotate(
            '', xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(facecolor=arrow_color, edgecolor=arrow_color, arrowstyle='->,head_width=0.35,head_length=0.35', lw=1.6)
        )

    def draw_elbow_arrow(points):
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            if i == len(points) - 2:
                ax.annotate(
                    '', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor=arrow_color, edgecolor=arrow_color, arrowstyle='->,head_width=0.35,head_length=0.35', lw=1.6)
                )
            else:
                ax.plot([x1, x2], [y1, y2], color=arrow_color, lw=1.6)

    # 1. Top Input
    draw_box(50, 93, 38, 5.5, 'User Query & Intent Inputs', 'Persona  |  Budget (₹)  |  5D Priority Sliders  |  Natural Intent', highlight=True)

    # 2. Stage 1 Retrieval
    draw_box(50, 81.5, 62, 6.2, 'Stage 1: Candidate Retrieval & Shielding', 'Knowledge Graph Defect Purging  |  India Catalogue Filter  |  Dynamic Budget Floor')
    draw_straight_arrow(50, 90.25, 50, 84.6)

    # 3. Two Parallel Branches
    draw_box(27, 68.5, 38, 6.2, 'Semantic & Spec Embedding Branch', 'all-MiniLM-L6-v2 Query  +  5D Hardware Vector Space')
    draw_box(73, 68.5, 38, 6.2, 'Aspect Sentiment Analysis Branch', 'Pattern 2 Gated ABSA  +  YouTube Review Aspect Store')

    draw_elbow_arrow([(50, 78.4), (50, 74.5), (27, 74.5), (27, 71.6)])
    draw_elbow_arrow([(50, 78.4), (50, 74.5), (73, 74.5), (73, 71.6)])

    # 4. Intermediate Embeddings
    draw_box(27, 56.5, 34, 5.5, '5D Hardware Spec Vectors', 'L2-Normalized BLOBs (soc, cam, disp, bat, bld)')
    draw_straight_arrow(27, 65.4, 27, 59.25)

    draw_box(73, 56.5, 34, 5.5, 'Domain Utility Sentiment Modulators', 'Aspect Scaling: Domain * (1.0 + 0.10 * ABSA)')
    draw_straight_arrow(73, 65.4, 73, 59.25)

    # 5. Fusion Aligner
    draw_box(50, 44.5, 58, 6.0, 'Feature Aligner & Canonical Matrix', '7-Feature Matrix: [persona, budget_ratio, price_ratio, bat_norm, ram_norm, hz_norm, tier]')
    draw_elbow_arrow([(27, 53.75), (27, 49.5), (50, 49.5), (50, 47.5)])
    draw_elbow_arrow([(73, 53.75), (73, 49.5), (50, 49.5), (50, 47.5)])

    # 6. Stage 2 Machine Learning Ranker
    draw_box(50, 32.5, 62, 6.2, 'Stage 2: 2-Stage DLRM Ranking Engine', 'Pre-Trained XGBoost (ranker.xgb)  +  25-Pt Bonus Cap  +  Brand Diversity Filter', highlight=True)
    draw_straight_arrow(50, 41.5, 50, 35.6)

    # 7. Two Output Prediction Heads
    draw_box(26.5, 19.5, 39, 6.2, 'Top-5 Ranked Recommendations', 'Calibrated Match Scores (50-99%)  +  Match Reasons & Trade-offs')
    draw_box(73.5, 19.5, 39, 6.2, '5D Hardware Spec Clones', 'Similar Spec Alternatives (/phones/{name}/similar)  +  Dual Compare')

    draw_elbow_arrow([(50, 29.4), (50, 25.5), (26.5, 25.5), (26.5, 22.6)])
    draw_elbow_arrow([(50, 29.4), (50, 25.5), (73.5, 25.5), (73.5, 22.6)])

    # 8. Bottom Client Presentation & RLHF Loop
    draw_box(50, 7.5, 72, 6.2, 'Presentation & Closed-Loop RLHF Feedback', 'Next.js Typographic Accordion & Deep Report  <--->  PostHog Telemetry & Retrainer', highlight=True)
    draw_elbow_arrow([(26.5, 16.4), (26.5, 12.5), (50, 12.5), (50, 10.6)])
    draw_elbow_arrow([(73.5, 16.4), (73.5, 12.5), (50, 12.5), (50, 10.6)])

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor=bg_color, bbox_inches='tight')
    plt.close()
    print(f'Successfully generated dark theme diagram: {output_path}')

if __name__ == '__main__':
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    out_file = os.path.join(root_dir, 'screenshots', 'system_architecture.png')
    generate_diagram(out_file)

