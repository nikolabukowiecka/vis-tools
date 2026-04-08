import ehtim as eh
import numpy as np
import pandas as pd
from pmodes_simple import *
#numpy-1.26.4-py311h64a7726_0

def quick_analysis(filename, beta_ms=range(6), verbose=True, resolution_muas=0.0, intensityRatioForAnalysis=None, rescaling_lp=None, rescaling_cp=None, frac_ceiling=10):
	#resolution_muas=20 #check wheter its overwritten
	#Load image with ehtim.
	im = eh.image.load_image(filename)

	#Assembly Stokes arrays.
	npix = im.xdim
	iarr = im.ivec.reshape(npix, npix)
	qarr = im.qvec.reshape(npix, npix)
	uarr = im.uvec.reshape(npix, npix)
	varr = im.vvec.reshape(npix, npix)

	#Optional rescaling. Necessary for synthetic data.
	if rescaling_lp is not None:
		q_new = qarr * rescaling_lp
		u_new = uarr * rescaling_lp
		mask = np.sqrt(q_new**2 + u_new**2)/iarr < frac_ceiling
		qarr[mask] = q_new[mask]
		uarr[mask] = u_new[mask]
	if rescaling_cp is not None:
		vnew = varr * rescaling_cp
		mask = np.abs(vnew/iarr) < frac_ceiling
		varr[mask] = vnew[mask]

	#We may want to consider masking the image in some areas.
	if intensityRatioForAnalysis is not None:
		mask = iarr < intensityRatioForAnalysis * np.max(iarr)
		iarr[mask] = 0
		qarr[mask] = 0
		uarr[mask] = 0
		varr[mask] = 0

	#Compute beta modes.
	betas = pmodes(im.blur_circ(resolution_muas*eh.RADPERUAS,fwhm_pol=resolution_muas*eh.RADPERUAS), beta_ms, intensityRatioForAnalysis=intensityRatioForAnalysis)

	#Net polarization.
	m_net = np.sqrt(np.sum(qarr)**2 + np.sum(uarr)**2) / np.sum(iarr)
	v_net = np.sum(varr) / np.sum(iarr)

	#Blur and obtain average polarization.
	im_blurred = im.blur_circ(resolution_muas*eh.RADPERUAS,fwhm_pol=resolution_muas*eh.RADPERUAS)
	iarr_blurred = im_blurred.ivec.reshape(npix, npix)
	qarr_blurred = im_blurred.qvec.reshape(npix, npix)
	uarr_blurred = im_blurred.uvec.reshape(npix, npix)
	parr_blurred = np.sqrt(qarr_blurred**2 + uarr_blurred**2)
	varr_blurred = im_blurred.vvec.reshape(npix, npix)
	m_avg = np.sum(parr_blurred) / np.sum(iarr_blurred)
	v_frac = np.abs(varr_blurred/iarr_blurred)
	v_frac_is_finite = np.isfinite(v_frac)
	finite_intensity = iarr_blurred != 0
	v_avg = np.sum(v_frac[finite_intensity] * iarr_blurred[finite_intensity]) / np.sum(iarr_blurred[finite_intensity])
	
	#Print what you found, if desired.
	if verbose:
		print("Beta Modes:")
		for i in beta_ms:
			print(f"   {i}: |beta_{i}|={np.abs(betas[i]):1.3f}, arg(beta_{i})={np.angle(betas[i], deg=True):1.3f}")
		print(f"|beta_2|/|beta_1| = {np.abs(betas[2])/np.abs(betas[1]):1.3f}")
		print(f"|beta_2|/sum(|beta_i|) = {np.abs(betas[2])/np.sum(np.abs(betas)):1.3f}")
		print(f"m_net = {m_net:1.3f}")
		print(f"m_avg = {m_avg:1.3f}")
		print(f"v_net = {v_net:1.3f}")
		print(f"v_avg = {v_avg:1.3f}")

	#Output a dictionary.
	D = {}
	D['m_net'] = m_net
	D['m_avg'] = m_avg
	D['v_net'] = v_net
	D['v_avg'] = v_avg
	D['beta_ms'] = beta_ms
	D['resolution_muas'] = resolution_muas
	D['betas'] = betas

	return D

if __name__ == '__main__':
	import sys
	filename = sys.argv[1]
	_ = quick_analysis(filename)
