# Day 3: Wound Healing Biology & Tissue Fluidity

> **Series**: 30-Day Interview Preparation Guide for scRNA-seq Wound Healing Project
> **Time**: ~3 hours of focused reading
> **Prerequisites**: Day 1 (Project Overview), Day 2 (scRNA-seq Technology)
> **Goal**: After today, you can explain wound healing biology, the 10 cell types in your data, and the tissue fluidity concept with enough depth to satisfy a biology-trained interviewer — even without a biology background.

---

## Why This Day Matters

Days 1 and 2 gave you the computational context: what the project does and how the data is generated. Today we go the other direction — **the biology**. This is the day where you stop being "someone who runs a pipeline" and start being "someone who understands wound healing."

In interviews for bioinformatics positions, you will face questions like:

- "Walk me through wound healing and how your data captures it."
- "What is tissue fluidity and why does it matter?"
- "Why did you pick these specific gene signatures?"
- "What do you expect to see in fibroblasts at day 7 versus day 14?"

If you cannot answer these confidently, the interviewer concludes that you treated the biology as a black box. Today we open that box.

---

## 1. Wound Healing — The Four Phases

### 1.1 Context: Why Wound Healing Is Worth Studying

**Skin is the largest organ in the body.** In a mouse, it accounts for about 12–15% of body weight. In a human, skin covers roughly 1.7 square metres. It is the primary barrier between you and the environment — bacteria, UV radiation, temperature, mechanical damage.

When that barrier breaks, the organism has a problem. Every second that a wound remains open is an opportunity for infection, fluid loss, and tissue damage. Evolution has produced an extraordinary multi-phase repair programme that involves dozens of cell types, hundreds of signalling molecules, and a precise timeline.

**When wound healing goes wrong**, the consequences are severe:

| Failure mode | What happens | Clinical example |
|---|---|---|
| **Too slow** | Wound stays open, infections | Diabetic foot ulcers, pressure sores |
| **Too much inflammation** | Tissue destruction, chronic wounds | Venous leg ulcers |
| **Too much fibrosis** | Excessive scar tissue | Keloids, hypertrophic scars |
| **Too little remodelling** | Dysfunctional scar | Contracture scars after burns |

Our project captures the **normal** healing process in controlled conditions (healthy, genetically identical mice). By understanding what "normal" looks like at single-cell resolution, we can eventually identify what goes wrong in disease.

### 1.2 Overview of the Four Phases

Wound healing is classically divided into four overlapping phases. This is critical — **they overlap in time**. A clean boundary between phases does not exist in biology, but the division is useful for understanding.

```
TIME ═══════════════════════════════════════════════════════════════════►

Phase 1       Phase 2             Phase 3                    Phase 4
HEMOSTASIS    INFLAMMATION        PROLIFERATION              REMODELLING
(min–hours)   (hours–days)        (days–weeks)               (weeks–months)

    ┃              ┃                    ┃                        ┃
    ▼              ▼                    ▼                        ▼
 Clotting      Immune cells         New tissue growth        Scar maturation
 Platelet      clear debris         ECM deposition           Collagen
 plug forms    and bacteria         Angiogenesis             crosslinking

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            ▲               ▲                 ▲                 ▲
         (not in          wound_3d          wound_7d          wound_14d
         our data)      (we capture)     (we capture)       (we capture)
```

### 1.3 Phase 1: Hemostasis (Minutes to Hours)

**What happens**: The moment skin is cut, blood vessels are severed. The body's first priority is to stop the bleeding.

1. **Vasoconstriction** — blood vessels near the wound clamp shut to slow blood flow.
2. **Platelet aggregation** — platelets (small cell fragments in blood) rush to the site and stick together, forming a **platelet plug**. Think of it like a plumber jamming a temporary cork into a leaking pipe.
3. **Coagulation cascade** — a complex chain of blood proteins converts fibrinogen into **fibrin**, which weaves a mesh around the platelet plug. This mesh hardens into a **blood clot** (the scab you see on a cut).
4. **Provisional matrix** — the clot is not just a plug. It also serves as a temporary scaffold that cells will later use as a highway to crawl into the wound.

**Analogy**: Hemostasis is like the emergency response after a water main breaks. First, you shut off the valve (vasoconstriction). Then you stuff rags into the hole (platelet plug). Then you apply quick-setting cement (fibrin clot). The cement also provides a surface for repair crews to walk on later (provisional matrix).

**Key molecules**: Thrombin, fibrinogen, fibrin, platelet-derived growth factors (including *Pdgfa*, which is in our wound_signals set). Platelets are the first cells to release *Tgfb1* and *Pdgfa* — chemical alarms that summon immune cells and fibroblasts.

**In our dataset**: Hemostasis happens within minutes. Our earliest wound time point is **3 days**. By that time, hemostasis is long complete. **We do not capture this phase directly**, but its legacy (the fibrin clot, the released growth factors) sets the stage for everything that follows.

---

### 1.4 Phase 2: Inflammation (Hours to Days 3–5) → Our `wound_3d` Condition

**What happens**: Once bleeding is controlled, the immune system launches a coordinated assault to clean up damage and fight infection.

This phase has two waves:

#### Wave 1: Neutrophils (the "first responders")

Neutrophils are the most abundant white blood cell in the body. They arrive at the wound within **hours** of injury, recruited by chemical signals called chemokines.

**What neutrophils do**:
- **Kill bacteria** — using reactive oxygen species (ROS), a chemical "bleach" that destroys microbes
- **Release proteases** — enzymes like elastase and *Mmp9* that break down damaged tissue
- **Form NETs** (Neutrophil Extracellular Traps) — they literally explode their own DNA into a web that traps bacteria
- **Die** — neutrophils are short-lived (hours to days). Their corpses form the yellowish fluid we know as pus

**Neutrophil markers in our data**: *S100a8*, *S100a9*, *Ly6g*
- *S100a8/S100a9* — calcium-binding proteins released during inflammation. These form a dimer called calprotectin, which is antimicrobial and also serves as a "danger signal" to recruit more immune cells. They are among the most highly expressed genes in neutrophils.
- *Ly6g* — a surface protein almost exclusively on neutrophils. It is the gold-standard marker for identifying neutrophils in mouse data.

#### Wave 2: Macrophages (the "foremen")

Macrophages arrive slightly later (24–48 hours). They are arguably the most important cell type in wound healing because they serve as both **cleaners** and **coordinators**.

**What macrophages do**:
- **Phagocytosis** — literally eat dead cells, debris, bacteria, and spent neutrophils. They are the garbage trucks.
- **Release growth factors** — *Tgfb1*, *Pdgfa*, *Vegfa* — signals that recruit fibroblasts, trigger angiogenesis, and initiate the proliferative phase
- **Polarise** — macrophages can switch between pro-inflammatory (M1) and pro-healing (M2) states. At day 3, most macrophages are M1 (killing mode). By day 7, they transition to M2 (healing mode). This switch is CRITICAL — if M1→M2 transition fails, the wound becomes chronic.

**Macrophage markers in our data**: *Cd68*, *Adgre1*, *Csf1r*, *Mrc1*
- *Cd68* — lysosomal protein, one of the most used pan-macrophage markers
- *Adgre1* (also known as F4/80) — surface glycoprotein, another classic macrophage marker in mouse
- *Csf1r* — colony-stimulating factor 1 receptor. Macrophages depend on this receptor for survival
- *Mrc1* (CD206) — more specific to M2/healing-type macrophages. Seeing *Mrc1* go up between wound_3d and wound_7d would be evidence of M1→M2 switching

**Key inflammatory signals from our gene set**:
- *Il6* (Interleukin-6) — a major pro-inflammatory cytokine. Elevated in acute inflammation. Tells the body "there is danger here."
- *Tnf* (Tumor Necrosis Factor) — another powerful pro-inflammatory signal. Activates endothelial cells to make blood vessels "leaky" so immune cells can exit the bloodstream and reach the wound.
- *Tgfb1* (Transforming Growth Factor beta 1) — released early by platelets and macrophages. At this stage it is primarily pro-inflammatory, but later it will switch to pro-fibrotic. *Tgfb1* is a master multi-tasker.

