## Spallation working example

This example is a **generic spallation target station** represented as simple concentric layers
(target, can, fuel ring, blanket, vessel wall) inside an air box and a surrounding blackhole.

### What it’s useful for
- **Spallation neutron sources** (target + shielding/blanket studies)
- **ADS-like concepts** (spallation target coupled to multiplying media)
- Quick studies of:
  - interface fluence/current (`USRBDX`)
  - region spectra (`USRTRACK`)
  - 3D maps of energy deposition / particle fluence (`USRBIN`)
  - residual nuclei production (`RESNUCLEi`)

### Axis convention used (important)
Assumed **FLUKA/FLAIR viewer convention**:
- **x** is vertical (up)
- **z** is horizontal (left → right) and used as the default beam direction
- **y** completes the right-hand system (into/out of screen)

### Notes
- Names are kept short (≤8 chars) to reduce fixed-field parsing surprises.
- If you replace built-in materials with custom ones and you need low-energy neutron transport,
  you may also need appropriate `LOW-MAT` mapping (not shown here to keep the example minimal).
