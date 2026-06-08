# vis-tools

Post-processing and analysis workflow for GRMHD simulations and polarized radiative-transfer images used in:

**On the observational distinguishability of the Kerr and Kerr-Hayward metrics to EHT**  
arXiv: [2604.06128](https://arxiv.org/abs/2604.06128)

This repository contains the run scripts, parameter files, conversion utilities, mass-scaling scripts, and plotting/analysis tools used to reproduce the simulation and figure-generation workflow for the Kerr and modified Kerr-Hayward models studied in the paper.

The repository does **not** include the full simulation frame data (`.phdf`, `.h5`, or large image products), because these files are too large for GitHub. The scripts and parameter files are included so that the runs and analysis can be reproduced on a suitable local machine or HPC system. Contact the repository author (bukowieckan@gmail.com or nikola.bukowiecka@uri.edu) if the simulation frames are needed.

---

## Repository structure

```text
vis-tools/
├── KHLow/                  # Kerr-Hayward, low-spin model: KHARMA .par files, run script, logs/metadata
├── KHMid/                  # Kerr-Hayward, mid-spin model: KHARMA .par files, run script, logs/metadata
├── KerrLow/                # Kerr, low-spin model: KHARMA .par files, run script, logs/metadata
├── KerrMid/                # Kerr, mid-spin model: KHARMA .par files, run script, logs/metadata
├── QuickImageStats/        # Quick-look image statistics / helper analysis
├── bashScripts/            # SLURM/bash wrappers for ipole and paper-analysis scripts
├── ipole_mfitting/         # Mass-unit fitting workflow for ipole
├── vistools/               # Python analysis and plotting scripts
├── AddSpacetimeToKHARMA.md # Notes on adding a new spacetime to KHARMA
├── convertBash.sh          # Batch conversion from KHARMA .phdf outputs to .h5 files
└── README.md
```

The four model directories correspond to the fiducial simulations used in the paper:

| Directory | Metric | Spin | Length-scale parameter |
|---|---|---:|---:|
| `KerrLow/` | Kerr | `a = 0.1` | `L = 0` |
| `KerrMid/` | Kerr | `a = 0.5` | `L = 0` |
| `KHLow/` | modified Kerr-Hayward | `a = 0.1` | `L = 0.5` |
| `KHMid/` | modified Kerr-Hayward | `a = 0.5` | `L = 0.5` |

---

## External software used

This repository is not a standalone simulation code. It documents and drives a workflow using several external tools.

Required or expected components:

- [KHARMA](https://github.com/AFD-Illinois/kharma) for GRMHD simulations.
- [IPOLE](https://github.com/AFD-Illinois/ipole) for polarized radiative transfer.
- [pyharm](https://github.com/AFD-Illinois/pyharm) for reading, converting, and analyzing KHARMA/HARM outputs.
- Python 3 with packages commonly used in the scripts, including `numpy`, `pandas`, `matplotlib`, `h5py`, and `scipy`.
- An HPC environment with SLURM is assumed for most shell scripts.
- HDF5 / parallel HDF5 support for KHARMA and output conversion.

Most paths inside the shell scripts are cluster-specific and should be edited before use.

---

## Full workflow

The workflow has five main stages:

1. Add the modified spacetime to KHARMA.
2. Run KHARMA GRMHD simulations.
3. Convert KHARMA `.phdf` files to `.h5`.
4. Fit the time-dependent mass unit `M_unit` for ipole.
5. Add the modified spacetime to ipole, run ipole and generate the paper plots/diagnostics.

Each stage is described below.

---

## 1. Add the spacetime to KHARMA

The first step is to implement the modified Kerr-Hayward metric in KHARMA.

See:

```text
AddSpacetimeToKHARMA.md
```

The implementation notes point to the KHARMA coordinate-system source files where a new metric class and coordinate embedding must be added. In the implementation used here, the Kerr-Hayward metric was implemented in horizon-penetrating / ingoing Kerr-Schild-like coordinates as `KHinKS`.

In outline:

1. Edit KHARMA coordinate systems, for example:

   ```text
   kharma/kharma/coordinates/coordinate_systems.hpp
   ```

2. Define a new metric/coordinate class for the spacetime.

3. Implement the transformation/Jacobian needed to connect the chosen coordinate system to Boyer-Lindquist/native coordinates.

4. Register the coordinate embedding, for example in:

   ```text
   kharma/kharma/coordinates/coordinate_embedding.hpp
   ```

5. Rebuild KHARMA.

The same kind of metric implementation must be added to `ipole` before polarized radiative transfer can be run in the modified spacetime.

---

## 2. Run the KHARMA simulations

Each model directory contains a KHARMA parameter file and a simulation launch script. For example:

```text
KHLow/
├── mad_KHLow.par
├── sim_run.sh
└── parthinput.archive.*
```

The general pattern is:

```bash
cd KHLow
sbatch sim_run.sh
```

or, for a direct local/test run:

```bash
/path/to/kharma.host -i mad_KHLow.par
```

Repeat analogously for:

```text
KerrLow/
KerrMid/
KHLow/
KHMid/
```

The `.par` files define the simulation setup used for each model. The `parthinput.archive.*` files preserve run metadata and resolved parameter values from KHARMA/Parthenon outputs.

---

## 3. Convert `.phdf` simulation frames to `.h5`

KHARMA outputs simulation dumps as `.phdf` files. The scripts in this repository assume conversion to `.h5` files for later use with `ipole` and the analysis tools.

Use:

```bash
sbatch convertBash.sh <SimulationDirectoryName>
```

Example:

```bash
sbatch convertBash.sh KerrLow
```

The script uses `pyharm-convert` to convert all `.phdf` files in a simulation directory. Edit the paths inside `convertBash.sh` before running on a new system.

Typical logic:

```bash
./pyharm-convert /path/to/newSimulations/$1/*.phdf --nthreads $SLURM_CPUS_PER_TASK
```

where `$1` is the simulation directory name.

---

## 4. Fit the mass unit for ipole

The `ipole_mfitting/` directory contains scripts used to fit the time-dependent mass normalization used for radiative transfer.

The intended order is:

1. Edit the directory paths and settings inside the relevant Python and SLURM scripts in `ipole_mfitting/`.
2. Run the log-linear fitting batch script, for example:

   ```bash
   sbatch fit_loglinear_munit_sbatch.sh <SimulationDirectoryName>
   ```

3. Run:

   ```bash
   python mfit.py /path/to/newSimulations/<SimulationDirectoryName>
   ```

4. Confirm that the output file exists:

   ```text
   Mfit_file.txt
   ```

`Mfit_file.txt` is read by the ipole image-generation scripts. Each line gives the `M_unit` value corresponding to one converted simulation frame.

---

## 5. Run ipole polarized radiative transfer

The main image-production wrappers are in:

```text
bashScripts/
```

Relevant scripts include:

```text
ipoleBash_image.sh
ipoleBash_movie.sh
ipoleKH_Bash_image.sh
paper_plots_movie.sh
plotIpoleImage.sh
plot_Stokes_interpolate.sh
```

Ipole image-generation call is:

```bash
sbatch bashScripts/ipoleBash_image.sh <SimulationDirectoryName>
```

The script loops over converted `.h5` simulation frames, reads the corresponding `M_unit` from the `Mfit_file.txt`, and calls `ipole` with the selected model parameter file and output path.

Before running, edit:

- the path to the `ipole` executable;
- the path to the `ipole` model `.par` file;
- the path to the simulation `.h5` frames;
- the path to the `Mfit_file.txt`;
- output directories for image files.

There is also a movie-generation script for turning image outputs into time-dependent movies.

---

## 6. Run diagnostics and generate paper figures

The `bashScripts/` and `vistools/` directories contain scripts for the paper-level diagnostics and plots.

The analysis includes quantities shown in the paper, including:

- time evolution of Eddington ratio;
- dimensionless magnetic flux;
- jet efficiency and Blandford-Znajek comparison;
- time-averaged Stokes-I images;
- polarization ticks / EVPA morphology;
- `n = all`, `n = 0`, and `n = 1` image components;
- image-domain polarization metrics:
  - average linear polarization fraction,
  - net linear polarization fraction,
  - `|β₂|`,
  - `arg(β₂)`;
- brightness asymmetry;
- theoretical critical curve and inner-shadow overlays;
- horizontal and vertical image-plane intensity cuts;
- photon-ring / image-ring metrics;
- demagnification-related quantities.

Some plotting scripts are intentionally exploratory: sections may need to be commented or uncommented depending on which figure or diagnostic is being generated. Before running a full paper-plot workflow, check paths, model names, and output directories inside the relevant Python scripts.

Example wrappers include:

```bash
sbatch bashScripts/pythonBashScript_EddRatio.sh <SimulationDirectoryName>
sbatch bashScripts/pythonBashScript_calcJetParams.sh <SimulationDirectoryName>
sbatch bashScripts/pythonBashScript_betaModes.sh <SimulationDirectoryName>
sbatch bashScripts/pythonBashScript_plot.sh <SimulationDirectoryName>
```

---

## Notes on KHARMA installation on Apple Silicon / M1 Macs

These notes were used for a local KHARMA installation on an M1 Mac. They are included as a practical reference, not as a general supported installation recipe.

Prerequisite: install `gcc-13`.

Create or edit:

```bash
~/.config/kharma.sh
```

with:

```bash
export PATH="/opt/homebrew/opt/make/libexec/gnubin:$PATH"
PREFIX_PATH=/opt/homebrew/
C_NATIVE=/opt/homebrew/bin/gcc-13
CXX_NATIVE=/opt/homebrew/bin/g++-13
CXXFLAGS="-Wl,-ld_classic"
```

Install parallel HDF5:

```bash
brew install hdf5-mpi
```

Set library/include flags as needed:

```bash
LDFLAGS="-L/opt/homebrew/opt/llvm/lib/c++ -Wl,-rpath,/opt/homebrew/opt/llvm/lib/c++"
export LDFLAGS="-L/opt/homebrew/opt/llvm/lib"
export CPPFLAGS="-I/opt/homebrew/opt/llvm/include"
```

Optional LLVM path line that was not needed in this setup:

```bash
# echo 'export PATH="/opt/homebrew/opt/llvm/bin:$PATH"' >> ~/.zshrc
```

A test KHARMA run can then be launched as:

```bash
./kharma.host -i pars/tori_3d/mad_test.par
```

---

## Reproducibility notes

This repository is intended to document the complete computational workflow, but several pieces are system-specific:

- Simulation frames are not stored in the repository because of file size.
- SLURM scripts contain cluster-specific paths and module names.
- The `ipole` and KHARMA metric modifications must be available in the local code checkouts.
- The Python scripts may require path edits before running.
- Some analysis scripts are interactive/exploratory and may require selecting the desired section by commenting or uncommenting blocks.

A minimal reproduction path is:

```bash
# 1. Clone this repository
git clone https://github.com/nikolabukowiecka/vis-tools.git
cd vis-tools

# 2. Build KHARMA with the modified Kerr-Hayward metric

# 3. Run one model
cd KHLow
sbatch sim_run.sh

# 4. Convert outputs
cd ..
sbatch convertBash.sh KHLow

# 5. Fit M_unit
cd ipole_mfitting
sbatch fit_loglinear_munit_sbatch.sh KHLow
python mfit.py /path/to/newSimulations/KHLow

# 6. Run ipole
cd ..
sbatch bashScripts/ipoleBash_image.sh KHLow

# 7. Run analysis/plotting scripts
sbatch vis_tools/pythonBashScript_plot.sh KHLow
or
python3 vis_tools/paper_plots.py
```

---

## Data availability

The scripts, parameter files, and workflow documentation are provided in this repository. Full simulation outputs are not tracked because of their size. Contact the author for access to large simulation frames or derived data products if needed for reproduction (bukowieckan@gmail.com or nikola.bukowiecka@uri.edu).

---


## Authorship and acknowledgments

This repository documents the computational workflow associated with the paper:

**On the observational distinguishability of the Kerr and Kerr-Hayward metrics to EHT**  
by Nikola Bukowiecka, Angelo Ricarte, Prashant Kocherlakota, and Cora Prather.

The manuscript and scientific analysis were developed in collaboration with all co-authors. The simulation, post-processing, and figure-generation code in this repository was written by Nikola Bukowiecka.

Some theoretical calculations related to the Kerr-Hayward spacetime were performed by Prashant Kocherlakota. These calculations are included in supplementary Jupyter notebooks in this repository (2-KHZM-Critical-Exponents-Data.ipynb for the critical curve clculations and vF.ipynb for the inner shadow calculations).

---

## Citation

If you use this repository, please cite both the paper and the archived software release.

Paper:

```bibtex
@misc{bukowiecka2026kerrhaywardeht,
  title        = {On the observational distinguishability of the Kerr and Kerr-Hayward metrics to EHT},
  author       = {Bukowiecka, Nikola and Ricarte, Angelo and Kocherlakota, Prashant and Prather, Cora},
  year         = {2026},
  eprint       = {2604.06128},
  archivePrefix= {arXiv},
  primaryClass = {gr-qc},
  url          = {https://arxiv.org/abs/2604.06128}
}
```

Software archive:

```bibtex
@software{vis_tools_zenodo,
  author    = {Bukowiecka, Nikola},
  title     = {vis-tools: GRMHD and polarized radiative-transfer analysis workflow for Kerr-Hayward EHT simulations},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {},
  url       = {}
}
```

---

## Contact

For questions about reproducing the simulations or obtaining large data products, contact:

**Nikola Bukowiecka**  
Email: `nikola.bukowiecka@uri.edu` or `bukowieckan@gmail.com` 
