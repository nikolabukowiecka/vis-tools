import matplotlib.pyplot as plt
import numpy as np
import h5py
import pandas as pd
import sys, glob, os
import json
import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.ticker as ticker
from scipy import stats
mpl.rcParams['mathtext.fontset'] = 'stix'

#load data
baseDir = '/project/u2grc/Nikola/newSimulations/'
folders = ['KerrLow',
           'KHLow',
           'KerrMid',
           'KHMid']

dumpsDir = [os.path.join(baseDir, folder) for folder in folders]
files = ["_" + folder + ".csv" for folder in folders]

observablesDir = os.path.join(baseDir, 'observables')
munitsDir = os.path.join('/project/u2grc/Nikola', 'ipole/mfitting')
munits = {
    folder: pd.read_csv(os.path.join(munitsDir, folder, 'Mfit_file.txt'))
    for folder in folders
}

#Jet params (from dumps): Mdot, Edot at r = 5, PhiB at the horizon
paramsDir =  os.path.join(baseDir, 'params')
paramsFiles = {
    folder: pd.read_csv(os.path.join(paramsDir, f"jetParams_{folder}.csv"))
    for folder in folders
}

#Eddington ratio: Mdot, MdotEdd
# eddRatioDir =  os.path.join(baseDir, 'observables/n_1_400_20muas')
eddRatioFiles = {
    folder: pd.read_csv(os.path.join(paramsDir, f"Edd_ratio_{folder}.csv"))
    for folder in folders
}

# Create jet efficiency dictionary
jetEfficiency5 = {}
jetEfficiency10 = {}
jetEfficiency50 = {}

for folder in folders:
    df = paramsFiles[folder]
    mdot_5 = df['t/Mdot_5'].values
    edot_5 = df['t/Edot_5'].values

    mdot_10 = df['t/Mdot_10'].values
    edot_10 = df['t/Edot_10'].values

    mdot_50 = df['t/Mdot_50'].values
    edot_50 = df['t/Edot_50'].values
    
    jet_eff_5 = (mdot_5 - edot_5) / np.mean(mdot_5)

    # jet_eff_5 = 1 - (edot_5 / mdot_5)
    # print(f"{folder}, {max(jet_eff_5)}")


    jet_eff_10 = np.abs(edot_10 - mdot_5) / np.mean(mdot_5)
    jet_eff_50 = np.abs(edot_50 - mdot_5) / np.mean(mdot_5)
    
    jetEfficiency5[folder] = jet_eff_5
    jetEfficiency10[folder] = jet_eff_10
    jetEfficiency50[folder] = jet_eff_50

    # print(f"Mean jet efficiency at 5 for {folder} (Mdot_5, Edot_5): {np.mean(jet_eff_5)}")
    # print(f"Mean jet efficiency at 10 for {folder} (Mdot_5, Edot_10): {np.mean(jet_eff_10)}")
    # print(f"Mean jet efficiency at 50 for {folder} (Mdot_5, Edot_50): {np.mean(jet_eff_50)}")



#Beta modes (with 20muas blurring )
# CREATE: Beta modes (from n_0_400_20muas)
configs_obs = {
    #"n_-1_160_20muas": "betaModes",
    "n_-1_400_20muas": "betaModes",
    "n_0_400_20muas":  "betaModes",
    "n_1_400_20muas":  "betaModes",
}

observablesData = {
    folder: {
        subdir: pd.read_csv(os.path.join(observablesDir, subdir, f"{prefix}_{folder}.csv"))
        for subdir, prefix in configs_obs.items()
    }
    for folder in folders
}

#Averaged data
#Create: averaged+averageBeta for n_0_400 + n_1_400
averaged_Dir = os.path.join(baseDir, 'averageData')

# Build averagedData dictionary dynamically
subdirs = ["n_-1_400", "n_0_400", "n_1_400"]
#subdirs = ["n_0_400"]

averagedData = {}
for folder in folders:
    averagedData[folder] = {}
    for subdir in subdirs:
        subdir_path = os.path.join(averaged_Dir, subdir)
        # Find the .png Stokes I image for this folder
        png_files = glob.glob(os.path.join(subdir_path, f"*{folder}*.Stokes_I_.png"))
        # Find the .h5 file for this folder
        h5_files = glob.glob(os.path.join(subdir_path, f"*{folder}*.h5"))

        if len(png_files) == 0:
            print(f"No PNG image found for {folder} in {subdir}")
            img_path = None
        else:
            img_path = png_files[0]  # take first match

        if len(h5_files) == 0:
            print(f"No H5 file found for {folder} in {subdir}")
            h5_path = None
        else:
            h5_path = h5_files[0]  # take first match

        averagedData[folder][subdir] = {
            "image": img_path,
            "h5file": h5_path
        }
#print(averagedData['KHLow']['n_-1_400'].keys())

#Ipole files
ipoleDir = [os.path.join(baseDir, os.path.splitext(file)[0].split('_')[1], 'ipole') for file in files]


#interpolatedCurves = {
#    folder: {
#        os.path.join(baseDir, folder, "ipole", subdir, f"interpolated_curves_centres_ipole_{folder}.csv")
#        for subdir in subdirs
#    }
#    for folder in folders
#}


## Calculations
#print(paramsFiles['KerrLow'])

cgs = {
    'CL': 2.99792458e10,
    'QE': 4.80320680e-10,
    'EE': 4.80320680e-10,
    'ME': 9.1093826e-28,
    'MP': 1.67262171e-24,
    'MN': 1.67492728e-24,
    'HPL': 6.6260693e-27,
    'HBAR': 1.0545717e-27,
    'KBOL': 1.3806505e-16,
    'GNEWT': 6.6742e-8,
    'SIG': 5.670400e-5,
    'AR': 7.5657e-15,
    'THOMSON': 0.665245873e-24,
    'JY': 1.e-23,
    'PC': 3.085678e18,
    'AU': 1.49597870691e13,
    'MSOLAR': 1.989e33,
    'RSOLAR': 6.96e10,
    'LSOLAR': 3.827e33
}
def get_units(MBH, M_unit, tp_over_te=3, gam=4/3):
    """Get derived units and certain quantities for a system, given a BH mass in Msolar,
    and accretion density M_unit.
    Arguments tp_over_te and gam only matter for calculating Thetae_unit.
    Also note the calculation of Mdotedd assumes 10% efficiency.

    :param MBH: Black hole mass in solar masses
    :param M_unit: Density unit in grams, as fit by imaging with e.g. ``ipole``
    """
    out = {}
    MBH *= cgs['MSOLAR'] # Take input in solar masses
    out['MBH'] = MBH
    out['M_unit'] = M_unit
    out['L_unit'] = L_unit = cgs['GNEWT']*MBH / cgs['CL']**2 #GNEWT - Gravitational constant
    out['T_unit'] = L_unit / cgs['CL'] #CL - speed of light 

    out['RHO_unit'] = RHO_unit  = M_unit / (L_unit ** 3)
    out['U_unit'] = RHO_unit * cgs['CL'] ** 2
    out['B_unit'] = cgs['CL'] * np.sqrt(4. * np.pi * RHO_unit)
    out['Ne_unit'] = RHO_unit / (cgs['MP'] + cgs['ME'])

    if tp_over_te is not None:
        out['Thetae_unit'] = (gam - 1.) * cgs['MP'] / cgs['ME'] / (1. + tp_over_te)
    else:
        out['Thetae_unit'] = cgs['MP'] / cgs['ME']

    out['Mdotedd'] = 4.*np.pi * cgs['GNEWT'] * MBH * cgs['MP'] / (0.1 * cgs['CL'] * cgs['THOMSON'])

    # Add constants
    out.update(cgs)

    return out

#Since radial profiles are already averaged, I need to average Munits to for the unit coversion too:
unitsAveraged = {
    "KerrLow": get_units(6.5e9, np.mean(munits["KerrLow"])),
    "KerrMid": get_units(6.5e9, np.mean(munits["KerrMid"])),
    "KHLow":   get_units(6.5e9, np.mean(munits["KHLow"])),
    "KHMid":   get_units(6.5e9, np.mean(munits["KHMid"])),
}

#print(np.mean(paramsFiles['KerrLow']['t/Phi_b']/(np.sqrt(np.mean(paramsFiles['KerrLow']['t/Mdot_5'])))))
#print(np.mean(paramsFiles['KerrMid']['t/Phi_b']/(np.sqrt(np.mean(paramsFiles['KerrMid']['t/Mdot_5'])))))
#print(np.mean(paramsFiles['KHLow']['t/Phi_b']/(np.sqrt(np.mean(paramsFiles['KHLow']['t/Mdot_5'])))))
#print(np.mean(paramsFiles['KHMid']['t/Phi_b']/(np.sqrt(np.mean(paramsFiles['KHMid']['t/Mdot_5'])))))

########################################################################################################################################################################

etaBZ = {}   
for folder in folders:
    #print(folder)
    df = paramsFiles[folder] #when reading from simulation files, we're in geometrical units c=G=1
    #PhiB = df['t/Phi_b'] #at the horizon # [B] = sqrt(4pi)*c*sqrt(rho)
    # Compute dimensionless Phi_B
    # PhiB_dim = df['t/Phi_b'] / np.sqrt(np.mean(df['t/Mdot_5']))
    PhiB_dim = np.sqrt(4*np.pi) * df['t/Phi_b'] / np.sqrt(np.abs(df['t/Mdot_5']))
    Edot = df['t/Edot_5']
    df2 = eddRatioFiles[folder]
    spinDict = {
    'KerrLow': 0.1,
    'KHLow': 0.1,
    'KerrMid': 0.5,
    'KHMid': 0.5
    }
    L = 0.5
    spinToHorizon = 1.0 + np.sqrt(1.0 - spinDict[folder]**2)
    if folder == 'KerrLow' or folder == 'KerrMid':
        Omega_H = np.abs(spinDict[folder]) / (2*spinToHorizon) #Omega-H <-> horizonAngularVelocity
        #print(f"{folder}, {spinToHorizon}, {Omega_H}")
    # elif folder == 'KHMid':
    #     #evaulated for theta = pi/2 equatorial observer
    #     Omega_H = (2.78207 * spinDict[folder] * (0.359445 - 0.359445 * (1 - 0.431002 / (0.129201 + 2 * L**4))) 
    #                - 2.78207 * ((0.359445 + spinDict[folder]**2)**2 - spinDict[folder]**2 * (spinDict[folder]**2 + 0.359445 * (1 - 0.431002 / (0.129201 + 2 * L**4)))))
    # elif folder == 'KHLow':
    #     #evaulated for theta = pi/2 equatorial observer
    #     Omega_H = (5.15122 * spinDict[folder] * (0.194129 - 0.194129 * (1 - 0.171066 / (0.0376859 + 2 * L**4))) 
    #                - 5.15122 * ((0.194129 + spinDict[folder]**2)**2 - spinDict[folder]**2 * (spinDict[folder]**2 + 0.194129 * (1 - 0.171066 / (0.0376859 + 2 * L**4)))))
    elif folder == 'KHLow':
        rH = 1.97877
        Omega_H = 0.0254743
    elif folder == 'KHMid':
        rH = 1.8429
        Omega_H = 0.137126
    kappa = 0.05
    #https://arxiv.org/pdf/1108.0412
    #etaBZ[folder] = kappa / (4*np.pi) * PhiB**2 * Omega_H**2 * (1. + 1.38*Omega_H**2 - 9.2*Omega_H**4)
    #print("Omega_H**2 = ", Omega_H**2)
    #print("Phi_B**2 = ", np.mean(PhiB_dim**2))
    #print(f"{folder}: Phi_B_dim = {np.mean(PhiB_dim)} ")
    etaBZ[folder] = np.mean(( kappa / (4*np.pi) ) * PhiB_dim**2 * Omega_H**2)
    #etaEM = np.mean(-Edot/np.abs(df['t/Mdot_5']))
    #print(f"{folder}: <eta_Edot> = {etaEM}")
    #print(f"{folder}: <eta_BZ_theory> = {np.mean(etaBZ[folder]):.5f}")

    #print(4*np.pi* etaEM/(np.mean(PhiB_dim**2) * Omega_H**2))

