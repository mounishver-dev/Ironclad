from vertexai.preview.vision_models import ImageEmbeddingModel
from PIL import Image
import numpy as np

# Load model once
model = ImageEmbeddingModel.from_pretrained("multimodalembedding")

def get_image_embedding(image: Image.Image):
    """
    Convert image → embedding vector
    """
    try:
        embedding = model.get_embeddings(image)
        return np.array(embedding[0].values)
    except Exception as e:
        raise Exception(f"Embedding failed: {str(e)}")