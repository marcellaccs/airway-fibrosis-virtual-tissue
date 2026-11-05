// Rebuilds "The Torres Lab" deck (18 slides) as an editable PowerPoint file.
// usage: node build_deck.js <scratch dir> <repo dir> <out.pptx>
const pptxgen = require("pptxgenjs");
const path = require("path");
const [S, R, OUT] = process.argv.slice(2);

const NAVY = "14213D", OFF = "FBFAF6", GREY = "EEF2F6", CARD = "FFFFFF", LINE = "D9DDE3",
      ORANGE = "E76F51", AMBER = "F4A261", BODY = "4A5568", MUTED = "6A7179", BLUE = "1F4E79",
      ICE = "BFD0E6", DARKCARD = "1F2F52", PURPLE = "8E44AD";
const HEAD = "Cambria", TEXT = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "The Torres Lab";
pres.author = "Marcella Torres";
pres.theme = { headFontFace: HEAD, bodyFontFace: TEXT };

const img = (p) => path.join(S, p);
const rimg = (p) => path.join(R, p);

function eyebrow(s, text, dark = false) {
  s.addText(text.toUpperCase(), { x: 0.6, y: 0.45, w: 12.1, h: 0.35, fontFace: TEXT, fontSize: 11, bold: true, color: dark ? AMBER : ORANGE, charSpacing: 3, isTextBox: true, margin: 0 });
}
function title(s, text, dark = false, size = 30) {
  s.addText(text, { x: 0.6, y: 0.85, w: 12.1, h: 1.3, fontFace: HEAD, fontSize: size, bold: true, color: dark ? OFF : NAVY, valign: "top", isTextBox: true, margin: 0 });
}
function footer(s, text, dark = false) {
  s.addText(text, { x: 0.6, y: 6.95, w: 12.1, h: 0.35, fontFace: TEXT, fontSize: 10, color: dark ? ICE : MUTED, isTextBox: true, margin: 0 });
}
function card(s, x, y, w, h, opts = {}) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: opts.fill || CARD }, line: { color: opts.line || LINE, width: 0.75 } });
}
function para(s, x, y, w, h, text, o = {}) {
  s.addText(text, Object.assign({ x, y, w, h, fontFace: TEXT, fontSize: 13, color: BODY, valign: "top", isTextBox: true, margin: 0 }, o));
}

// ---------- sections ----------
pres.addSection({ title: "Why" });
pres.addSection({ title: "The first model" });
pres.addSection({ title: "The virtual tissue" });
pres.addSection({ title: "Now and next" });

// 1 cover
{
  const s = pres.addSlide({ sectionTitle: "Why" });
  s.background = { color: NAVY };
  s.addImage({ path: img("photos/photo_1_2400.jpg"), x: 7.2, y: 0, w: 6.13, h: 7.5, sizing: { type: "cover", w: 6.13, h: 7.5 } });
  s.addText("THE TORRES LAB", { x: 0.7, y: 1.2, w: 6.2, h: 0.4, fontFace: TEXT, fontSize: 12, bold: true, color: AMBER, charSpacing: 3, isTextBox: true, margin: 0 });
  s.addText("Mathematical models of how the lung responds to smoke", { x: 0.7, y: 1.7, w: 6.2, h: 2.4, fontFace: HEAD, fontSize: 36, bold: true, color: OFF, valign: "top", isTextBox: true, margin: 0 });
  s.addText("From equations for immune cells to a virtual airway wall that remodels itself", { x: 0.7, y: 4.2, w: 6.2, h: 0.9, fontFace: TEXT, fontSize: 15, color: ICE, valign: "top", isTextBox: true, margin: 0 });
  s.addText("Marcella Torres\nDepartment of Mathematics & Statistics, University of Richmond", { x: 0.7, y: 6.1, w: 6.2, h: 0.9, fontFace: TEXT, fontSize: 13, color: OFF, valign: "bottom", isTextBox: true, margin: 0 });
  s.addNotes("Welcome. Tonight is a tour of one research program: how a math department ends up studying lung disease, and what students actually do in it. The iPads around the room are running the current model live.");
}

// 2 motivation
{
  const s = pres.addSlide({ sectionTitle: "Why" });
  s.background = { color: OFF };
  eyebrow(s, "Why smoke, why the lung");
  title(s, "Smoke in the small airways is a global problem that is getting closer to home");
  const cards = [["2.7 billion", "people cook and heat with wood and other biomass fuels, breathing the smoke indoors every day"],
                 ["COPD", "Wood smoke is the leading risk factor for chronic obstructive pulmonary disease in those households, and it attacks the small airways first"],
                 ["Wildfires", "Climate change now brings weeks of wood-smoke air to cities that never had it, so the same biology matters here"]];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.35, 3.9, 2.9);
    s.addText(c[0], { x: x + 0.3, y: 2.55, w: 3.3, h: 0.9, fontFace: HEAD, fontSize: 34, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    para(s, x + 0.3, 3.5, 3.3, 1.6, c[1], { fontSize: 13 });
  });
  para(s, 0.6, 5.55, 12.1, 1.0, [{ text: "Remodeling", options: { bold: true } }, { text: " is the step that turns reversible inflammation into permanent structural disease. That step is what the lab studies." }], { fontSize: 16, color: NAVY });
  footer(s, "Sources: Bennitt et al. 2025; Zhao et al. 2018; Ortiz-Quintero et al. 2022");
  s.addNotes("Start with the people, not the equations. Biomass smoke exposure is one of the largest environmental health burdens on earth, and the lesion it produces sits in the small airways, the part of the lung we model. Wildfire smoke makes this a local story too.");
}

