"""
Paraphrase Service
==================
Provides functionality to paraphrase Indonesian text using the 
Wikidepia/IndoT5-base-paraphrase model.
"""

import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

logger = logging.getLogger(__name__)

MODEL_NAME = "Wikidepia/IndoT5-base-paraphrase"
_tokenizer = None
_model = None

def get_model():
    """Lazily load the tokenizer and model."""
    global _tokenizer, _model
    if _model is None:
        logger.info("Loading paraphrase model: %s ...", MODEL_NAME)
        try:
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error("Failed to load model: %s", e)
            raise e
    return _tokenizer, _model

def paraphrase_text(text: str, num_sequences: int = 1) -> list[str]:
    """
    Generate paraphrases for the given text.
    
    Args:
        text (str): Input text to paraphrase.
        num_sequences (int): Number of variations to generate.
        
    Returns:
        list[str]: List of paraphrased texts.
    """
    tokenizer, model = get_model()
    
    # Preprocess input
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=512,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            num_return_sequences=num_sequences,
            early_stopping=True
        )
    
    # Decode
    results = []
    for output in outputs:
        decoded = tokenizer.decode(output, skip_special_tokens=True)
        results.append(decoded)
        
    return results
