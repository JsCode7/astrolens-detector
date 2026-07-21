import numpy as np
import os
import glob
import random
from lenstronomy.LensModel.lens_model import LensModel
from lenstronomy.LightModel.light_model import LightModel
from lenstronomy.Util import util
from scipy.ndimage import gaussian_filter

REAL_BACKGROUNDS = []
BG_DIR = os.path.join(os.path.dirname(__file__), 'real_backgrounds')
if os.path.exists(BG_DIR):
    bg_files = glob.glob(os.path.join(BG_DIR, '*.npy'))
    if bg_files:
        print(f"Loading {len(bg_files)} real backgrounds into memory for Sim-to-Real...")
        for f in bg_files:
            try:
                bg = np.load(f)
                if bg.shape[0] >= 64 and bg.shape[1] >= 64:
                    REAL_BACKGROUNDS.append(bg)
            except:
                pass
    else:
        print("\n" + "="*60)
        print("WARNING: 'real_backgrounds' directory is empty or missing!")
        print("Training will fallback to pure black synthetic noise.")
        print("This will cause the Sim-to-Real gap to fail on real SDSS images!")
        print("="*60 + "\n")
else:
    print("\n" + "="*60)
    print("WARNING: 'real_backgrounds' directory not found!")
    print("Training will fallback to pure black synthetic noise.")
    print("This will cause the Sim-to-Real gap to fail on real SDSS images!")
    print("="*60 + "\n")



def generate_lens_image(has_lens=True, num_pix=64, delta_pix=0.396):
    """
    Generates a mock astronomical image.
    If has_lens=True, simulates a Strong Gravitational Lens curving a background source.
    """
    x, y = util.make_grid(num_pix=num_pix, delta_pix=delta_pix)
    
    lens_light_model = LightModel(light_model_list=['SERSIC_ELLIPSE'])
    kwargs_lens_light = [{
        'amp': 100, 
        'R_sersic': 0.5, 
        'n_sersic': 4, 
        'e1': np.random.uniform(-0.2, 0.2), 
        'e2': np.random.uniform(-0.2, 0.2), 
        'center_x': 0, 
        'center_y': 0
    }]
    
    flux = lens_light_model.surface_brightness(x, y, kwargs_lens_light)
    
    source_light_model = LightModel(light_model_list=['SERSIC_ELLIPSE'])
    src_x = np.random.uniform(-0.4, 0.4)
    src_y = np.random.uniform(-0.4, 0.4)
    
    kwargs_source = [{
        'amp': 60, 
        'R_sersic': 0.2, 
        'n_sersic': 1.5, 
        'e1': np.random.uniform(-0.4, 0.4), 
        'e2': np.random.uniform(-0.4, 0.4), 
        'center_x': src_x, 
        'center_y': src_y
    }]

    if has_lens:
        lens_model = LensModel(lens_model_list=['SIE', 'SHEAR'])
        theta_E = np.random.uniform(1.0, 2.2)
        e1, e2 = np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3)
        gamma1, gamma2 = np.random.uniform(-0.05, 0.05), np.random.uniform(-0.05, 0.05)
        
        kwargs_lens = [
            {'theta_E': theta_E, 'e1': e1, 'e2': e2, 'center_x': 0, 'center_y': 0},
            {'gamma1': gamma1, 'gamma2': gamma2, 'ra_0': 0, 'dec_0': 0}
        ]
        
        beta_x, beta_y = lens_model.ray_shooting(x, y, kwargs_lens)
        flux_source = source_light_model.surface_brightness(beta_x, beta_y, kwargs_source)
    else:
        flux_source = source_light_model.surface_brightness(x, y, kwargs_source)
        
    flux += flux_source
    
    flux = (flux / np.sum(flux)) * 50000.0
        
    image = util.array2image(flux)
    
    image = gaussian_filter(image, sigma=1.2)
    
    if REAL_BACKGROUNDS:
        bg = random.choice(REAL_BACKGROUNDS)
        h, w = bg.shape
        y = np.random.randint(0, h - num_pix + 1)
        x = np.random.randint(0, w - num_pix + 1)
        bg_crop = bg[y:y+num_pix, x:x+num_pix].copy()
        
        if np.random.rand() > 0.5: bg_crop = np.fliplr(bg_crop)
        if np.random.rand() > 0.5: bg_crop = np.flipud(bg_crop)
        bg_crop = np.rot90(bg_crop, np.random.randint(0, 4))
        
        bg_max = np.max(bg_crop) if np.max(bg_crop) > 0 else 1.0
        
        synthetic_flux = (image / np.max(image)) * (bg_max * 0.7) 
        final_image = bg_crop + synthetic_flux
    else:
        image[image < 0] = 0
        image = np.random.poisson(image * 10.0) / 10.0
        bkg_noise = np.random.normal(0, 1.5, image.shape)
        image += bkg_noise
        final_image = (image + 5.0) / 40.0  

    if np.random.rand() > 0.6:  # Reducido a un 40% de probabilidad
        num_stars = np.random.randint(1, 3)
        for _ in range(num_stars):
            sy = np.random.choice([np.random.randint(0, 15), np.random.randint(49, num_pix)])
            sx = np.random.choice([np.random.randint(0, 15), np.random.randint(49, num_pix)])
            
            star = np.zeros((num_pix, num_pix))
            star[sy, sx] = np.random.uniform(10, 50) 
            star = gaussian_filter(star, sigma=np.random.uniform(0.5, 1.5))
            final_image += star
        
    final_image = np.maximum(final_image, 0.0)
    final_image = np.log10(final_image + 1.0) / np.log10(np.max(final_image) + 1.0)
    
    final_image = np.clip(final_image, 0, 1)
        
    return final_image