########################################################################################################################################################################

## Plots

plot_style = {
    'KerrLow': dict(label='a0.1.L0', color='red', linewidth=2),
    'KerrMid': dict(label='a0.5.L0', color='blue', linewidth=2),
    'KHLow': dict(label='a0.1.L0.5', color='orange', linewidth=1),
    'KHMid': dict(label='a0.5.L0.5', color='purple', linewidth=1),
}

# Directory to save figures

figDir = os.path.join(baseDir, 'figures')
os.makedirs(figDir, exist_ok=True)

################################################################################################################
'''
# 3-panel figure (stacked vertically) of Eddington ratios, magnetic flux and jet efficiency
#fig, axes = plt.subplots(3, 1, figsize=(8, 12), sharex=True)  # share x-axis for time

# 4-panel figure of Eddington ratios, magnetic flux and jet efficiency (split by folders)
fig, axes = plt.subplots(2, 2, figsize=(16, 8), sharex=True) 
axes = axes.ravel()


# 1) Eddington ratios
ax = axes[0]
for folder in folders:
    df = eddRatioFiles[folder]
    style = plot_style[folder].copy()
    style['label'] = f"{style['label']} " + r'$\dot{M} / \dot{M}_{\mathrm{Edd}}$'
    ax.plot(df['t'], df['Mdot']/df['MdotEdd'], **style, alpha=0.8) #this is the Eddington ratio in terms of mass accretion rate, using a fiducial radiative efficiency of 0.1.
    ax.axhline(
    y=np.percentile(df['Mdot']/df['MdotEdd'], 50),
    color=style.get("color", "black"),
    linestyle='--',
    linewidth=1.2
    #label=f"{style['label']} " + r'$\mathrm{50th\ percentile}$'
    )
ax.set_ylabel(r'$\dot{M} / \dot{M}_{\mathrm{Edd}}$')
ax.set_title('Eddington Ratio')
ax.legend()
#ax.grid(True, alpha=0.3)


# 2) PhiB
ax = axes[1]
PhiB_dim_list = []
PhiB_list = []
PhiB_dim_Std_list = []
i=0
for folder in folders:
    df = paramsFiles[folder]
    style = plot_style[folder].copy()

    # Compute dimensionless Phi_B
    PhiB_dim = np.sqrt(4 * np.pi) * df['t/Phi_b'] / np.sqrt(np.mean(df['t/Mdot_5']))
    PhiB_dim_list.append(PhiB_dim)
    PhiB_list.append(df['t/Phi_b'])
    PhiB_dim_Std = np.std(PhiB_dim)
    PhiB_dim_Std_list.append(PhiB_dim_Std)
    i=i+1
    # Main Phi_B evolution curve
    ax.plot(
        df['coord/t'],
        PhiB_dim,
        color=style['color'],
        linewidth=style['linewidth'],
        alpha = 0.8,
        label=f"{style['label']} " + r'$\phi_B$'
    )

    # Horizontal line for average Phi_B
    ax.axhline(
        y=np.mean(PhiB_dim),
        color=style['color'],
        linestyle='--',
        linewidth=1.2
        #label=f"{style['label']} " + r'$\langle \phi_B \rangle$'
    )
print(f"<PhiB_dim_KL> - <PhiB_dim_KHL> = {np.mean(PhiB_dim_list[0]) - np.mean(PhiB_dim_list[1]):.3f}")
print(f"<PhiB_dim_KM> - <PhiB_dim_KHM> = {np.mean(PhiB_dim_list[2]) - np.mean(PhiB_dim_list[3]):.3f}")
for j in range(0,4):
    print(f"PhiB_dim_Std of {folders[j]} = {PhiB_dim_Std_list[j]}")
# for j in range(0,4):
#     print(f"PhiB_dim_ of {folders[j]} = {np.mean(PhiB_dim_list[j])}")
# print(f"<PhiB_KL> / <PhiB_KHL> = {np.mean(PhiB_list[0]/PhiB_list[1]):.3f}")
# print(f"<PhiB_KM> / <PhiB_KHM> = {np.mean(PhiB_list[2]/PhiB_list[3]):.3f}")
ax.set_ylabel(r'$\phi_B$')
ax.set_title('Dimensionless Magnetic Flux ' + r'$\phi_B$')
ax.legend()
#ax.grid(True, alpha=0.3)


# Function to plot jet efficiency for a subset of folders
def plot_jet_efficiency(ax, folder_subset):
    n_bins = 12  # number of time windows
    for folder in folder_subset:
        df = paramsFiles[folder]
        style = plot_style[folder].copy()
        t = df['coord/t'].values
        eta = jetEfficiency5[folder]

        print(f"{folder}: <eta_BZ_simulation> = {np.mean(eta):.3f}")

        # Bin eta into n_bins windows 
        t_min, t_max = t.min(), t.max()
        bins = np.linspace(t_min, t_max, n_bins+1)
        bin_centers = 0.5 * (bins[:-1] + bins[1:])

        eta_means, eta_stds = [], []

        # Draw bin borders (light green)
        for edge in bins:
            ax.axvline(edge, color='green', alpha=0.6, linewidth=0.8, zorder=0)

        for i in range(n_bins):
            mask = (t >= bins[i]) & (t < bins[i+1])
            eta_bin = eta[mask]
            if len(eta_bin) > 0:
                eta_means.append(np.mean(eta_bin))
                eta_stds.append(np.std(eta_bin))
            else:
                eta_means.append(np.nan)
                eta_stds.append(np.nan)

        eta_means = np.array(eta_means)
        eta_stds = np.array(eta_stds)
        
        #print(f"Std of error means for {folder}: {np.std(eta_means)}")
        
        # Plot error bars + main curve
        ax.errorbar(bin_centers, eta_means, yerr=eta_stds,
                    fmt='o', capsize=4, color=style['color'], alpha=0.8)
                    #label=f"{style['label']} (binned)")
        ax.plot(df['coord/t'], jetEfficiency5[folder],
                color=style['color'], linewidth=style['linewidth'],
                alpha=0.6, label=f"{style['label']} " + r'$\eta_{\mathrm{jet}}$')
        ax.axhline(y=np.mean(jetEfficiency5[folder]),
                   color=style['color'], linestyle='--', linewidth=1.2)
                   #label=f"{style['label']} " + r'$\langle \eta_{\mathrm{jet}} \rangle$')
        ax.axhline(y=np.mean(etaBZ[folder]),
                   color=style['color'], linestyle='-', linewidth=1.2)
                   #label=f"{style['label']} " + r'$\langle \eta_{\mathrm{BZ}} \rangle$')

    ax.set_ylabel(r'$\eta_{\mathrm{jet}}$')
    ax.legend()
    #ax.grid(True, alpha=0.3)

##########################
# 3) Jet efficiency for Low spin
plot_jet_efficiency(axes[2], [folders[0], folders[1]])
axes[2].set_title('Jet Efficiency: Low spin')

##########################
# 4) Jet efficiency for Mid spin
plot_jet_efficiency(axes[3], [folders[2], folders[3]])
axes[3].set_title('Jet Efficiency: Mid spin')
axes[3].set_xlabel('$t_g$')

##########################
axes[3].xaxis.set_major_locator(ticker.MaxNLocator(nbins=12))  # More ticks
plt.tight_layout()
fig_path = os.path.join(figDir, 'four_panel_vertical.png')
fig.savefig(fig_path, dpi=300)
plt.close(fig)

'''
###########################################################################################################################################################################

## Figure for IPOLE Stokes I with total linear polarization ticks

#Add shadow/inifity ring 
a_Val = 0.5
l_Val = 0.
a_Val_str = str(a_Val).replace('.', 'dot')
l_Val_str = str(l_Val).replace('.', 'dot')
file_name_str_KerrMid = "/project/u2grc/Nikola/newSimulations/Data/Fig2a_Kerr_Crit_Params_a" + a_Val_str + "_l_" + l_Val_str + "_inc_163deg" ".csv"
a_Val = 0.1
a_Val_str = str(a_Val).replace('.', 'dot')
file_name_str_KerrLow = "/project/u2grc/Nikola/newSimulations/Data/Fig2a_Kerr_Crit_Params_a" + a_Val_str + "_l_" + l_Val_str + "_inc_163deg" ".csv"

a_Val = 0.5
l_Val = 0.5
a_Val_str = str(a_Val).replace('.', 'dot')
l_Val_str = str(l_Val).replace('.', 'dot')
file_name_str_KHMid = "/project/u2grc/Nikola/newSimulations/Data/Fig2d_KHZM4_Crit_Params_a" + a_Val_str + "_l_" + l_Val_str + "_inc_163deg" ".csv"
a_Val = 0.1
a_Val_str = str(a_Val).replace('.', 'dot')
file_name_str_KHLow = "/project/u2grc/Nikola/newSimulations/Data/Fig2d_KHZM4_Crit_Params_a" + a_Val_str + "_l_" + l_Val_str + "_inc_163deg" ".csv"

KHZM4_Crit_Params_File = pd.read_csv(file_name_str_KHLow)
alpha_M_KHLow             = (KHZM4_Crit_Params_File.alpha)
beta_M_KHLow             = (KHZM4_Crit_Params_File.beta)
gamma_p_M_KHLow           = (KHZM4_Crit_Params_File.gamma)
innerShadow_KHL_File = pd.read_csv("/project/u2grc/Nikola/newSimulations/Data/Fig20b-KH-a-0p1-L-0p5.csv")
alpha_M_KHLow_IS = (innerShadow_KHL_File.alpha_phys)
beta_M_KHLow_IS = (innerShadow_KHL_File.beta_phys)

KHZM4_Crit_Params_File = pd.read_csv(file_name_str_KHMid)
alpha_M_KHMid             = (KHZM4_Crit_Params_File.alpha)
beta_M_KHMid             = (KHZM4_Crit_Params_File.beta)
gamma_p_M_KHMid           = (KHZM4_Crit_Params_File.gamma)
innerShadow_KHMid_File = pd.read_csv("/project/u2grc/Nikola/newSimulations/Data/Fig20d-KH-a-0p5-L-0p5.csv")
alpha_M_KHMid_IS = (innerShadow_KHMid_File.alpha_phys)
beta_M_KHMid_IS = (innerShadow_KHMid_File.beta_phys)

