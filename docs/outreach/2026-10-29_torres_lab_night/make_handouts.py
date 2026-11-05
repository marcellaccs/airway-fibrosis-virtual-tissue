"""Assemble the printable handout PDF (US Letter, landscape) for the Torres Lab night.

usage: python make_handouts.py <outreach dir> <scratch dir> <analysis png> <out pdf>
"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

outreach, scratch, analysis_png, out = sys.argv[1:5]
W, H = 11, 8.5
_n = [0]
def _preview(fig):
    d = os.environ.get("HANDOUT_PREVIEW")
    if d:
        os.makedirs(d, exist_ok=True); _n[0] += 1; fig.savefig(os.path.join(d, f"page_{_n[0]:02d}.png"), dpi=70)


def image_page(pdf, path, title, caption, credit=None):
    fig = plt.figure(figsize=(W, H))
    fig.text(0.04, 0.955, title, fontsize=15, weight="bold", va="top")
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    top = 0.90; bottom = 0.14 if caption else 0.06
    avail_h = top - bottom; avail_w = 0.92
    scale = min(avail_w / (iw / W), avail_h / (ih / H))
    w = scale * iw / W; h = scale * ih / H
    ax = fig.add_axes([0.04 + (avail_w - w) / 2, top - h, w, h])
    ax.imshow(im); ax.axis("off")
    if caption:
        fig.text(0.04, 0.115, caption, fontsize=9.5, va="top", wrap=True, linespacing=1.4)
    if credit:
        fig.text(0.04, 0.025, credit, fontsize=8, color="#555555")
    fig.text(0.96, 0.025, "The Torres Lab, University of Richmond, 2026-10-29", fontsize=8, color="#555555", ha="right")
    pdf.savefig(fig); _preview(fig); plt.close(fig)


def text_page(pdf, title, blocks):
    fig = plt.figure(figsize=(W, H))
    fig.text(0.05, 0.95, title, fontsize=16, weight="bold", va="top")
    y = 0.90
    for head, body in blocks:
        fig.text(0.05, y, head, fontsize=12.5, weight="bold", va="top", color="#14213d"); y -= 0.034
        fig.text(0.05, y, body, fontsize=10.5, va="top", linespacing=1.45); y -= 0.022 + 0.026 * (body.count("\n") + 1)
    fig.text(0.96, 0.025, "The Torres Lab, University of Richmond, 2026-10-29", fontsize=8, color="#555555", ha="right")
    pdf.savefig(fig); _preview(fig); plt.close(fig)


with PdfPages(out) as pdf:
    text_page(pdf, "The Torres Lab in one page", [
        ("The problem", "About 2.7 billion people cook and heat with wood and other biomass; wood smoke is the leading COPD risk\nfactor among them, and wildfire smoke now brings the same exposure to cities. The damage starts in the small\nairways, where repeated injury turns a repair response into permanent scarring (subepithelial fibrosis)."),
        ("The biology chain we model", "Smoke lands on the airway lining  ->  epithelial cells are injured and release cytokines  ->  macrophages respond,\nfirst a 'fight' state (M1) then a 'repair' state (M2)  ->  repeated exposure keeps the repair signal (TGF-beta) on  ->\nfibroblasts become myofibroblasts  ->  collagen accumulates under the lining, the wall thickens, the airway narrows."),
        ("Chapter 1 (2019-2024): equations", "Nine quantities (healthy and damaged epithelium, macrophage states, two cytokine pools) and nine rates of change,\neach term one arrow in the chain above, each rate a number with units from cell-culture measurements.\nBakry, Brashear, Brashear, Jones & Torres (2024), Journal of Theoretical Biology."),
        ("Chapter 2 (2025-now): a virtual tissue", "A 250 x 125 micrometre slice of airway wall in CompuCell3D: cells are clusters of pixels that push, stick and\nfollow chemical gradients; the equations from Chapter 1 run inside and set the injury. 1 pixel = 1.25 um,\n1 step = 62.4 s, 20,000 steps = 14 days. Every parameter is a published measurement or labelled 'free'."),
        ("The question for the 2027 paper", "Same total injury, different arrangement (one patch vs scattered cells): does the scar come out different?\nThe test: Ripley's K on the collagen pattern separates focal from diffuse while total collagen does not."),
        ("What a student does here", "Turn a paper into a number with units and a confidence. Decide which of two conflicting studies the model should\ntrust. Run the equations in Tellurium, change one parameter, explain what happened in biological words.\nDesign the ELISA that would pin a free parameter. Present a poster. Ask of every claim: compared to what, measured how?"),
    ])
    image_page(pdf, os.path.join(outreach, "figures", "model_schematic_2026-10-28.png"),
               "The virtual tissue as it runs today (state at 2026-10-27)",
               "Left: the tissue layer, four bands from the airway lumen (top) to the fixed outer wall (bottom), with the two chemical fields. Right: the "
               "ordinary-differential-equation layer (the published immune-response model) and the three quantities it hands to the tissue every step. "
               "Nothing is written back: the tissue reads the immune model as a set of near-constant inputs.")
    image_page(pdf, os.path.join(outreach, "figures", "model_schematic_target_2026-10-29.png"),
               "The model the 2027 paper will use (roadmap revision 2026-10-29)",
               "Additions in teal, each behind a switch: a spatial pro-inflammatory field with three consumers, an MMP (collagen-digesting enzyme) field, and collagen as "
               "volume-occupying objects. The focal-vs-diffuse experiment is run with each loop off and on, so the result is a table of which mechanisms carry or erase pattern dependence.")
    image_page(pdf, analysis_png,
               "Proposed analysis: the same measurements on a real section and on the virtual tissue",
               "Top: Masson's trichrome sections of rat small airways after 7 months (Zou et al. 2014, PLoS ONE 9:e96708, Fig. 4, CC BY 4.0) with a 60 um band around the lumen, "
               "trichrome-blue collagen in the band (collagen area fraction) and wall thickness along rays. Bottom: the same two readouts on the final model frame, and Ripley's K on "
               "myofibroblast centres against random placement. The overlays demonstrate the method on a published figure; they are not a re-analysis of that study.")
    image_page(pdf, os.path.join(outreach, "histology", "zou2014_fig4_masson_trichrome_collagen_control_vs_woodsmoke.png"),
               "Real tissue: collagen builds up around small airways after months of smoke",
               "Rat small airways after 7 months of exposure: control, cigarette smoke, wood smoke. Top row Masson's trichrome (collagen blue); bottom row immunostaining for type I collagen (brown); "
               "(g, h) quantification. This is the blue ring the model's amber 'collagen burden' stands for.",
               "Zou et al. 2014, PLoS ONE 9:e96708, Fig. 4, doi:10.1371/journal.pone.0096708 (CC BY 4.0)")
    image_page(pdf, os.path.join(outreach, "histology", "higham2019_fig2_COPD_bronchiole_masson_trichrome_and_HE.png"),
               "Real tissue: human COPD small airways",
               "(A) Masson's trichrome: a COPD bronchiole with a thick fibrotic wall of blue collagen bundles under the epithelium. (B) H&E: a mucus plug in the lumen. (C) goblet-cell hyperplasia. "
               "(D) inflammatory cells in the wall. Human COPD small airways narrow by roughly 22%; the model currently reaches about 2.5%, a gap we list as a limitation and a question.",
               "Higham, Quinn, Cancado & Singh 2019, Respir Res 20:49, Fig. 2, doi:10.1186/s12931-019-1017-y (CC BY 4.0)")
    image_page(pdf, os.path.join(outreach, "histology", "hsieh2023_fig1_HE_nonasthmatic_vs_asthmatic_airway_subepithelial_fibrosis.png"),
               "Real tissue: a labelled section showing sub-epithelial fibrosis (asthma)",
               "H&E of a non-asthmatic and a fatal-asthma human airway. Not a smoke lesion, but the clearest labelled picture of the layer the model simulates: the arrow marked sub-epithelial fibrosis.",
               "Hsieh, Assadinia & Hackett 2023, Front Physiol 14:1113100, Fig. 1, doi:10.3389/fphys.2023.1113100 (CC BY 4.0)")
    for name, title in [("model_still_day0.png", "Model frame: day 0"), ("model_still_day2.png", "Model frame: day 2"), ("model_still_day14.png", "Model frame: day 14")]:
        p = os.path.join(scratch, "stills", name)
        if os.path.exists(p):
            image_page(pdf, p, title, "Left: cells (green healthy epithelium, orange damaged, blue fibroblasts, purple myofibroblasts, amber collagen burden). Right: the growth-factor field the fibroblasts climb. Lumen at top; 1 px = 1.25 um; 1 step = 62.4 s.")
print("wrote", out)