**What to expect in our `wound_3d` data**:
- **HIGH** proportion of neutrophils (they flood the wound area)
- **HIGH** proportion of macrophages (rapidly recruited)
- **LOW** proportion of keratinocytes and fibroblasts (relative — they are displaced/destroyed at the wound site)
- **HIGH** expression of *Il6*, *Tnf*, *Tgfb1* in immune cells
- **HIGH** expression of *S100a8*/*S100a9* (neutrophil alarm proteins)
- **Rising** EMT scores at the wound edge (keratinocytes starting to loosen for later migration)

**Why inflammation matters for tissue fluidity**: For immune cells to reach the wound, they must **squeeze through tissue**. Neutrophils and macrophages actively degrade ECM to move. This degradation begins the process of making the tissue more "fluid." The inflammatory phase is the **trigger** that initiates the solid→fluid transition.

---

### 1.5 Phase 3: Proliferation (Days 3–14) → Our `wound_7d` Condition

**What happens**: This is the constructive phase — the wound goes from "cleaned but empty" to "filled with new tissue." Four major processes occur simultaneously:

#### Process 1: Fibroblast proliferation and ECM deposition

**Fibroblasts** — the "construction workers" of the body — are recruited to the wound by *Pdgfa* and *Tgfb1*. They migrate from the surrounding dermis into the wound bed and begin doing two things:

1. **Proliferate** — divide rapidly to increase their numbers
2. **Deposit new ECM** — secrete collagen (*Col1a1*, *Col3a1*), fibronectin (*Fn1*), and other extracellular matrix proteins

At this stage, fibroblasts primarily secrete **type III collagen** (*Col3a1*), which is thinner and more flexible than type I (*Col1a1*). Think of it as building a temporary structure with plywood before upgrading to brick.

**Fibroblast markers in our data**: *Col1a1*, *Col3a1*, *Dcn*, *Pdgfra*
- *Col1a1* — type I collagen, the most abundant protein in the body
- *Col3a1* — type III collagen, the "emergency collagen" laid down first in wounds
- *Dcn* (Decorin) — a proteoglycan that binds to collagen and regulates its assembly
- *Pdgfra* — PDGF receptor alpha, the receptor for the recruitment signal *Pdgfa*

#### Process 2: Myofibroblast differentiation and wound contraction

Some fibroblasts undergo a dramatic transformation: they differentiate into **myofibroblasts** — hybrid cells that combine the collagen-producing ability of a fibroblast with the contractile ability of a muscle cell.

**What myofibroblasts do**:
- **Contract the wound** — they pull the wound edges together, physically shrinking the wound. This is why wounds get smaller over time even before new skin covers them.
- **Produce massive amounts of ECM** — especially collagen. Myofibroblasts are ECM-production machines.
- **Generate mechanical tension** — their contractile force reorganises the surrounding tissue.

**The key signal**: *Tgfb1* drives fibroblast→myofibroblast differentiation. This is one of the most important transitions in wound healing. Too few myofibroblasts = wound stays open. Too many = fibrosis/scarring.

**Myofibroblast markers in our data**: *Acta2*, *Tagln*, *Cnn1*, *Postn*
- *Acta2* (α-SMA, alpha smooth muscle actin) — THE defining marker. When a fibroblast starts expressing *Acta2*, it has become a myofibroblast. This is like a construction worker putting on a hard hat — it means they are now doing heavy structural work.
- *Tagln* (SM22α) — another smooth muscle protein, co-expressed with *Acta2*
- *Cnn1* (Calponin) — regulates smooth muscle contraction
- *Postn* (Periostin) — a matricellular protein that promotes cell migration and ECM organisation. Very specific to active wound myofibroblasts.

**Analogy**: If fibroblasts are construction workers, myofibroblasts are forklift operators — they do the heavy lifting (contraction) while also building (ECM deposition). They arrive when the construction project gets serious.

#### Process 3: Re-epithelialisation (keratinocyte migration)

While fibroblasts and myofibroblasts fill the wound from below, **keratinocytes** migrate from the wound edges to cover it from above.

**How it works**:
1. Basal keratinocytes at the wound edge **undergo partial EMT** — they loosen their connections to neighbours (downregulate *Cdh1*/E-cadherin) and gain motility (upregulate *Vim*/Vimentin)
2. They crawl across the provisional matrix (the fibrin clot from Phase 1)
3. Once they meet keratinocytes migrating from the other side, they stop and re-form the epithelial sheets
4. Then they differentiate, re-establishing the layered epidermis

This is one of the clearest examples of tissue fluidity in our data: keratinocytes must temporarily become "fluid" (mobile) to close the wound, then become "solid" (stationary) again once it is closed.

#### Process 4: Angiogenesis (new blood vessels)

New tissue needs blood supply. **Endothelial cells** sprout from existing blood vessels near the wound and grow into the new tissue, forming a network of new capillaries.

**Key signal**: *Vegfa* (Vascular Endothelial Growth Factor A) — the "build blood vessels here" signal. Macrophages are the primary source of *Vegfa* at this stage. It is in our wound_signals gene set.

**Endothelial markers in our data**: *Pecam1*, *Cdh5*, *Kdr*
- *Pecam1* (CD31) — the classic endothelial marker, found on cell-cell junctions between endothelial cells
- *Cdh5* (VE-cadherin) — vascular endothelial cadherin, the "glue" between endothelial cells
- *Kdr* (VEGFR2) — the receptor for *Vegfa*. When *Kdr* is active, the cell is responding to the "build vessels" signal.

**What to expect in our `wound_7d` data**:
- **HIGHEST** proportion of fibroblasts and myofibroblasts (they are the dominant cell type in the wound bed)
- **HIGH** expression of ECM genes (*Col1a1*, *Col3a1*, *Fn1*)
- **Appearance of myofibroblasts** — a cluster expressing *Acta2*/*Tagln*/*Postn* that was absent or minimal in control
- **Active re-epithelialisation** — keratinocytes at the wound edge showing EMT markers
- **Rising** endothelial cells due to angiogenesis
- **PEAK tissue fluidity** — maximum cell migration + ECM remodelling happening simultaneously
- **HIGH** expression of ECM remodelling genes (*Mmp2*, *Mmp14*, *Fn1*) in fibroblasts
- **HIGH** mechanotransduction scores — cells at the wound edge are experiencing massive mechanical forces
- **Macrophage polarisation shift** — proportion of M2 (*Mrc1*-high) macrophages increasing

**Why proliferation is the fluidity peak**: This phase has the most migration (keratinocytes crawling, fibroblasts invading, endothelial cells sprouting, macrophages infiltrating), the most ECM turnover (simultaneous degradation and deposition), and the strongest mechanical forces (myofibroblast contraction). All five of our fluidity gene categories should peak here.

---

### 1.6 Phase 4: Remodelling (Weeks 2 onwards) → Our `wound_14d` Condition

**What happens**: The wound is closed, new tissue is in place, but it is immature and disorganised. The remodelling phase is about **upgrading the temporary repair to a durable structure**.

#### Key events:

**1. Collagen maturation**: Type III collagen (*Col3a1*) is gradually replaced by type I collagen (*Col1a1*). Type I is thicker, stronger, and more organised. The ratio of Col3:Col1 shifts from roughly 30:70 (normal skin) → 50:50 (active wound) → back toward 30:70 (healed).

**2. Collagen crosslinking**: Lysyl oxidases (*Lox*, *Loxl2* — both in our ECM gene set) crosslink collagen fibres. This is like welding steel beams together: each individual beam is strong, but crosslinking makes the structure rigid.

**3. Myofibroblast apoptosis**: Once their job is done, myofibroblasts undergo programmed cell death (apoptosis). This is essential. If myofibroblasts persist, they continue contracting tissue and depositing collagen → **fibrosis and scarring**. One of the big questions in wound healing is: what signals tell myofibroblasts to die?

**4. Tissue stiffening**: As collagen is crosslinked and reorganised, the tissue becomes stiffer again. Mechanotransduction genes respond: *Yap1* activity shifts, *Piezo1* senses increasing stiffness.

**5. Scar vs. regeneration**: In most adult mammals (including mice and humans), the outcome is a **scar** — tissue that is functional but not identical to the original. The scar has:
- No hair follicles
- No sebaceous glands
- Altered collagen architecture (parallel fibres instead of the basket-weave pattern of normal dermis)
- Reduced strength (~80% of original at best)

