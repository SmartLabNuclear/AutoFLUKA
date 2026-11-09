*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 2020:  CERN                                        *
*     All Rights Reserved.                                             *
*                                                                      *
*     Source routine or FLUKA 4:                                       *
*                                                                      *
*     Created on 24 September 2020 by David Horvath & Roberto Versaci  *
*                                             ELI Beamlines            *
*                                                                      *
*  This is a simplified user written source routine utilizing separate *
*  source routine library.                                             *
*                                                                      *
*  Note that the beam card still has some meaning - in the scoring the *
*  maximum momentum used in deciding the binning is taken from the     *
*  beam momentum.  Other beam card parameters are obsolete.            *
*                                                                      *
*       Output variables:                                              *
*                                                                      *
*              nomore = if > 0 the run will be terminated              *
*                                                                      *
*----------------------------------------------------------------------*

      include 'source_library.inc'

*=== Source ===========================================================*

      subroutine SOURCE ( nomore )

      use source_library

      implicit none

      logical lfirst
      save lfirst
      data lfirst / .true. /

      integer nomore

      integer particle_code, ionid

      logical energy_logical_flag
      double precision momentum_energy, particle_weight

      logical gaussian_divergence_logical_flag
      double precision divergence_x, divergence_y

      double precision coordinate_x, coordinate_y, coordinate_z

      integer direction_flag
      double precision direction_cosx, direction_cosy, direction_cosz

      double precision polarization_cosx, polarization_cosy
      double precision polarization_cosz

      double precision particle_age
      double precision kshort_component
      double precision delayed_radioactive_decay

*     Function declarations

      double precision sample_flat_momentum_energy
      double precision sample_gaussian_momentum_energy
      double precision sample_maxwell_boltzmann_energy
      double precision sample_histogram_momentum_energy

      double precision sample_gaussian_distribution
      double precision sample_flat_distribution

      double precision FLRNDM, xdummy

c my own variables

      double precision emin , emax

      nomore = 0

      if ( lfirst ) then
         call initialization( lfirst )
      end if

*     Beginning of customizable code
*     ==============================

*     Accessing variables from the SOURCE card
*     ----------------------------------------
*     Values set on the SOURCE card can be accessed with the following
*     variables:
*        Numerical values (double precision):
*           WHASOU(1), WHATSOU(2), .., WHASOU(18)
*        SDUM text (8 character):
*           SDUSOU

*     Particle type
*     -------------
*     particle_code:
*        FLUKA particle code of the primary
*        See section 5.1 of the FLUKA manual for the list
*           of particle code
*     Default:
*        IJBEAM: Particle code of the primary defined on the
*           BEAM card

      particle_code = WHASOU(1)

*     Partice momentum / energy and weight
*     ------------------------------------
*     momentum_energy:
*        Set the momentum or the kinetic energy of the primary
*     energy_logical_flag:
*        Possible values:
*           .false. : The momentum_energy variable contains the momentum
*              of the particle
*           .true.  : The momentum_energy variable contains the kinetic
*              energy of the particle
*     particle weight:
*        Sets the initial weight of the primary
*     Default:
*        PBEAM: Particle momentum, even if energy was set on the BEAM
*           card.

      if ( SDUSOU == 'histo' ) then
         momentum_energy =
     +        sample_histogram_momentum_energy('histo.txt','MeV')
      else
         emin = WHASOU(4)/1.0D3
         emax = WHASOU(5)/1.0D3
         momentum_energy = sample_flat_momentum_energy(emin,emax)
      endif
      energy_logical_flag = .false.

      particle_weight = ONEONE

*        Implemented samplings functions
*        ---
*        momentum_energy = ...
*        ... = sample_flat_momentum_energy( [min], [max] )
*        ... = sample_gaussian_momentum_energy( [mean], [fwhm] )
*        ... = sample_maxwell_boltzmann_energy( [temperature] )
*           temperature is given in GeV
*        ... = sample_histogram_momentum_energy( [filename], [unit] )
*           possible [unit]s: "TeV",   "GeV",   "MeV",   "keV"   "eV"
*                             "TeV/c", "GeV/c", "MeV/c", "keV/c", "eV/c"
*
*           Histogram file has to have 3 columns:
*              Emin (of the bin),
*              Emax (of the bin),
*              dN/dE (particle fluence in the bin)

*        Implemented sampling subroutines
*        ---
*        sample_exponential_energy_importance:
*           Input variables:
*              - e_min, e_max, intensity_ratio = (int_e_max / int_e_min)
*           Output variables:
*              - momentum_energy, particle_weight
*           call sample_exponential_energy_importance( [e_min], [e_max],
*    &         [intensity_ratio], momentum_energy, particle_weight)

