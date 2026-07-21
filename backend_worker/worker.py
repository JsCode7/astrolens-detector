import asyncio
import httpx
import logging
import random
import os
import matplotlib.pyplot as plt
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from PIL import Image
from lenstronomy.LensModel.lens_model import LensModel

from pydantic_settings import BaseSettings
from astroquery.sdss import SDSS
from astropy import coordinates as coords
import astropy.units as u
from astropy.visualization import AsinhStretch, ZScaleInterval
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    api_url: str = "http://localhost:8000"

settings = Settings()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.warning(f"Could not initialize Supabase client: {e}")
    supabase = None

logger.info("Loading ResNet18 model...")
vit_model = models.resnet18(weights=None)
vit_model.fc = nn.Linear(vit_model.fc.in_features, 2)

weights_path = os.path.join(os.path.dirname(__file__), '..', 'ml_training', 'lens_real_weights_best.pth')
if os.path.exists(weights_path):
    vit_model.load_state_dict(torch.load(weights_path, map_location='cpu'))
    logger.info("Successfully loaded REAL synthetic-trained weights!")
else:
    logger.warning("WARNING: lens_real_weights.pth not found! Using random untrained weights.")
vit_model.eval()

class GradCAMHook:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        self.forward_handle = self.target_layer.register_forward_hook(self.save_activation)
        self.backward_handle = self.target_layer.register_full_backward_hook(self.save_gradient)
        
    def save_activation(self, module, input, output):
        self.activations = output.detach()
        
    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()
        
    def remove(self):
        self.forward_handle.remove()
        self.backward_handle.remove()

def run_inference(raw_data, norm_data):
    try:
        from torchvision import transforms
        
        inference_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        h, w = raw_data.shape
        patch_size = 64
        stride = 32
        
        global_attention = np.zeros((h, w), dtype=np.float32)
        hit_counts = np.zeros((h, w), dtype=np.float32)
        max_prob = 0.0
        
        patches = []
        coords = []
        
        for y in range(0, max(1, h - patch_size + 1), stride):
            for x in range(0, max(1, w - patch_size + 1), stride):
                ey, ex = min(y+patch_size, h), min(x+patch_size, w)
                patch = raw_data[y:ey, x:ex]
                
                if patch.shape[0] < patch_size or patch.shape[1] < patch_size:
                    padded = np.zeros((patch_size, patch_size), dtype=patch.dtype)
                    padded[:patch.shape[0], :patch.shape[1]] = patch
                    patch = padded
                
                norm_patch = np.clip(patch, 0, 1)
                img_8u = (norm_patch * 255).astype(np.uint8)
                img_rgb = np.stack([img_8u]*3, axis=-1)
                pil_img = Image.fromarray(img_rgb).resize((224, 224))
                tensor = inference_transform(pil_img)
                patches.append(tensor)
                coords.append((y, x))
                
        if not patches:
            return 0.0, np.zeros_like(norm_data), None, None
            
        batch_tensor = torch.stack(patches)
        batch_size = 32
        cam_hook = GradCAMHook(vit_model, vit_model.layer4)
        
        for i in range(0, len(batch_tensor), batch_size):
            batch = batch_tensor[i:i+batch_size].clone()
            batch.requires_grad = True
            
            with torch.enable_grad():
                outputs = vit_model(batch)
                probs = F.softmax(outputs, dim=1)[:, 0]
                
                vit_model.zero_grad()
                target_scores = outputs[:, 0].sum()
                target_scores.backward()
                
            pooled_gradients = torch.mean(cam_hook.gradients, dim=[2, 3]) # [B, C]
            activations = cam_hook.activations # [B, C, H, W]
            
            for b in range(activations.size(0)):
                act = activations[b].clone()
                for c in range(act.size(0)):
                    act[c, :, :] *= pooled_gradients[b, c]
                    
                heatmap = torch.mean(act, dim=0).cpu().detach().numpy()
                heatmap = np.maximum(heatmap, 0)
                if np.max(heatmap) != 0:
                    heatmap /= np.max(heatmap)
                    
                heatmap_tensor = torch.tensor(heatmap).unsqueeze(0).unsqueeze(0)
                attention_patch = F.interpolate(heatmap_tensor, size=(patch_size, patch_size), mode='bilinear', align_corners=False).squeeze().numpy()
                
                py, px = coords[i+b]
                prob = probs[b].item()
                
                if prob > max_prob:
                    max_prob = prob
                    
                global_attention[py:py+patch_size, px:px+patch_size] += attention_patch * prob
                hit_counts[py:py+patch_size, px:px+patch_size] += 1
                
        cam_hook.remove()
        
        hit_counts[hit_counts == 0] = 1
        global_attention /= hit_counts
        
        if np.max(global_attention) != 0:
            global_attention /= np.max(global_attention)
            
        return max_prob, global_attention, None, None
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        return 0.0, np.zeros_like(raw_data), None, None

