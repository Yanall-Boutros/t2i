# ------------------------------------------------------------------------
# Import Statements
# ------------------------------------------------------------------------
import sys
import numpy as np
from torchvision.utils import save_image
from diffusers import DiffusionPipeline
import torch
import cv2
import pdb
# ------------------------------------------------------------------------
# config
# ------------------------------------------------------------------------
n_steps = 40
high_noise_frac = 0.8
# Define how many steps and what % of steps to be run on each experts (80/20) here

# run both experts
def main(prompt):
    # load both base & refiner
    base = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    base.to("cuda")
    image = base(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_end=high_noise_frac,
        output_type="latent",
    ).images
    vae = base.vae
    text_encoder = base.text_encoder_2
    del(base)
    torch.cuda.empty_cache()
    refiner = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0",
    text_encoder_2=text_encoder,
    vae=vae,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",)
    refiner.to("cuda")
    
    image = refiner(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_start=high_noise_frac,
        image=image,
    ).images[0]
    image.save(f"{prompt}.png")

if __name__ == "__main__": main(sys.argv[1])
