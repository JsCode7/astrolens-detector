import os
import numpy as np
from PIL import Image
from tqdm import tqdm
from synthetic_dataset import generate_lens_image

def create_dirs(base_path):
    for split in ['train', 'val']:
        for cls in ['lens', 'no_lens']:
            os.makedirs(os.path.join(base_path, split, cls), exist_ok=True)

def generate_and_save(base_path, split, num_samples):
    print(f"Generating {num_samples} {split} images to disk...")
    for i in tqdm(range(num_samples)):
        has_lens = np.random.rand() > 0.5
        img = generate_lens_image(has_lens=has_lens)
        
        img_8u = (img * 255).astype(np.uint8)
        img_rgb = np.stack([img_8u]*3, axis=-1)
        
        pil_img = Image.fromarray(img_rgb)
        
        cls_dir = 'lens' if has_lens else 'no_lens'
        file_path = os.path.join(base_path, split, cls_dir, f"{split}_{i:05d}.png")
        pil_img.save(file_path, format="PNG")
        
        pil_img.close()

if __name__ == "__main__":
    BASE_DIR = "dataset"
    create_dirs(BASE_DIR)
    
    train_samples = 40000
    val_samples = 10000
    
    generate_and_save(BASE_DIR, 'train', train_samples)
    generate_and_save(BASE_DIR, 'val', val_samples)
    print("Dataset generated successfully on disk!")