Kerr_Crit_Params_File = pd.read_csv(file_name_str_KerrLow)
alpha_M_KerrLow             = (Kerr_Crit_Params_File.alpha)
beta_M_KerrLow              = (Kerr_Crit_Params_File.beta)
gamma_p_M_KerrLow             = (Kerr_Crit_Params_File.gamma)
innerShadow_KerrLow_File = pd.read_csv("/project/u2grc/Nikola/newSimulations/Data/Fig20a-KH-a-0p1-L-0p001.csv")
alpha_M_KerrLow_IS = (innerShadow_KerrLow_File.alpha_phys)
beta_M_KerrLow_IS = (innerShadow_KerrLow_File.beta_phys)


Kerr_Crit_Params_File = pd.read_csv(file_name_str_KerrMid)
alpha_M_KerrMid             = (Kerr_Crit_Params_File.alpha)
beta_M_KerrMid             = (Kerr_Crit_Params_File.beta)
gamma_p_M_KerrMid             = (Kerr_Crit_Params_File.gamma)
innerShadow_KerrMid_File = pd.read_csv("/project/u2grc/Nikola/newSimulations/Data/Fig20c-KH-a-0p5-L-0p001.csv")
alpha_M_KerrMid_IS = (innerShadow_KerrMid_File.alpha_phys)
beta_M_KerrMid_IS = (innerShadow_KerrMid_File.beta_phys)

rad_to_muas = 206265 * 1e6 #rad to microarcseconds
M = 6.5 * 1e9 * 1.989 * 1e30 #M87 mass (6.5e9 solar masses in kg)
dist = 16.8 * 1e6 * 3.0856 * 1e16 #distance to M87 in m (16.8Mpc)
G = 6.674 * 1e-11
c = 2.997 * 1e8

rg = G * M / c**2 #gravtiational length scale or "1M"
M_to_uas = rad_to_muas * rg/dist

def MtoMuas(alpha_M, beta_M):
    alpha_mu = alpha_M * M_to_uas
    beta_mu  = beta_M  * M_to_uas
    return alpha_mu, beta_mu

def MtoMuas1(value_M):
    return value_M * M_to_uas



alpha_mu_KerrLow, beta_mu_KerrLow = MtoMuas(alpha_M_KerrLow, beta_M_KerrLow)
alpha_mu_KerrLow_IS, beta_mu_KerrLow_IS = MtoMuas(alpha_M_KerrLow_IS, beta_M_KerrLow_IS)

#print("Shadow diameter from alpha, theoretical,  KerrLow= ", np.abs(np.min(alpha_mu_KerrLow))+np.abs(np.max(alpha_mu_KerrLow)))
# print("Shadow diameter from beta, theoretical,  KerrLow= ", 2 * np.abs(np.max(beta_mu_KerrLow)))
alpha_mu_KerrMid, beta_mu_KerrMid = MtoMuas(alpha_M_KerrMid, beta_M_KerrMid)
alpha_mu_KerrMid_IS, beta_mu_KerrMid_IS = MtoMuas(alpha_M_KerrMid_IS, beta_M_KerrMid_IS)

#print("Shadow diameter from alpha, theoretical,  KerrMid= ", np.abs(np.min(alpha_mu_KerrMid))+np.abs(np.max(alpha_mu_KerrMid)))
alpha_mu_KHLow, beta_mu_KHLow = MtoMuas(alpha_M_KHLow, beta_M_KHLow)
alpha_mu_KHLow_IS, beta_mu_KHLow_IS = MtoMuas(alpha_M_KHLow_IS, beta_M_KHLow_IS)

#print("Shadow diameter from alpha, theoretical,  KHLow= ", np.abs(np.min(alpha_mu_KHLow))+np.abs(np.max(alpha_mu_KHLow)))
alpha_mu_KHMid, beta_mu_KHMid = MtoMuas(alpha_M_KHMid, beta_M_KHMid)
alpha_mu_KHMid_IS, beta_mu_KHMid_IS = MtoMuas(alpha_M_KHMid_IS, beta_M_KHMid_IS)

#print("Shadow diameter from alpha, theoretical,  KHMid= ", np.abs(np.min(alpha_mu_KHMid))+np.abs(np.max(alpha_mu_KHMid)))

gamma_p_list = {
    "KerrLow": (gamma_p_M_KerrLow, "b"),
    "KerrMid": (gamma_p_M_KerrMid, "b"),
    "KHMid":   (gamma_p_M_KHMid, "b"),
    "KHLow":   (gamma_p_M_KHLow, "b")
}

ring_params = {
    "KerrMid": (alpha_mu_KerrMid, beta_mu_KerrMid, "b"),
    "KerrLow": (alpha_mu_KerrLow, beta_mu_KerrLow, "b"),
    "KHMid":   (alpha_mu_KHMid,   beta_mu_KHMid,   "b"),
    "KHLow":   (alpha_mu_KHLow,   beta_mu_KHLow,   "b"),
}

inner_params = {
    "KerrMid": (alpha_mu_KerrMid_IS, beta_mu_KerrMid_IS, "b"),
    "KerrLow": (alpha_mu_KerrLow_IS, beta_mu_KerrLow_IS, "b"),
    "KHMid":   (alpha_mu_KHMid_IS,   beta_mu_KHMid_IS,   "b"),
    "KHLow":   (alpha_mu_KHLow_IS,   beta_mu_KHLow_IS,   "b"),
}

def ring_metrics(alpha, beta):

    alpha_max = np.nanmax(alpha)
    alpha_min = np.nanmin(alpha)
    beta_max = np.nanmax(beta)
    beta_min = np.nanmin(beta)

    D_alpha = alpha_max - alpha_min #horizontal diameter of the critical curve (“shadow diameter from alpha”).
    D_beta = beta_max - beta_min
    #center estimate
    x_c = 0.5 * (alpha_max + alpha_min) #horizontal offset of the ring center (frame-dragging + inclination tends to shift it)
    y_c = 0.5 * (beta_max + beta_min)

    #left-right asymmetry (0 is symmetric abount alpha=0)
    A_alpha = (np.abs(alpha_max) - np.abs(alpha_min)) / (np.abs(alpha_max) + np.abs(alpha_min) + 1e-30) #quantifies whether the ring is shifted toward positive or negative due to frame dragging.

    #Normalized horizontal displacmenet (0 if centered) (*2 to put in on the [0,1] scale rel to diameter)
    A_disp = (2.0 * np.abs(x_c)) / (D_alpha + 1e-30) #center offset normalized by diameter (dimensionless).

    #fractional shape asymmetry https://journals.aps.org/prd/pdf/10.1103/PhysRevD.111.103042
    A_shape = (beta_min - beta_max) / (alpha_min + alpha_max)

    # r = np.sqrt((alpha - x_c)**2 + (beta - y_c)**2)
    # r_mean = np.nanmean(r)
    # A_shape = (np.nanmax(r) - np.nanmin(r)) / (r_mean + 1e-30) #noncircularity of the curve about its center

    return dict(
        D_alpha = D_alpha, D_beta = D_beta, x_c = x_c, y_c = y_c,
        A_alpha = A_alpha, A_disp = A_disp, A_shape = A_shape
    )

for folder in folders:
    if folder in ring_params:
            alpha_mu, beta_mu, color = ring_params[folder]
            #beta stored only beta>=0; so need to concatenate alpha too to keep the paring
            beta_mu = np.concatenate([beta_mu, -beta_mu])
            alpha_mu = np.concatenate([alpha_mu, alpha_mu])
            dict_ring = ring_metrics(alpha_mu, beta_mu)
            # print(
            #     f"Critical curve metrics, theoretical, {folder}: "
            #     f"D_alpha={dict_ring['D_alpha']:.3f}, D_beta={dict_ring['D_beta']:.3f}, D_alpha/D_beta={(dict_ring['D_alpha']/dict_ring['D_beta']):.3f}, x_c={dict_ring['x_c']:.3f}, "
            #     #f"A_disp={dict_ring['A_disp']:.4f}, A_alpha={dict_ring['A_alpha']:.4f}, A_shape={dict_ring['A_shape']:.4f}"
            # )

for folder in folders:
    if folder in inner_params:
        alpha_mu_IS, beta_mu_IS, color = inner_params[folder]
        dict_ring2 = ring_metrics(alpha_mu_IS, beta_mu_IS)
        # print(
        #          f"Inner shadow metrics, theoretical, {folder}: "
        #          f"D_alpha={dict_ring2['D_alpha']:.3f}, D_beta={dict_ring2['D_beta']:.3f}, D_alpha/D_beta={(dict_ring2['D_alpha']/dict_ring2['D_beta']):.3f}, x_c={dict_ring2['x_c']:.3f}, "
        #     )
        #print("Inner shadow metrics, theoretical: FROM PRASHANT - help with a fix")
        
#subdir = ["n_-1_400", "n_0_400", "n_1_400"] 
subdirs = ["n_-1_400", "n_0_400", "n_1_400"] 
diameters2D = {}

def calc_diameter2D(I, x, y):
    d = np.gradient(I, y, x)


nrows = len(subdirs)
ncols = len(folders)