*     Beam angular divergence
*     -----------------------
*     divergence_x:
*        Beam angular divergence in the X-Z plane
*        (before applying beam diretion)
*     divergence_y:
*        Beam angular divergence in the Y-Z plane
*     gaussian_divergence_logical_flag:
*        If .true., divergence values are taken as fwhm of a Gaussian
*           distribution
*        If .false., divergence values are taken as full angle of a flat
*           distribution
*     Defaults:
*        DIVBM: Divergence set on the BEAM card [in rad]
*        LDVGSS: Flag indicating Gaussian divergence, set on the BEAM
*           card

      divergence_x = WHASOU(2)/1.0D3
      divergence_y = WHASOU(3)/1.0D3
      gaussian_divergence_logical_flag = .false.

*     Beam starting position
*     ----------------------
*     coordinate_x:
*        The X coordinate of the beam's starting position
*     coordinate_y:
*        The Y coordinate of the beam's starting position
*     coordinate_z:
*        The Z coordinate of the beam's starting position
*     Defaults:
*        XBEAM, YBEAM, ZBEAM: Coordinates set on the BEAMPOS card

      coordinate_x = XBEAM
      coordinate_y = YBEAM
      coordinate_z = ZBEAM

*        Implemented samplings functions
*        ---
*        coordinate_xyz = ...
*        ... = sample_flat_distribution( [min], [max] )
*        ... = sample_gaussian_distribution( [mean], [fwhm] )

*        Implemented sampling subroutines
*        ---
*        sample_annular_distribution:
*           Input variables:
*              - rmin, rmax [cm]
*              - Coordinates of the center of the annular distribution
*           Output variables:
*              - Modified coordinates of the sampled loaction
*                   (input values have been overwritten)
*           call sample_annular_distribution( [rmin], [rmax],
*          &   coordinate_x, coordinate_y )

*     Beam direction
*     --------------
*     direction_cosx:
*        Direction cosine of the beam with respect to the X-axis
*     direction_cosy:
*        Direction cosine of the beam with respect to the Y-axis
*     direction_cosz:
*        Direction cosine of the beam with respect to the Z-axis
*     direction_flag:
*        Possible values:
*           0: All 3 direction cosines are taken into account (values will
*              be normalized)
*           1: Only direction cosines with respect to the X- and Y-axis
*              are taken into account, the third cosine is calculated
*              with a positive sign
*           2: Only direction cosines with respect to the X- and Y-axis
*              are taken into account, the third cosine is calculated
*              with a negative sign
*     Defaults:
*        UBEAM, VBEAM, WBEAM: Direction cosines set on the BEAMPOS card

      direction_cosx = UBEAM
      direction_cosy = VBEAM
      direction_cosz = WBEAM

      direction_flag = 0

*        Implemented sampling subroutines
*        ---
*        sample_isotropic_direction:
*           Output variables:
*              - direction_cosx, direction_cosy, direction_cosz
*           call sample_isotropic_direction( direction_cosx, direction_cosy,
*          &   direction_cosz)

*     Other changeable parameters
*     ---------------------------
*     For most of the uses none of these parameters should be changed from
*     the defaults

*     polarization_cos_:
*        The three inputs indicate the direction cosines of the particle
*        polarization
*     particle_age:
*        Set the starting age of the primary particle in seconds
*     kshort_component:
*        The Kshort component of the K0/K0bar
*     delayed_radioactive_decay:
*        the delay for the radioactive decaye with respect to the
*        standard primary zero time

      polarization_cosx = -TWOTWO
      polarization_cosy = ZERZER
      polarization_cosz = ZERZER

      particle_age = ZERZER
      kshort_component = -TWOTWO
      delayed_radioactive_decay = ZERZER

*     End of customizable code - Do not change below
*     ==============================================

      call set_internal_flags()
      call set_beam_type( particle_code, ionid )
      call set_particle_momentum_energy_weight( particle_code, ionid,
     &     momentum_energy, energy_logical_flag, particle_weight )
      call set_particle_coordinates( coordinate_x, coordinate_y,
     &     coordinate_z )
      call set_particle_direction( direction_cosx, direction_cosy,
     &     direction_cosz, direction_flag, divergence_x, divergence_y,
     &     gaussian_divergence_logical_flag )
      call set_particle_polarization( polarization_cosx,
     &     polarization_cosy, polarization_cosz )
      call set_particle_age( particle_code, particle_age,
     &     kshort_component, delayed_radioactive_decay )
      call search_starting_region()

      return
*=== End of subroutine Source =========================================*
      end
