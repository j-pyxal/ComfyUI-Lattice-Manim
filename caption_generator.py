"""
Caption overlay generation and formatting module.
Generates Manim code for caption overlays with configurable styles.
"""

from .presets import FontPresets, ColorPresets


def generate_caption_code(words, caption_style, position, font_config, color_config):
    """
    Generate Manim code for caption overlays.
    
    Args:
        words: List of word dicts with 'word', 'start', 'end' keys
        caption_style: 'word_by_word', 'sentence', or 'hybrid'
        position: 'top', 'bottom', or 'center'
        font_config: Dict with 'font', 'size', 'color'
        color_config: Dict with 'text_color', 'bg_color'
    
    Returns:
        String of Manim code for captions
    """
    if caption_style == "word_by_word":
        return create_word_by_word_animation(words, position, font_config, color_config)
    elif caption_style == "sentence":
        return create_sentence_captions(words, position, font_config, color_config)
    elif caption_style == "hybrid":
        return create_hybrid_captions(words, position, font_config, color_config)
    else:
        raise ValueError(f"Unknown caption style: {caption_style}")


def create_word_by_word_animation(words, position, font_config, color_config):
    """
    Create word-by-word highlighting animation (karaoke style).
    Uses ReplacementTransform for proper text content changes.
    
    Args:
        words: List of word dicts with 'word', 'start', 'end'
        position: Position on screen
        font_config: Font configuration
        color_config: Color configuration
    
    Returns:
        Manim code string
    """
    font = font_config.get('font', 'Arial')
    font_size = font_config.get('size', 48)
    text_color = color_config.get('text_color', 'WHITE')
    bg_color = color_config.get('bg_color', 'TRANSPARENT')
    
    # Position mapping
    position_map = {
        'bottom': 'DOWN',
        'top': 'UP',
        'center': 'ORIGIN'
    }
    pos = position_map.get(position, 'DOWN')
    
    # Filter out empty words
    valid_words = [w for w in words if w.get('word', '').strip()]
    if not valid_words:
        return "# No words to display\n"
    
    # Build initial empty text
    code = f"""
# Word-by-word caption animation
# Initialize with empty text
caption_text = Text("", font="{font}", font_size={font_size}, color={text_color})
caption_text.to_edge({pos}, buff=0.5)
"""
    
    # Background rectangle if needed
    if bg_color != 'TRANSPARENT':
        code += f"""
# Background rectangle
bg_rect = Rectangle(
    width=config.frame_width * 0.9,
    height={font_size * 1.5} / config.pixel_height * config.frame_height,
    fill_opacity=0.7,
    fill_color={bg_color},
    stroke_width=0
)
bg_rect.to_edge({pos}, buff=0.3)
self.add(bg_rect)
"""
    
    code += """
# Add caption text to scene
self.add(caption_text)

# Animate words word-by-word
"""
    
    # Generate code for each word - build sentence progressively
    for i, word_data in enumerate(valid_words):
        word = word_data['word']
        start = word_data['start']
        end = word_data['end']
        duration = max(0.1, end - start)  # Ensure minimum duration
        
        # Clean and escape text
        clean_word = word.strip().replace('"', '\\"').replace("'", "\\'")
        if not clean_word:
            continue
        
        # Build full sentence up to current word for display
        words_so_far = ' '.join([w['word'].strip() for w in valid_words[:i+1] if w['word'].strip()])
        words_so_far = words_so_far.replace('"', '\\"').replace("'", "\\'")
        
        code += f"""
# Word {i}: "{clean_word}" ({start:.2f}s - {end:.2f}s)
next_caption = Text("{words_so_far}", font="{font}", font_size={font_size}, color={text_color})
next_caption.to_edge({pos}, buff=0.5)

# Use ReplacementTransform for text content changes
self.play(
    ReplacementTransform(caption_text, next_caption),
    run_time={duration:.3f}
)
caption_text = next_caption
"""
    
    return code