###########################################################################################################################################################
'''
def calc_flux(intensity):
    return np.sum(intensity)

fig, axes = plt.subplots(
    nrows, ncols + 1, figsize=(16, 12),
    gridspec_kw={'width_ratios': [1]*ncols + [0.05], 'wspace': 0.05},
    constrained_layout=True
)

cmap = plt.get_cmap('afmhot').copy()
cmap.set_bad('black')
for i, subdir in enumerate(subdirs):
    row_im = None
    for j, folder in enumerate(folders):
        ax = axes[i, j]           # image axes
        cax = axes[i, -1]
        img_path = averagedData[folder][subdir]["h5file"]
        img_path2 = averagedData[folder][subdir]["image"]

        if os.path.exists(img_path):
            img = mpimg.imread(img_path2)
            
            # set extent (assumption of square image)
            hfp = h5py.File(img_path,'r')    
            dx = hfp['header']['camera']['dx'][()]
            dsource = hfp['header']['dsource'][()]
            lunit = hfp['header']['units']['L_unit'][()]
            fov_muas = dx / dsource * lunit * 2.06265e11

            extent = [ -fov_muas/2, fov_muas/2, -fov_muas/2, fov_muas/2 ]
            imagep = np.copy(hfp['pol']).transpose((1,0,2))
            I = imagep[:,:,0]
            flux = calc_flux(I)
            print(f"For demagnification test F: Folder = {folder}, Subdir = {subdir}, Flux = {flux}")
            Q = imagep[:,:,1]
            U = imagep[:,:,2]
            V = imagep[:,:,3]
            Imaskval = np.abs(I.min()) * 100.
            #Imaskval = np.nanmax(I) / np.power(I.shape[0],5.)
            #vmin = I.min()
            #vmax = I.max()
            # ax.imshow(I, vmin=vmin, vmax=vmax , cmap='afmhot',  origin='lower', extent=extent)
            # mask the ticks of pol < thresh
            # dashed lines for theory

            
            im=ax.imshow(np.log10(I), vmin=np.max(np.log10(I)-3), vmax=np.max(np.log10(I)) , cmap=cmap,  origin='lower', extent=extent)
            #im=ax.imshow(I, vmin=0, vmax=np.max(I) , cmap=cmap,  origin='lower', extent=extent)
            
            if row_im is None:
                row_im = im

            # evpa
            evpa = (180./3.14159)*0.5*np.arctan2(U,Q)
            evpa_0 = 'W'
            if 'evpa_0' in hfp['header']:
                evpa_0 = hfp['header']['evpa_0'][()]
            if evpa_0 == "W":
                evpa += 90.
                evpa[evpa > 90.] -= 180.
            EVPA_CONV = "EofN"
            if EVPA_CONV == "NofW":
                evpa += 90.
                evpa[evpa > 90.] -= 180.
            evpa2 = np.copy(evpa)
            evpa2[np.abs(I)<Imaskval] = np.nan
            npix = I.shape[0]
            xs = np.linspace(-fov_muas/2,fov_muas/2,npix)
            Xs,Ys = np.meshgrid(xs,xs)
            lpscal = np.max(np.sqrt(Q*Q+U*U))
            vxp = np.sqrt(Q*Q+U*U)*np.sin(evpa2*3.14159/180.)/lpscal
            vyp = -np.sqrt(Q*Q+U*U)*np.cos(evpa2*3.14159/180.)/lpscal
            skip = int(npix/32) 
            ax.quiver(Xs[::skip,::skip],Ys[::skip,::skip],vxp[::skip,::skip],vyp[::skip,::skip], 
            headwidth=1, headlength=1, 
            width=0.005,
            color='#00ff00', 
            units='width', 
            scale=4,
            pivot='mid',
            minlength=0)

            #ax.imshow(img)
            #ax.imshow(img, extent=extent)
            ax.set_title(f"{folder}", fontsize=10)
            #ax.set_title(f"{folder}\n n = {subdir.split('_')[1]}, resultion 400x400", fontsize=10)
            ax.set_ylabel(r"${\mu}\mathrm{as}$")
            ax.set_xlabel(r"${\mu}\mathrm{as}$")
            ax.set_xticks(np.linspace(-80, 80, 9))
            if folder in ring_params:
                alpha_mu, beta_mu, color = ring_params[folder]
                ax.plot(alpha_mu,  beta_mu, color, lw=1, alpha = 0.8)
                ax.plot(alpha_mu, -beta_mu, color, lw=1, alpha = 0.8)
            if folder in inner_params:
                alpha_mu_IS, beta_mu_IS, color = inner_params[folder]
                #dict_ring_inner = ring_metrics(alpha_mu_IS, beta_mu_IS)
                #ax.plot(alpha_mu_IS - dict_ring_inner['x_c'],  beta_mu_IS - dict_ring_inner['y_c'], color='r', lw=1, alpha = 0.8)
                ax.plot(alpha_mu_IS,  -beta_mu_IS, color='r', lw=1, alpha = 0.8)
        else:
            ax.text(0.5, 0.5, "Missing", ha='center', va='center', fontsize=12, color='red')
            ax.set_title(f"{folder}", fontsize=10)

        #ax.axis("off")
        ax.set_aspect(1)

    if row_im is not None:
        cbar = fig.colorbar(row_im, cax=axes[i, -1])
        cbar.set_label(r'$\log_{10}(I)$')
    else:
        axes[i, -1].axis('off')   # no data in that row
    
fig.suptitle("Averaged Stokes I images [Jy ${\mu}as^{-2}$]", fontsize=16)
#plt.tight_layout(rect=[0, 0, 1, 0.97])

fig_path = os.path.join(figDir, "averaged_images_grid.png")
fig.savefig(fig_path, dpi=300)
plt.close(fig)
'''
###########################################################################################################################################################

## Figure with curves - photon ring

# Directories and folders
averagedFigDir = '/project/u2grc/Nikola/newSimulations/figures/averaged_curves'
os.makedirs(averagedFigDir, exist_ok=True)

# Read all interpolated curves into a dictionary
curvesDict = {folder: {} for folder in folders}
curves = curvesDict

#subdirs = ["n_-1_400"]
subdirs = ["n_-1_res_400", "n_0_res_400", "n_1_res_400"]
#subdirs = ["n_0_res_400"]

# Averaged-curves y-axis mode.
AVERAGED_CURVES_YSCALE = "linear"
if AVERAGED_CURVES_YSCALE not in ("linear", "log"):
    raise ValueError("AVERAGED_CURVES_YSCALE must be 'linear' or 'log'")

# Split-log treatment (used when AVERAGED_CURVES_YSCALE == "log").
# n=-1,0: slightly deeper y-min to show central depression better.
# n=1: stronger positive floor and masking below floor to avoid triangular/fill-looking artifacts.
LOG_SUBDIR_CFG = {
    "n_-1_res_400": {"floor_pct": 0.8, "ymin_scale": 0.70, "mask_below_floor": False, "line_width_scale": 1.00, "abs_floor": None},
    "n_0_res_400": {"floor_pct": 0.8, "ymin_scale": 0.70, "mask_below_floor": False, "line_width_scale": 1.00, "abs_floor": None},
    "n_1_res_400": {"floor_pct": 0.8, "ymin_scale": 0.70, "mask_below_floor": False, "line_width_scale": 1.00, "abs_floor": None},
}
for _subdir in subdirs:
    cfg = LOG_SUBDIR_CFG.get(_subdir, {})
    floor_pct = cfg.get("floor_pct", 1.0)
    ymin_scale = cfg.get("ymin_scale", 1.0)
    if floor_pct <= 0 or floor_pct >= 100:
        raise ValueError(f"Invalid floor_pct for {_subdir}: {floor_pct}")
    if ymin_scale <= 0:
        raise ValueError(f"Invalid ymin_scale for {_subdir}: {ymin_scale}")

for folder in folders:
    for subdir in subdirs:
        csv_path = os.path.join(baseDir, folder, 'ipole', subdir, f"interpolated_curves_centres_{folder}_file.csv")
        #csv_path = os.path.join(baseDir,  'averageData', subdir, f"interpolated_curves_centres_{folder}_file.csv")
        if os.path.exists(csv_path):
            curves[folder][subdir] = pd.read_csv(csv_path)
        else:
            print(f"File {csv_path} does not exist")
            curves[folder][subdir] = None

#Calculating inner shadow diameter from curves
from scipy.signal import savgol_filter
def shadow_diameter_from_gradient(x, I, derType, x0_window=10.0, smooth_window=21, poly=3,
                                  frac=0.02, persist=5):
    x = np.asarray(x)
    I = np.asarray(I)

    # --- smooth I ---
    w = min(smooth_window, len(x) - (1 - len(x) % 2))
    if w < 5:
        return np.nan, {"reason": "Too few points"}
    if w % 2 == 0:
        w -= 1
    I_s = savgol_filter(I, w, poly)

    # --- find shadow minimum near x=0 ---
    mask0 = np.abs(x) <= x0_window
    if not np.any(mask0):
        return np.nan, {"reason": "x0_window contains no samples"}
    idx0 = np.where(mask0)[0]
    i_min = idx0[np.argmin(I_s[idx0])]

    # --- derivative ---
    d = np.gradient(I_s, x)

    if derType == 'local':
        # setting slope threshold based on the max slope OUTSIDE the center
        # (using the whole curve so it's scale-free)
        d_abs_max = np.nanmax(np.abs(d))
        if not np.isfinite(d_abs_max) or d_abs_max == 0:
            return np.nan, {"reason": "Bad derivative"}
        thr = frac * d_abs_max  # 5% of max slope

        def find_edge_right():
            # need d > +thr for persist points
            for k in range(i_min + 1, len(x) - persist):
                if np.all(d[k:k+persist] > thr):
                    return k
            return None

        def find_edge_left():
            # moving left, the rising edge corresponds to d < -thr
            for k in range(i_min - 1, persist, -1):
                if np.all(d[k-persist+1:k+1] < -thr):
                    return k
            return None

        i_edge_R = find_edge_right()
        i_edge_L = find_edge_left()

        if i_edge_L is None or i_edge_R is None:
            return np.nan, {"reason": "Edge not found", "i_min": i_min}

    elif derType == 'global':
        left = np.where(x < x[i_min])[0]
        right = np.where(x > x[i_min])[0]
        if len(left) < 3 or len(right) < 3:
            return np.nan, {"reason": "Not enough samples on one side"}

        # Peak locations (ring spikes)
        i_pL = left[np.argmax(I_s[left])]
        i_pR = right[np.argmax(I_s[right])]

        Imin = I_s[i_min]
        IpkL = I_s[i_pL]
        IpkR = I_s[i_pR]

        level = 0.99 
        ItargL = Imin + level * (IpkL - Imin)
        ItargR = Imin + level * (IpkR - Imin)

        def interp_crossing(x, y, k0, k1, y_target):
            y0, y1 = y[k0], y[k1]
            if y1 == y0:
                return x[k0]
            t = (y_target - y0) / (y1 - y0)
            return x[k0] + t * (x[k1] - x[k0])

        # ---------- RIGHT: start at peak, move inward toward i_min ----------
        i_edge_R = None
        for k in range(i_pR, i_min, -1):
            # We are moving inward; we want the first time we go from above to below Itarg
            if I_s[k] >= ItargR and I_s[k-1] < ItargR:
                i_edge_R = k
                xR = interp_crossing(x, I_s, k, k-1, ItargR)
                break

        # ---------- LEFT: start at peak, move inward toward i_min ----------
        i_edge_L = None
        for k in range(i_pL, i_min):
            # moving inward (increasing index); crossing from above to below
            if I_s[k] >= ItargL and I_s[k+1] < ItargL:
                i_edge_L = k
                xL = interp_crossing(x, I_s, k, k+1, ItargL)
                break

        if i_edge_L is None or i_edge_R is None:
            return np.nan, {"reason": "Edge not found in global (peak->center)", "i_min": i_min, "i_pL": i_pL, "i_pR": i_pR}
        

    # If xL/xR not computed in branch, fall back to index positions
    if "xL" not in locals():
        xL = x[i_edge_L]
    if "xR" not in locals():
        xR = x[i_edge_R]
    D = xR - xL

    info = {
        "xL": xL, "xR": xR, "D": D,
        "i_min": i_min, "xmin": x[i_min], "Imin": I_s[i_min],
        "i_edge_L": i_edge_L, "i_edge_R": i_edge_R,
        "I_smooth": I_s, "dIdx": d
    }
    return D, info

def peak_fwhm(x, y, i_peak):
    ymax = y[i_peak]
    half = 0.5 * ymax

    # left crossing
    i_left = np.where(y[:i_peak] < half)[0][-1]
    x0, x1 = x[i_left], x[i_left + 1]
    y0, y1 = y[i_left], y[i_left + 1]
    x_left = x0 + (half - y0) * (x1 - x0) / (y1 - y0)

    # right crossing
    i_right = i_peak + np.where(y[i_peak:] < half)[0][0] - 1
    x0, x1 = x[i_right], x[i_right + 1]
    y0, y1 = y[i_right], y[i_right + 1]
    x_right = x0 + (half - y0) * (x1 - x0) / (y1 - y0)

    return {
        "x_left": x_left,
        "x_right": x_right,
        "fwhm": x_right - x_left,
        "half": half,
        "i_peak": i_peak,
    }


def shadow_fwhm(x, y, info):
    I = info.get("I_smooth", y)
    i_min = info["i_min"]

    # peak index on each side of the center minimum
    i_peak_L = np.argmax(I[:i_min])
    i_peak_R = i_min + np.argmax(I[i_min:])


    left = peak_fwhm(x, I, i_peak_L)
    right = peak_fwhm(x, I, i_peak_R)

    return {
        "left_peak": left,
        "right_peak": right,
        "i_peak_L": i_peak_L,
        "i_peak_R": i_peak_R,
    }
    

