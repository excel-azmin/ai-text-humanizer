"""
AI Text Humanizer Engine
Fast, open-source solution for humanizing AI-generated content
"""

import random
import re
import numpy as np
from typing import List, Dict, Tuple, Optional
import nltk
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    T5ForConditionalGeneration,
    T5Tokenizer,
    pipeline
)
import torch
from sentence_transformers import SentenceTransformer
import spacy
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

class HumanizerEngine:
    """
    Multi-technique AI text humanizer for fast, effective results
    """
    
    def __init__(self, 
                 use_gpu: bool = True,
                 model_size: str = "small",  # small, medium, large
                 techniques: List[str] = None):
        """
        Initialize the humanizer with configurable models and techniques
        
        Args:
            use_gpu: Use CUDA if available
            model_size: Model size preference for speed/quality tradeoff
            techniques: List of techniques to apply
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.model_size = model_size
        
        # Default techniques - can be customized
        self.techniques = techniques or [
            "sentence_variation",
            "perplexity_modulation", 
            "stylistic_injection",
            "semantic_paraphrasing",
            "human_patterns"
        ]
        
        # Initialize models based on size preference
        self._init_models()
        
        # Pattern banks for humanization
        self._init_pattern_banks()
        
    def _init_models(self):
        """Initialize models based on size preference"""
        
        if self.model_size == "small":
            # Fast, lightweight models
            self.paraphrase_model = "Vamsi/T5_Paraphrase_Paws"
            self.style_model = "distilgpt2"
            self.semantic_model = "sentence-transformers/all-MiniLM-L6-v2"
        elif self.model_size == "medium":
            # Balanced performance
            self.paraphrase_model = "ramsrigouthamg/t5-large-paraphraser-diverse-high-quality"
            self.style_model = "gpt2-medium"
            self.semantic_model = "sentence-transformers/all-mpnet-base-v2"
        else:  # large
            # Best quality, slower
            self.paraphrase_model = "humarin/chatgpt_paraphraser_on_T5_base"
            self.style_model = "gpt2-large"
            self.semantic_model = "sentence-transformers/all-roberta-large-v1"
            
        # Load models lazily to save memory
        self.models_loaded = False
        
    def _load_models(self):
        """Lazy load models when first needed"""
        if self.models_loaded:
            return
            
        print(f"Loading models on {self.device}...")
        
        # Paraphrasing model
        self.paraphraser_tokenizer = T5Tokenizer.from_pretrained(self.paraphrase_model)
        self.paraphraser = T5ForConditionalGeneration.from_pretrained(
            self.paraphrase_model
        ).to(self.device)
        
        # Style transfer model  
        self.style_tokenizer = AutoTokenizer.from_pretrained(self.style_model)
        self.style_generator = AutoModelForCausalLM.from_pretrained(
            self.style_model
        ).to(self.device)
        
        # Semantic similarity model
        self.semantic_encoder = SentenceTransformer(self.semantic_model)
        
        # SpaCy for linguistic analysis
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
            
        self.models_loaded = True
        print("Models loaded successfully!")
        
    def _init_pattern_banks(self):
        """Initialize human writing pattern banks"""
        
        # Transition phrases humans commonly use
        self.transitions = [
            "Actually,", "You know,", "To be honest,", "Interestingly,",
            "Here's the thing:", "The way I see it,", "From my perspective,",
            "Let me explain:", "Basically,", "In other words,", "Simply put,",
            "Well,", "So,", "Now,", "Look,", "See,", "Anyway,", "Besides,",
        ]
        
        # Filler phrases and hedges
        self.fillers = [
            "kind of", "sort of", "pretty much", "more or less", "essentially",
            "basically", "actually", "really", "quite", "rather", "somewhat",
            "perhaps", "maybe", "probably", "I think", "I believe", "it seems",
        ]
        
        # Colloquialisms and informal expressions
        self.colloquialisms = [
            "a bit", "a lot", "tons of", "bunch of", "loads of",
            "got to", "gotta", "gonna", "want to", "wanna",
            "isn't", "aren't", "won't", "can't", "doesn't",
        ]
        
        # Personal touches
        self.personal_touches = [
            "I'd say", "I mean", "if you ask me", "in my experience",
            "from what I've seen", "personally", "honestly",
        ]
        
        # Minor imperfections patterns
        self.imperfections = [
            ("it's", "its", 0.02),  # Occasional its/it's variation
            ("their", "there", 0.01),  # Very rare their/there
            ("effect", "affect", 0.01),  # effect/affect
            ("who", "that", 0.03),  # who/that for people
        ]
        
    def humanize(self, 
                 text: str, 
                 intensity: float = 0.7,
                 preserve_meaning: bool = True,
                 fast_mode: bool = False) -> str:
        """
        Main humanization function
        
        Args:
            text: Input text to humanize
            intensity: How much to modify (0.0-1.0)
            preserve_meaning: Maintain semantic similarity
            fast_mode: Skip heavy processing for speed
            
        Returns:
            Humanized text
        """
        # Load models on first use
        if not self.models_loaded:
            self._load_models()
            
        # Split into sentences for processing
        sentences = self._split_sentences(text)
        
        # Process based on selected techniques
        if fast_mode:
            # Fast mode: Only lightweight techniques
            humanized = self._fast_humanize(sentences, intensity)
        else:
            # Full processing
            humanized = self._full_humanize(sentences, intensity, preserve_meaning)
            
        return humanized
    
    def _split_sentences(self, text: str) -> List[str]:
        """Smart sentence splitting"""
        # Use regex for better sentence boundary detection
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _fast_humanize(self, sentences: List[str], intensity: float) -> str:
        """Fast humanization using pattern-based techniques only"""
        result = []
        
        for i, sentence in enumerate(sentences):
            # Apply lightweight modifications
            if "sentence_variation" in self.techniques:
                sentence = self._vary_sentence_structure(sentence, intensity)
            
            if "human_patterns" in self.techniques:
                sentence = self._add_human_patterns(sentence, intensity)
                
            # Add transitions between sentences
            if i > 0 and random.random() < intensity * 0.3:
                sentence = random.choice(self.transitions) + " " + sentence.lower()
                
            result.append(sentence)
            
        # Vary paragraph structure
        humanized = self._create_paragraph_variation(result, intensity)
        
        return humanized
    
    def _full_humanize(self, 
                       sentences: List[str], 
                       intensity: float,
                       preserve_meaning: bool) -> str:
        """Full humanization with all techniques"""
        result = []
        
        # Store original embeddings if preserving meaning
        if preserve_meaning:
            original_embeddings = self.semantic_encoder.encode(sentences)
        
        for i, sentence in enumerate(sentences):
            # Apply multiple techniques based on configuration
            
            if "semantic_paraphrasing" in self.techniques:
                sentence = self._paraphrase_sentence(sentence, intensity)
            
            if "sentence_variation" in self.techniques:
                sentence = self._vary_sentence_structure(sentence, intensity)
            
            if "perplexity_modulation" in self.techniques:
                sentence = self._modulate_perplexity(sentence, intensity)
                
            if "stylistic_injection" in self.techniques:
                sentence = self._inject_style(sentence, intensity)
                
            if "human_patterns" in self.techniques:
                sentence = self._add_human_patterns(sentence, intensity)
            
            # Check semantic preservation
            if preserve_meaning:
                new_embedding = self.semantic_encoder.encode([sentence])[0]
                similarity = np.dot(original_embeddings[i], new_embedding) / (
                    np.linalg.norm(original_embeddings[i]) * np.linalg.norm(new_embedding)
                )
                
                # Revert if meaning changed too much
                if similarity < 0.7:
                    sentence = sentences[i]  # Revert to original
                    # Apply only lightweight changes
                    sentence = self._add_human_patterns(sentence, intensity * 0.5)
            
            result.append(sentence)
        
        # Create natural paragraph flow
        humanized = self._create_paragraph_variation(result, intensity)
        
        return humanized
    
    def _paraphrase_sentence(self, sentence: str, intensity: float) -> str:
        """Use T5 model for paraphrasing"""
        if random.random() > intensity:
            return sentence
            
        try:
            # Prepare input
            input_text = f"paraphrase: {sentence}"
            inputs = self.paraphraser_tokenizer(
                input_text, 
                return_tensors="pt", 
                max_length=512,
                truncation=True
            ).to(self.device)
            
            # Generate paraphrase
            with torch.no_grad():
                outputs = self.paraphraser.generate(
                    **inputs,
                    max_length=len(sentence.split()) * 2,
                    num_beams=4,
                    temperature=0.7 + (intensity * 0.5),
                    do_sample=True,
                    top_p=0.9,
                    num_return_sequences=1
                )
            
            paraphrased = self.paraphraser_tokenizer.decode(
                outputs[0], 
                skip_special_tokens=True
            )
            
            return paraphrased
        except:
            return sentence
    
    def _vary_sentence_structure(self, sentence: str, intensity: float) -> str:
        """Vary sentence structure and length"""
        words = sentence.split()
        
        # Randomly split long sentences
        if len(words) > 15 and random.random() < intensity * 0.5:
            mid = len(words) // 2
            # Find good split point (after comma, conjunction, etc.)
            for i in range(mid - 3, mid + 3):
                if i < len(words) and words[i] in [',', 'and', 'but', 'or', 'while', 'although']:
                    sentence = ' '.join(words[:i]) + '. ' + ' '.join(words[i+1:]).capitalize()
                    break
        
        # Randomly combine short sentences (handled at paragraph level)
        
        # Reorder clauses occasionally
        if ',' in sentence and random.random() < intensity * 0.3:
            parts = sentence.split(',')
            if len(parts) == 2:
                sentence = parts[1].strip().capitalize() + ', ' + parts[0].strip().lower()
        
        return sentence
    
    def _modulate_perplexity(self, sentence: str, intensity: float) -> str:
        """Add controlled unpredictability to word choices"""
        words = sentence.split()
        doc = self.nlp(sentence)
        
        for token in doc:
            if random.random() < intensity * 0.1:
                # Replace with synonyms for content words
                if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'ADV']:
                    # Simple synonym replacement (can be enhanced with WordNet)
                    synonyms = self._get_simple_synonyms(token.text)
                    if synonyms:
                        words[token.i] = random.choice(synonyms)
        
        return ' '.join(words)
    
    def _get_simple_synonyms(self, word: str) -> List[str]:
        """Get simple synonyms (can be enhanced with WordNet)"""
        # Basic synonym mapping - in production, use WordNet or similar
        synonyms = {
            'good': ['great', 'fine', 'nice', 'excellent', 'solid'],
            'bad': ['poor', 'terrible', 'awful', 'lousy'],
            'big': ['large', 'huge', 'massive', 'enormous'],
            'small': ['little', 'tiny', 'minor', 'slight'],
            'fast': ['quick', 'rapid', 'speedy', 'swift'],
            'slow': ['gradual', 'leisurely', 'sluggish'],
            # Add more as needed
        }
        return synonyms.get(word.lower(), [])
    
    def _inject_style(self, sentence: str, intensity: float) -> str:
        """Inject human-like stylistic elements"""
        if random.random() > intensity:
            return sentence
            
        # Add rhetorical questions
        if random.random() < 0.1:
            questions = [
                "You know what?",
                "But here's the question:",
                "Want to know something interesting?",
                "Guess what?",
            ]
            sentence = random.choice(questions) + " " + sentence
        
        # Add emphasis with italics simulation (markdown)
        words = sentence.split()
        if len(words) > 5 and random.random() < 0.15:
            idx = random.randint(1, len(words) - 2)
            if words[idx] not in ['the', 'a', 'an', 'and', 'or', 'but']:
                words[idx] = f"*{words[idx]}*"
        
        return ' '.join(words)
    
    def _add_human_patterns(self, sentence: str, intensity: float) -> str:
        """Add human-like patterns and imperfections"""
        
        # Add fillers occasionally
        if random.random() < intensity * 0.2:
            filler = random.choice(self.fillers)
            words = sentence.split()
            if len(words) > 3:
                insert_pos = random.randint(1, len(words) - 1)
                words.insert(insert_pos, filler)
                sentence = ' '.join(words)
        
        # Use contractions
        if random.random() < intensity * 0.4:
            replacements = [
                ("it is", "it's"), ("is not", "isn't"), ("cannot", "can't"),
                ("will not", "won't"), ("do not", "don't"), ("I am", "I'm"),
                ("you are", "you're"), ("they are", "they're"),
            ]
            for formal, informal in replacements:
                sentence = sentence.replace(formal, informal)
        
        # Add minor imperfections (very sparingly)
        if random.random() < intensity * 0.05:
            for correct, variant, chance in self.imperfections:
                if correct in sentence and random.random() < chance:
                    sentence = sentence.replace(correct, variant, 1)
        
        # Add personal touches
        if random.random() < intensity * 0.15:
            touch = random.choice(self.personal_touches)
            sentence = touch + ", " + sentence.lower()
        
        return sentence
    
    def _create_paragraph_variation(self, sentences: List[str], intensity: float) -> str:
        """Create natural paragraph structure with variation"""
        result = []
        paragraph = []
        
        for i, sentence in enumerate(sentences):
            paragraph.append(sentence)
            
            # Vary paragraph length
            para_length = random.randint(2, 5) if intensity > 0.5 else random.randint(3, 6)
            
            if len(paragraph) >= para_length or i == len(sentences) - 1:
                # Join paragraph
                result.append(' '.join(paragraph))
                paragraph = []
        
        # Add final paragraph if needed
        if paragraph:
            result.append(' '.join(paragraph))
        
        # Join with appropriate spacing
        if len(result) > 1:
            return '\n\n'.join(result)
        else:
            return ' '.join(sentences)


class FastHumanizer:
    """
    Optimized fast humanizer for real-time processing
    """
    
    def __init__(self):
        self.engine = HumanizerEngine(
            use_gpu=torch.cuda.is_available(),
            model_size="small",  # Use small models for speed
            techniques=["sentence_variation", "human_patterns"]  # Fast techniques only
        )
    
    async def humanize_async(self, text: str) -> str:
        """Async humanization for web services"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self.engine.humanize,
                text,
                0.7,  # Default intensity
                True,  # Preserve meaning
                True   # Fast mode
            )
        return result
    
    def humanize_batch(self, texts: List[str]) -> List[str]:
        """Process multiple texts efficiently"""
        results = []
        for text in texts:
            results.append(self.engine.humanize(text, fast_mode=True))
        return results