// 3 biology
{
  const s = pres.addSlide({ sectionTitle: "Why" });
  s.background = { color: OFF };
  eyebrow(s, "The biology, in one line");
  title(s, "Injury, then a repair response that never switches off");
  const steps = [["1 · Exposure", "Smoke particles land on the airway lining (the epithelium)"],
                 ["2 · Injury", "Epithelial cells are damaged and release alarm signals (cytokines)"],
                 ["3 · Immune response", "Macrophages arrive: first a “fight” state (M1), then a “repair” state (M2)"],
                 ["4 · Repair stuck on", "Repeated exposure keeps the repair signal (TGF-β) high; fibroblasts turn into myofibroblasts"],
                 ["5 · Remodeling", "Collagen piles up under the lining; the wall thickens and the airway narrows"]];
  const cw = 2.2, gap = 0.27, y = 2.3, h = 2.5;
  steps.forEach((st, i) => {
    const x = 0.6 + i * (cw + gap);
    const last = i === 4;
    card(s, x, y, cw, h, { fill: last ? NAVY : CARD, line: last ? NAVY : LINE });
    s.addText(st[0], { x: x + 0.2, y: y + 0.2, w: cw - 0.4, h: 0.4, fontFace: TEXT, fontSize: 12, bold: true, color: last ? AMBER : ORANGE, isTextBox: true, margin: 0 });
    para(s, x + 0.2, y + 0.65, cw - 0.4, h - 0.8, st[1], { fontSize: 12.5, color: last ? OFF : NAVY });
    if (i < 4) s.addShape(pres.ShapeType.rightArrow, { x: x + cw + 0.02, y: y + 1.05, w: 0.24, h: 0.32, fill: { color: "9AA5B1" }, line: { color: "9AA5B1", width: 0 } });
  });
  para(s, 0.6, 5.1, 12.1, 1.3, "Every step is measurable in a lab: cytokines by ELISA, myofibroblasts by α-SMA staining, collagen by trichrome or picrosirius red, narrowing by morphometry. Those measurements are the raw material of the models.", { fontSize: 15, color: NAVY });
  footer(s, "Biomass-smoke COPD is macrophage-dominated with little emphysema, which is why the model has macrophages and no neutrophils (Zhao et al. 2018)");
  s.addNotes("For a biology audience, this chain is familiar. The point to land: each arrow is a rate, and each box is a quantity. That is all a differential equation is.");
}

// 4 math-bio
{
  const s = pres.addSlide({ sectionTitle: "Why" });
  s.background = { color: NAVY };
  eyebrow(s, "Where the math comes in", true);
  title(s, "A model is a hypothesis you can run", true);
  const cols = [["Observe", "Biology supplies the players and the rules: which cells, which signals, who responds to whom, and the numbers (how fast, how far, how many)"],
                ["Formalize", "Each rule becomes a rate of change (an equation) or a rule a simulated cell follows. Vague words like “drives” and “promotes” have to become specific"],
                ["Predict and test", "Run it. Compare the output to real measurements. When it disagrees, the model tells you exactly which assumption to go back and check"]];
  cols.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.3, 3.9, 3.1, { fill: DARKCARD, line: DARKCARD });
    s.addText(c[0], { x: x + 0.3, y: 2.5, w: 3.3, h: 0.6, fontFace: HEAD, fontSize: 22, bold: true, color: OFF, isTextBox: true, margin: 0 });
    para(s, x + 0.3, 3.2, 3.3, 2.1, c[1], { fontSize: 13.5, color: ICE });
  });
  para(s, 0.6, 5.7, 12.1, 1.0, "The loop runs both ways: biology constrains the math, and the math says which experiment would be most informative to do next.", { fontSize: 16, color: OFF });
  s.addNotes("This is the slide that answers why a mathematician studies lungs. The two-way loop is the honest version: we take numbers from the literature and the lab, and we hand back a ranked list of which measurements would change the model's answer.");
}