# My averaging function
def average_curves(curvesOriginal):
    x = curvesOriginal.iloc[1]
    y = curvesOriginal.iloc[2]
    curves = curvesOriginal[3:]  # skip first 3 rows (header, x, y)
    curves_polar = curves.iloc[::2].reset_index(drop=True).mean(axis=0)
    curves_horizontal = curves.iloc[1::2].reset_index(drop=True).mean(axis=0)
    return curves_polar, curves_horizontal, x, y

# Compute averaged curves
averaged_curves = {}

for folder in folders:
    averaged_curves[folder] = {}
    for subdir in subdirs:
        if curves[folder][subdir] is not None:
            pol, hor, x, y = average_curves(curves[folder][subdir])
            averaged_curves[folder][subdir] = {'polar': pol, 'horizontal': hor, 'x': x}
        else:
            averaged_curves[folder][subdir] = {'polar': None, 'horizontal': None, 'x': None}

def robust_ylim(value_arrays, lower_pct=0.5, upper_pct=99.5, pad_fraction=0.08):
    finite_values = []
    for arr in value_arrays:
        arr = np.asarray(arr, dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size:
            finite_values.append(arr)
    if not finite_values:
        return None

    all_values = np.concatenate(finite_values)
    y_low = np.percentile(all_values, lower_pct)
    # Keep peaks fully visible: never clip the upper limit by percentile.
    y_high = np.nanmax(all_values)
    if not np.isfinite(y_low) or not np.isfinite(y_high) or y_high <= y_low:
        y_low = np.nanmin(all_values)
        y_high = np.nanmax(all_values)
        if not np.isfinite(y_low) or not np.isfinite(y_high) or y_high <= y_low:
            return None

    pad = (y_high - y_low) * pad_fraction
    return (y_low - pad, y_high + pad)

def get_positive_floor(value_arrays, floor_pct=1.0):
    pos_vals = []
    for arr in value_arrays:
        arr = np.asarray(arr, dtype=float)
        arr = arr[np.isfinite(arr) & (arr > 0)]
        if arr.size:
            pos_vals.append(arr)
    if not pos_vals:
        return None
    floor = np.percentile(np.concatenate(pos_vals), floor_pct)
    if not np.isfinite(floor) or floor <= 0:
        return None
    return float(floor)

def scale_aware_ylim(ylim, yscale, value_arrays=None, log_floor_pct=1.0, abs_floor=None):
    if ylim is None:
        return None
    y_low, y_high = ylim
    if yscale == "log":
        pos_floor = get_positive_floor(value_arrays or [], floor_pct=log_floor_pct)
        if abs_floor is not None:
            pos_floor = max(pos_floor or 0.0, float(abs_floor))
        if pos_floor is None or not np.isfinite(pos_floor) or pos_floor <= 0:
            pos_floor = np.finfo(float).tiny
        y_low = max(y_low, pos_floor)
        if y_high <= y_low:
            return None
    return (y_low, y_high)

def prepare_curve_for_plot(y_values, yscale, log_floor=None, mask_below_floor=False):
    y_plot = np.asarray(y_values, dtype=float).copy()
    if yscale != "log":
        return y_plot
    if log_floor is None or not np.isfinite(log_floor) or log_floor <= 0:
        log_floor = np.finfo(float).tiny
    if mask_below_floor:
        y_plot[y_plot < log_floor] = np.nan
    else:
        y_plot = np.where(y_plot > 0, y_plot, np.nan)
        y_plot = np.maximum(y_plot, log_floor)
    return y_plot

all_polar_curves = []
all_horizontal_curves = []
for folder in folders:
    for subdir in subdirs:
        curves_df = averaged_curves[folder][subdir]
        if curves_df['polar'] is not None:
            all_polar_curves.append(curves_df['polar'].values)
        if curves_df['horizontal'] is not None:
            all_horizontal_curves.append(curves_df['horizontal'].values)

# Global limits for linear mode (keeps cross-n comparability when linear).
linear_polar_ylim = robust_ylim(all_polar_curves)
linear_horizontal_ylim = robust_ylim(all_horizontal_curves)
linear_polar_ylim = scale_aware_ylim(linear_polar_ylim, "linear", all_polar_curves)
linear_horizontal_ylim = scale_aware_ylim(linear_horizontal_ylim, "linear", all_horizontal_curves)

# Per-n limits for log mode (avoids one shared range crushing contrast).
log_polar_ylim = {}
log_horizontal_ylim = {}
log_floor_by_subdir_polar = {}
log_floor_by_subdir_horizontal = {}
for subdir in subdirs:
    cfg = LOG_SUBDIR_CFG.get(subdir, {})
    floor_pct = cfg.get("floor_pct", 1.0)
    ymin_scale = cfg.get("ymin_scale", 1.0)
    abs_floor = cfg.get("abs_floor", None)

    subdir_polar = []
    subdir_horizontal = []
    for folder in folders:
        curves_df = averaged_curves[folder][subdir]
        if curves_df['polar'] is not None:
            subdir_polar.append(curves_df['polar'].values)
        if curves_df['horizontal'] is not None:
            subdir_horizontal.append(curves_df['horizontal'].values)
    p_ylim = robust_ylim(subdir_polar)
    h_ylim = robust_ylim(subdir_horizontal)
    log_polar_ylim[subdir] = scale_aware_ylim(
        p_ylim, "log", subdir_polar, log_floor_pct=floor_pct, abs_floor=abs_floor
    )
    log_horizontal_ylim[subdir] = scale_aware_ylim(
        h_ylim, "log", subdir_horizontal, log_floor_pct=floor_pct, abs_floor=abs_floor
    )

    # Apply optional deeper lower limit for depression visibility.
    if log_polar_ylim[subdir] is not None:
        y0, y1 = log_polar_ylim[subdir]
        log_polar_ylim[subdir] = (y0 * ymin_scale, y1)
    if log_horizontal_ylim[subdir] is not None:
        y0, y1 = log_horizontal_ylim[subdir]
        log_horizontal_ylim[subdir] = (y0 * ymin_scale, y1)

    floor_p = get_positive_floor(subdir_polar, floor_pct=floor_pct)
    floor_h = get_positive_floor(subdir_horizontal, floor_pct=floor_pct)
    if abs_floor is not None:
        floor_p = max(floor_p or 0.0, float(abs_floor))
        floor_h = max(floor_h or 0.0, float(abs_floor))
    log_floor_by_subdir_polar[subdir] = floor_p
    log_floor_by_subdir_horizontal[subdir] = floor_h

for subdir in subdirs:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax_polar, ax_horizontal = axes
    subdir_yscale = AVERAGED_CURVES_YSCALE
    subdir_cfg = LOG_SUBDIR_CFG.get(subdir, {})
    line_width_scale = subdir_cfg.get("line_width_scale", 1.0)
    mask_below_floor = bool(subdir_cfg.get("mask_below_floor", False))

    for folder in folders:
        curves_df = averaged_curves[folder][subdir]
        x = curves_df['x'].values
        curves_polar = curves_df['polar'].values
        curves_horizontal = curves_df['horizontal'].values
        style = plot_style[folder].copy()
        base_lw = style.get('linewidth', 1.5)
        style['linewidth'] = base_lw * line_width_scale

        curves_polar_plot = prepare_curve_for_plot(
            curves_polar, subdir_yscale,
            log_floor=log_floor_by_subdir_polar.get(subdir),
            mask_below_floor=mask_below_floor
        )
        curves_horizontal_plot = prepare_curve_for_plot(
            curves_horizontal, subdir_yscale,
            log_floor=log_floor_by_subdir_horizontal.get(subdir),
            mask_below_floor=mask_below_floor
        )

        #Edges - Theoretical ones overlaid on the images
        #slice through the critical curve:
        # two points from alpha for horizontal -> two lines
        # two points from beta for polar 
        # alpha_mu, beta_mu, color = ring_params[folder]
        ax_polar.axvline(np.min(-beta_mu), color=style['color'], linestyle='--', alpha=0.6)
        ax_polar.axvline(np.max(beta_mu), color=style['color'], linestyle='--', alpha=0.6)

        # --- Polar curve ---
        ax_polar.plot(x, curves_polar_plot, color=style['color'],
                      linewidth=style['linewidth'], alpha=0.8, label=f"{style['label']}")
        D_polar_global, dict_polar_global = shadow_diameter_from_gradient(x, curves_polar, derType = 'global')
        xL_global = dict_polar_global['xL']
        xR_global = dict_polar_global['xR']

        #ax_polar.set_yscale('log')

        #Edges - Calculated form the images overlaid on the images
        # ax_polar.axvline(xL_global, color=style['color'], linestyle='--', alpha=0.6)
        # ax_polar.axvline(xR_global, color=style['color'], linestyle='--', alpha=0.6)
        # print(f"Shadow diameter, polar, from the curves, {folder} = {D_polar}")

        # --- Horizontal curve ---
        import matplotlib.ticker as mticker

        ax_horizontal.plot(x, curves_horizontal_plot, color=style['color'], 
                           linewidth=style['linewidth'], alpha=0.8, label=style['label'])

        #ax_horizontal.set_yscale('log')

        # # Only label full decades
        # ax_horizontal.yaxis.set_major_locator(mticker.LogLocator(base=10, subs=(1.0,)))
        # ax_horizontal.yaxis.set_major_formatter(mticker.LogFormatterMathtext(base=10, labelOnlyBase=True))

        # # No minor labels
        # ax_horizontal.yaxis.set_minor_locator(mticker.NullLocator())
        # ax_horizontal.yaxis.set_minor_formatter(mticker.NullFormatter())


        if subdir in ("n_-1_res_400", "n_0_res_400", "n_1_res_400"):
            D_horizontal_global, dict_horizontal_global = shadow_diameter_from_gradient(x, curves_horizontal, derType = 'global')
            #print(f"Photon ring inner edge, horizontal, from the image, {folder} = {D_horizontal_global}")
            
            xL_global = dict_horizontal_global['xL']
            xR_global = dict_horizontal_global['xR']

            dx_uas = x[1]-x[0]
            #print(folder, "dx=", dx_uas)

        #Edges - Theoretical ones overlaid on the images
        #slice through the critical curve:
        # two points from alpha for horizontal -> two lines
        # two points from beta for polar 
        alpha_mu, beta_mu, color = ring_params[folder]
        ax_horizontal.axvline(np.min(alpha_mu), color=style['color'], linestyle='--', alpha=0.6) #theoretical line
        ax_horizontal.axvline(np.max(alpha_mu), color=style['color'], linestyle='--', alpha=0.6) #thereotical line
        
        #Edges global - Calculated form the images overlaid on the images
        #ax_horizontal.axvline(xL_global, color=style['color'], linestyle='--', alpha=0.6)
        #ax_horizontal.axvline(xR_global, color=style['color'], linestyle='--', alpha=0.6)

        if (subdir == "n_-1_res_400" or subdir == "n_0_res_400" or subdir == "n_1_res_400"):
            D_horizontal_local, dict_horizontal_local = shadow_diameter_from_gradient(x, curves_horizontal, derType = 'local')

            #Edges local - Calculated form the images overlaid on the images
            #ax_horizontal.axvline(float(dict_horizontal_local['xL']) , color=style['color'], linestyle='--', alpha=0.6) #image extacted line
            #ax_horizontal.axvline(float(dict_horizontal_local['xR']) , color=style['color'], linestyle='--', alpha=0.6) #image extacted line

            D_polar_local, dict_polar_local = shadow_diameter_from_gradient(x, curves_polar, derType = 'local')

            #Edges local - Calculated form the images overlaid on the images
            #ax_polar.axvline(float(dict_polar_local['xL']) , color=style['color'], linestyle='--', alpha=0.6) #image extacted line
            #ax_polar.axvline(float(dict_polar_local['xR']) , color=style['color'], linestyle='--', alpha=0.6) #image extacted line

            #print(f"Dimensionless ratio, horizontal, from the curves, {folder}, depression width/photon ring diameter = {D_horizontal_local/D_horizontal_global}")
        
        #ring metrics form image
        def ring_metric_image(dict_horizontal, dict_polar = None):
            xL = float(dict_horizontal['xL'])
            xR = float(dict_horizontal['xR'])

            D_alpha = xR - xL
            x_c = 0.5 * (xR + xL)

            A_disp = (2.0 * np.abs(x_c))/ (D_alpha + 1e-30)
            A_alpha = (np.abs(xR) - np.abs(xL)) / (np.abs(xL) + np.abs(xL) + 1e-30)

            out = dict(D_alpha = D_alpha, x_c = x_c, A_disp = A_disp, A_alpha = A_alpha, A_shape = None)

            if dict_polar is not None:
                yL = float(dict_polar['xL'])
                yR = float(dict_polar['xR'])
                yL = float(dict_polar["xL"])
                yR = float(dict_polar["xR"])
                out["D_beta"] = yR - yL
                out["y_c"] = 0.5 * (yR + yL)

            return out
        
        if (subdir == "n_-1_res_400" or subdir == "n_0_res_400" or subdir == "n_1_res_400"):
            dict_ring_image = ring_metric_image(dict_horizontal_global, dict_polar_global)

            print(
                f"Photon ring metrics, from image, {folder}, {subdir}, "
                f"D_alpha={dict_ring_image['D_alpha']:.3f}, "
                f"D_beta={dict_ring_image['D_beta']:.3f}, "
                f"D_alpha/D_beta={(dict_ring_image['D_alpha']/dict_ring_image['D_beta']):.3f},"
                f"x_c={dict_ring_image['x_c']:.3f}"
            )

            dict_ring_image_local = ring_metric_image(dict_horizontal_local, dict_polar_local)

            print(
                f"Inner shadow metrics, from image, {folder}, {subdir} "
                f"D_alpha={dict_ring_image_local['D_alpha']:.3f}, "
                f"D_beta={dict_ring_image_local['D_beta']:.3f}, "
                f"D_alpha/D_beta={(dict_ring_image_local['D_alpha']/dict_ring_image_local['D_beta']):.3f},"
                f"x_c={dict_ring_image_local['x_c']:.3f}"
            )
        
            betaM  = beta_mu        

            alphaM = alpha_mu
            gammaS = gamma_p_list[folder][0]    

            mask0 = np.isclose(betaM, 0.0, atol=1e-3)   # μas tolerance
            

            iL = np.where(mask0 & (alphaM < 0))[0][0]
            iR = np.where(mask0 & (alphaM > 0))[0][0]

            left_gamma_p  = float(gammaS.iloc[iL])
            right_gamma_p = float(gammaS.iloc[iR])
            
            half_horizontal_global = shadow_fwhm(x, curves_horizontal, dict_horizontal_global)
        
            # ax_horizontal.plot(half_horizontal_global['right_peak']['x_left'], half_horizontal_global['right_peak']['half'], 'o', color=style['color'])
            # ax_horizontal.plot(half_horizontal_global['right_peak']['x_right'], half_horizontal_global['right_peak']['half'], 'o', color=style['color'])

            # ax_horizontal.plot(half_horizontal_global['left_peak']['x_right'], half_horizontal_global['left_peak']['half'], 'o', color=style['color'])
            # ax_horizontal.plot(half_horizontal_global['left_peak']['x_left'], half_horizontal_global['left_peak']['half'], 'o', color=style['color'])
            
            #print(half_horizontal_global['left_peak']['fwhm'], half_horizontal_global['right_peak']['fwhm'])
            
            print(
                f"For demagnification test H: "
                f"Folder = {folder}, " 
                f"Subdir = {subdir}, " 
                f"HWHM left peak = {half_horizontal_global['left_peak']['fwhm']},"
                f"HWHM right peak {half_horizontal_global['right_peak']['fwhm']}")
            
            #demagnification_test(dict_horizontal_global['x_L'], dict_horizontal_global['x_R'], x_cc)
            print(
                f"For demagnification test R: "
                f"Folder = {folder}, " 
                f"Subdir = {subdir}, " 
                f"x_L = {dict_horizontal_global['xL']}, " 
                f"x_R = {dict_horizontal_global['xR']}, " 
                f"left x_CC = {np.min(alpha_mu)} ," 
                f"right x_CC = {np.max(alpha_mu)},"
                f"left gamma_p = {left_gamma_p}, "
                f"right gamma_p = {right_gamma_p}")

        
            horizontal_diameter_values = x[dict_horizontal_global['i_edge_L']:dict_horizontal_global['i_edge_R']]
            polar_diameter_values = (x[dict_polar_global['i_edge_L']:dict_polar_global['i_edge_R']])
            #if not the same length, trimming to be the same
            n = min(len(horizontal_diameter_values), len(polar_diameter_values))
            horizontal_diameter_values = horizontal_diameter_values[:n]
            polar_diameter_values = polar_diameter_values[:n]
            dict_ring = ring_metrics(horizontal_diameter_values, polar_diameter_values)
            # print(
            #             f"Ring metrics, from curves, {folder}: "
            #             f"D_alpha={dict_ring['D_alpha']:.3f}, x_c={dict_ring['x_c']:.3f}, "
            #             f"A_disp={dict_ring['A_disp']:.4f}, A_shape={dict_ring['A_shape']:.4f}"
        #         )
    

    # Titles, labels, legends
    ax_polar.set_title(f"n = {subdir.split('_')[1]}, polar averaged curve")
    #ax_polar.set_title(f"n = all, polar averaged curve")
    ax_horizontal.set_title(f"n = {subdir.split('_')[1]}, horizontal averaged curve")
    #ax_horizontal.set_title(f"n = all, horizontal averaged curve")
    ax_polar.set_xlabel(u"\u03bcas")
    ax_horizontal.set_xlabel(u"\u03bcas")
    ax_polar.set_ylabel("Intensity [Jy ${\mu}as^{-2}$]")
    ax_horizontal.set_ylabel("Intensity [Jy ${\mu}as^{-2}$]")

    ax_polar.legend(loc='best', fontsize=10, frameon=True)
    ax_horizontal.legend(loc='best', fontsize=10, frameon=True)

    if subdir_yscale == "log":
        ax_polar.set_yscale("log")
        ax_horizontal.set_yscale("log")

    if subdir_yscale == "linear":
        if linear_polar_ylim is not None:
            ax_polar.set_ylim(*linear_polar_ylim)
        if linear_horizontal_ylim is not None:
            ax_horizontal.set_ylim(*linear_horizontal_ylim)
    else:
        ax_polar.set_ylim(1e-9, 1e-3)
        ax_horizontal.set_ylim(1e-9, 1e-3)

    for ax in (ax_polar, ax_horizontal):
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=12))
        if subdir_yscale == "linear":
            ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=12))
        else:
            ax.yaxis.set_major_locator(ticker.LogLocator(base=10, subs=(1.0,)))
            ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
            ax.yaxis.set_minor_formatter(ticker.NullFormatter())
        ax.tick_params(axis='both', which='both', direction='in', top=True, right=True)
        # ax_polar.set_yscale('log')
        # ax_polar.set_yticks([1e-5, 2e-5, 5e-5, 1e-4])
        # ax_polar.yaxis.set_minor_locator(mticker.NullLocator())
        # ax_horizontal.set_yscale('log')
        # ax_horizontal.set_yticks([1e-5, 2e-5, 5e-5, 1e-4])
        # ax_horizontal.yaxis.set_minor_locator(mticker.NullLocator())
        # ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig_path = os.path.join(averagedFigDir, f"averaged_curves_{subdir}.png")
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)





