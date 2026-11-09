# photon_3mev_iso_pb_sphere

## Summary
A 3 MeV photon point source that emits isotropically (4π) from the centre of a 5 cm-radius lead sphere in vacuum. The source is made isotropic with standard cards alone (`BEAM` + `BEAMPOS`), with no `SOURCE` user routine.

## How the isotropic source works
- `BEAM` WHAT(3) is the beam divergence in mrad. Any value above 2000π mrad (about 6283.2) makes FLUKA emit isotropically; this deck uses `10000.0` (FLUKA manual, BEAM Note 7).
- WHAT(4) = WHAT(5) = 0.0 gives zero beam width, i.e. a true point.
- `BEAMPOS` holds the point (the origin here). Its direction cosines are ignored for an isotropic source (FLUKA manual, BEAMPOS Note 4).

## What This Input Includes
- Source: 3 MeV photons (`BEAM -0.003 ... PHOTON`), isotropic, at (0, 0, 0).
- Geometry: outer `BLCKHOLE` boundary, `VACUUM` filler, and a lead sphere (`SPH`, radius 5.0 cm) centred on the source.
- Materials/assignment: `BLCKHOLE`, `VACUUM`, `LEAD`.
- Thresholds: `EMFCUT` transport and production cuts at 1 keV.
- Scoring:
  - `USRBIN` energy deposition on a 10 × 10 × 10 mesh (1 cm bins) centred on the source (unit 30). This is the isotropy check.
  - `USRTRACK` photon track-length fluence in the lead (unit 31). WHAT(5) = sphere volume 4/3·π·5³ = 523.599 cm³.
  - `USRBDX` photon fluence escaping the sphere (unit 32). WHAT(6) = sphere area 4π·5² = 314.159 cm².
- Run control: `RANDOMIZ`, `START 20000.0`, `STOP`.

Every card was generated with the project's column formatter (values right-aligned to columns 20, 30, …, 70; SDUM from column 71).

## Verification (2026-10-18, `rfluka -M 1`, 20,000 primaries)
- The run completed with no errors, and the `.out` reports 20000 primaries run, `detector volume: 5.2360E+02 cm**3` and `detector area: 3.1416E+02 cm**2`.
- Isotropy, as the share of the total mesh energy deposition in each half-space:

  | Axis | Negative half | Positive half | Ratio +/− |
  |---|---|---|---|
  | x | 0.497 | 0.503 | 1.012 |
  | y | 0.504 | 0.496 | 0.983 |
  | z | 0.502 | 0.498 | 0.992 |

  Every half holds between 49.6% and 50.4% of the energy. No formal uncertainty was computed (one cycle), but a rough estimate of the statistical scatter for 20,000 photons is ±0.35 percentage points or more, so the imbalance is what random scatter would give.

- Contrast: the same deck with `BEAM` WHAT(3) = 0.0 (a pencil beam along +z) puts 98.7% of the energy in z > 0 and 1.3% in z < 0 (ratio 77). The ±x and ±y halves stay balanced. So the check does tell an isotropic source from a directed one.
- Run time: about 8 minutes for 20,000 primaries on one core, dominated by the 1 keV electron and photon cuts in lead.

## Canonical Input
- `photon_3mev_iso_pb_sphere.inp`