Some organisms (like axolotls, or neonatal mice) can regenerate perfectly — no scar. Understanding why adult wound healing produces scars instead of regeneration is a major research frontier.

**What to expect in our `wound_14d` data**:
- **Declining** myofibroblast proportions (apoptosis underway)
- **Decreasing** immune cell proportions (inflammation resolving)
- **Rising** differentiated keratinocyte proportions (epithelium maturing)
- **Increasing** *Col1a1:Col3a1* ratio in fibroblasts
- **Increasing** *Lox*/*Loxl2* expression (crosslinking activity)
- **Increasing** *Timp1* expression (MMP activity being curtailed — demolition phase is ending)
- **Declining** fluidity scores — tissue is resolidifying
- Cell proportions trending **back toward control** but not identical (scar tissue has a different cellular composition than normal skin)

**Analogy**: Remodelling is like the final phase of a construction project. The building is standing (wound is closed), but now the temporary scaffolding is removed, the rough finishes are smoothed, the wiring is tested, and the inspectors (immune cells) gradually sign off and leave. The building works, but it is not quite the same as the original.

---

### 1.7 Summary: Phases Mapped to Our Conditions

| Phase | Time | Our condition | Key cells | Key genes | Fluidity |
|---|---|---|---|---|---|
| Hemostasis | min–hrs | Not captured | Platelets | Thrombin, fibrinogen | N/A |
| Inflammation | hrs–3d | `wound_3d` | Neutrophils, macrophages | *Il6*, *Tnf*, *S100a8*, *Tgfb1* | Rising |
| Proliferation | 3–14d | `wound_7d` | Fibroblasts, myofibroblasts, keratinocytes | *Acta2*, *Col1a1*, *Mmp2*, *Vegfa* | **PEAK** |
| Remodelling | 2wk+ | `wound_14d` | Fibroblasts (mature), keratinocytes | *Lox*, *Loxl2*, *Timp1*, *Col1a1* | Declining |

```
TISSUE FLUIDITY OVER TIME

Fluidity
  ▲
  │
  │               ╭────╮
  │              ╱      ╲
  │            ╱          ╲
  │          ╱              ╲
  │        ╱                  ╲
  │      ╱                      ╲──────
  │────╱
  │
  └──────┬──────┬──────┬──────┬──────► Time
       control  3d     7d     14d
       (solid) (rising)(PEAK)  (re-solidifying)
```

---

## 2. The 10 Cell Types in Our Data

Our analysis identifies 10 cell types from skin tissue. For each, you need to understand: (a) what the cell does, (b) its marker genes, (c) what changes across our conditions, and (d) a real-world analogy.

All marker genes are defined in `configs/analysis_config.yaml` under `cell_type_markers`.

---

### 2.1 Basal Keratinocytes

**Markers**: *Krt14*, *Krt5*, *Tp63*, *Itga6*

**What they are**: The stem cells of the skin's outermost layer (epidermis). They sit on the **basement membrane** — a thin sheet of ECM that separates the epidermis from the dermis. "Basal" means "at the base."

**What they do in wound healing**:
- They are the soldiers who close the wound from above (re-epithelialisation)
- At the wound edge, they undergo **partial EMT**: loosening connections and migrating across the wound bed
- Once the gap is closed, they stop migrating and start dividing to rebuild the multi-layered epidermis
- *Tp63* is a master transcription factor that maintains their stem cell identity
- *Itga6* (integrin α6) anchors them to the basement membrane — like grappling hooks

**Expected behaviour across conditions**:
- `control` — abundant, organised layer at the base of epidermis
- `wound_3d` — proportion drops (cells at wound site are destroyed/displaced)
- `wound_7d` — proportion recovers as they migrate and proliferate. EMT markers (*Vim*↑, *Cdh1*↓) in migrating cells
- `wound_14d` — re-established, proportion returning to normal

**Analogy**: Basal keratinocytes are like floor tiles. Normally they sit neatly in a row. When the floor cracks, the tiles at the edge start sliding to fill the gap (EMT). Once the gap is filled, they cement themselves back in place.

---

### 2.2 Differentiated Keratinocytes

**Markers**: *Krt10*, *Krt1*, *Ivl*, *Lor*

**What they are**: Mature keratinocytes that have moved upward from the basal layer. They form the water-proof, dead-cell layers at the skin surface (stratum corneum). The process of moving up and dying is called **cornification** or **terminal differentiation**.

**What they do in wound healing**:
- In healthy skin, they provide the barrier function (keeping water in, pathogens out)
- At the wound site, the differentiated layers are destroyed
- They cannot migrate or divide — they have already exited the cell cycle
- Re-established only after basal keratinocytes have closed the wound and begin differentiating again
- *Ivl* (Involucrin) and *Lor* (Loricrin) are cross-linking proteins in the cornified envelope — they make the dead cell layer waterproof

**Expected behaviour across conditions**:
- `control` — present as the top layers of epidermis
- `wound_3d` — proportion drops (barrier destroyed at wound)
- `wound_7d` — still low (re-epithelialisation not yet complete in deeper layers)
- `wound_14d` — proportion increasing as new epidermis matures

**Analogy**: If basal keratinocytes are the factory producing bricks, differentiated keratinocytes are the finished bricks cemented into the wall. You cannot move them once they are placed. If the wall breaks, you need new bricks from the factory, not the broken ones.

---

### 2.3 Fibroblasts

**Markers**: *Col1a1*, *Col3a1*, *Dcn*, *Pdgfra*

**What they are**: The primary structural cells of the **dermis** (the layer below the epidermis). They produce and maintain the extracellular matrix — the scaffold that gives skin its strength and elasticity.

**What they do in wound healing**:
- THE central cell type in wound repair
- Recruited to wound by *Pdgfa* and *Tgfb1*
- Proliferate rapidly during the proliferative phase
- Deposit new ECM: collagen, fibronectin, proteoglycans
- A subset differentiates into myofibroblasts (see below)
- In remodelling phase, they reorganise collagen and gradually become quiescent again
- *Dcn* (Decorin) regulates collagen fibril assembly — it is a "quality control" protein

**Expected behaviour across conditions**:
- `control` — steady-state dermal fibroblasts, moderate collagen production
- `wound_3d` — beginning to be recruited, proportion rising
- `wound_7d` — **peak** proportion, heavy ECM deposition, highest *Col1a1*/*Fn1* expression
- `wound_14d` — still present but transitioning to quiescent, more *Lox* expression (crosslinking)

**Analogy**: Fibroblasts are the construction workers of the body. They build the infrastructure (ECM), maintain the roads (collagen fibres), and when a building collapses (wound), they rush in to rebuild. They are the most versatile and hardworking cell type in the dermis.

---

### 2.4 Myofibroblasts

**Markers**: *Acta2*, *Tagln*, *Cnn1*, *Postn*

**What they are**: A specialised, activated form of fibroblast that combines collagen production with smooth-muscle-like contractile ability. They are essentially fibroblasts that have been "upgraded" for heavy-duty wound repair.

**What they do in wound healing**:
- **Contract the wound** — they generate mechanical tension that physically pulls wound edges together. This is why a wound on your arm gets visibly smaller over days.
- **Deposit massive amounts of ECM** — even more than regular fibroblasts
- **Generate mechanical signals** — their contraction transmits forces through the tissue, activating mechanotransduction pathways (*Yap1*, *Piezo1*) in neighbouring cells
- **Must die on schedule** — persistence of myofibroblasts causes fibrosis (excessive scarring). Diseases like scleroderma and pulmonary fibrosis involve myofibroblasts that refuse to die.
- *Postn* (Periostin) is particularly interesting — it promotes cell migration and is a marker of actively remodelling tissue

**Expected behaviour across conditions**:
- `control` — absent or extremely rare (healthy skin does not need them)
- `wound_3d` — beginning to appear (fibroblasts exposed to *Tgfb1* start differentiating)
- `wound_7d` — **peak** proportion. A distinct cluster on UMAP expressing *Acta2*/*Tagln*/*Postn*.
- `wound_14d` — **declining** (apoptosis underway). If they persist, it indicates potential fibrosis.

**Analogy**: Myofibroblasts are like heavy-duty cranes brought to a construction site for a specific big job (closing a large wound). They are expensive to run and dangerous if left active too long. Once the building is up, the cranes must be removed — otherwise they will keep pulling and distort the structure.