##################################################################################################################################################################################
'''
def brightness_asymmetry(intensity_row, center_index=None):
    """
    Compute brightness asymmetry for a single horizontal cut (1x220 array),
    following Medeiros+ Eq. (2):  A = max(F_L, F_R) / min(F_L, F_R).
    """

    # If center not given, take middle of the array
    if center_index is None:
        center_index = len(intensity_row) // 2

    left = np.sum(intensity_row[:center_index])
    right = np.sum(intensity_row[center_index:])

    # Avoid division by zero
    if left == 0 or right == 0:
        return np.nan  # or return 1.0 if you prefer symmetry

    return max(left, right) / min(left, right)


## BETA MODES

# Directory to save figures
betaFigDir = os.path.join(figDir, 'betaModes')
os.makedirs(betaFigDir, exist_ok=True)

beta_columns = ['m_avg', 'm_net', 'beta2', 'arg(beta2)']
beta_columns_names = ['average polarization', 'net polarization', u"\u03b2\u2082", u"arg(\u03b2\u2082)"]
keys = list(observablesData[folders[0]].keys())

fig, axes = plt.subplots(3, 2, figsize=(12, 8))
axes = axes.flatten()
subdirsMuas = ["n_1_400_20muas"]
#subdirs = ["n_-1_res_400"]
subdirs = ["n_1_400"]

# ============================================================
# 1) BETA MODES IN PANELS 0–3
# ============================================================

NBINS = 50

for i, col in enumerate(beta_columns):
    ax = axes[i]

    #set common bin edges - gathering all x 
    all_x_axis = []
    for folder in folders:
        for subdir in subdirsMuas:
            s = observablesData[folder][subdir][col].dropna().to_numpy()
            if s.size:
                all_x_axis.append(s)

    all_x_axis = np.concatenate(all_x_axis)
    bin_edges = np.histogram_bin_edges(all_x_axis, bins=NBINS) 

    for folder in folders:
        for subdir in subdirsMuas:
            df = observablesData[folder][subdir]
            counts, _ = np.histogram(df[col], bins=bin_edges, density=True)

            style = plot_style[folder].copy()
            style['label'] = plot_style[folder]['label']
            ax.stairs(counts, bin_edges, **style)

    #ax.set_title(beta_columns_names[i])
    ax.legend().remove()

    # show 7 ticks
    idx = np.linspace(0, len(bin_edges)-1, 7, dtype=int)
    ax.set_xticks(bin_edges[idx])
    #ax.set_xlabel(col)  # optional
    
    ax.set_ylabel("Probability density")

# ============================================================
# 2) BRIGHTNESS ASYMMETRY IN PANEL axes[4]
# ============================================================


A_all = []
for folder in folders:
    for subdir in subdirs:
 
        #csv_path = os.path.join(
            #baseDir, folder, "ipole", subdir,
        #    f"interpolated_curves_centres_{folder}_file.csv"
        #)
        csv_path = os.path.join(baseDir,  'averageData', subdir, f"interpolated_curves_centres_{folder}_file.csv")

        if not os.path.exists(csv_path):
            print(f"File {csv_path} does not exist")
            continue

        df = pd.read_csv(csv_path)

        df_body = df.iloc[3:]
        curves_horizontal = df_body.iloc[1::2].reset_index(drop=True)

        curve_array = curves_horizontal.values
        center_idx = curve_array.shape[1] // 2

        for row in curve_array:
            A_all.append(brightness_asymmetry(row, center_idx))

    #A_values = np.array(A_values)
A_all = np.asarray(A_all, dtype=float)
A_all = A_all[np.isfinite(A_all)]  # drop NaN/inf if any

bin_edges_A = np.histogram_bin_edges(A_all, bins=NBINS)
axA = axes[4]   # third row left plot
for folder in folders:
    A_values = []
    for subdir in subdirs:
        csv_path = os.path.join(baseDir, 'averageData', subdir,
                                f"interpolated_curves_centres_{folder}_file.csv")
        if not os.path.exists(csv_path):
            print(f"File {csv_path} does not exist")
            continue
        df = pd.read_csv(csv_path)
        df_body = df.iloc[3:]
        curves_horizontal = df_body.iloc[1::2].reset_index(drop=True)

        curve_array = curves_horizontal.values
        center_idx = curve_array.shape[1] // 2

        for row in curve_array:
            A_values.append(brightness_asymmetry(row, center_idx))


    #counts, bins = np.histogram(A_values, bins=30)
    counts, _ = np.histogram(A_values, bins=bin_edges_A, density=True)

    style = plot_style[folder].copy()
    style['label'] = plot_style[folder]['label']

    axA.stairs(counts, bin_edges_A, **style)
    #axA.stairs(counts, bins, **style)

    idx = np.linspace(0, len(bin_edges_A)-1, 7, dtype=int)
    axA.set_xticks(bin_edges_A[idx])
    axA.set_ylabel("Probability density")

#axA.set_title("Brightness Asymmetry, Medeiros+21")
#axA.set_ylabel("density")
# ============================================================
# 3) DEDICATED LEGEND PANEL (axes[5])
# ============================================================

# ONLY legend in the entire figure, in axes[5]
legend_ax = axes[5]
legend_ax.axis("off")  # blank panel

# Get handles/labels from the A–panel
handles, labels = axA.get_legend_handles_labels()

legend_ax.legend(
    handles,
    labels,
    title="Legend:",
    loc="center",
    fontsize=14,
    title_fontsize=16,
    frameon=False,
)

xlabels = {
    "m_avg": r"$m_\mathrm{avg}$",
    "m_net": r"$m_\mathrm{net}$",
    "beta_abs": r"$|\beta_2|$",
    "beta_angle": r"$\angle \beta_2$",
    "A": r"$A$",
    }

axes[0].set_xlabel(r"$m_\mathrm{avg}$")
axes[1].set_xlabel(r"$m_\mathrm{net}$")
axes[2].set_xlabel(r"$|\beta_2|$")
axes[3].set_xlabel(r"$\angle \beta_2$")
axes[4].set_xlabel(r"$A$")

#fig.suptitle(f"Polarization coefficients and brightness assymetry, \n n = {subdir.split('_')[1]}, resolution 400x400", fontsize=16)
#fig.suptitle(f"Polarization coefficients and brightness assymetry, \n n = all, resolution 400x400", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.97])

fig_path = os.path.join(betaFigDir, f"betaModes+A_{subdir}.png")
fig.savefig(fig_path, dpi=300)
plt.close(fig)


# ============================================================
# 4) EXTRA FIGURE: m_avg AS A FUNCTION OF TIME
# ============================================================

fig_time, ax_time = plt.subplots(figsize=(10, 5))

for folder in folders:
    df_params = paramsFiles[folder]
    t = df_params['coord/t'].values

    for subdir in subdirsMuas:
        df_obs = observablesData[folder][subdir]
        m_avg = df_obs['m_avg'].to_numpy()

        # Make sure time and observable arrays have compatible lengths
        n = min(len(t), len(m_avg))
        if len(t) != len(m_avg):
            print(f"Length mismatch for {folder}, {subdir}: "
                  f"len(t)={len(t)}, len(m_avg)={len(m_avg)} -> using first {n} points")

        style = plot_style[folder].copy()
        style['label'] = plot_style[folder]['label']

        ax_time.plot(t[:n], m_avg[:n], **style)

ax_time.set_xlabel("t")
ax_time.set_ylabel(r"$m_\mathrm{avg}$")
ax_time.grid(True, alpha=0.3)

# avoid duplicated legend entries if several subdirs are plotted
handles, labels = ax_time.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax_time.legend(by_label.values(), by_label.keys())

plt.tight_layout()

fig_time_path = os.path.join(betaFigDir, "m_avg_vs_time.png")
fig_time.savefig(fig_time_path, dpi=300)
plt.close(fig_time)
'''
##########################################################################################################################################################################
'''


################################################################
## KS test (Kolmogorov-Smirnov test)
#Example problem: Suppose we wish to test the null hypothesis that a sample is distributed according to the standard normal. We choose a confidence level of 95%; that is, we will reject the null hypothesis in favor of the alternative if the p-value is less than 0.05.
# When testing uniformly distributed data, we would expect the null hypothesis to be rejected.
# For example, when two samples are drawn from the same distribution, we expect the data to be consistent with the null hypothesis most of the time.
# If the p-value of 0.45 is not below our threshold of 0.05, so we cannot reject the null hypothesis.
# If the p-value is lower than our threshold of 0.05, so we reject the null hypothesis in favor of the default “two-sided” alternative: the data are not distributed according to the standard normal.

import h5py

#acces xy points in all 15k images, calc means and stdvs and pis and nntds between the two

intensities = {folder: {subdir: {'z': []} for subdir in subdirs} for folder in folders}

subdirs = ['n_-1_res_400', 'n_0_res_400', 'n_1_res_400']

#subsubdirs = ['x', 'y', 'z']

for folder in folders:
#for i in [0, 2]:
    #folder = folders[i]
    for subdir in subdirs[0:1]:
        h5_path = os.path.join(baseDir, folder, "ipole", subdir)
        if os.path.exists(h5_path):
            files = np.sort(glob.glob(os.path.join(h5_path,'*.h5')))
            for fname in files:
                hfp = h5py.File(fname,'r')    
                imagep = np.copy(hfp['pol']).transpose((1,0,2))
                z = imagep[:,:,0] #intensity (Stokes I)
                #x, y = np.meshgrid(np.linspace(-z.shape[0]/2, z.shape[0]/2, z.shape[0]), np.linspace(-z.shape[0]/2, z.shape[0]/2, z.shape[0]))
                #intensities[folder][subdir] = {'z': z}
                intensities[folder][subdir]['z'].append(z)

stacked_arrays = {folder: {subdir: {'z': []} for subdir in subdirs} for folder in folders}
pointwise_mean = {folder: {subdir: {'z': []} for subdir in subdirs} for folder in folders}
pointwise_std = {folder: {subdir: {'z': []} for subdir in subdirs} for folder in folders}

for folder in folders:
#for i in [0, 2]:
#    folder = folders[i]
    for subdir in subdirs[0:1]:
        stacked_arrays[folder][subdir] = np.stack(intensities[folder][subdir]['z'], axis=0)
        pointwise_mean[folder][subdir] = np.mean(stacked_arrays[folder][subdir], axis=0)
        pointwise_std[folder][subdir] = np.std(stacked_arrays[folder][subdir], axis=0, ddof = 1) #population data doff = 0, ddof = 1 for sample data

#print('1' , pointwise_mean['KerrLow']['n_-1_res_400'])
#print('2', pointwise_mean['KHLow']['n_-1_res_400'])

statistics = {
    'NNTD_KLvsKHL': {},
    'NNTD_KMvsKHM': {},
    #'z-score_KL': {},
    #'z-score_KM': {},
    #'z-score_KHL': {},
    #'z-score_KHM': {},
    'effect-size_KLvsKHL': {},
    'effect-size_KMvsKHM': {}
}
#https://www.tandfonline.com/doi/full/10.1080/13645579.2015.1091235#d1e416
def calc_NNTD (mean1, mean2, N, sigma):
    if np.mean(mean1) < np.mean(mean2):
        c = mean2 + sigma
    elif np.mean(mean1) >= np.mean(mean2):
        c = mean2 - sigma
    return N * np.abs(mean1 - mean2) / np.abs(mean1 - c)
    

h5_path = os.path.join(baseDir, 'KerrLow', "ipole", 'n_-1_res_400')
N = len(glob.glob(os.path.join(h5_path,'*.h5')))
print(N)

mean1_KL = pointwise_mean['KerrLow']['n_-1_res_400']
mean2_KHL = pointwise_mean['KHLow']['n_-1_res_400']
sigma_KHL = pointwise_std['KHLow']['n_-1_res_400']

mean1_KM = pointwise_mean['KerrMid']['n_-1_res_400']
mean2_KHM = pointwise_mean['KHMid']['n_-1_res_400']
sigma_KHM = pointwise_std['KHMid']['n_-1_res_400']

NNTD_KLvsKHL = calc_NNTD(mean1_KL, mean2_KHL, N, sigma_KHL)
NNTD_KMvsKHM = calc_NNTD(mean1_KM, mean2_KHM, N, sigma_KHM)
# https://en.wikipedia.org/wiki/Standard_score
#z_score_KL = (stacked_arrays['KerrLow']['n_-1_res_400'] - pointwise_mean['KerrLow']['n_-1_res_400']) / pointwise_std['KerrLow']['n_-1_res_400']
#z_score_KM = (stacked_arrays['KerrMid']['n_-1_res_400'] - pointwise_mean['KerrMid']['n_-1_res_400']) / pointwise_std['KerrMid']['n_-1_res_400']
#z_score_KHL = (stacked_arrays['KHLow']['n_-1_res_400'] - pointwise_mean['KHLow']['n_-1_res_400']) / pointwise_std['KHLow']['n_-1_res_400']
#z_score_KHM = (stacked_arrays['KHMid']['n_-1_res_400'] - pointwise_mean['KHMid']['n_-1_res_400']) / pointwise_std['KHMid']['n_-1_res_400']
##https://en.wikipedia.org/wiki/Effect_size
effect_size_KLvsKHL = (mean1_KL - mean2_KHL) / sigma_KHL 
effect_size_KMvsKHM = (mean1_KM - mean2_KHM) / sigma_KHM 


statistics = {
    'NNTD_KLvsKHL': NNTD_KLvsKHL,
    'NNTD_KMvsKHM': NNTD_KMvsKHM,
    #'z-score_KL': z_score_KL,
    #'z-score_KM': z_score_KM,
    #'z-score_KHL': z_score_KHL,
    #'z-score_KHM': z_score_KHM,
    'effect-size_KLvsKHL': effect_size_KLvsKHL,
    'effect-size_KMvsKHM': effect_size_KMvsKHM
}


#######################
## Save statistics
statistics_file = os.path.join(figDir, "statistics.json")
def to_serializable(obj):
    """Convert NumPy arrays and scalars to Python-native types for JSON."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.generic,)):  # np.float64, np.int64, etc.
        return obj.item()
    return obj

statistics_serializable = {k: to_serializable(v) for k, v in statistics.items()}

with open(statistics_file, "w") as f:
    json.dump(statistics_serializable, f, indent=4)

'''
'''
#################
## Plot statistics 

# Load JSON
statistics_file = os.path.join(figDir, "statistics.json")

with open(statistics_file, "r") as f:
    statistics = json.load(f)

# Convert lists back to numpy arrays
for key in statistics:
    statistics[key] = np.array(statistics[key])

# --- Select keys to plot ---
top_keys = ["NNTD_KLvsKHL", "NNTD_KMvsKHM"]
bottom_keys = ["effect-size_KLvsKHL", "effect-size_KMvsKHM"]

# --- Compute color limits separately for each row ---
top_values = np.concatenate([statistics[k].flatten() for k in top_keys])
bottom_values = np.concatenate([statistics[k].flatten() for k in bottom_keys])

top_vmin, top_vmax = np.nanmin(top_values), np.nanmax(top_values)
bottom_vmin, bottom_vmax = np.nanmin(bottom_values), np.nanmax(bottom_values)

fig, axes = plt.subplots(
    2, 2, figsize=(8, 8), sharex=True, sharey=True, constrained_layout=True
)
axes = axes.reshape(2, 2)

# --- Plot Top Row (NNTD) ---
for ax, key in zip(axes[0], top_keys):
    im = ax.imshow(
        statistics[key],
        cmap="viridis",
        origin="lower",
        aspect="equal",  # ensures data aspect = 1
        vmin=top_vmin,
        vmax=top_vmax,
    )
    ax.set_title(key, fontsize=12)

# Shared colorbar for top row
cbar_top = fig.colorbar(
    im, ax=axes[0].tolist(), orientation="vertical", fraction=0.046, pad=0.04
)
cbar_top.set_label("NNTD", fontsize=12)

# --- Plot Bottom Row (Effect Sizes) ---
for ax, key in zip(axes[1], bottom_keys):
    im2 = ax.imshow(
        statistics[key],
        cmap="coolwarm",
        origin="lower",
        aspect="equal",
        vmin=bottom_vmin,
        vmax=bottom_vmax,
    )
    ax.set_title(key, fontsize=12)

# Shared colorbar for bottom row
cbar_bottom = fig.colorbar(
    im2, ax=axes[1].tolist(), orientation="vertical", fraction=0.046, pad=0.04
)
cbar_bottom.set_label("Effect Size", fontsize=12)

# --- Force square axes explicitly (after layout) ---
for ax in axes.flat:
    ax.set_aspect("equal", adjustable="box")

# --- Common labels ---
for ax in axes[-1]:
    ax.set_xlabel("X index")
for ax in axes[:, 0]:
    ax.set_ylabel("Y index")

# --- Save ---
fig_path = os.path.join(figDir, "statistics_two_panels.png")
plt.savefig(fig_path, dpi=300)
plt.close(fig)



#######################
## print out some statistics

# Load JSON
statistics_file = os.path.join(figDir, "statistics.json")

with open(statistics_file, "r") as f:
    statistics = json.load(f)

# Convert lists back to numpy arrays
for key in statistics:
    statistics[key] = np.array(statistics[key])

print(
    f"Min NNTD_KLvsKHL = {np.min(statistics['NNTD_KLvsKHL']):.2f}, "
    f"Max NNTD_KLvsKHL = {np.max(statistics['NNTD_KLvsKHL']):.2f}, "
    f"Mean NNTD_KLvsKHL = {np.mean(statistics['NNTD_KLvsKHL']):.2f}")
print(
    f"Min NNTD_KMvsKHM = {np.min(statistics['NNTD_KMvsKHM']):.2f}, "
    f"Max NNTD_KMvsKHM = {np.max(statistics['NNTD_KMvsKHM']):.2f}, "
    f"Mean NNTD_KMvsKHM = {np.mean(statistics['NNTD_KMvsKHM']):.2f}")
print(
    f"Min effect-size_KLvsKHL = {np.min(statistics['effect-size_KLvsKHL']):.2f}, "
    f"Max effect-size_KLvsKHL = {np.max(statistics['effect-size_KLvsKHL']):.2f}, "
    f"Mean effect-size_KLvsKHL = {np.mean(statistics['effect-size_KLvsKHL']):.2f}")
print(
    f"Min effect-size_KMvsKHM = {np.min(statistics['effect-size_KMvsKHM']):.2f}, "
    f"Max effect-size_KMvsKHM = {np.max(statistics['effect-size_KMvsKHM']):.2f}, "
    f"Mean effect-size_KMvsKHM = {np.mean(statistics['effect-size_KMvsKHM']):.2f}")
'''
####################################################################################################################################################################################


