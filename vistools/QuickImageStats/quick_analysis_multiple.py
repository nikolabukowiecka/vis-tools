import ehtim as eh
import numpy as np
import pandas as pd
from pmodes_simple import *
#numpy-1.26.4-py311h64a7726_0

def quick_analysis(files, name, beta_ms=range(6), verbose=True, resolution_muas=20.0, intensityRatioForAnalysis=None, rescaling_lp=None, rescaling_cp=None, frac_ceiling=10):
	data= {'m_net': [],
		'm_avg': [],
		'v_net': [],
		'v_avg': [],
		'beta0': [],
		'arg(beta0)':[],
		'beta1': [],
		'arg(beta1)':[],
		'beta2': [],
		'arg(beta2)':[],
		'beta3': [],
		'arg(beta3)':[],
		'beta4': [],
		'arg(beta4)':[],
		'beta5': [],
		'arg(beta5)':[]}
		
		
	for filename in files:	
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
		'''
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
		for i in beta_ms:
			D['beta'+str(i)] = betas[i]
		#D['beta_ms'] = 0
		'''
		
		data['m_net'].append(m_net)
		data['m_avg'].append(m_avg)
		data['v_net'].append(v_net)
		data['v_avg'].append(v_avg)
		data['beta0'].append(np.abs(betas[0]))
		data['arg(beta0)'].append(np.angle(betas[0], deg=True))
		data['beta1'].append(np.abs(betas[0]))
		data['arg(beta1)'].append(np.angle(betas[1], deg=True))
		data['beta2'].append(np.abs(betas[0]))
		data['arg(beta2)'].append(np.angle(betas[2], deg=True))
		data['beta3'].append(np.abs(betas[0]))
		data['arg(beta3)'].append(np.angle(betas[3], deg=True))
		data['beta4'].append(np.abs(betas[0]))
		data['arg(beta4)'].append(np.angle(betas[4], deg=True))
		data['beta5'].append(np.abs(betas[0]))
		data['arg(beta5)'].append(np.angle(betas[5], deg=True))
		#for i in beta_ms:
		#	data['beta'+str(i)].append({'beta'+str(i):[np.abs(betas[i])]})
		#	data['beta'+str(i)].append({'arg(beta'+str(i):[np.angle(betas[i], deg=True)]})
		'''
		data.update({'m_net': [m_net],
		'm_avg': [m_avg],
		'v_net': [v_net],
		'v_avg': [v_avg]})
		for i in beta_ms:
			data.update({'beta'+str(i):[np.abs(betas[i])]})
			data.update({'arg(beta'+str(i):[np.angle(betas[i], deg=True)]})
		'''
	df = pd.DataFrame(data)
	df.to_csv('betaModes_'+str(name)+'.csv', index=False)
	return data

if __name__ == '__main__':
	import sys, os
	import glob
	files = np.sort(glob.glob(os.path.join(sys.argv[1],'*.h5')))
	name = sys.argv[1].split('/')[5]
	print(name)
	_ = quick_analysis(files, name)