---

### 2.5 Macrophages

**Markers**: *Cd68*, *Adgre1*, *Csf1r*, *Mrc1*

**What they are**: Professional immune cells that eat debris, coordinate healing, and act as the bridge between inflammation and repair. The word macrophage literally means "big eater" (Greek: makros = large, phagein = to eat).

**What they do in wound healing**:
- **Early (M1/pro-inflammatory)**: Phagocytose bacteria and dead cells, release *Tnf* and *Il6*
- **Late (M2/pro-healing)**: Release *Tgfb1*, *Pdgfa*, *Vegfa* — signals that drive tissue repair
- **M1→M2 switching** is one of the most critical transitions. If macrophages stay in M1 mode, the wound becomes chronically inflamed.
- *Mrc1* (CD206) marks M2 macrophages. If you see *Mrc1* expression increasing from wound_3d to wound_7d, that is evidence of successful polarisation switching.

**Expected behaviour across conditions**:
- `control` — small resident population (tissue surveillance)
- `wound_3d` — **HIGH** proportion, mostly M1 (*Tnf*-high, *Mrc1*-low)
- `wound_7d` — moderate proportion, shifting to M2 (*Mrc1*-high, *Tgfb1*-high)
- `wound_14d` — declining, mostly M2, starting to leave the tissue

**Analogy**: Macrophages are like the coordinating foremen on a disaster response team. On Day 1, they direct the demolition crew (inflammation). By Day 7, they have switched to directing the construction crew (repair). If they never switch roles, the demolition never stops and the site remains a wasteland.

---

### 2.6 Neutrophils

**Markers**: *S100a8*, *S100a9*, *Ly6g*

**What they are**: The most abundant immune cell type and the first to arrive at a wound. They are aggressive, short-lived, and single-minded: kill microbes.

**What they do in wound healing**:
- Arrive within hours via the bloodstream (attracted by chemokines and complement)
- Kill bacteria through ROS, antimicrobial peptides, and phagocytosis
- Release NETs (Neutrophil Extracellular Traps) — literally casting a "net" of DNA and antimicrobial proteins to trap bacteria
- Release proteases (*Mmp9*) that degrade damaged ECM
- Die quickly (1–2 days) and are eaten by macrophages
- **IMPORTANT**: If neutrophils persist beyond the early inflammatory phase, they cause tissue damage. They are attack dogs — useful for the initial fight, dangerous if not recalled.

**Expected behaviour across conditions**:
- `control` — very rare in healthy skin (no infection to fight)
- `wound_3d` — **HIGHEST** proportion (peak neutrophil infiltration)
- `wound_7d` — declining (their job is done, macrophages clean them up)
- `wound_14d` — near-zero (should be gone if healing is normal)

**Analogy**: Neutrophils are like the fire department. They arrive first, blast everything with water (ROS), and leave once the fire is out. If they keep spraying water after the fire is controlled, they cause water damage. Chronic wounds are like houses where the fire department never leaves.

---

### 2.7 T Cells

**Markers**: *Cd3d*, *Cd3e*, *Cd4*, *Cd8a*

**What they are**: Adaptive immune cells that provide targeted, specific immune responses. While neutrophils and macrophages are "innate" (respond to general danger signals), T cells recognise specific threats.

**What they do in wound healing**:
- **Regulatory T cells (Tregs)** — suppress excessive inflammation, promote tissue repair. They are the "peacemakers."
- **Helper T cells (CD4+)** — secrete cytokines that modulate macrophage and fibroblast behaviour
- **Cytotoxic T cells (CD8+)** — kill infected cells (minor role in sterile wounds)
- T cells are not the stars of wound healing (unlike in infection or autoimmunity), but they play important **regulatory** roles
- *Cd3d*/*Cd3e* are components of the T cell receptor complex — present on ALL T cells
- *Cd4* marks helper T cells; *Cd8a* marks cytotoxic T cells

**Expected behaviour across conditions**:
- `control` — small resident population in skin (tissue-resident memory T cells)
- `wound_3d` — increasing (recruited with the inflammatory wave)
- `wound_7d` — moderate (Tregs dampening inflammation)
- `wound_14d` — returning to baseline

**Analogy**: T cells are like the legal team that arrives after the emergency. The fire department (neutrophils) and construction foremen (macrophages) did the hands-on work. T cells make sure the response stays proportional and does not cause collateral damage.

---

### 2.8 Endothelial Cells

**Markers**: *Pecam1*, *Cdh5*, *Kdr*

**What they are**: The cells that line blood vessels. They form the inner wall of every artery, vein, and capillary. When you think "blood vessels," you are thinking about endothelial cells.

**What they do in wound healing**:
- **Angiogenesis** — the formation of new blood vessels. Endothelial cells sprout from existing vessels and migrate into the wound. New tissue MUST have blood supply or it dies.
- They respond to *Vegfa* (via the receptor *Kdr*/VEGFR2) — the signal that says "this tissue needs blood supply"
- Blood vessels also ferry immune cells, nutrients, and oxygen to the wound
- *Pecam1* (CD31) is at cell-cell junctions between endothelial cells
- *Cdh5* (VE-cadherin) controls the "leakiness" of blood vessels. When *Cdh5* is disrupted, vessels become permeable — allowing immune cells to squeeze through into tissue

**Expected behaviour across conditions**:
- `control` — steady-state blood vessel network
- `wound_3d` — vessels near wound are dilated and "leaky" (allowing immune cell exit). *Vegfa* rising.
- `wound_7d` — **peak** angiogenesis. New vessels sprouting into wound bed. Highest *Kdr* expression.
- `wound_14d` — vessel normalisation. Excess vessels are pruned. Network matures.

**Analogy**: Endothelial cells are the road construction crew. When a new neighbourhood is being built (the wound), they extend the road network (blood vessels) so that supplies (oxygen, nutrients) and workers (immune cells) can reach the area.

---

### 2.9 Hair Follicle Stem Cells (HFSCs)

**Markers**: *Sox9*, *Lgr5*, *Cd34*, *Lhx2*

**What they are**: Stem cells that reside in a specialised niche called the **bulge** of the hair follicle. They are among the most potent stem cells in skin.

**What they do in wound healing**:
- In normal conditions, they maintain the hair follicle cycle (growth → regression → rest)
- During wound healing, they can be activated to contribute to **epidermal regeneration** — they migrate out of the follicle and help re-epithelialise the wound surface
- This is a key reason wounds near hair-bearing skin heal faster
- *Sox9* — transcription factor that maintains the HFSC state
- *Lgr5* — Wnt target gene, marks actively cycling stem cells
- *Cd34* — surface marker of quiescent HFSCs (mouse-specific; human HFSCs do not express *Cd34*)
- *Lhx2* — transcription factor required for hair follicle morphogenesis

**Expected behaviour across conditions**:
- `control` — present in hair follicles, a small but distinct cluster
- `wound_3d` — hair follicles at wound site destroyed; proportion drops
- `wound_7d` — activated HFSCs from follicles at wound edge contributing to healing
- `wound_14d` — scar tissue typically **lacks hair follicles**, so HFSCs may be reduced in wound area

**Analogy**: HFSCs are like a strategic reserve army. Normally they maintain the local base (hair follicle), but in an emergency (wound), they can be deployed to the front lines (epidermis). The fact that scars often lack hair shows that this reserve was used up or the base was destroyed.

---

### 2.10 Melanocytes

**Markers**: *Dct*, *Tyrp1*, *Pmel*, *Mitf*

**What they are**: Pigment-producing cells. They synthesise melanin and transfer it to keratinocytes, giving skin its colour. In mice, they are primarily in hair follicles; in humans, they are throughout the epidermis.

**What they do in wound healing**:
- Have a minimal direct role in wound repair
- They do NOT contribute to wound closure
- However, scars often have altered pigmentation (lighter or darker than surrounding skin) because melanocyte repopulation of the wound is incomplete or abnormal
- *Mitf* — master transcription factor of melanocyte identity (controls all melanin pathway genes)
- *Dct* (Dopachrome tautomerase) and *Tyrp1* (Tyrosinase-related protein 1) — enzymes in the melanin biosynthesis pathway
- *Pmel* — structural protein of melanosomes (the organelles where melanin is made)

