
import pesummary
from pesummary.io import read
print(pesummary.__version__)
import h5py
from glob import glob

# %matplotlib inline
# %config InlineBackend.figure_format = 'retina'

# -- Get big PE sample file from
# -- https://dcc.ligo.org/public/0169/P2000223/005/all_posterior_samples.tar

# -- Set output directory name
indir = 'all_posterior_samples'
outdir = 'small-pe-gwtc2'

# -- Get list of file names
filelist = glob(indir + '/GW*comoving.h5')
print(filelist)


# -- Get list of file names
filelist = glob(indir + '/GW*comoving.h5')
print(filelist)

# -- Loop over files
for number, infile in enumerate(filelist):

    #-- Construct out file name
    outfile = infile.replace(indir, outdir).replace('comoving', 'small')
    wavefile = infile.replace(indir, outdir).replace('comoving', 'waveform')
    
    #-- open input and output files
    with h5py.File(infile, 'r') as f:
        with h5py.File(outfile,'w') as fn:
            
            print("Making file: ", number)
            #-- copy samples to new file
            f.copy('PublicationSamples', fn)
            f.copy('history', fn)
            f.copy('version', fn)

        with h5py.File(wavefile,'w') as fn:
        
            try: f.copy('C01:IMRPhenomPv2', fn)
            except:
                print(infile, 'PhenomP waveform samples not found!')
                try:
                   f.copy('C01:IMRPhenomPv3HM', fn) 
                except:
                    try:
                        f.copy('C01:TaylorF2-LS', fn)
                    except:                        
                        print('FAILED', infile, f.keys())
                        


            
