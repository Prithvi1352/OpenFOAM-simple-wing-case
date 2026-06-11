# OpenFOAM 3D Wing Study — NACA 2412 Wing Sweep Comparison

A complete OpenFOAM simulation study of a 3D NACA 2412 wing, comparing a straight (zero sweep) baseline against a 15° swept configuration. The flow is solved with transient, incompressible RANS using the PIMPLE algorithm. The repository contains both full case setups, from parametric geometry generation in Python through meshing, solution, and post-processing. The study serves as the high fidelity reference for my [vortex panel method solver](https://github.com/Prithvi1352/Vortex_panel_method), developed in parallel as a fast low-order comparison tool.

> **Status:** Work in progress. Both case setups are complete and running; results and post-processed comparisons (lift, drag, surface pressure, wall shear) will be added as the study progresses.

---

## Repository Structure

```
.                          # Baseline case — NACA 2412 wing, zero sweep
├── 0/                     # Initial and boundary conditions (U, p, k, omega, nut)
├── constant/              # Transport and turbulence properties, wing geometry (STL)
├── system/                # Meshing and solver dictionaries
├── Allrun / Allclean      # Full workflow automation
│
└── sweep_15/              # 15° swept wing case — same workflow
    └── generate_naca2412_swept_wing.py   # Parametric swept wing geometry generator
```

## Case Overview

| | |
|---|---|
| Geometry | NACA 2412 wing, generated parametrically (zero sweep and 15° sweep) |
| Meshing | `blockMesh` background + `snappyHexMesh` surface snapping and refinement |
| Solver | `pimpleFoam` (transient, incompressible) |
| Initialization | `potentialFoam` |
| Turbulence model | k-omega SST |
| Parallelization | 4-processor domain decomposition (`decomposeParDict`) |
| Post-processing | Wall shear stress and y+ function objects |

## Workflow

The `Allrun` script automates the full pipeline:

1. **`blockMesh`** — background hex mesh of the domain
2. **`checkMesh`** — background mesh quality verification
3. **`surfaceFeatureExtract`** — feature edge extraction from the wing STL
4. **`snappyHexMesh`** — refinement, snapping, and boundary layer addition around the wing
5. **`checkMesh -allTopology -allGeometry`** — full quality check on the final mesh
6. **`patchSummary`** — boundary condition verification across patches
7. **`potentialFoam`** — potential flow initialization for stable convergence
8. **`pimpleFoam`** — transient RANS solution

## Geometry Generation

The wing geometry is generated parametrically with `generate_naca2412_swept_wing.py`, which builds a watertight STL of the NACA 2412 wing at any specified sweep angle. This makes the study extensible: new sweep angles require only a regenerated STL and a copy of the case setup.

## Running a Case

Requires OpenFOAM with the standard utilities above.

```bash
./Allrun     # mesh + initialize + solve
./Allclean   # reset the case
```

The same workflow applies inside `sweep_15/`.

## Purpose

This study has two goals. First, to quantify the aerodynamic effect of wing sweep on an identical airfoil section, mesh strategy, and flow setup. Second, to provide trustworthy higher-fidelity reference data for validating low-order methods: the panel method solver predicts pressure distributions and lift in seconds, and this study quantifies where those predictions hold and where 3D and viscous effects take over.

## Results

*(Coming as the sweep comparison completes — lift and drag comparison, surface pressure distributions, wall shear and y+ fields.)*