// 5 ode-model
{
  const s = pres.addSlide({ sectionTitle: "The first model" });
  s.background = { color: OFF };
  eyebrow(s, "Chapter 1 · 2019 to 2024 · the published model");
  title(s, "Nine quantities, nine rates of change: the immune response as differential equations");
  card(s, 0.6, 2.3, 5.6, 3.3);
  s.addImage({ path: img("drive_exports/jtb_fig1_s1.png"), x: 0.75, y: 2.4, w: 5.3, h: 3.1, sizing: { type: "contain", w: 5.3, h: 3.1 } });
  para(s, 6.6, 2.3, 6.1, 1.0, "The model tracks healthy and damaged epithelium, macrophages in their fight and repair states (recruited and resident), and two cytokine pools: pro-inflammatory and anti-inflammatory.", { fontSize: 13.5 });
  card(s, 6.6, 3.4, 6.1, 1.55, { fill: NAVY, line: NAVY });
  s.addText("dD/dt = e₃·WS·H − e₄(1 + e₈·M2 + e₉·A)·D − e₂·D", { x: 6.85, y: 3.5, w: 5.6, h: 0.5, fontFace: HEAD, fontSize: 17, color: OFF, isTextBox: true, margin: 0 });
  para(s, 6.85, 4.05, 5.6, 0.85, "D = damaged epithelium, H = healthy. Damaged cells appear when smoke (WS) hits healthy cells, and are repaired faster when repair-state macrophages (M2) and anti-inflammatory signal (A) are present", { fontSize: 11.5, color: ICE });
  para(s, 6.6, 5.1, 6.1, 0.9, "Every e and m is a number with units, taken from or fitted to cell-culture measurements. “Smoke” is a schedule: three one-hour cooking fires a day.", { fontSize: 13 });
  footer(s, "Bakry, Brashear, Brashear, Jones & Torres (2024), Journal of Theoretical Biology. Jones: the biology collaborator; the Brashears: former undergraduates.");
  s.addNotes("Read the equation in words, not symbols. Each term is one arrow from the biology slide. The audience should see that writing it down forced us to decide: does repair depend on macrophages, on cytokines, or both?");
}

// 6 ode-results
{
  const s = pres.addSlide({ sectionTitle: "The first model" });
  s.background = { color: OFF };
  eyebrow(s, "What the equations predict");
  title(s, "Fight first, then repair: the model reproduces the timing of the immune switch");
  card(s, 0.6, 2.3, 5.6, 4.5);
  s.addImage({ path: img("drive_exports/jtb_fig2_panelsABC.png"), x: 0.7, y: 2.4, w: 5.4, h: 4.3, sizing: { type: "contain", w: 5.4, h: 4.3 } });
  const rows = [["Top row", "Healthy epithelium drops when the fires start and partly recovers; damaged epithelium rises and settles."],
                ["Middle row", "M1 “fight” macrophages peak within the first day or two and fade; M2 “repair” macrophages climb afterwards and stay."],
                ["Bottom row", "The pro-inflammatory pool spikes early; the anti-inflammatory pool rises slowly and stays high. That persistent repair state is the seed of fibrosis."]];
  rows.forEach((r, i) => {
    const y = 2.3 + i * 1.25;
    s.addText(r[0], { x: 6.6, y, w: 6.1, h: 0.35, fontFace: TEXT, fontSize: 14, bold: true, color: BLUE, isTextBox: true, margin: 0 });
    para(s, 6.6, y + 0.38, 6.1, 0.85, r[1], { fontSize: 13 });
  });
  para(s, 6.6, 6.05, 6.1, 0.8, "Grey: hundreds of runs with the parameters jittered; black: the median. The spread is the honest statement of what we do not know.", { fontSize: 12.5, color: MUTED });
  footer(s, "Torres et al. 2024, Fig. 2. Submodels were calibrated to cytokine measurements in cultured macrophages and epithelial cells.");
  s.addNotes("Three rows, six quantities, 200 hours. Point at the M1 peak then the M2 rise: that is the fight-then-repair switch. The grey band is a Latin hypercube over the parameters.");
}

// 7 students
{
  const s = pres.addSlide({ sectionTitle: "The first model" });
  s.background = { color: GREY };
  eyebrow(s, "Summer 2025 · the team that set up the virtual tissue");
  title(s, "Undergraduates did the biology homework the model is built on");
  s.addImage({ path: img("photos/photo_1_2400.jpg"), x: 0.6, y: 2.3, w: 6.0, h: 3.7, sizing: { type: "cover", w: 6.0, h: 3.7 } });
  para(s, 6.9, 2.3, 5.8, 0.7, "Six undergraduate researchers, summer 2025", { fontSize: 13 });
  s.addText([{ text: "Learned Python and ran the published model in Tellurium", options: { bullet: true, breakLine: true } },
             { text: "Read the fibrosis literature and wrote the model’s assumptions, each with its evidence", options: { bullet: true, breakLine: true } },
             { text: "Presented posters at the Arts & Sciences Symposium", options: { bullet: true } }],
            { x: 6.9, y: 3.05, w: 5.8, h: 1.5, fontFace: TEXT, fontSize: 13, color: NAVY, valign: "top", paraSpaceAfter: 4, isTextBox: true, margin: 0 });
  card(s, 6.9, 4.65, 5.8, 1.35);
  s.addText("Three assumptions that students identified and that shaped the model", { x: 7.1, y: 4.75, w: 5.4, h: 0.35, fontFace: TEXT, fontSize: 12, bold: true, color: ORANGE, isTextBox: true, margin: 0 });
  para(s, 7.1, 5.12, 5.4, 0.85, "Stationary vs mobile sources of growth factor · latent vs active TGF-β · stiffness-driven feedback", { fontSize: 12 });
  footer(s, "No one on this team had coded before May. Reading papers carefully was the job that mattered most.");
  s.addNotes("Point at the chalkboard photo. The three named assumptions are literally cited by name in the model documentation. That is the recruiting message: a bio or chem student's reading is a contribution.");
}