**Expected behaviour across conditions**:
- `control` — small population, primarily associated with hair follicles in mice
- `wound_3d` — depleted at wound site (destroyed with epidermis)
- `wound_7d` — still depleted (melanocytes are slower to repopulate than keratinocytes)
- `wound_14d` — beginning to return, but often incomplete (hence scar hypopigmentation)

**Analogy**: Melanocytes are like the painters in a construction project. They do not build the structure, but they make it look right. The painters arrive last, and sometimes they never come — which is why scars often look different from surrounding skin.

---

### 2.11 Cell Type Summary Table

| Cell Type | Markers | Peak Condition | Wound Role |
|---|---|---|---|
| Basal Keratinocyte | *Krt14, Krt5, Tp63, Itga6* | Control / wound_14d | Re-epithelialisation |
| Diff. Keratinocyte | *Krt10, Krt1, Ivl, Lor* | Control / wound_14d | Barrier function |
| Fibroblast | *Col1a1, Col3a1, Dcn, Pdgfra* | wound_7d | ECM deposition |
| Myofibroblast | *Acta2, Tagln, Cnn1, Postn* | wound_7d | Wound contraction |
| Macrophage | *Cd68, Adgre1, Csf1r, Mrc1* | wound_3d | Phagocytosis, signalling |
| Neutrophil | *S100a8, S100a9, Ly6g* | wound_3d | Bacterial killing |
| T Cell | *Cd3d, Cd3e, Cd4, Cd8a* | wound_3d / wound_7d | Immune regulation |
| Endothelial | *Pecam1, Cdh5, Kdr* | wound_7d | Angiogenesis |
| HFSC | *Sox9, Lgr5, Cd34, Lhx2* | Control | Stem cell reserve |
| Melanocyte | *Dct, Tyrp1, Pmel, Mitf* | Control | Pigmentation |

---

## 3. Tissue Fluidity — The Core Research Concept

### 3.1 What Is Tissue Fluidity? (The Deep Explanation)

Tissue fluidity is a **physics concept applied to biology**. It describes how easily cells within a tissue can rearrange — move past each other, change neighbours, reorganise.

#### The states-of-matter framework

In physics, matter exists in three primary states: solid, liquid, and gas. Tissues behave similarly:

| State | Cell behaviour | Adhesion | ECM | Movement | Example |
|---|---|---|---|---|---|
| **Solid** | Tightly packed, immobile | Strong | Rigid, cross-linked | None | Healthy skin barrier |
| **Fluid** | Rearranging, flowing | Weakened | Soft, being remodelled | Active migration | Healing wound |
| **Gas** | Completely dissociated | None | Absent | Uncontrolled | Metastatic cancer |

Wound healing requires a **solid → fluid → solid** transition:

```
SOLID (healthy)         FLUID (healing)          SOLID (healed)
┌──────────────┐       ┌──────────────┐        ┌──────────────┐
│ ■─■─■─■─■─■ │       │ ○  →  ○  → ○ │        │ ■─■─■─■─■─■ │
│ │  │  │  │  ││  ──►  │ ↓  ○  ↑  ○  │  ──►   │ │  │  │  │  ││
│ ■─■─■─■─■─■ │       │ ○  →  ○  → ○ │        │ ■─■─■─■─■─■ │
└──────────────┘       └──────────────┘        └──────────────┘
  Cells locked in         Cells flowing           Cells locked
  position (─ = tight     freely (arrows =        again (new
  adhesion bonds)         movement direction)     connections)
```

#### Why "fluidity" and not just "migration"?

You might ask: why not just say "cells are migrating"? Because tissue fluidity encompasses MORE than individual cell movement:

1. **Cell-cell adhesion changes** — the glue between cells weakens (EMT genes)
2. **ECM remodelling** — the scaffold around cells is softened (MMP genes)
3. **Active migration** — cells crawl using their internal motors (Rho/Rac/Cdc42)
4. **Mechanical sensing** — cells feel forces and respond (YAP/Piezo1)
5. **Chemical coordination** — signalling molecules orchestrate the timing (TGF-β, VEGF)

All five must happen in concert. A cell that activates its migration machinery (*Rac1*) but does not loosen its adhesions (*Cdh1* stays high) cannot actually move. A cell that loosens adhesions but the surrounding ECM is rigid (*Lox*-crosslinked) is still stuck. Tissue fluidity is the **collective state** that emerges when all five systems are activated.

**Analogy**: Imagine you want to rearrange furniture in a room. You need to:
1. Unbolt the furniture from the floor (EMT — loosen adhesions)
2. Remove walls that are in the way (ECM remodelling — soften barriers)
3. Physically push the furniture (cell migration — generate force)
4. Know how much space you have (mechanotransduction — sense the environment)
5. Have someone coordinating the movers (wound signals — chemical communication)

If any one of these fails, the rearrangement stalls. Tissue fluidity is not one gene or one process — it is the emergent property of multiple systems working together.

---

### 3.2 The Five Gene Signature Categories — Deep Biology

Our project measures tissue fluidity by scoring five categories of genes. Here is the biology behind each.

#### Category 1: EMT (Epithelial-Mesenchymal Transition)

**Genes**: *Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2*

**What EMT is**: A fundamental cell biological process where a cell changes its identity from **epithelial** (stationary, polarised, forming sheets) to **mesenchymal** (mobile, unpolarised, solitary).

**The molecular logic**:

```
EPITHELIAL CELL                     MESENCHYMAL CELL
(stuck in a sheet)                  (free to move)

  ┌──────────┐                       ┌──────────┐
  │  Cdh1 ↑  │  ──── EMT ────►      │  Cdh1 ↓  │
  │  Vim  ↓  │     (Snai1,          │  Vim  ↑  │
  │ tight    │      Twist1,          │ motile   │
  │ junctions│      Zeb1/2)          │ invasive │
  └──────────┘                       └──────────┘
```

**The players**:
- **Cdh1 (E-cadherin)**: The master "glue" protein. Cdh1 forms bridges between adjacent epithelial cells. When Cdh1 is on the surface, cells are stuck together like Velcro. EMT *requires* Cdh1 to go **DOWN**. This is one of the best-studied molecules in all of cell biology.
- **Cdh2 (N-cadherin)**: Replaces Cdh1 during EMT. N-cadherin makes weaker, more dynamic connections. It is like replacing industrial Velcro with Post-it notes — cells can still touch each other but easily separate. The "cadherin switch" (Cdh1↓ Cdh2↑) is a classic EMT hallmark.
- **Vim (Vimentin)**: An intermediate filament protein that forms the mesenchymal cell's internal skeleton. Vimentin gives cells the mechanical rigidity to crawl. Think of it as the cell's internal "tent poles" that allow it to maintain shape while moving.
- **Snai1/Snai2 (Snail/Slug)**: Zinc-finger transcription factors that directly REPRESS *Cdh1*. They bind to the *Cdh1* promoter and shut it down. Snai1 is the "master switch" — when it is activated, EMT begins.
- **Twist1**: A bHLH transcription factor that promotes EMT. It represses *Cdh1* through a different mechanism than Snai1 (indirect). *Twist1* also promotes cell survival during migration — it prevents migrating cells from dying.
- **Zeb1/Zeb2**: Zinc-finger/homeodomain transcription factors. They also repress *Cdh1* and activate *Vim*. They are particularly important for MAINTAINING the mesenchymal state (Snai1 initiates, Zeb1/2 stabilise).

**In wound healing specifically**:
- Keratinocytes at the wound edge undergo **partial EMT** — not a full switch, but enough to become motile
- "Partial" means Cdh1 goes down somewhat, Vim goes up somewhat, but cells retain some epithelial features
- This is biologically different from EMT in cancer (metastasis), where the switch is more complete and pathological
- Look for: gradient of EMT scores from the wound edge (high) to away from wound (low)

#### Category 2: ECM Remodelling

**Genes**: *Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2*

**What ECM remodelling is**: The extracellular matrix (ECM) is the protein scaffold between cells. Remodelling means simultaneously **degrading** old ECM and **depositing** new ECM.

**Why this is necessary for fluidity**: Imagine cells are cars and ECM is the road. During wound healing, you need to simultaneously demolish damaged roads (old ECM), build new roads (new ECM), and keep traffic flowing (cell migration). ECM remodelling is this coordinated demolition-and-construction operation.