# Utility functions for detection evasion
class DetectionEvasion:
    """Additional techniques to evade AI detection"""
    
    @staticmethod
    def add_unicode_variations(text: str, rate: float = 0.001) -> str:
        """Add invisible Unicode variations"""
        # Use zero-width spaces and other invisible characters sparingly
        if random.random() < rate:
            text = text.replace(' ', ' \u200b', 1)  # Zero-width space
        return text
    
    @staticmethod
    def vary_punctuation(text: str) -> str:
        """Vary punctuation styles"""
        # Use different dash styles
        text = text.replace(' - ', ' — ' if random.random() < 0.5 else ' – ')
        
        # Vary quote styles
        if '"' in text:
            if random.random() < 0.3:
                text = text.replace('"', '"', 1).replace('"', '"', 1)
        
        return text
    
    @staticmethod  
    def add_typos(text: str, rate: float = 0.001) -> str:
        """Add realistic typos very sparingly"""
        typo_patterns = [
            ('the', 'teh'), ('and', 'adn'), ('you', 'yuo'),
            ('that', 'taht'), ('with', 'wiht'), ('have', 'ahve'),
        ]
        
        for correct, typo in typo_patterns:
            if correct in text and random.random() < rate:
                text = text.replace(correct, typo, 1)
                break  # Only one typo max
        
        return text


def main():
    """Example usage"""
    
    # Initialize humanizer
    humanizer = HumanizerEngine(
        use_gpu=True,
        model_size="medium",
        techniques=["sentence_variation", "semantic_paraphrasing", "human_patterns"]
    )
    
    # Example AI-generated text
    ai_text = """
    Artificial intelligence has revolutionized numerous industries through its capacity 
    to process vast amounts of data and identify patterns. The technology enables 
    organizations to automate complex tasks, enhance decision-making processes, and 
    deliver personalized experiences to users. Machine learning algorithms continue 
    to evolve, demonstrating remarkable capabilities in natural language processing, 
    computer vision, and predictive analytics.
    """
    
    # Humanize the text
    print("Humanizing text...")
    humanized = humanizer.humanize(
        ai_text, 
        intensity=0.7,
        preserve_meaning=True,
        fast_mode=False
    )
    
    print("\nOriginal:")
    print(ai_text)
    print("\nHumanized:")
    print(humanized)
    
    # Fast mode example
    fast_humanizer = FastHumanizer()
    fast_result = fast_humanizer.engine.humanize(ai_text, fast_mode=True)
    print("\nFast Mode Result:")
    print(fast_result)


if __name__ == "__main__":
    main()
