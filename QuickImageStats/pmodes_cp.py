import ehtim as eh
import numpy as np
from .convolveSquareImage import *

def pmodes_cp(im, ms, r_min=0, r_max=np.inf, norm_with_StokesI=False, blur_fwhm_muas=20):
	'''
	An adaptation of the pmodes script for circular polarization.

	Note the unusual default of norm_with_StokesI = False
	'''

	if type(im) == eh.image.Image:
		npix = im.xdim
		iarr = im.ivec.reshape(npix, npix)
		qarr = im.qvec.reshape(npix, npix)
		uarr = im.uvec.reshape(npix, npix)
		varr = im.vvec.reshape(npix, npix)
		fov_muas = im.fovx()/eh.RADPERUAS
	else:
		with h5py.File(im,'r') as hfp:
			DX = hfp['header']['camera']['dx'][()]
			dsource = hfp['header']['dsource'][()]
			lunit = hfp['header']['units']['L_unit'][()]
			scale = hfp['header']['scale'][()]
			pol = np.flip(np.copy(hfp['pol']).transpose((1,0,2)),axis=0) * scale

		fov_muas = DX / dsource * lunit * 2.06265e11
		npix = pol.shape[0]
		iarr = pol[:,:,0]
		varr = pol[:,:,3]

	if blur_fwhm_muas > 0:
		iarr = convolveSquareImage(iarr, fov_muas, blur_fwhm_muas)
		varr = convolveSquareImage(varr, fov_muas, blur_fwhm_muas)

	normvarr = np.abs(varr)
	area = (r_max*r_max - r_min*r_min) * np.pi
	pxi = (np.arange(npix)-0.01)/npix-0.5
	pxj = np.arange(npix).astype(float)/npix-0.5
	mui = pxi*fov_muas
	muj = pxj*fov_muas
	MUI,MUJ = np.meshgrid(mui,muj)
	MUDISTS = np.sqrt(np.power(MUI,2.)+np.power(MUJ,2.))

	# get angles measured East of North
	PXI,PXJ = np.meshgrid(pxi,pxj)

	#Razi wants this.  Check this.
	'''
	angles = np.arctan2(PXI,PXJ)
	'''
	angles = np.arctan2(-PXJ,PXI) - np.pi/2.
	angles[angles<0.] += 2.*np.pi

	# get flux in annulus
	tf = iarr[(MUDISTS<=r_max) & (MUDISTS>=r_min)].sum()

	# get total polarized flux in annulus
	pf = normvarr[(MUDISTS<=r_max) & (MUDISTS>=r_min)].sum()

	#get number of pixels in annulus
	npix = iarr[(MUDISTS<=r_max) & (MUDISTS>=r_min)].size

	# compute betas
	betas = []
	for m in ms:
		v1basis = np.cos(-angles*m)
		v2basis = np.sin(-angles*m)
		pbasis = v1basis + 1.j*v2basis
		prod = varr * pbasis	## This is the analog of the quantity of interest for the circular polarization >>>  varr
		coeff = prod[(MUDISTS<=r_max) & (MUDISTS>=r_min)].sum()
		if norm_with_StokesI:
			coeff /= tf
		else:
			coeff /= pf
		betas.append(coeff)

	return betas