**The players, grouped by function**:

**Builders** (deposit new ECM):
- **Col1a1 (Collagen I alpha 1)**: The most abundant protein in the body. It forms thick, strong fibres. Think: reinforced concrete beams. Dominant in mature tissue and remodelling phase.
- **Col3a1 (Collagen III alpha 1)**: Thinner, more flexible fibres. Think: temporary scaffolding. Dominant in the early wound (proliferative phase). The ratio of Col3:Col1 shifts during healing.
- **Fn1 (Fibronectin)**: A glycoprotein that cells use as a "runway" for migration. Fn1 binds to integrins (*Itgb1*) on the cell surface. Think: the pavement that tyres grip on. Without fibronectin, cells cannot crawl effectively.

**Demolishers** (degrade ECM):
- **Mmp2 (Matrix metalloproteinase 2)**: Cuts type IV collagen (basement membrane) and gelatin. Relevant for cells crossing tissue boundaries.
- **Mmp9 (Matrix metalloproteinase 9)**: Also cuts basement membrane components. Particularly important in neutrophils and macrophages — they use Mmp9 to bore through tissue.
- **Mmp14 (MT1-MMP, membrane-type MMP)**: Unique because it is anchored to the cell surface. It acts locally — cutting ECM right in front of the moving cell. Also activates Mmp2 (the enzyme that activates another enzyme!).

**Regulators**:
- **Timp1 (Tissue inhibitor of metalloproteinases 1)**: The "stop sign" for MMPs. Timp1 physically binds to and inhibits MMPs. Think: a foreman telling the demolition crew to stop — the building has been cleared, don't tear down the new one. The balance between MMPs and TIMPs determines how much ECM degradation occurs.
- **Lox / Loxl2 (Lysyl oxidase / Lysyl oxidase-like 2)**: Enzymes that cross-link collagen fibres. They connect individual collagen strands into a rigid network. Think: welding individual steel beams into a frame. Active in the late proliferative and remodelling phases. High *Lox* = tissue stiffening = fluidity decreasing.

**How to interpret ECM scores**:
- High MMP + Low TIMP = active degradation → more fluid
- High MMP + High TIMP = balanced turnover → controlled remodelling
- Low MMP + High Lox = stiffening → more solid
- High Fn1 = cells have "roads" for migration → facilitates fluidity

#### Category 3: Cell Migration

**Genes**: *Rac1, Cdc42, Itgb1, RhoA, Rock1, Rock2*

**What cell migration is**: The physical process of a cell moving from point A to point B. This is not passive (cells are not "pushed") — it is actively driven by the cell's internal machinery.

**How a cell moves — the 5-step cycle**:

```
CELL MIGRATION CYCLE

   1. POLARISE              2. EXTEND                3. ADHERE
   (set direction)          (reach forward)          (grab the ground)
   
   ┌────────┐              ┌──────────┐             ┌──────────┐
   │  Cdc42 │              │  Rac1    │             │  Itgb1   │
   │  (GPS) │              │  → → →  │             │ (tyres   │
   │  sets  │              │(pushes   │             │  grip    │
   │  front │              │ membrane)│             │  ECM)    │
   └────────┘              └──────────┘             └──────────┘
   
   4. DE-ADHERE             5. RETRACT
   (release the back)       (squeeze forward)
   
   ┌──────────┐            ┌──────────┐
   │ release  │            │ RhoA     │
   │ old      │            │ Rock1/2  │
   │ contacts │            │(squeeze  │
   │          │            │ the rear)│
   └──────────┘            └──────────┘
```

**The players**:
- **Cdc42**: A small GTPase that establishes cell polarity — it tells the cell which end is the "front." Without Cdc42, cells move randomly instead of toward the wound.
- **Rac1**: A small GTPase that drives **lamellipodia** (flat, sheet-like protrusions) at the leading edge. Rac1 activates actin polymerisation, pushing the membrane forward like a bulldozer blade.
- **RhoA**: A small GTPase that generates **contractile force** at the rear of the cell. It activates Rock1/2, which phosphorylate myosin to squeeze the back of the cell forward. Analogy: squeezing a tube of toothpaste from the back.
- **Rock1 / Rock2 (Rho-kinase 1/2)**: Downstream effectors of RhoA. They phosphorylate myosin light chain, generating contractile force. ROCK inhibitors are used experimentally to study cell migration.
- **Itgb1 (Integrin β1)**: The "foot" that a cell uses to grip the ECM. Integrins span the cell membrane — outside they bind ECM proteins (fibronectin, collagen), inside they connect to the actin cytoskeleton. Without integrins, a cell is like a car on ice: the engine runs, but the wheels have no traction.

**In wound healing**:
- Fibroblasts, macrophages, keratinocytes, and endothelial cells ALL migrate during healing — using the same core machinery
- Different cell types emphasise different components: macrophages are very Rac1-dependent (amoeboid movement), fibroblasts rely more on Itgb1 (mesenchymal movement)
- HIGH migration scores at wound_7d indicate peak cell motility

#### Category 4: Mechanotransduction

**Genes**: *Yap1, Wwtr1, Piezo1, Trpv4, Lats1, Lats2*

**What mechanotransduction is**: The process by which cells convert physical forces (pressure, stretch, stiffness) into biochemical signals that change gene expression.

**Why this matters in wound healing**: A wound dramatically changes the mechanical environment. Where there was once taut, elastic skin, there is now a soft, disorganised wound bed. Cells must detect this change and respond appropriately: "This area is soft and broken → activate migration and repair programmes."

**The Hippo pathway — the central circuit**:

```
MECHANICAL SIGNAL FLOW

  STIFF tissue                          SOFT tissue
  (healthy skin)                        (wound bed)
       │                                     │
       ▼                                     ▼
  ┌─────────┐                           ┌─────────┐
  │ Piezo1  │ ← ion channel             │ Piezo1  │ ← less active
  │ Trpv4   │   (senses stretch)        │ Trpv4   │
  └────┬────┘                           └────┬────┘
       │                                     │
       ▼                                     ▼
  ┌─────────┐                           ┌─────────┐
  │ Lats1/2 │ ← ACTIVE                  │ Lats1/2 │ ← INACTIVE
  │ (kinase)│   (phosphorylates         │ (kinase)│
  └────┬────┘    YAP → degradation)     └────┬────┘
       │                                     │
       ▼                                     ▼
  ┌─────────┐                           ┌─────────┐
  │ Yap1    │ ← CYTOPLASM               │ Yap1    │ ← NUCLEUS
  │ Wwtr1   │   (inactive,              │ Wwtr1   │   (active,
  │ (TAZ)   │    degraded)              │ (TAZ)   │    drives gene
  └─────────┘                           └─────────┘    expression)
       │                                     │
       ▼                                     ▼
  Result: quiescence,                   Result: proliferation,
  no growth                             migration, ECM production
```

**The players**:
- **Piezo1**: A mechanically-activated ion channel. When the cell membrane is stretched (by physical forces), Piezo1 opens and lets calcium ions flood in. Calcium is a universal intracellular signal that triggers many downstream responses. Think: a pressure gauge on a pipe.
- **Trpv4**: Another mechano-sensitive ion channel. Responds to cell swelling, heat, and mechanical forces. Complements Piezo1.
- **Yap1 (Yes-associated protein 1)**: A transcription co-activator. When active (in the nucleus), it turns on genes for proliferation, survival, and migration. The cell "decides" to grow and move. When inactive (in the cytoplasm, phosphorylated by Lats1/2), the cell stays quiet.
- **Wwtr1 (TAZ)**: A paralogue of Yap1 — works through similar mechanisms. YAP and TAZ often act redundantly.
- **Lats1 / Lats2**: Kinases that phosphorylate and inactivate YAP/TAZ. They are the "brakes" on YAP signalling. When tissue is stiff and stable, Lats1/2 keep YAP inactive. During wound healing, Lats1/2 activity decreases, releasing the brake.

**In wound healing**:
- At the wound edge, cells experience reduced mechanical constraint → YAP enters the nucleus → cells proliferate and migrate
- Myofibroblasts generate strong mechanical forces → activates Piezo1 in neighbouring cells → propagates the "wound signal" mechanically
- As the wound closes and tissue stiffens, YAP activity normalises → cells return to quiescence