// 8 why-space
{
  const s = pres.addSlide({ sectionTitle: "The virtual tissue" });
  s.background = { color: OFF };
  eyebrow(s, "Chapter 2 · 2025 to now · the virtual tissue");
  title(s, "The equations assume everything is well mixed. Real injury has a pattern.");
  [["Focal injury", "why-space_0.png", "Four damaged cells side by side. One strong, concentrated growth-factor source. Fibroblasts converge on one spot."],
   ["Diffuse injury", "why-space_1.png", "The same four damaged cells, spread out. Four weak sources. Fibroblasts are pulled in four directions."]].forEach((c, i) => {
    const x = 0.6 + i * 6.2;
    card(s, x, 2.3, 5.9, 2.9);
    s.addText(c[0], { x: x + 0.3, y: 2.45, w: 5.3, h: 0.45, fontFace: HEAD, fontSize: 20, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addImage({ path: img("pptx/svg/" + c[1]), x: x + 0.3, y: 2.95, w: 5.3, h: 0.88 });
    para(s, x + 0.3, 3.95, 5.3, 1.1, c[2], { fontSize: 13 });
  });
  para(s, 0.6, 5.5, 12.1, 1.3, [{ text: "The question the lab is now asking: ", options: { bold: true } }, { text: "same total amount of injury, different arrangement. Does the scar that forms come out different? An equation with no space in it cannot even ask this. A spatial model can." }], { fontSize: 16, color: NAVY });
  s.addNotes("This is the research question for the 2027 paper, stated for a general audience. Everything in the virtual tissue is built so that this one comparison is fair: same immune drive, same amount of damage, only the pattern differs.");
}

// 9 cpm
{
  const s = pres.addSlide({ sectionTitle: "The virtual tissue" });
  s.background = { color: OFF };
  eyebrow(s, "How a virtual tissue works");
  title(s, "Cells as blobs of pixels that push, stick and follow chemical trails");
  s.addImage({ path: img("pptx/svg/cpm_0.png"), x: 0.6, y: 2.4, w: 4.6, h: 3.22 });
  const rows = [["Each cell is a cluster of pixels on a grid", "It wants a target size and shape, and it sticks to some neighbours more than others."],
                ["The computer tries to flip one boundary pixel at a time", "The move is kept if it lowers the cell’s “effort” (stretch and adhesion), and sometimes kept anyway, a little randomness, like thermal jiggling. Millions of tries make cells crawl, round up and sort."],
                ["Chemicals diffuse on the same grid", "A cell can read the concentration at its own edge and prefer moves that go uphill: that is chemotaxis."],
                ["Then rules on top", "“If the growth factor here is above a threshold, start converting to a myofibroblast.” The equations from Chapter 1 run inside the same program and set the signals."]];
  rows.forEach((r, i) => {
    const y = 2.3 + i * 1.1;
    s.addText(r[0], { x: 5.6, y, w: 7.1, h: 0.32, fontFace: TEXT, fontSize: 13.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    para(s, 5.6, y + 0.34, 7.1, 0.75, r[1], { fontSize: 12 });
  });
  footer(s, "This is the Cellular Potts model, run in CompuCell3D (open source, Indiana University). The same “minimize effort” idea describes how soap bubbles find their shape.");
  s.addNotes("Keep this physical: pixels, stickiness, a random nudge. Chemistry students know Monte Carlo from statistical mechanics; biology students know chemotaxis. Both are in this one picture.");
}

// 10 virtual-airway
{
  const s = pres.addSlide({ sectionTitle: "The virtual tissue" });
  s.background = { color: OFF };
  eyebrow(s, "The virtual airway wall");
  title(s, "A slice of the small-airway wall, 250 µm wide, that remodels itself over two weeks");
  const x0 = 0.6, y0 = 2.3, w = 6.9, h = 4.03;
  s.addImage({ path: img("pptx/svg/virtual-airway_0.png"), x: x0, y: y0, w, h });
  const lab = (t, x, y, ww, hh, o = {}) => s.addText(t, Object.assign({ x, y, w: ww, h: hh, fontFace: TEXT, fontSize: 10.5, color: NAVY, isTextBox: true, margin: 0, valign: "top" }, o));
  lab("Airway lumen (air). Readout: how much of it is lost.", x0 + 0.1, y0 + 0.08, 5, 0.3, { bold: true, color: BLUE });
  lab("Epithelium: 25 cells of 10 µm; green healthy, orange damaged. Damaged cells leak growth factor (the orange glow).", x0 + 0.1, y0 + 0.62, 6.7, 0.3, { fontSize: 9.5 });
  lab("Subepithelium: fibroblasts (blue) crawl up the gradient, convert to myofibroblasts (purple) near the damage and lay down collagen (amber), which pushes the lining upward.", x0 + 3.4, y0 + 2.15, 3.4, 0.9);
  lab("Fixed outer wall: growth can only go inward.", x0 + 0.1, y0 + 3.77, 5, 0.25, { bold: true, color: OFF });
  const tbl = [[{ text: "Model quantity", options: { bold: true, fill: { color: GREY } } }, { text: "Real-world value", options: { bold: true, fill: { color: GREY } } }],
               ["1 pixel", "1.25 µm"], ["Grid", "200 × 100 px = 250 × 125 µm"], ["1 time step", "62.4 seconds"], ["20,000 steps", "14.4 days"], ["Starting cells", "25 epithelial, 11 fibroblasts"]];
  s.addTable(tbl, { x: 7.8, y: 2.3, w: 4.9, colW: [2.1, 2.8], fontFace: TEXT, fontSize: 11.5, color: NAVY, border: { type: "solid", color: LINE, pt: 0.75 }, rowH: 0.34, margin: 0.05 });
  card(s, 7.8, 4.55, 4.9, 1.75, { fill: NAVY, line: NAVY });
  s.addText("Chapter 1 runs inside Chapter 2", { x: 8.0, y: 4.65, w: 4.5, h: 0.35, fontFace: TEXT, fontSize: 12, bold: true, color: AMBER, isTextBox: true, margin: 0 });
  para(s, 8.0, 5.02, 4.5, 1.2, "The immune-response equations run live inside the tissue and set three things every step: the fraction of cells that are damaged, how fast they repair, and the baseline level of repair signal.", { fontSize: 11.5, color: ICE });
  s.addNotes("Walk top to bottom. Then the table: the point is that every model number is a real number with a unit, and the ODE from the first paper is not thrown away, it is the engine under the hood.");
}

// 11 numbers
{
  const s = pres.addSlide({ sectionTitle: "The virtual tissue" });
  s.background = { color: GREY };
  eyebrow(s, "Math and biology, concretely");
  title(s, "Every number in the model is a biology measurement");
  const hdr = (t) => ({ text: t, options: { bold: true, color: OFF, fill: { color: NAVY } } });
  const rows = [[hdr("What biologists measured"), hdr("Source"), hdr("What it becomes in the model")],
    ["Small-airway epithelial cell is about 10 µm wide and tall", "Devalia 1990; Mariassy 1984", "Each epithelial cell is 8 × 8 pixels, so 1 pixel = 1.25 µm"],
    ["Lung fibroblasts crawl at about 10.7 µm per hour", "Tisler 2020", "One simulation step = 62.4 seconds"],
    ["Fibroblasts double about every 30 hours", "Mio 1992; Holz 2004", "A fibroblast may divide every 1,730 steps"],
    ["About 2.2 epithelial cells per fibroblast in the airway wall", "Zajicek 1992", "25 epithelial cells and 11 fibroblasts at the start"],
    ["Damaged epithelium makes about twice the cytokine of healthy epithelium", "JTB model, from cell culture", "Damaged cells are stronger signal sources"],
    ["Airway-on-a-chip smoke experiments run 15 days", "Bennet 2026 (UBC)", "A run is 20,000 steps = 14.4 days, so outputs can be compared"]];
  s.addTable(rows, { x: 0.6, y: 2.25, w: 12.1, colW: [5.4, 2.4, 4.3], fontFace: TEXT, fontSize: 11.5, color: NAVY, fill: { color: CARD }, border: { type: "solid", color: LINE, pt: 0.75 }, rowH: 0.36, margin: 0.05, valign: "middle" });
  para(s, 0.6, 5.95, 12.1, 1.0, [{ text: "Where no measurement exists, the parameter is labelled " }, { text: "free", options: { bold: true } }, { text: ", and that label is a to-do list: it is exactly the assay we ask a biology lab to run next (ELISAs for TGF-β, IL-6, α-SMA and collagen in fibroblasts and epithelial cells)." }], { fontSize: 14.5, color: NAVY });
  s.addNotes("This is the slide for the chem and bio students in the room. Each row is a paper someone read closely. The free parameters are the reason we are talking to wet labs: the model generates the experiment list.");
}

// 12 in-action
{
  const s = pres.addSlide({ sectionTitle: "The virtual tissue" });
  s.background = { color: OFF };
  eyebrow(s, "The model in action · live on the iPads");
  title(s, "Fourteen days in the virtual airway: fibroblasts find the damage, convert, and build the scar");
  [["Day 0", "day0", "11 fibroblasts, intact lining, no signal"], ["Day 2", "day2", "damaged cells leak signal; fibroblasts arrive and convert"], ["Day 14", "day14", "45 myofibroblasts, collagen rings, lumen −6.5%"]].forEach((r, i) => {
    const x = 0.6 + i * 4.1, w = 3.6, h = 1.8;
    s.addText(r[0], { x, y: 2.15, w, h: 0.35, fontFace: TEXT, fontSize: 15, bold: true, color: BLUE, isTextBox: true, margin: 0 });
    s.addImage({ path: img("stills/" + r[1] + "_cells.png"), x, y: 2.5, w, h });
    s.addImage({ path: img("stills/" + r[1] + "_field.png"), x, y: 2.5 + h + 0.1, w, h });
    para(s, x, 2.5 + 2 * h + 0.18, w, 0.4, r[2], { fontSize: 11, color: MUTED });
  });
  s.addText("Top row: cells (green healthy, orange damaged, blue fibroblast, purple myofibroblast, amber collagen). Bottom row: the growth-factor field the fibroblasts climb, pale to dark red. Lumen at the top; 1 px = 1.25 µm. The iPads show all 400 frames on a loop.", { x: 0.6, y: 6.75, w: 12.1, h: 0.55, fontFace: TEXT, fontSize: 10, color: MUTED, valign: "top", isTextBox: true, margin: 0 });
  s.addNotes("Point at the iPads. Narrate the three rows: nothing, then the gradient appears under damaged cells and the blue cells arrive, then the purple clusters with the amber collagen push the lining up. The counts in the frame headers are computed from the same lattice the picture is drawn from.");
}

// 13 measure
{
  const s = pres.addSlide({ sectionTitle: "The virtual tissue" });
  s.background = { color: OFF };
  eyebrow(s, "Proposed analysis");
  title(s, "The same four measurements on a microscope slide and on the simulation");
  const mk = (x, head, color, items, dark) => {
    card(s, x, 2.3, 3.9, 3.4, dark ? { fill: NAVY, line: NAVY } : {});
    s.addText(head, { x: x + 0.25, y: 2.45, w: 3.4, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true, color, isTextBox: true, margin: 0 });
    s.addText(items.map((t, i) => ({ text: t, options: { bullet: !dark, breakLine: i < items.length - 1 } })), { x: x + 0.25, y: 2.95, w: 3.4, h: 2.6, fontFace: TEXT, fontSize: 12, color: dark ? ICE : BODY, valign: "top", paraSpaceAfter: 5, isTextBox: true, margin: 0 });
  };
  mk(0.6, "In real tissue", BLUE, ["Wall thickness: distance from the lining to the outer wall, measured on H&E sections", "Collagen area fraction: the share of the wall that stains blue (trichrome) or red (picrosirius)", "Myofibroblast density: α-SMA-positive cells per area under the epithelium", "Lumen narrowing: airway cross-section area, healthy vs exposed"]);
  mk(4.7, "In the simulation", PURPLE, ["Wall thickness: rows from the outer wall to the epithelial sheet", "Collagen area fraction: pixels of collagen over pixels of subepithelium", "Myofibroblast density: purple cells per area", "Lumen narrowing: empty pixels above the sheet, day 14 vs day 0"]);
  mk(8.8, "The new statistic: pattern", AMBER, ["Ripley’s K asks, for every distance r, whether collagen patches are more clustered than chance. Focal injury should give a clustered curve, diffuse injury a flat one, even when total collagen is the same.", "That is the pre-registered test for the 2027 paper: pass if K separates while area fraction does not."], true);
  para(s, 0.6, 5.95, 12.1, 0.9, "Computing the same statistic on both is what makes a simulation falsifiable. The printouts on the table show these measurements drawn on a real section and on a model frame.", { fontSize: 14, color: NAVY });
  s.addNotes("The handout version of this slide has the overlays. If a student asks how you would know the model is wrong, this is the answer: same numbers, same definitions, on both.");
}

// 14 histology
{
  const s = pres.addSlide({ sectionTitle: "The virtual tissue" });
  s.background = { color: OFF };
  eyebrow(s, "What the real thing looks like");
  title(s, "Collagen (blue) piles up under the airway lining after months of wood smoke");
  s.addImage({ path: img("zou2014_fig4_trichrome_row.png"), x: 0.6, y: 2.2, w: 8.0, h: 1.67 });
  para(s, 0.6, 3.92, 8.0, 0.6, "Rat small airways after 7 months: control, cigarette smoke, wood smoke. Masson’s trichrome stains collagen blue. The model’s amber “collagen burden” is this blue ring. Zou et al. 2014, PLoS ONE, Fig. 4 (CC BY 4.0).", { fontSize: 10.5 });
  s.addImage({ path: img("higham2019_fig2A_COPD_trichrome_crop.png"), x: 8.9, y: 2.2, w: 3.8, h: 1.67, sizing: { type: "cover", w: 3.8, h: 1.67 } });
  para(s, 8.9, 3.92, 3.8, 0.7, "Human COPD bronchiole: dense collagen bundles under the epithelium. Higham et al. 2019, Respir Res, Fig. 2A (CC BY 4.0).", { fontSize: 10.5 });
  s.addImage({ path: img("histology_images/hsieh2023_fig1_HE_nonasthmatic_vs_asthmatic_airway_subepithelial_fibrosis.png"), x: 0.6, y: 4.65, w: 5.6, h: 2.2, sizing: { type: "contain", w: 5.6, h: 2.2 } });
  para(s, 6.5, 4.65, 6.2, 1.0, "A labelled example of airway-wall remodeling (asthma, not smoke): the arrow marked sub-epithelial fibrosis points at exactly the layer the virtual tissue simulates. Hsieh, Assadinia & Hackett 2023, Front Physiol, Fig. 1 (CC BY 4.0).", { fontSize: 11.5 });
  para(s, 6.5, 5.75, 6.2, 1.1, [{ text: "What the pathologist measures", options: { bold: true } }, { text: " on slides like these: wall thickness, the fraction of the wall that is collagen, myofibroblasts per area, and how much lumen is left. The next slide shows the same list for the model." }], { fontSize: 12, color: NAVY });
  s.addNotes("Orient the audience: lumen is the white hole, the lining is the dark rim, blue is collagen. Then point out that in the model the amber tint under the sheet is the same thing. The asthma panel is there only because it is the clearest labelled picture of the lesion.");
}

// 15 status
{
  const s = pres.addSlide({ sectionTitle: "Now and next" });
  s.background = { color: OFF };
  eyebrow(s, "Where it stands · October 2026");
  title(s, "A working virtual airway with a reproducible baseline, and an honest gap");
  [["−2.5%", "mean lumen narrowing after 14 simulated days, six replicate runs (range −0.3% to −4.2%)"],
   ["11 → 42–62", "fibroblast-lineage cells at day 0 and day 14: recruitment, division and conversion all happen"],
   ["6 of 6", "runs kept the epithelial sheet intact with no collagen leaking into the airway: the tissue behaves like tissue"]].forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.3, 3.9, 2.2);
    s.addText(c[0], { x: x + 0.3, y: 2.45, w: 3.3, h: 0.8, fontFace: HEAD, fontSize: 32, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    para(s, x + 0.3, 3.3, 3.3, 1.1, c[1], { fontSize: 12.5 });
  });
  [["A finding on the way", BLUE, "Seeding 80 fibroblasts instead of the measured 11 gave five times more narrowing. The starting cell count, a number from a 1992 anatomy paper, controls the outcome more than any rate does."],
   ["An honest gap", ORANGE, "Human COPD small airways narrow by roughly 22%. The model is about nine times short. That gap is now a listed limitation and a question: which missing mechanism closes it?"]].forEach((c, i) => {
    const x = 0.6 + i * 6.2;
    card(s, x, 4.8, 5.9, 1.9, { fill: GREY, line: GREY });
    s.addText(c[0], { x: x + 0.3, y: 4.92, w: 5.3, h: 0.35, fontFace: TEXT, fontSize: 13, bold: true, color: c[1], isTextBox: true, margin: 0 });
    para(s, x + 0.3, 5.3, 5.3, 1.3, c[2], { fontSize: 12.5 });
  });
  s.addNotes("Numbers from the Gate B rebaseline on 2026-10-27. Say the gap out loud: students should hear that a model being wrong by a known amount is progress, because it names the next experiment.");
}

// 16 next
{
  const s = pres.addSlide({ sectionTitle: "Now and next" });
  s.background = { color: OFF };
  eyebrow(s, "Next steps · November 2026 to May 2027");
  title(s, "Add the feedback loops, run the focal-vs-diffuse experiment, write the paper");
  const cols = [["Nov to Dec · build", "Three new ingredients", ["A spatial pro-inflammatory signal (IL-6-like) that slows repair near a damaged patch and speeds fibroblast division", "An enzyme field (MMP) that digests collagen: the only brake in the model", "Collagen as objects that take up space, so the lining is pushed by matrix, as in tissue"], false],
                ["Jan to Feb · the experiment", "Focal vs diffuse, as an ablation", ["Same total damage, same immune drive, only the pattern differs", "Run with each loop switched off and on, six replicates each", "Pass: the pattern statistic separates while total collagen does not"], false],
                ["In parallel · wet lab", "Pin the free numbers", ["Epithelial cells + smoke extract: TGF-β, IL-6, IL-8, LDH by ELISA", "Fibroblasts + TGF-β: α-SMA and collagen output over 3 days", "Each assay maps to one model parameter and gets a model figure back"], false],
                ["Feb to May · write", "Frontiers in Immunology", ["Research topic on epithelial-immune interactions in the lung, deadline 15 May 2027", "Reaching out to the UBC airway-on-a-chip group, whose device runs the same exposure in real cells"], true]];
  cols.forEach((c, i) => {
    const x = 0.6 + i * 3.08, w = 2.9, dark = c[3];
    card(s, x, 2.3, w, 4.4, dark ? { fill: NAVY, line: NAVY } : {});
    s.addText(c[0], { x: x + 0.22, y: 2.42, w: w - 0.44, h: 0.3, fontFace: TEXT, fontSize: 11, bold: true, color: dark ? AMBER : ORANGE, isTextBox: true, margin: 0 });
    s.addText(c[1], { x: x + 0.22, y: 2.75, w: w - 0.44, h: 0.6, fontFace: HEAD, fontSize: 15, bold: true, color: dark ? OFF : NAVY, valign: "top", isTextBox: true, margin: 0 });
    s.addText(c[2].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < c[2].length - 1 } })), { x: x + 0.22, y: 3.4, w: w - 0.44, h: 3.2, fontFace: TEXT, fontSize: 11.5, color: dark ? ICE : BODY, valign: "top", paraSpaceAfter: 5, isTextBox: true, margin: 0 });
  });
  s.addNotes("The roadmap from 2026-10-29. Note for the audience that the wet-lab column is where chemistry and biology students plug in directly.");
}

