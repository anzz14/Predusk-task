import pytest
from services.analysis_engine import (
    compute_word_count,
    compute_readability_score,
    compute_primary_keywords,
    compute_summary,
    compute_all,
)


class TestComputeWordCount:
    """Test word count computation with various inputs."""

    def test_basic_word_count(self):
        """Test counting words in a normal sentence."""
        text = "This is a simple test string"
        result = compute_word_count(text)
        assert result == 6

    def test_word_count_with_punctuation(self):
        """Test that punctuation doesn't create extra words."""
        text = "Hello, world! How are you?"
        result = compute_word_count(text)
        assert result == 5

    def test_word_count_empty_string(self):
        """Test word count on empty string."""
        result = compute_word_count("")
        assert result == 0

    def test_word_count_only_punctuation(self):
        """Test word count on punctuation-only string."""
        result = compute_word_count("!!!???...")
        assert result == 0

    def test_word_count_with_numbers(self):
        """Test word count including numbers."""
        text = "I have 123 apples and 456 oranges"
        result = compute_word_count(text)
        assert result == 7


class TestComputeReadabilityScore:
    """Test readability score (Flesch Reading Ease) computation."""

    def test_simple_sentence_readability(self):
        """Test readability of a simple sentence."""
        text = "The cat sat on the mat."
        result = compute_readability_score(text)
        assert isinstance(result, float)
        assert 0 <= result <= 100

    def test_complex_sentence_lower_score(self):
        """Test that complex text has lower readability score."""
        simple = "The cat is on the mat."
        complex_text = "The onomatopoeia serendipitously obfuscated pedagogical paradigms."
        
        simple_score = compute_readability_score(simple)
        complex_score = compute_readability_score(complex_text)
        
        assert simple_score > complex_score

    def test_readability_score_clamped(self):
        """Test that readability score is clamped to [0, 100]."""
        # Very simple text
        result = compute_readability_score("a b c d e f g")
        assert 0 <= result <= 100

    def test_readability_empty_string(self):
        """Test readability on empty string."""
        result = compute_readability_score("")
        assert isinstance(result, float)


class TestComputePrimaryKeywords:
    """Test keyword extraction and frequency computation."""

    def test_basic_keyword_extraction(self):
        """Test extracting keywords from text."""
        text = "python python python java java cpp"
        result = compute_primary_keywords(text, top_n=10)
        
        assert len(result) > 0
        assert result[0]["keyword"] == "python"
        assert result[0]["count"] == 3
        assert isinstance(result[0]["density_percentage"], float)

    def test_stopwords_excluded(self):
        """Test that stopwords (the, is, etc.) are excluded."""
        text = "the the the python python"
        result = compute_primary_keywords(text)
        
        keywords = [kw["keyword"] for kw in result]
        assert "the" not in keywords
        assert "python" in keywords

    def test_top_n_limiting(self):
        """Test that top_n parameter limits results."""
        text = "a b c d e f g h i j k l m"
        result = compute_primary_keywords(text, top_n=5)
        
        assert len(result) <= 5

    def test_keywords_case_insensitive(self):
        """Test that keyword extraction is case-insensitive."""
        text = "Python python PYTHON"
        result = compute_primary_keywords(text)
        
        assert result[0]["count"] == 3

    def test_all_stopwords(self):
        """Test text containing only stopwords."""
        text = "the is a an and or but in at to"
        result = compute_primary_keywords(text)
        
        assert len(result) == 0

    def test_empty_string_keywords(self):
        """Test keyword extraction on empty string."""
        result = compute_primary_keywords("")
        assert len(result) == 0


class TestComputeSummary:
    """Test automatic summary generation."""

    def test_basic_summary(self):
        """Test extracting first 3 sentences as summary."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = compute_summary(text)
        
        assert "First sentence" in result
        assert "Second sentence" in result
        assert "Third sentence" in result
        assert "Fourth sentence" not in result

    def test_summary_single_sentence(self):
        """Test summary with single sentence."""
        text = "Only one sentence."
        result = compute_summary(text)
        
        assert "Only one sentence" in result

    def test_summary_two_sentences(self):
        """Test summary with two sentences."""
        text = "First. Second."
        result = compute_summary(text)
        
        assert len(result) > 0

    def test_summary_empty_string(self):
        """Test summary generation on empty string."""
        result = compute_summary("")
        assert result == ""

    def test_summary_handles_various_punctuation(self):
        """Test summary with various sentence endings."""
        text = "First sentence! Second sentence? Third sentence. Fourth."
        result = compute_summary(text)
        
        assert len(result) > 0


class TestComputeAll:
    """Test the comprehensive compute_all function."""

    def test_compute_all_returns_dict_with_all_keys(self):
        """Test that compute_all returns a dict with all expected keys."""
        text = "This is a test document with multiple sentences. It contains keywords and analysis. The results should be comprehensive."
        result = compute_all(text)
        
        assert isinstance(result, dict)
        assert "word_count" in result
        assert "readability_score" in result
        assert "primary_keywords" in result
        assert "auto_summary" in result

    def test_compute_all_correct_types(self):
        """Test that compute_all returns correct types."""
        text = "Sample text for testing."
        result = compute_all(text)
        
        assert isinstance(result["word_count"], int)
        assert isinstance(result["readability_score"], float)
        assert isinstance(result["primary_keywords"], list)
        assert isinstance(result["auto_summary"], str)

    def test_compute_all_consistency(self):
        """Test that compute_all results are consistent with individual functions."""
        text = "Consistent results matter for reliability."
        all_result = compute_all(text)
        
        individual_word_count = compute_word_count(text)
        individual_readability = compute_readability_score(text)
        
        assert all_result["word_count"] == individual_word_count
        assert all_result["readability_score"] == individual_readability