#### Category 5: Wound Signals

**Genes**: *Tgfb1, Tgfb2, Tgfb3, Pdgfa, Vegfa, Wnt5a, Il6, Tnf*

**What wound signals are**: Secreted signalling molecules — growth factors and cytokines — that cells release to communicate with each other. They coordinate the timing and execution of healing phases.

**The players**:

**TGF-β family** (*Tgfb1, Tgfb2, Tgfb3*):
- The most important signalling family in wound healing
- *Tgfb1* is the master regulator: it drives fibroblast→myofibroblast differentiation, stimulates ECM production, and modulates inflammation
- *Tgfb1* is also the primary driver of fibrosis — too much Tgfb1 = scarring
- *Tgfb3* has the opposite effect: it promotes **regeneration** over scarring in some contexts. The ratio of Tgfb1:Tgfb3 may predict scar outcome.
- Analogy: *Tgfb1* is like a general issuing orders to build fortifications (ECM). If the general keeps ordering more fortifications after the battle, you get an overbuilt bunker (fibrosis).

**Growth factors** (*Pdgfa, Vegfa*):
- *Pdgfa* (Platelet-derived growth factor A): Recruits fibroblasts and stimulates their proliferation. Released by platelets (Phase 1) and macrophages (Phase 2). Think: a "Help Wanted" sign for construction workers (fibroblasts).
- *Vegfa* (Vascular endothelial growth factor A): THE angiogenesis signal. It tells endothelial cells to sprout new blood vessels. Released mainly by macrophages in hypoxic (oxygen-deprived) wound tissue. Think: "We need supply lines!" — Vegfa calls in the road-building crew (endothelial cells).

**Wnt signalling** (*Wnt5a*):
- *Wnt5a* controls cell polarity and directional migration through the non-canonical (planar cell polarity) Wnt pathway
- Important for coordinating the direction of keratinocyte migration during re-epithelialisation
- Think: a traffic director pointing which way the cars should go

**Inflammatory cytokines** (*Il6, Tnf*):
- *Il6* (Interleukin-6): A pleiotropic cytokine — it does many things. In early wounds: pro-inflammatory, recruits immune cells. Later: promotes fibroblast functions. It is like both an alarm bell AND a work whistle.
- *Tnf* (Tumor Necrosis Factor): Powerful pro-inflammatory signal. Activates endothelial cells (makes vessels leaky for immune cell exit), activates macrophages, induces apoptosis in some cells. In excess, causes tissue damage. Think: the fire alarm — essential for emergency response, damaging if it never stops.

---

## 4. How We Measure Fluidity Computationally

### 4.1 Gene Set Scoring with `sc.tl.score_genes`

We cannot directly watch cells move in our scRNA-seq data (that would require live imaging). Instead, we **infer** fluidity by measuring the expression of genes that control movement, adhesion, and remodelling.

**How scoring works — step by step**:

1. **Define a gene set** — e.g., EMT_signature = [*Vim*, *Cdh1*, *Cdh2*, *Snai1*, *Snai2*, *Twist1*, *Zeb1*, *Zeb2*]
2. **For each cell**, calculate the **mean expression** of the genes in the set
3. **Select control genes** — a random set of genes with similar expression levels (this controls for the overall expression level of the cell)
4. **Subtract** the mean expression of control genes from the mean expression of signature genes
5. **Result**: a single number per cell — the **score**. Positive = signature genes are expressed more than expected. Negative = less than expected.

```
SCORING EXAMPLE FOR ONE CELL

  Signature genes:    Vim=3.2   Snai1=1.8   Cdh1=0.1   Zeb1=2.1
                      Mean = (3.2 + 1.8 + 0.1 + 2.1) / 4 = 1.80

  Control genes:      Gene_X=1.1  Gene_Y=0.9  Gene_Z=1.3  Gene_W=0.7
  (randomly chosen)   Mean = (1.1 + 0.9 + 1.3 + 0.7) / 4 = 1.00

  SCORE = 1.80 - 1.00 = +0.80
  
  Interpretation: This cell has moderately HIGH EMT activity
```

**Why subtract control genes?** Because some cells have higher gene expression overall (they might just be bigger or more transcriptionally active). Without the control subtraction, a large cell would score high on every signature. The control genes normalise for this.

### 4.2 Computing Overall Fluidity

We score each cell for all five signatures and then combine them:

```python
# In our pipeline (scripts/python/01_scrna_analysis_pipeline.py):
fluidity_sets = {
    'EMT_signature': ['Vim', 'Cdh1', 'Cdh2', 'Snai1', 'Snai2', 'Twist1', 'Zeb1', 'Zeb2'],
    'ECM_remodeling': ['Fn1', 'Col1a1', 'Col3a1', 'Mmp2', 'Mmp9', 'Mmp14', 'Timp1', 'Lox', 'Loxl2'],
    'Cell_migration': ['Rac1', 'Cdc42', 'RhoA', 'Itgb1', 'Itga6', 'Cxcl12', 'Cxcr4'],
    'Mechanotransduction': ['Yap1', 'Wwtr1', 'Piezo1', 'Trpv4', 'Lats1', 'Lats2'],
    'Wound_signals': ['Tgfb1', 'Tgfb2', 'Tgfb3', 'Pdgfa', 'Pdgfb', 'Fgf2', 'Vegfa', 'Wnt5a'],
}

for name, genes in fluidity_sets.items():
    available = [g for g in genes if g in adata.var_names]
    if available:
        sc.tl.score_genes(adata, gene_list=available, score_name=f'fluidity_{name}')
```

### 4.3 Expected Results Across Conditions

```
Condition   | EMT     | ECM        | Migration | Mechano  | Wound Sig | Overall
            | Score   | Remodeling | Score     | Score    | Score     | Fluidity
----------- | ------- | ---------- | --------- | -------- | --------- | ----------
control     | Low     | Low        | Low       | Low      | Low       | Baseline
wound_3d    | Medium  | Low-Med    | High      | Medium   | High      | Rising
wound_7d    | High    | High       | High      | High     | High      | ★ PEAK ★
wound_14d   | Medium  | Medium     | Low       | Medium   | Low-Med   | Declining
```

**Why these patterns?**

- **wound_3d (inflammation)**: EMT begins at wound edge (keratinocytes loosening). Migration is high (immune cells flooding in). Wound signals are high (*Il6*, *Tnf*). ECM remodelling is just starting (MMPs from neutrophils).
- **wound_7d (proliferation)**: EVERYTHING peaks. EMT, ECM remodelling, migration, mechanotransduction, wound signals — all at maximum because this is when the most active repair is happening.
- **wound_14d (remodelling)**: Fluidity declines. EMT genes re-normalise (keratinocytes settling). ECM shifts from degradation to crosslinking (*Lox* up, MMP activity down). Migration decreases. Wound signals reduce as the injury resolves.

### 4.4 Cell-Type-Specific Fluidity

Not all cell types contribute equally to fluidity. In our data:

| Cell Type | Dominant Fluidity Signature | Why |
|---|---|---|
| Fibroblasts | ECM remodelling | They build the new scaffold |
| Myofibroblasts | ECM + Migration + Mechanotransduction | They do everything — build, contract, sense force |
| Basal Keratinocytes | EMT | They undergo the cadherin switch to migrate |
| Macrophages | Migration + Wound signals | They crawl in and release cytokines |
| Endothelial | Migration | They sprout into the wound (angiogenesis) |
| Neutrophils | Migration + Wound signals | They invade aggressively and signal alarm |

---

## 5. Interview Questions & Answers

### Q1: "Walk me through the wound healing phases and how they map to your data."

**Answer**:

> "Wound healing has four overlapping phases. First is hemostasis — blood clotting within the first hours — which we don't capture because our earliest time point is day 3. Second is inflammation, captured by our wound_3d condition: neutrophils and macrophages flood the wound site, clearing debris and bacteria, releasing signals like Il6 and Tnf. Third is proliferation, captured by wound_7d: fibroblasts deposit new extracellular matrix, myofibroblasts contract the wound, keratinocytes migrate to re-cover the surface, and new blood vessels form. This is where tissue fluidity peaks. Fourth is remodelling, captured by wound_14d: collagen matures from type III to type I, myofibroblasts undergo apoptosis, and the tissue stiffens back toward its pre-wound state. We also have a healthy control condition as our baseline. The four-condition design gives us a temporal window across the critical healing transitions."

