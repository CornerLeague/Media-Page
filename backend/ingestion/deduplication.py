"""
Content Deduplication System

Implements URL-based and content-based deduplication using MinHash
to achieve <1% duplicate rates in content ingestion.
"""

import hashlib
import re
from typing import Set, List, Optional
from urllib.parse import urlparse, parse_qs, urlunparse

from datasketch import MinHash
import numpy as np


class URLHasher:
    """
    URL normalization and hashing for primary deduplication.

    Handles various URL formats and parameters to identify truly unique content.
    """

    def __init__(self):
        # Parameters to remove from URLs for normalization
        self.remove_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
            'fbclid', 'gclid', 'ref', 'source', 'campaign_id', 'click_id',
            'tracking_id', 'affiliate_id', 'partner_id', '_ga', '_gl'
        }

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing tracking parameters and standardizing format

        Args:
            url: Raw URL string

        Returns:
            Normalized URL string
        """
        if not url:
            return ""

        try:
            # Parse URL
            parsed = urlparse(url.strip())

            # Remove fragment (everything after #)
            parsed = parsed._replace(fragment='')

            # Normalize scheme
            if not parsed.scheme:
                parsed = parsed._replace(scheme='https')
            elif parsed.scheme == 'http':
                parsed = parsed._replace(scheme='https')

            # Normalize netloc (domain)
            netloc = parsed.netloc.lower()
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            parsed = parsed._replace(netloc=netloc)

            # Normalize path
            path = parsed.path
            if path.endswith('/') and len(path) > 1:
                path = path[:-1]
            parsed = parsed._replace(path=path)

            # Filter query parameters
            if parsed.query:
                query_params = parse_qs(parsed.query, keep_blank_values=False)
                filtered_params = {
                    k: v for k, v in query_params.items()
                    if k.lower() not in self.remove_params
                }

                # Rebuild query string
                if filtered_params:
                    query_parts = []
                    for key in sorted(filtered_params.keys()):
                        for value in sorted(filtered_params[key]):
                            query_parts.append(f"{key}={value}")
                    query = "&".join(query_parts)
                else:
                    query = ""
                parsed = parsed._replace(query=query)

            return urlunparse(parsed)

        except Exception:
            # If URL parsing fails, fall back to basic normalization
            return url.strip().lower()

    def hash_url(self, url: str) -> str:
        """
        Generate SHA-256 hash of normalized URL

        Args:
            url: URL to hash

        Returns:
            Hexadecimal hash string
        """
        normalized = self.normalize_url(url)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


class TextPreprocessor:
    """
    Text preprocessing for content similarity comparison.

    Normalizes text content to improve duplicate detection accuracy.
    """

    def __init__(self):
        # Compile regex patterns for efficiency
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.whitespace_pattern = re.compile(r'\s+')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        self.number_pattern = re.compile(r'\d+')

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for comparison

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove HTML tags
        text = self.html_tag_pattern.sub(' ', text)

        # Replace numbers with placeholder
        text = self.number_pattern.sub('NUM', text)

        # Remove punctuation
        text = self.punctuation_pattern.sub(' ', text)

        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text)

        return text.strip()

    def extract_shingles(self, text: str, k: int = 3) -> Set[str]:
        """
        Extract k-shingles (k-grams) from text

        Args:
            text: Input text
            k: Shingle size (number of consecutive words)

        Returns:
            Set of k-shingles
        """
        cleaned = self.clean_text(text)
        words = cleaned.split()

        if len(words) < k:
            return {' '.join(words)} if words else set()

        shingles = set()
        for i in range(len(words) - k + 1):
            shingle = ' '.join(words[i:i + k])
            shingles.add(shingle)

        return shingles


class MinHashDeduplicator:
    """
    MinHash-based content deduplication for near-duplicate detection.

    Uses locality-sensitive hashing to efficiently find similar content
    even when there are minor differences.
    """

    def __init__(self, num_perm: int = 128, threshold: float = 0.8):
        """
        Initialize MinHash deduplicator

        Args:
            num_perm: Number of permutations for MinHash (higher = more accurate)
            threshold: Similarity threshold for considering items duplicates
        """
        self.num_perm = num_perm
        self.threshold = threshold
        self.preprocessor = TextPreprocessor()

    def generate_signature(self, text: str) -> MinHash:
        """
        Generate MinHash signature for text content

        Args:
            text: Text content to hash

        Returns:
            MinHash signature
        """
        # Extract shingles from text
        shingles = self.preprocessor.extract_shingles(text)

        # Create MinHash object
        minhash = MinHash(num_perm=self.num_perm)

        # Add shingles to MinHash
        for shingle in shingles:
            minhash.update(shingle.encode('utf-8'))

        return minhash

    def calculate_similarity(self, sig1: MinHash, sig2: MinHash) -> float:
        """
        Calculate Jaccard similarity between two MinHash signatures

        Args:
            sig1: First MinHash signature
            sig2: Second MinHash signature

        Returns:
            Similarity score between 0 and 1
        """
        return sig1.jaccard(sig2)

    def is_duplicate(self, sig1: MinHash, sig2: MinHash) -> bool:
        """
        Check if two signatures represent duplicate content

        Args:
            sig1: First MinHash signature
            sig2: Second MinHash signature

        Returns:
            True if content is considered duplicate
        """
        similarity = self.calculate_similarity(sig1, sig2)
        return similarity >= self.threshold

    def serialize_signature(self, signature: MinHash) -> bytes:
        """
        Serialize MinHash signature for database storage

        Args:
            signature: MinHash signature to serialize

        Returns:
            Serialized signature as bytes
        """
        return signature.digest()

    def deserialize_signature(self, data: bytes) -> MinHash:
        """
        Deserialize MinHash signature from database

        Args:
            data: Serialized signature bytes

        Returns:
            MinHash signature object
        """
        minhash = MinHash(num_perm=self.num_perm)

        # Convert bytes to hashvalues array
        hashvalues = np.frombuffer(data, dtype=np.uint64)

        # Ensure we have the right number of hash values
        if len(hashvalues) != self.num_perm:
            raise ValueError(f"Invalid signature length: expected {self.num_perm}, got {len(hashvalues)}")

        minhash.hashvalues = hashvalues
        return minhash

    def find_duplicates(
        self,
        signatures: List[MinHash],
        query_signature: MinHash
    ) -> List[int]:
        """
        Find duplicate signatures from a list

        Args:
            signatures: List of existing signatures
            query_signature: Signature to check for duplicates

        Returns:
            List of indices of duplicate signatures
        """
        duplicates = []

        for i, signature in enumerate(signatures):
            if self.is_duplicate(query_signature, signature):
                duplicates.append(i)

        return duplicates


class ContentDeduplicator:
    """
    High-level content deduplication system combining multiple strategies.

    Provides a unified interface for both URL-based and content-based deduplication.
    """

    def __init__(
        self,
        minhash_num_perm: int = 128,
        minhash_threshold: float = 0.85,
        content_similarity_threshold: float = 0.9
    ):
        """
        Initialize content deduplicator

        Args:
            minhash_num_perm: Number of permutations for MinHash
            minhash_threshold: Threshold for MinHash similarity
            content_similarity_threshold: Threshold for exact content similarity
        """
        self.url_hasher = URLHasher()
        self.minhash_dedup = MinHashDeduplicator(minhash_num_perm, minhash_threshold)
        self.content_threshold = content_similarity_threshold

    def is_exact_duplicate(self, content1: str, content2: str) -> bool:
        """
        Check for exact content duplicates using hash comparison

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            True if content is exactly the same
        """
        if not content1 and not content2:
            return True
        if not content1 or not content2:
            return False

        hash1 = hashlib.sha256(content1.encode('utf-8')).hexdigest()
        hash2 = hashlib.sha256(content2.encode('utf-8')).hexdigest()

        return hash1 == hash2

    def is_near_duplicate(self, content1: str, content2: str) -> bool:
        """
        Check for near-duplicate content using MinHash

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            True if content is similar enough to be considered duplicate
        """
        sig1 = self.minhash_dedup.generate_signature(content1)
        sig2 = self.minhash_dedup.generate_signature(content2)

        return self.minhash_dedup.is_duplicate(sig1, sig2)

    def calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate similarity score between two content strings

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            Similarity score between 0 and 1
        """
        sig1 = self.minhash_dedup.generate_signature(content1)
        sig2 = self.minhash_dedup.generate_signature(content2)

        return self.minhash_dedup.calculate_similarity(sig1, sig2)

    def generate_content_fingerprint(self, title: str, content: str) -> dict:
        """
        Generate comprehensive fingerprint for content

        Args:
            title: Content title
            content: Content body

        Returns:
            Dictionary with various fingerprint components
        """
        combined_text = f"{title}\n{content}"

        return {
            'content_hash': hashlib.sha256(combined_text.encode('utf-8')).hexdigest(),
            'title_hash': hashlib.sha256(title.encode('utf-8')).hexdigest(),
            'minhash_signature': self.minhash_dedup.serialize_signature(
                self.minhash_dedup.generate_signature(combined_text)
            ),
            'word_count': len(combined_text.split()),
            'character_count': len(combined_text)
        }


