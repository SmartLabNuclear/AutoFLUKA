# Geometry, Region, and Material Rules

These rules prevent the region parsing and assignment errors seen in FLAIR logs.

## Coordinate-axis convention (default for authoring)
Unless the user explicitly specifies otherwise, assume the **FLUKA/FLAIR viewer convention**:
- **x-axis**: vertical (bottom → top)
- **z-axis**: horizontal (left → right)
- **y-axis**: completes the right-hand system (into/out of the screen)

Practical default:
- If the user says “beamline direction” but does not specify an axis, write the beam to travel along **+z** and align axial cylinders/slabs along **z**.
- Do not assume “z is vertical” when translating a hand sketch into FLUKA bodies/regions.
- If the user explicitly asks to change the reference axes for a source definition, use the dedicated card (for example `BEAMAXES`) rather than silently rotating geometry assumptions.

## Beam-target alignment rule (CRITICAL)

The beam source must be placed **upstream** of the target entry face along the beam direction.

| Beam direction | Target entry face | Required BEAMPOS position |
|---|---|---|
| Along +z | z = 0 | z < 0 (e.g., −5.0 cm) |
| Along +x | x = 0 | x < 0 |
| Along −z | z = L | z > L |

Checklist before finalising the deck:
1. BEAMPOS point is inside a **transport region** (not BLCKHOLE, not outside the outermost body).
2. BEAMAXES direction cosines (WHAT 1–3) point **from source toward target**.
3. The beam traverses the intended target depth — a source inside or behind the target deposits dose at the wrong location and defeats depth-dose or Bragg-peak objectives.
4. For a pencil beam along +z incident on a phantom at z = 0–30 cm, a BEAMPOS of (0, 0, −5) and BEAMAXES (0, 0, 1, 1, 0, 0) is a safe starting template.

## Geometry block structure
- Start with `GEOBEGIN ... COMBNAME`.
- Define bodies first (e.g., `RPP`, `SPH`, `RCC`, planes).
- Close body section with `END`.
- Define regions as boolean combinations of bodies.
- Close region section with `END`, then `GEOEND`.

## Geometry “recipes” (authoring shortcuts that avoid axis confusion)
Use these as deterministic templates when the user describes shapes in words.

### Cylinder aligned with +z (typical beamline component)
- Use `RCC` with its axis vector pointing along **z**:
  - base point at \((x_0, y_0, z_0)\)
  - axis/height vector \((0, 0, L)\) for a cylinder of length \(L\) along +z
  - radius \(R\)

Example:

```text
RCC CYL1       x0 y0 z0   0.0 0.0 L    R
```

### Simple slab/box aligned to the global axes
- Use `RPP` for an axis-aligned box (easy to read and hard to mis-parameterize).

```text
RPP BOX1       Xmin Xmax  Ymin Ymax  Zmin Zmax
```

### “Air box + blackhole” outer boundary
- Make one large `WORLD` box and a smaller `AIRBOX`.
- Create a `BH` region as `+WORLD -AIRBOX`, assign `BLCKHOLE` to it.
- Put all simulation content inside `AIRBOX` and subtract solids as needed.

## Region expression rules
- `+BODY` means inside, `-BODY` means outside.
- Use `|` for union when needed.
- Ensure every referenced body exists exactly as named.
- Keep region expression tokenized with spaces:
  - good: `AIR  5     +AIRBOX -WATBOX`
  - bad: `AIR 5 +AIRBOX-WATBOX` (easy to misread/parse)

## Region hierarchy guidance
- Typical robust stack:
  - outer boundary (`BLCKHOLE`)
  - vacuum shell
  - ambient region (`AIR`)
  - target/detector regions
- Order and boolean signs must make regions non-overlapping unless intentionally shared.

## Material definition and assignment
- Prefer FLUKA built-ins unless custom composition is required.

### Common built-in material tokens (curated reference; verify in your install/FLAIR DB)
This list is intentionally “common and practical” rather than exhaustive.

```text
# Special-purpose / environment
BLCKHOLE
VACUUM
AIR
WATER

# Frequently used elemental materials (often available as built-ins)
HYDROGEN
HELIUM
ALUMINUM
ARGON
BERYLLIU
BORON
CARBON
CHLORINE
COPPER
GOLD
GRAPHITE
IRON
LEAD
LITHIUM
MAGNESIU
MERCURY
NITROGEN
OXYGEN
SILVER
SILICON
SODIUM
TANTALUM
TITANIUM
TIN
TUNGSTEN
URANIUM

# Frequently used compounds / mixtures (often available as built-ins or via Flair DB import)
DRYAIR
POLYSTYR
POLYETHY
PMMA
CONCRETE
GLASS
```

Guidance:
- **Prefer exact built-in tokens** when they exist; don’t invent aliases like `LeadMetal` or `Fe`.
- If you must define a custom material, pick a short unique name (≤8 chars) that does not collide with any built-in.
 - Some built-in tokens are historically constrained/truncated (example patterns like `BERYLLIU`); copy the token exactly as recognized by your environment.

### Built-in reuse rule (avoid accidental overrides)
- If a requested material is already available as a FLUKA built-in, **reuse the built-in token**.
- Do **not** create a new `MATERIAL` with the same name as a built-in: that can override the built-in definition and can break downstream physics expectations.

- If custom materials are required, define via `MATERIAL` and `COMPOUND` before `ASSIGNMA`.
- Keep custom material identifiers short and stable (≤8 chars) and avoid near-collisions.
- Every transport-relevant region must be assigned exactly once through `ASSIGNMA`.
- In `ASSIGNMA`, verify both names:
  - material exists
  - region exists

### Low-energy neutron transport note (`LOW-MAT`)
- If your physics setup relies on **low-energy neutron transport** and you introduce **custom material names**, you may need an explicit `LOW-MAT` mapping so the correct low-energy neutron data are applied.
- Heuristic rule: **built-in names** are the safest path when you need low-energy neutron data; if you must use a custom material name, be prepared to add the corresponding `LOW-MAT` card(s) and validate the run completes without neutron-library errors.

## Name consistency safeguards
- Keep region/material identifiers short and consistent to avoid fixed-width truncation confusion.
- Avoid near-colliding names such as `regWAT4` vs `regWA`.
- Reuse one naming scheme across bodies/regions/materials (for example: `body*`, `reg*`, semantic material names).

## Error-to-fix map
- `Bad alignment in region definition`: reformat region line spacing and token separation.
- `material XXXX is not defined`: material token mismatch or truncation; fix name and definition order.
- `Region 'XXXX' is not defined`: `ASSIGNMA` references a typo/truncated region name.
- `Region ... is not assigned any material`: add missing `ASSIGNMA`.