// 17 join
{
  const s = pres.addSlide({ sectionTitle: "Now and next" });
  s.background = { color: GREY };
  eyebrow(s, "What a student actually does");
  title(s, "You do not need to be a math major. You need to read carefully and ask “how much, how fast?”");
  s.addImage({ path: img("photos/photo_0_2400.jpg"), x: 0.6, y: 2.3, w: 5.0, h: 4.0, sizing: { type: "cover", w: 5.0, h: 4.0 } });
  [["Biology and chemistry students", "Turn a paper into a number with units and a confidence. Decide which of two conflicting studies the model should trust. Design the ELISA that would settle it."],
   ["Anyone willing to learn a little Python", "Run the equations in Tellurium, change one parameter, explain what happened in biological words. Then run the virtual tissue and watch it."],
   ["What you leave with", "A symposium poster, your name on an assumption in the model record, and a habit of asking any biology claim: compared to what, and measured how?"]].forEach((r, i) => {
    const y = 2.3 + i * 1.4;
    s.addText(r[0], { x: 6.0, y, w: 6.7, h: 0.35, fontFace: TEXT, fontSize: 14.5, bold: true, color: BLUE, isTextBox: true, margin: 0 });
    para(s, 6.0, y + 0.38, 6.7, 0.95, r[1], { fontSize: 13 });
  });
  footer(s, "Summer research, independent study, or a journal club seat. Ask me tonight.");
  s.addNotes("End on the invitation. The photo is the 2025 team presenting in week 3. Emphasize that the literature work is real research, not a warm-up.");
}