# Utility functions for deduplication metrics

def calculate_duplicate_rate(total_items: int, duplicates_found: int) -> float:
    """Calculate duplicate rate as percentage"""
    if total_items == 0:
        return 0.0
    return (duplicates_found / total_items) * 100


def estimate_storage_savings(
    total_items: int,
    duplicates_found: int,
    avg_item_size_kb: float
) -> dict:
    """
    Estimate storage savings from deduplication

    Args:
        total_items: Total number of items processed
        duplicates_found: Number of duplicates found
        avg_item_size_kb: Average item size in KB

    Returns:
        Dictionary with storage metrics
    """
    unique_items = total_items - duplicates_found
    total_size_kb = total_items * avg_item_size_kb
    unique_size_kb = unique_items * avg_item_size_kb
    savings_kb = total_size_kb - unique_size_kb

    return {
        'total_items': total_items,
        'unique_items': unique_items,
        'duplicates_found': duplicates_found,
        'duplicate_rate_percent': calculate_duplicate_rate(total_items, duplicates_found),
        'total_size_kb': total_size_kb,
        'unique_size_kb': unique_size_kb,
        'storage_savings_kb': savings_kb,
        'storage_efficiency_percent': (savings_kb / total_size_kb * 100) if total_size_kb > 0 else 0
    }