def run_lenstronomy():
    lens_model = LensModel(lens_model_list=['SIS'])
    kwargs = [{'theta_E': 1.5, 'center_x': 0, 'center_y': 0}]
    alpha_x, alpha_y = lens_model.alpha(1.0, 1.0, kwargs)
    einstein_radius = kwargs[0]['theta_E']
    mass_estimate = 1e12 # dummy solar masses
    return einstein_radius, mass_estimate

async def process_job(job: dict, client: httpx.AsyncClient):
    job_id = job["id"]
    logger.info(f"Processing job {job_id}")
    
    await client.put(f"{settings.api_url}/api/jobs/{job_id}/status?status=processing")
    
    png_filename = f"candidate_{job_id}.png"
    attn_filename = f"attention_{job_id}.png"
    input_tensor = None
    output = None
    
    try:
        if not supabase:
            raise Exception("Supabase client not initialized.")
            
        logger.info(f"Downloading FITS data for job {job_id} using astroquery...")
        
        job_name = job.get('job_name', '')
        try:
            ra_str, dec_str = job_name.strip().split()
            ra = float(ra_str)
            dec = float(dec_str)
            coord_str = f"{ra}d {dec}d"
        except Exception:
            coord_str = '179.68929342d -0.45437906d'
            logger.warning(f"Could not parse RA DEC from '{job_name}', using default {coord_str}")

        pos = coords.SkyCoord(coord_str, frame='icrs')
        
        try:
            xid = SDSS.query_region(pos, radius=20*u.arcsec, photoobj_fields=['run', 'rerun', 'camcol', 'field', 'ra', 'dec', 'type', 'modelMag_g'], specobj_fields=['z'])
            if xid is None or len(xid) == 0:
                raise Exception("Empty result for spectroscopy")
        except Exception as e:
            logger.warning(f"Spectroscopy failed or not available, trying photometry only. Error: {e}")
            try:
                xid = SDSS.query_region(pos, radius=20*u.arcsec, photoobj_fields=['run', 'rerun', 'camcol', 'field', 'ra', 'dec', 'type', 'modelMag_g'])
            except:
                xid = None
                
        if xid is None or len(xid) == 0:
            raise Exception("No SDSS matches found.")
            
        images = SDSS.get_images(matches=xid, band='g')
        if not images:
            raise Exception("Failed to download FITS image.")
            
        hdul = images[0]
        data = hdul[0].data
        
        transform = AsinhStretch() + ZScaleInterval()
        norm_data = transform(data)
        
        plt.imsave(png_filename, norm_data, cmap='gray', origin='lower')
        
        logger.info(f"Uploading {png_filename} to Supabase...")
        with open(png_filename, 'rb') as f:
            supabase.storage.from_('candidates').upload(
                file=f,
                path=png_filename,
                file_options={"content-type": "image/png", "upsert": "true"}
            )
        image_url = supabase.storage.from_('candidates').get_public_url(png_filename)
        
        logger.info(f"Running inference for job {job_id}...")
        prob, attention_map, input_tensor, output = await asyncio.to_thread(run_inference, data, norm_data)
        
        plt.imsave(attn_filename, attention_map, cmap='hot', origin='lower')
        with open(attn_filename, 'rb') as f:
            supabase.storage.from_('candidates').upload(
                file=f,
                path=attn_filename,
                file_options={"content-type": "image/png", "upsert": "true"}
            )
        attention_url = supabase.storage.from_('candidates').get_public_url(attn_filename)
        
        redshift = None
        magnitude = None
        obj_type_str = "UNKNOWN"
        
        if xid is not None and len(xid) > 0:
            cols = xid.colnames
            if 'z' in cols:
                redshift = float(xid['z'][0])
            if 'modelMag_g' in cols:
                magnitude = float(xid['modelMag_g'][0])
            if 'type' in cols:
                obj_type = int(xid['type'][0])
                if obj_type == 3:
                    obj_type_str = "GALAXY"
                elif obj_type == 6:
                    obj_type_str = "STAR"
                else:
                    obj_type_str = f"TYPE_{obj_type}"
                    
        candidate_data = {
            "id": random.randint(1, 1000000),
            "job_id": job_id,
            "candidate_name": f"Candidate from {job.get('job_name', 'Job')}",
            "confidence_score": prob,
            "image_url": image_url,
            "redshift": redshift,
            "magnitude": magnitude,
            "object_type": obj_type_str,
            "attention_image_url": attention_url
        }
        await client.post(f"{settings.api_url}/api/candidates", json=candidate_data)
        
        await client.put(f"{settings.api_url}/api/jobs/{job_id}/status?status=completed")
        logger.info(f"Job {job_id} completed successfully.")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        await client.put(f"{settings.api_url}/api/jobs/{job_id}/status?status=failed")
    finally:
        if os.path.exists(png_filename):
            os.remove(png_filename)
        if os.path.exists(attn_filename):
            os.remove(attn_filename)
            
        if input_tensor is not None:
            del input_tensor
        if output is not None:
            del output
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

async def worker_loop():
    logger.info("Worker started.")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(f"{settings.api_url}/api/jobs/pending")
                if response.status_code == 200:
                    jobs = response.json()
                    for job in jobs:
                        await process_job(job, client)
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
            
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
