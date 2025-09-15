"""Content deduplication utilities for the ingestion pipeline."""

import hashlib
import re
from typing import List, Optional, Set, Tuple
from urllib.parse import urlparse, parse_qs

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Article, IngestionLog
from ..models.enums import IngestionStatus


class URLHasher:
    """URL normalization and hashing for deduplication."""

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL for consistent hashing."""
        # Parse URL
        parsed = urlparse(url.lower().strip())

        # Remove common tracking parameters
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'mc_cid', 'mc_eid', '_ga', 'ref', 'source',
            'campaign', 'medium', 'content', 'term'
        }

        # Parse and filter query parameters
        if parsed.query:
            params = parse_qs(parsed.query)
            filtered_params = {
                k: v for k, v in params.items()
                if k.lower() not in tracking_params
            }
            # Sort parameters for consistency
            sorted_params = sorted(filtered_params.items())
            query_string = '&'.join(f"{k}={'&'.join(v)}" for k, v in sorted_params)
        else:
            query_string = ''

        # Reconstruct normalized URL
        scheme = parsed.scheme or 'https'
        netloc = parsed.netloc
        path = parsed.path.rstrip('/')  # Remove trailing slash
        fragment = ''  # Ignore fragments for deduplication

        normalized = f"{scheme}://{netloc}{path}"
        if query_string:
            normalized += f"?{query_string}"

        return normalized

    @staticmethod
    def hash_url(url: str) -> str:
        """Generate hash for URL."""
        normalized = URLHasher.normalize_url(url)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


class ContentDeduplicator:
    """Content-based deduplication using text similarity."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', '', text)

        # Strip whitespace
        text = text.strip()

        return text

    @staticmethod
    def extract_content_features(title: str, content: Optional[str] = None) -> str:
        """Extract key features from content for comparison."""
        features = []

        # Title is most important
        if title:
            normalized_title = ContentDeduplicator.normalize_text(title)
            features.append(normalized_title)

        # Extract first few sentences of content
        if content:
            normalized_content = ContentDeduplicator.normalize_text(content)
            # Take first 200 characters as content fingerprint
            content_fingerprint = normalized_content[:200]
            features.append(content_fingerprint)

        return ' '.join(features)

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        # Tokenize
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())

        if not tokens1 or not tokens2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))

        return intersection / union if union > 0 else 0.0

    @classmethod
    def find_duplicates(cls, session: Session, title: str, content: Optional[str] = None,
                       threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find potential duplicates based on content similarity."""
        content_features = cls.extract_content_features(title, content)

        # Get recent articles for comparison (last 1000 to avoid performance issues)
        recent_articles = session.execute(
            select(Article.id, Article.title, Article.content)
            .where(Article.status == 'published')
            .order_by(Article.created_at.desc())
            .limit(1000)
        ).fetchall()

        duplicates = []
        for article_id, article_title, article_content in recent_articles:
            article_features = cls.extract_content_features(article_title, article_content)
            similarity = cls.calculate_similarity(content_features, article_features)

            if similarity >= threshold:
                duplicates.append((str(article_id), similarity))

        # Sort by similarity (highest first)
        duplicates.sort(key=lambda x: x[1], reverse=True)
        return duplicates


class MinHashDeduplicator:
    """MinHash-based near-duplicate detection for improved performance."""

    def __init__(self, num_hashes: int = 128):
        self.num_hashes = num_hashes
        self.large_prime = 2**61 - 1
        self.hash_functions = self._generate_hash_functions()

    def _generate_hash_functions(self) -> List[Tuple[int, int]]:
        """Generate hash function coefficients."""
        import random
        random.seed(42)  # For reproducible results

        hash_funcs = []
        for _ in range(self.num_hashes):
            a = random.randint(1, self.large_prime - 1)
            b = random.randint(0, self.large_prime - 1)
            hash_funcs.append((a, b))

        return hash_funcs

    def _shingle(self, text: str, k: int = 3) -> Set[str]:
        """Create k-shingles from text."""
        normalized = ContentDeduplicator.normalize_text(text)
        words = normalized.split()

        if len(words) < k:
            return {' '.join(words)}

        shingles = set()
        for i in range(len(words) - k + 1):
            shingle = ' '.join(words[i:i + k])
            shingles.add(shingle)

        return shingles

    def compute_minhash(self, text: str) -> List[int]:
        """Compute MinHash signature for text."""
        shingles = self._shingle(text)

        if not shingles:
            return [0] * self.num_hashes

        # Convert shingles to hash values
        shingle_hashes = [hash(shingle) for shingle in shingles]

        minhash_sig = []
        for a, b in self.hash_functions:
            min_hash = min((a * h + b) % self.large_prime for h in shingle_hashes)
            minhash_sig.append(min_hash)

        return minhash_sig

    def estimate_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """Estimate Jaccard similarity from MinHash signatures."""
        if len(sig1) != len(sig2):
            return 0.0

        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)

    def find_similar_content(self, session: Session, title: str, content: Optional[str] = None,
                           threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Find similar content using MinHash signatures."""
        # Create content for hashing
        search_text = f"{title} {content or ''}"
        search_signature = self.compute_minhash(search_text)

        # Get articles with their content (could be optimized with signature storage)
        recent_articles = session.execute(
            select(Article.id, Article.title, Article.content)
            .where(Article.status == 'published')
            .order_by(Article.created_at.desc())
            .limit(500)  # Limit for performance
        ).fetchall()

        similar_articles = []
        for article_id, article_title, article_content in recent_articles:
            article_text = f"{article_title} {article_content or ''}"
            article_signature = self.compute_minhash(article_text)

            similarity = self.estimate_similarity(search_signature, article_signature)
            if similarity >= threshold:
                similar_articles.append((str(article_id), similarity))

        # Sort by similarity
        similar_articles.sort(key=lambda x: x[1], reverse=True)
        return similar_articles


class DuplicationChecker:
    """Main deduplication coordinator."""

    def __init__(self):
        self.content_deduplicator = ContentDeduplicator()
        self.minhash_deduplicator = MinHashDeduplicator()

    def check_for_duplicates(self, session: Session, url: str, title: str,
                           content: Optional[str] = None) -> Tuple[bool, Optional[str], float]:
        """
        Check for duplicates using multiple strategies.

        Returns:
            (is_duplicate, duplicate_article_id, confidence_score)
        """
        # First check: URL hash (exact duplicates)
        url_hash = URLHasher.hash_url(url)

        existing_article = session.execute(
            select(Article.id).where(Article.url_hash == url_hash)
        ).scalar_one_or_none()

        if existing_article:
            return True, str(existing_article), 1.0

        # Check ingestion logs for this URL hash
        existing_log = session.execute(
            select(IngestionLog.duplicate_of, IngestionLog.similarity_score)
            .where(
                IngestionLog.url_hash == url_hash,
                IngestionLog.ingestion_status == IngestionStatus.DUPLICATE
            )
            .order_by(IngestionLog.created_at.desc())
        ).first()

        if existing_log and existing_log[0]:
            return True, str(existing_log[0]), existing_log[1] or 0.9

        # Second check: Content similarity
        content_duplicates = self.content_deduplicator.find_duplicates(
            session, title, content, threshold=0.85
        )

        if content_duplicates:
            article_id, similarity = content_duplicates[0]
            return True, article_id, similarity

        # Third check: MinHash for near-duplicates
        minhash_duplicates = self.minhash_deduplicator.find_similar_content(
            session, title, content, threshold=0.75
        )

        if minhash_duplicates:
            article_id, similarity = minhash_duplicates[0]
            return True, article_id, similarity

        # No duplicates found
        return False, None, 0.0

    def log_duplicate_detection(self, session: Session, source_id: Optional[str],
                              url_hash: str, source_url: str, duplicate_of: str,
                              similarity_score: float) -> None:
        """Log duplicate detection for analytics."""
        IngestionLog.log_duplicate(
            source_id=source_id,
            url_hash=url_hash,
            source_url=source_url,
            duplicate_of=duplicate_of,
            similarity_score=similarity_score
        )