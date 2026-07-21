import os
import time
import random
import numpy as np
from tqdm import tqdm
from astroquery.sdss import SDSS
from astropy import coordinates as coords
import astropy.units as u
from astropy.visualization import AsinhStretch, ZScaleInterval
import warnings

warnings.filterwarnings('ignore')

def download_backgrounds(num_images=100, output_dir="real_backgrounds"):
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Downloading {num_images} real SDSS backgrounds...")
    
    transform = AsinhStretch() + ZScaleInterval()
    successful = 0
    attempts = 0
    
    
    pbar = tqdm(total=num_images)
    
    while successful < num_images:
        attempts += 1
        ra = random.uniform(120, 250)
        dec = random.uniform(0, 50)
        
        pos = coords.SkyCoord(f"{ra}d {dec}d", frame='icrs')
        
        try:
            xid = SDSS.query_region(pos, radius=30*u.arcsec)
            if xid is None or len(xid) == 0:
                continue
                
            images = SDSS.get_images(matches=xid, band='g')
            if not images:
                continue
                
            hdul = images[0]
            data = hdul[0].data
            
            if data is None or data.shape[0] < 64 or data.shape[1] < 64:
                continue
                
            norm_data = transform(data)
            
            filepath = os.path.join(output_dir, f"bg_{successful:04d}.npy")
            np.save(filepath, norm_data)
            
            successful += 1
            pbar.update(1)
            
            time.sleep(1)
            
        except Exception as e:
            time.sleep(2)
            continue
            
    pbar.close()
    print(f"Successfully downloaded {successful} backgrounds in {attempts} attempts.")

if __name__ == "__main__":
    download_backgrounds(100)
