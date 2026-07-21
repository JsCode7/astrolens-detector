import numpy as np
import matplotlib.pyplot as plt

file_path = r'C:\Users\Crissys\personalWorkspace\AstroLens\ml_training\real_backgrounds\bg_0000.npy'
data = np.load(file_path)

print(f"Shape: {data.shape}")
print(f"Dtype: {data.dtype}")
print(f"Min: {data.min():.4f}")
print(f"Max: {data.max():.4f}")
print(f"Mean: {data.mean():.4f}")
print(f"Std: {data.std():.4f}")

try:
    plt.imshow(data, cmap='gray' if data.ndim == 2 else None)
    plt.colorbar()
    plt.title('bg_0000.npy preview')
    out_path = r'C:\Users\Crissys\personalWorkspace\AstroLens\ml_training\real_backgrounds\bg_0000_preview.png'
    plt.savefig(out_path)
    print(f"Successfully saved preview to {out_path}")
except Exception as e:
    print(f"Could not save preview image due to: {e}")