'''
##############################
## MOVIE WITH 4-panel and rho plot


import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.image as mpimg
from tqdm import tqdm
import subprocess

# ----------------------------
# Parameters
# ----------------------------
folders = ["KerrLow", "KHLow", "KerrMid", "KHMid"]  # example
t_start = 15000
t_end   = 30000

aDict = {
    'KerrLow': 0.1,
    'KHLow': 0.1,
    'KerrMid': 0.5,
    'KHMid': 0.5
}

# Existing data
# eddRatioFiles, paramsFiles, jetEfficiency5, etaBZ, plot_style

# ----------------------------
# Directories
# ----------------------------
folder = 'KerrLow'
oldImageDir = '/project/u2grc/Nikola/newSimulations/KerrLow/images'  # your existing PNGs
frameDir = '/project/u2grc/Nikola/newSimulations/KerrLow/images_frames'  # new frames
os.makedirs(frameDir, exist_ok=True)

n_frames = len([f for f in os.listdir(oldImageDir) if f.endswith('.png')])
#n_frames = 10
output_movie = '/project/u2grc/Nikola/newSimulations/figures/four_panel_movie_KerrLow.mp4'

# ----------------------------
# Frame times
# ----------------------------
t_values = np.linspace(t_start, t_end, n_frames)

# ----------------------------
# Frame plotting function
# ----------------------------
def plot_four_panel_frame(t_marker, i_frame, folder,
                          eddRatioFiles, paramsFiles,
                          jetEfficiency5, etaBZ, plot_style, aDict,
                          imageDir, oldImageDir):
    
    fig, axes = plt.subplots(4, 1, figsize=(8, 16), 
                             gridspec_kw={'height_ratios': [1, 1, 1, 2]},  # <-- give image more space
                             constrained_layout=True) 

    # --- 1) Eddington ratio ---
    ax = axes[0]
    #for folder in folders:
    df = eddRatioFiles[folder]
    style = plot_style[folder].copy()
    style['label'] = f"{style['label']} " + r'$\dot{M} / \dot{M}_{\mathrm{Edd}}$'
    ax.plot(df['t'], df['Mdot']/df['MdotEdd'], color=style['color'], linewidth=style['linewidth'], alpha=0.8,
                label=f"{style['label']} " + 'Eddratio')
    ax.axhline(np.mean(df['Mdot']/df['MdotEdd']),
                   color=style.get("color", "black"), linestyle='--', linewidth=1.2)
    ax.set_xlim(t_start, t_end)
        # red marker
    idx = np.searchsorted(df['t'].values, t_marker)
    if idx < len(df):
        ax.plot(df['t'].values[idx], df['Mdot'].values[idx]/df['MdotEdd'].values[idx],
                    'go', markersize=6)
    ax.set_ylabel(r'$\dot{M} / \dot{M}_{\mathrm{Edd}}$')
    ax.set_title('Eddington Ratio')
    ax.legend(fontsize=9)

    # --- 2) Dimensionless magnetic flux ---
    ax = axes[1]
    #for folder in folders:
    df = paramsFiles[folder]
    style = plot_style[folder].copy()
    PhiB_dim = np.sqrt(4 * np.pi) * df['t/Phi_b'] / np.sqrt(np.mean(df['t/Mdot_5']))
    ax.plot(df['coord/t'], PhiB_dim,
                color=style['color'], linewidth=style['linewidth'], alpha=0.8,
                label=f"{style['label']} " + r'$\phi_B$')
    ax.axhline(np.mean(PhiB_dim), color=style['color'], linestyle='--', linewidth=1.2)
    ax.set_xlim(t_start, t_end)
        # red marker
    idx = np.searchsorted(df['coord/t'].values, t_marker)
    if idx < len(df):
        ax.plot(df['coord/t'].values[idx], PhiB_dim[idx], 'go', markersize=6)
    ax.set_ylabel(r'$\phi_B$')
    ax.set_title('Dimensionless Magnetic Flux')
    ax.legend(fontsize=9)

    # --- 3) Jet efficiency ---
    ax = axes[2]
    #for folder in folders:
    df = paramsFiles[folder]
    t = df['coord/t'].values
    eta = jetEfficiency5[folder]
    if len(eta) != len(t):
        eta = eta[:len(t)]  # quick trim if mismatch
    style = plot_style[folder].copy()
    ax.plot(t, eta, color=style['color'], linewidth=style['linewidth'], alpha=0.6)
    ax.set_xlim(t_start, t_end)
    idx = np.searchsorted(t, t_marker)
    if idx < len(t):
        ax.plot(t[idx], eta[idx], 'go', markersize=6)
    ax.set_ylabel(r'$\eta_{\mathrm{jet}}$')
    ax.set_title('Jet Efficiency')
    ax.grid(True, alpha=0.3)

    # --- 4) Movie PNG frame ---
    ax = axes[3]
    # Find closest PNG by index
    old_pngs = sorted([f for f in os.listdir(oldImageDir) if f.endswith('.png')])
    if old_pngs:
        frame_idx = int(i_frame / n_frames * len(old_pngs))
        frame_idx = min(frame_idx, len(old_pngs)-1)
        png_file = os.path.join(oldImageDir, old_pngs[frame_idx])
        img = mpimg.imread(png_file)
        ax.imshow(img, aspect='auto')
        ax.axis('off')
    #ax.set_title(f'Movie Frame t={t_marker:.0f}')

    # --- Common x-axis ---
    axes[-1].set_xlabel('$t_g$')
    for ax in axes:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=12))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=12))
        ax.tick_params(axis='both', which='both', direction='in', top=True, right=True)
        ax.grid(True, alpha=0.3)

    #plt.tight_layout()

    frame_path = os.path.join(imageDir, f'frame_{i_frame:04d}.png')
    fig.savefig(frame_path, dpi=150)
    plt.close(fig)
    return frame_path

# ----------------------------
# Generate all frames
# ----------------------------
frame_files = []
for i, t_marker in enumerate(tqdm(t_values, desc="Generating frames")):
    frame_path = plot_four_panel_frame(
        t_marker, i, folder,
        eddRatioFiles, paramsFiles,
        jetEfficiency5, etaBZ, plot_style, aDict,
        frameDir, oldImageDir
    )
    frame_files.append(frame_path)

# ----------------------------
# Create movie with ffmpeg
# ----------------------------
cmd = [
    'ffmpeg',
    '-y',  # overwrite
    '-framerate', '30',
    '-i', os.path.join(frameDir, 'frame_%04d.png'),
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    output_movie
]
subprocess.run(cmd, check=True)
print(f"Movie saved to {output_movie}")

'''
####################################################################################################################################################################################
