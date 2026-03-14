# Working Examples

One folder per FLUKA example. Each folder contains a canonical `.inp` and a short `README.md`.

## Examples
- `proton_100mev_usrbin_uncertainty/` - 100 MeV proton case with multiple DETECT scorers and USRBIN/USRBDX for uncertainty-style analysis.
- `proton_20mev_tepc_no_al_shell/` - 20 MeV proton TEPC geometry without aluminum shell, with detector and mesh scoring.
- `proton_20mev_tepc_with_al_shell/` - 20 MeV proton TEPC geometry including aluminum shell, with detector and mesh scoring.
- `proton_30mev_tepc_no_al_shell_disc_source/` - 30 MeV proton TEPC-like case without aluminum shell using a disc-source setup.
- `proton_62mev_500nm_detect_card/` - 62 MeV proton, 500 nm-scale detector-focused example centered on DETECT card usage.
- `proton_62mev_500nm_water_sphere/` - 62 MeV proton with 500 nm water sphere geometry and detector-focused scoring setup.
- `proton_126mev_500nm_water_cylinder/` - 126 MeV proton with 500 nm water cylinder geometry, DETECT/USRBIN, and boundary scoring.
- `proton_126mev_cyltepc_2cm_water_1um_sv/` - 126 MeV proton cylindrical TEPC-like setup with 2 cm water context and 1 um-scale sensitive volume.
- `proton_150mev_water_cube_5cm_air_multiscoring/` - 150 MeV proton beam 20 cm upstream of a 5 cm water cube in air, with dose, track-length, boundary fluence, and energy-deposition scoring.
- `proton_70mev_water_cube_10cm_air_multiscoring/` - 70 MeV proton beam in air on a centered 10 cm water cube, with USRBIN/USRTRACK/USRBDX multi-scoring.
- `proton_70mev_water_sphere_5cm_air_multiscoring/` - 70 MeV proton beam in air on a centered 5 cm-radius water sphere, with dose, track-length, boundary, and energy-deposition scoring.
- `pion_fluence_current_beryllium_2slabs/` - 50 GeV proton beam on a two-slab beryllium target with pion interface fluence/current (USRBDX), slab-wise pion fluence (USRTRACK), and 3D pion/energy maps (USRBIN).
- `pion_fluence_current_beryllium_3slabs/` - PION+ beam on a three-slab beryllium target with slab-wise/surrounding fluence (USRTRACK) and entrance/interface/exit boundary current (USRBDX).
- `neutron_1mev_point_source_water_cube_10cm_air_multiscoring/` - 1 MeV monoenergetic neutron point-source in air on a centered 10 cm water cube, with USRTRACK, USRBDX, and USRBIN dose/energy scoring.
- `neutron_245mev_point_source_water_cube_air_multiscoring/` - 2.45 MeV monoenergetic neutron point-source in air irradiating a 10 cm water cube, with USRTRACK, USRBDX, and USRBIN dose/energy scoring.
- `neutron_45mev_point_source_water_cube_5cm_air_multiscoring/` - 4.5 MeV monoenergetic neutron point-source at z=-30 cm irradiating a 5 cm water cube, with USRTRACK, USRBDX, and USRBIN dose/energy scoring.