// 18 thanks
{
  const s = pres.addSlide({ sectionTitle: "Now and next" });
  s.background = { color: NAVY };
  s.addText("THANK YOU", { x: 0.7, y: 1.3, w: 12, h: 0.4, fontFace: TEXT, fontSize: 12, bold: true, color: AMBER, charSpacing: 3, isTextBox: true, margin: 0 });
  s.addText("The model is running on the iPads. Come watch a scar form and ask it questions.", { x: 0.7, y: 1.8, w: 11.5, h: 1.9, fontFace: HEAD, fontSize: 34, bold: true, color: OFF, valign: "top", isTextBox: true, margin: 0 });
  s.addText("People", { x: 0.7, y: 4.2, w: 5.6, h: 0.35, fontFace: TEXT, fontSize: 13, bold: true, color: AMBER, isTextBox: true, margin: 0 });
  para(s, 0.7, 4.55, 5.6, 1.3, "Summer 2025 team · Jacob and Emma Brashear, Bakry (JTB co-authors) · Dr. Jones (biology) · CompuCell3D community (Indiana University)", { fontSize: 13, color: ICE });
  s.addText("Read more", { x: 6.9, y: 4.2, w: 5.8, h: 0.35, fontFace: TEXT, fontSize: 13, bold: true, color: AMBER, isTextBox: true, margin: 0 });
  para(s, 6.9, 4.55, 5.8, 1.3, "Bakry et al. 2024, J. Theor. Biol. · Zou et al. 2014, PLoS ONE · Higham et al. 2019, Respir. Res. · Swat et al. 2012 (CompuCell3D)", { fontSize: 13, color: ICE });
  s.addText("Marcella Torres · Department of Mathematics & Statistics, University of Richmond", { x: 0.7, y: 6.3, w: 12, h: 0.4, fontFace: TEXT, fontSize: 13, color: ICE, isTextBox: true, margin: 0 });
  s.addNotes("Leave this up during the open floor.");
}

pres.writeFile({ fileName: OUT }).then((f) => console.log("wrote", f));
