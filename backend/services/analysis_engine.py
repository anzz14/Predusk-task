import re
import string
from collections import Counter


# Hardcoded stopwords frozenset (~150 common English words)
STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
    "from", "up", "about", "out", "if", "as", "is", "was", "are", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "can", "shall", "it", "its", "this", "that", "these", "those",
    "i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them", "what", "which",
    "who", "whom", "why", "how", "when", "where", "there", "here", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "because", "through", "during", "before",
    "after", "above", "below", "between", "under", "over", "again", "further", "then", "once",
    "while", "also", "am", "my", "your", "his", "our", "their", "yours", "himself", "herself",
    "itself", "myself", "yourself", "ourselves", "themselves", "ours", "theirs", "yours",
    "as", "being", "have", "has", "having", "is", "was", "are", "were", "been", "be", "been",
    "doing", "does", "did", "do", "will", "would", "should", "could", "ought", "i've", "you've",
    "we've", "they've", "i'm", "you're", "he's", "she's", "it's", "we're", "they're", "isn't",
    "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't", "doesn't", "don't", "didn't",
    "won't", "wouldn't", "shan't", "shouldn't", "can't", "couldn't", "shouldn't", "mightn't",
    "mustn't", "let's", "that's", "who's", "what's", "here's", "there's", "when's", "where's",
    "why's", "how's", "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if",
    "in", "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", "their",
    "then", "there", "these", "they", "this", "to", "was", "will", "with", "us",
})


def compute_word_count(text: str) -> int:
    """
    Count the number of words in the text.
    
    Splits on whitespace and filters out tokens that are only punctuation.
    """
    if not text or not text.strip():
        return 0
    
    tokens = text.split()
    words = [token for token in tokens if token.strip(string.punctuation)]
    return len(words)


def compute_readability_score(text: str) -> float:
    """
    Compute Flesch Reading Ease score.
    
    Formula: 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    Result clamped to [0.0, 100.0]
    """
    if not text or not text.strip():
        return 0.0
    
    # Count words
    words = text.split()
    word_count = len([w for w in words if w.strip(string.punctuation)])
    
    if word_count == 0:
        return 0.0
    
    # Count sentences (split on sentence-ending punctuation)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    if sentence_count == 0:
        return 0.0
    
    # Count syllables
    syllable_count = 0
    for word in words:
        syllable_count += _count_syllables(word)
    
    # Ensure at least 1 syllable to avoid division issues
    if syllable_count == 0:
        syllable_count = word_count  # fallback: assume 1 syllable per word
    
    # Calculate Flesch Reading Ease
    score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
    
    # Clamp to [0, 100]
    return max(0.0, min(100.0, score))


def _count_syllables(word: str) -> int:
    """
    Estimate syllable count by counting vowel groups.
    
    A vowel group is a sequence of consecutive vowels.
    Special cases: silent "e" at end reduces count by 1.
    """
    word = word.lower().strip(string.punctuation)
    
    if not word:
        return 0
    
    # Count vowel groups
    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent 'e' at the end
    if word.endswith('e'):
        syllable_count -= 1
    
    # Adjust for le ending
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        syllable_count += 1
    
    # Ensure at least 1 syllable
    return max(1, syllable_count)


def compute_primary_keywords(text: str, top_n: int = 10) -> list[dict]:
    """
    Extract primary keywords from text.
    
    Tokenizes, lowercases, removes punctuation, filters stopwords, counts frequency,
    and computes density percentage. Returns top_n keywords as list of dicts.
    
    Returns list of dicts: [{"keyword": str, "count": int, "density_percentage": float}, ...]
    """
    if not text or not text.strip():
        return []
    
    # Tokenize and clean
    tokens = text.lower().split()
    cleaned_tokens = []
    
    for token in tokens:
        # Strip punctuation
        cleaned = token.strip(string.punctuation)
        # Filter out empty strings and stopwords
        if cleaned and cleaned not in STOPWORDS:
            cleaned_tokens.append(cleaned)
    
    if not cleaned_tokens:
        return []
    
    # Count frequency
    counter = Counter(cleaned_tokens)
    total_tokens = len(cleaned_tokens)
    
    # Build results with density
    results = []
    for keyword, count in counter.most_common(top_n):
        density_percentage = (count / total_tokens) * 100
        results.append({
            "keyword": keyword,
            "count": count,
            "density_percentage": round(density_percentage, 2),
        })
    
    return results


def compute_summary(text: str) -> str:
    """
    Extract summary as first 3 sentences.
    
    Splits text on sentence-ending punctuation and takes the first 3 sentences.
    """
    if not text or not text.strip():
        return ""
    
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Take first 3 non-empty sentences
    summary_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            summary_sentences.append(sentence)
        if len(summary_sentences) >= 3:
            break
    
    return " ".join(summary_sentences)


def compute_all(text: str) -> dict:
    """
    Compute all SEO metrics at once.
    
    Returns dict with keys: word_count, readability_score, primary_keywords, auto_summary
    """
    return {
        "word_count": compute_word_count(text),
        "readability_score": compute_readability_score(text),
        "primary_keywords": compute_primary_keywords(text),
        "auto_summary": compute_summary(text),
    }