### Q2: "What is tissue fluidity and why is it important?"

**Answer**:

> "Tissue fluidity is a biophysical concept that describes how easily cells within a tissue can rearrange and move past each other. In healthy skin, the tissue is solid-like: cells are tightly adhered, the ECM is rigid, and there is minimal movement. During wound healing, the tissue must temporarily become fluid-like: cells loosen their adhesions, the ECM is enzymatically softened, and multiple cell types migrate to fill the wound. Once healing is complete, the tissue re-solidifies. This solid-to-fluid-to-solid transition is essential for successful repair. If the tissue never becomes fluid enough, the wound stays open — as in chronic diabetic ulcers. If it becomes too fluid or never re-solidifies, you get pathological outcomes like excessive scarring or fibrosis. We measure fluidity computationally by scoring cells for five gene signatures that collectively control this transition."

### Q3: "How do you define and measure fluidity computationally?"

**Answer**:

> "We define tissue fluidity through five gene signature categories: EMT genes that control cell-cell adhesion, ECM remodelling genes that control the structural scaffold, cell migration genes that provide the cellular motor machinery, mechanotransduction genes that sense physical forces, and wound signalling molecules that coordinate the process. For each category, we define a set of 6 to 9 genes based on literature. Then, using Scanpy's score_genes function, we score every individual cell for each signature. The scoring works by comparing the average expression of signature genes against random control genes matched for expression level. This gives us a normalised score per cell per signature. We can then compare these scores across conditions — control, wound_3d, wound_7d, wound_14d — to see the temporal dynamics of fluidity, and we can stratify by cell type to see which cells are driving the transition."

### Q4: "Why these specific gene signatures?"

**Answer**:

> "These five signature categories were chosen because they represent the five molecular pillars of tissue fluidity: first, EMT genes because tissue fluidity begins with cells detaching from their neighbours. Second, ECM remodelling because the surrounding scaffold must be softened for cells to move. Third, cell migration because the actual motility machinery must be activated. Fourth, mechanotransduction because cells need to sense and respond to the changing physical environment. Fifth, wound signals because the whole process requires chemical coordination between cell types. Each category addresses a different aspect, and all five must be active simultaneously for effective tissue fluidity. The specific genes within each category — like Cdh1 for adhesion, Mmp9 for ECM degradation, Rac1 for motility — are well-established in the wound healing and cell biology literature. We cross-referenced with multiple reviews and pathway databases to ensure completeness."

---

## 6. Self-Check Questions

Test yourself. Cover the answers and try to respond from memory.

### Q1: Name the four phases of wound healing in order.
**Answer**: (1) Hemostasis, (2) Inflammation, (3) Proliferation, (4) Remodelling. They overlap in time. Our data captures phases 2–4 with wound_3d, wound_7d, and wound_14d respectively.

### Q2: Which cell type arrives first at a wound, and what are its markers in our data?
**Answer**: Neutrophils. Markers: *S100a8*, *S100a9*, *Ly6g*. They arrive within hours, kill bacteria, and die quickly. We expect peak neutrophil proportions at wound_3d.

### Q3: What is the difference between a fibroblast and a myofibroblast?
**Answer**: Fibroblasts produce ECM (collagen, fibronectin) and are the baseline structural cells. Myofibroblasts are fibroblasts that have differentiated (driven by *Tgfb1*) to also express smooth muscle proteins (*Acta2*), giving them contractile ability. Myofibroblasts both build ECM AND contract the wound. They must undergo apoptosis or they cause fibrosis.

### Q4: What does the "cadherin switch" mean, and which genes are involved?
**Answer**: The cadherin switch is the replacement of *Cdh1* (E-cadherin, strong adhesion) with *Cdh2* (N-cadherin, weak adhesion) during EMT. Cdh1 goes DOWN, Cdh2 goes UP. This allows cells to detach from their neighbours and become motile. It is driven by transcription factors *Snai1*, *Snai2*, *Twist1*, *Zeb1*, *Zeb2*.

### Q5: Why is the MMP:TIMP balance important?
**Answer**: MMPs (matrix metalloproteinases) degrade ECM — necessary for cell migration. TIMPs inhibit MMPs. If MMP activity is too high (low TIMPs), excessive tissue destruction occurs. If MMPs are too inhibited (high TIMPs), cells cannot move through the ECM and healing stalls. The balance determines the degree of ECM softening.

### Q6: What does YAP do in wound healing, and how is it regulated?
**Answer**: *Yap1* is a transcription co-activator that promotes cell proliferation, survival, and migration when it enters the nucleus. It is inactivated by *Lats1*/*Lats2* kinases (Hippo pathway), which phosphorylate YAP and keep it in the cytoplasm. In soft/wounded tissue, Lats1/2 activity decreases → YAP enters the nucleus → cells become active. It is part of our mechanotransduction signature.

### Q7: Which cell type do we expect to appear as a new cluster at wound_7d that is absent in control?
**Answer**: Myofibroblasts. They are virtually absent in healthy skin but appear during the proliferative phase in response to *Tgfb1* signalling. They form a distinct cluster expressing *Acta2*, *Tagln*, *Cnn1*, and *Postn*.

### Q8: What is the difference between *Vegfa* and *Pdgfa* in wound healing?
**Answer**: *Vegfa* signals endothelial cells to form new blood vessels (angiogenesis). *Pdgfa* recruits fibroblasts to the wound and stimulates their proliferation. Both are growth factors released by macrophages, but they target different cell types: *Vegfa* → endothelial cells, *Pdgfa* → fibroblasts.

### Q9: Why does wound_14d show increasing *Lox* / *Loxl2* expression?
**Answer**: *Lox* and *Loxl2* are lysyl oxidases that crosslink collagen fibres. During the remodelling phase, the provisional (loose) collagen is being stabilised into a rigid network. This crosslinking causes tissue stiffening — the re-solidification that ends the fluid phase. High *Lox* = tissue becoming more solid.

### Q10: If you saw a macrophage cluster at wound_7d expressing high *Mrc1* but low *Tnf*, what would you conclude?
**Answer**: These are **M2-polarised (pro-healing) macrophages**. *Mrc1* (CD206) is an M2 marker, while *Tnf* is an M1 (pro-inflammatory) marker. M2 macrophages release growth factors (*Tgfb1*, *Vegfa*, *Pdgfa*) that promote tissue repair rather than inflammation. Seeing this at wound_7d is expected — it indicates successful M1→M2 polarisation switching, which is critical for the transition from inflammation to proliferation.

---

## 7. Key Vocabulary Quick Reference

| Term | Definition |
|---|---|
| **EMT** | Epithelial-Mesenchymal Transition — cells switch from stationary to mobile |
| **ECM** | Extracellular Matrix — the scaffold between cells (collagen, fibronectin) |
| **MMP** | Matrix Metalloproteinase — enzyme that degrades ECM |
| **TIMP** | Tissue Inhibitor of Metalloproteinases — inhibits MMPs |
| **Angiogenesis** | Formation of new blood vessels |
| **Re-epithelialisation** | Keratinocytes migrating to re-cover the wound surface |
| **Myofibroblast** | Fibroblast + smooth muscle contraction = wound-closing cell |
| **Cadherin switch** | Cdh1↓ Cdh2↑ = cells loosen adhesion (EMT hallmark) |
| **Hippo pathway** | Yap1/Lats1/2 signalling cascade controlling cell growth via mechanical sensing |
| **M1/M2 polarisation** | Macrophage states: M1 = kill/inflame, M2 = repair/heal |
| **Partial EMT** | Cells gain some motility without fully becoming mesenchymal |
| **Phagocytosis** | Immune cell eating debris/bacteria ("big eater") |
| **Cytokine** | Small signalling protein released by cells (e.g., Il6, Tnf) |
| **Growth factor** | Signalling protein that promotes cell growth/division (e.g., Tgfb1, Vegfa) |
| **Chemokine** | Small protein that attracts immune cells to a site |

---

> **Tomorrow (Day 4)**: Quality Control & Preprocessing — the first computational step. You will learn how to filter bad cells, remove doublets, and normalise counts.