def create_sentence_captions(words, position, font_config, color_config):
    """
    Create full sentence captions.
    
    Args:
        words: List of word dicts with 'word', 'start', 'end'
        position: Position on screen
        font_config: Font configuration
        color_config: Color configuration
    
    Returns:
        Manim code string
    """
    font = font_config.get('font', 'Arial')
    font_size = font_config.get('size', 48)
    text_color = color_config.get('text_color', 'WHITE')
    bg_color = color_config.get('bg_color', 'TRANSPARENT')
    
    # Group words into sentences (simple: split on periods, exclamation, question marks)
    sentences = []
    current_sentence = []
    
    for word_data in words:
        word = word_data['word'].strip()
        if not word:
            continue
        
        current_sentence.append(word_data)
        
        # Check if word ends sentence
        if any(word.endswith(p) for p in ['.', '!', '?']):
            if current_sentence:
                sentences.append(current_sentence)
                current_sentence = []
    
    # Add remaining words as last sentence
    if current_sentence:
        sentences.append(current_sentence)
    
    position_map = {
        'bottom': 'DOWN',
        'top': 'UP',
        'center': 'ORIGIN'
    }
    pos = position_map.get(position, 'DOWN')
    
    code = f"""
# Sentence captions
caption_text = Text("", font="{font}", font_size={font_size}, color={text_color})
caption_text.to_edge({pos}, buff=0.5)
"""
    
    if bg_color != 'TRANSPARENT':
        code += f"""
bg_rect = Rectangle(
    width=config.frame_width * 0.9,
    height={font_size * 2} / config.pixel_height * config.frame_height,
    fill_opacity=0.7,
    fill_color={bg_color},
    stroke_width=0
)
bg_rect.to_edge({pos}, buff=0.3)
self.add(bg_rect)
"""
    
    code += """
# Add caption text to scene
self.add(caption_text)

# Animate sentences
"""
    
    for i, sentence_words in enumerate(sentences):
        if not sentence_words:
            continue
        
        # Build sentence text
        sentence_text = ' '.join(w['word'].strip() for w in sentence_words)
        start_time = sentence_words[0]['start']
        end_time = sentence_words[-1]['end']
        duration = end_time - start_time
        
        # Escape text properly
        sentence_text_escaped = sentence_text.replace('"', '\\"').replace("'", "\\'")
        
        code += f"""
# Sentence {i}: "{sentence_text[:50]}..." ({start_time:.2f}s - {end_time:.2f}s)
sentence_obj = Text("{sentence_text_escaped}", font="{font}", font_size={font_size}, color={text_color})
sentence_obj.to_edge({pos}, buff=0.5)

# Use ReplacementTransform for text content changes
self.play(
    ReplacementTransform(caption_text, sentence_obj),
    run_time={duration:.3f}
)
caption_text = sentence_obj
self.wait(0.1)
"""
    
    return code


def create_hybrid_captions(words, position, font_config, color_config):
    """
    Create both word-by-word and sentence captions simultaneously.
    
    Args:
        words: List of word dicts with 'word', 'start', 'end'
        position: Position on screen
        font_config: Font configuration
        color_config: Color configuration
    
    Returns:
        Manim code string
    """
    font = font_config.get('font', 'Arial')
    font_size = font_config.get('size', 48)
    text_color = color_config.get('text_color', 'WHITE')
    bg_color = color_config.get('bg_color', 'TRANSPARENT')
    
    # Group words into sentences
    sentences = []
    current_sentence = []
    
    for word_data in words:
        word = word_data['word'].strip()
        if not word:
            continue
        
        current_sentence.append(word_data)
        
        if any(word.endswith(p) for p in ['.', '!', '?']):
            if current_sentence:
                sentences.append(current_sentence)
                current_sentence = []
    
    if current_sentence:
        sentences.append(current_sentence)
    
    position_map = {
        'bottom': 'DOWN',
        'top': 'UP',
        'center': 'ORIGIN'
    }
    pos = position_map.get(position, 'DOWN')
    
    code = f"""
# Hybrid captions (word-by-word + sentence)
sentence_text = Text("", font="{font}", font_size={font_size}, color={text_color})
word_text = Text("", font="{font}", font_size={font_size * 0.7}, color=YELLOW)

sentence_text.to_edge({pos}, buff=0.7)
word_text.to_edge({pos}, buff=0.3)
"""
    
    if bg_color != 'TRANSPARENT':
        code += f"""
bg_rect = Rectangle(
    width=config.frame_width * 0.9,
    height={font_size * 3} / config.pixel_height * config.frame_height,
    fill_opacity=0.7,
    fill_color={bg_color},
    stroke_width=0
)
bg_rect.to_edge({pos}, buff=0.2)
self.add(bg_rect)
"""
    
    code += """
self.add(sentence_text, word_text)

# Animate
"""
    
    current_sentence_idx = 0
    current_sentence_words = sentences[0] if sentences else []
    
    for i, word_data in enumerate(words):
        word = word_data['word'].strip()
        if not word:
            continue
        
        start = word_data['start']
        end = word_data['end']
        duration = end - start
        
        # Check if we need to update sentence
        if current_sentence_words and word_data in current_sentence_words:
            sentence_text_str = ' '.join(w['word'].strip() for w in current_sentence_words)
        else:
            # Find which sentence this word belongs to
            for sent_idx, sent_words in enumerate(sentences):
                if word_data in sent_words:
                    current_sentence_idx = sent_idx
                    current_sentence_words = sent_words
                    sentence_text_str = ' '.join(w['word'].strip() for w in sent_words)
                    break
        
        # Escape text properly
        word_escaped = word.replace('"', '\\"').replace("'", "\\'")
        sentence_escaped = sentence_text_str.replace('"', '\\"').replace("'", "\\'")
        
        code += f"""
# Word {i}: "{word_escaped}" | Sentence: "{sentence_text_str[:30]}..."
word_obj = Text("{word_escaped}", font="{font}", font_size={font_size * 0.7}, color=YELLOW)
sentence_obj = Text("{sentence_escaped}", font="{font}", font_size={font_size}, color={text_color})

word_obj.to_edge({pos}, buff=0.3)
sentence_obj.to_edge({pos}, buff=0.7)

# Use ReplacementTransform for text content changes
self.play(
    ReplacementTransform(word_text, word_obj),
    ReplacementTransform(sentence_text, sentence_obj),
    run_time={duration:.3f}
)
word_text = word_obj
sentence_text = sentence_obj
"""
    
    return code

