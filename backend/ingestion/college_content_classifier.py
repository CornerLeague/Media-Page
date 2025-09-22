"""
College Basketball Content Classifier

Extends the existing content classification system with college basketball-specific
classification capabilities. Integrates with the Phase 5 content models and provides
enhanced categorization for college basketball content.
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models import CollegeTeam, CollegePlayer as Player, College, CollegeConference
from backend.models.enums import (
    CollegeContentType, PlayerPosition, InjuryType, InjurySeverity,
    RecruitingEventType, CoachingChangeType
)

logger = logging.getLogger(__name__)


@dataclass
class CollegeContentClassification:
    """Classification result for college basketball content"""
    content_type: CollegeContentType
    teams: List[Tuple[UUID, float]]  # (team_id, relevance_score)
    players: List[Tuple[str, float]]  # (player_name, relevance_score)
    coaches: List[Tuple[str, float]]  # (coach_name, relevance_score)
    conferences: List[str]
    injury_indicators: Optional[Dict[str, any]] = None
    recruiting_indicators: Optional[Dict[str, any]] = None
    coaching_indicators: Optional[Dict[str, any]] = None
    sentiment_score: Optional[float] = None
    urgency_score: Optional[float] = None
    confidence: float = 0.5


class CollegeBasketballClassifier:
    """
    Enhanced content classifier for college basketball specific content.

    Extends the base content classification system with:
    - College basketball specific content type detection
    - Team and player entity extraction
    - Injury report classification
    - Recruiting news detection
    - Coaching change identification
    - Conference and tournament context
    """

    def __init__(self, session: AsyncSession):
        self.session = session

        # Content type classification patterns
        self.content_patterns = {
            CollegeContentType.GAME_PREVIEW: [
                r'\b(?:preview|preview:|looking ahead|what to watch|game preview)\b',
                r'\b(?:vs\.?|versus|against|face|meet|battle|clash)\b',
                r'\b(?:matchup|showdown|contest|game|tip-off)\b',
                r'\b(?:keys? to (?:the )?game|what to expect|predictions?)\b'
            ],
            CollegeContentType.GAME_RECAP: [
                r'\b(?:recap|final|result|score|defeat|beat|win|loss)\b',
                r'\b(?:\d+\-\d+|scored? \d+|final score)\b',
                r'\b(?:overtime|ot|double overtime|2ot)\b',
                r'\b(?:highlights|top plays|game summary)\b'
            ],
            CollegeContentType.INJURY_REPORT: [
                r'\b(?:injur(?:y|ed|ies)|hurt|sidelined|out|questionable|doubtful)\b',
                r'\b(?:ankle|knee|shoulder|back|concussion|sprain|tear|strain)\b',
                r'\b(?:mri|x-ray|surgery|rehabilitation|recovery)\b',
                r'\b(?:day-to-day|week-to-week|indefinitely|season-ending)\b'
            ],
            CollegeContentType.RECRUITING_NEWS: [
                r'\b(?:recruit|recruiting|commit|commitment|decommit)\b',
                r'\b(?:offer|scholarship|visit|official visit|unofficial visit)\b',
                r'\b(?:class of 20\d{2}|star recruit|top prospect|ranked)\b',
                r'\b(?:high school|prep|academy)\b'
            ],
            CollegeContentType.TRANSFER_PORTAL: [
                r'\b(?:transfer portal|enters? (?:the )?portal|leaving|departing)\b',
                r'\b(?:transfer|transferring|graduate transfer)\b',
                r'\b(?:eligibility|years? remaining|sit out)\b',
                r'\b(?:new school|new team|destination)\b'
            ],
            CollegeContentType.COACHING_NEWS: [
                r'\b(?:coach|coaching|head coach|assistant coach)\b',
                r'\b(?:hire|hired|firing|fired|resign|retirement|extension)\b',
                r'\b(?:contract|deal|agreement|terms)\b',
                r'\b(?:staff|coaching staff|assistant|associate)\b'
            ],
            CollegeContentType.TOURNAMENT_NEWS: [
                r'\b(?:tournament|march madness|ncaa tournament|big dance)\b',
                r'\b(?:bracket|seeding|seed|selection|committee)\b',
                r'\b(?:conference tournament|acc tournament|big ten tournament)\b',
                r'\b(?:bubble|at-large|automatic bid|qualification)\b'
            ],
            CollegeContentType.RANKING_NEWS: [
                r'\b(?:ranking|ranked|poll|ap poll|coaches poll)\b',
                r'\b(?:top 25|#\d+|number \d+|unranked)\b',
                r'\b(?:rise|fall|climb|drop|move up|move down)\b',
                r'\b(?:kenpom|net ranking|rpi|strength of schedule)\b'
            ]
        }

        # Injury-related patterns
        self.injury_patterns = {
            InjuryType.ANKLE: [r'\bankle\b', r'\bsprain(?:ed)?\b'],
            InjuryType.KNEE: [r'\bknee\b', r'\bacl\b', r'\bmcl\b', r'\bmeniscus\b'],
            InjuryType.CONCUSSION: [r'\bconcussion\b', r'\bhead injur\w+\b', r'\bconcussion protocol\b'],
            InjuryType.BACK: [r'\bback\b', r'\bspine\b', r'\blower back\b'],
            InjuryType.SHOULDER: [r'\bshoulder\b', r'\brotator cuff\b'],
            InjuryType.HAND: [r'\bhand\b', r'\bfinger\b', r'\bthumb\b'],
            InjuryType.FOOT: [r'\bfoot\b', r'\btoe\b', r'\bplantar\b']
        }

        self.severity_patterns = {
            InjurySeverity.MINOR: [r'\bday-to-day\b', r'\bminor\b', r'\bmild\b'],
            InjurySeverity.MODERATE: [r'\bweek-to-week\b', r'\bmoderate\b', r'\bseveral weeks?\b'],
            InjurySeverity.MAJOR: [r'\bmajor\b', r'\bmonths?\b', r'\bextended\b'],
            InjurySeverity.SEASON_ENDING: [r'\bseason-ending\b', r'\bout for (?:the )?season\b', r'\bwill miss (?:the )?rest\b']
        }

        # Cache for team and player data
        self._team_cache: Dict[str, Tuple[UUID, str]] = {}
        self._player_cache: Dict[str, Tuple[UUID, str]] = {}
        self._conference_cache: Dict[str, str] = {}

    async def initialize_cache(self) -> None:
        """Initialize team, player, and conference caches for fast lookup"""
        logger.info("Initializing college basketball classification cache...")

        # Load teams
        result = await self.session.execute(
            select(CollegeTeam.id, CollegeTeam.name, CollegeTeam.mascot, College.name.label('college_name'))
            .join(College, CollegeTeam.college_id == College.id)
        )

        for row in result:
            # Store both full name and mascot for matching
            self._team_cache[row.name.lower()] = (row.id, row.name)
            self._team_cache[row.mascot.lower()] = (row.id, row.name)
            self._team_cache[row.college_name.lower()] = (row.id, row.name)

        # Load players
        result = await self.session.execute(
            select(Player.id, Player.full_name, Player.first_name, Player.last_name, CollegeTeam.name.label('team_name'))
            .join(CollegeTeam, Player.team_id == CollegeTeam.id)
        )

        for row in result:
            self._player_cache[row.full_name.lower()] = (row.id, row.team_name)
            self._player_cache[f"{row.first_name} {row.last_name}".lower()] = (row.id, row.team_name)

        # Load conferences
        result = await self.session.execute(
            select(CollegeConference.name, CollegeConference.abbreviation)
        )

        for row in result:
            self._conference_cache[row.name.lower()] = row.name
            if row.abbreviation:
                self._conference_cache[row.abbreviation.lower()] = row.name

        logger.info(f"Cached {len(self._team_cache)} team entries, {len(self._player_cache)} player entries, {len(self._conference_cache)} conference entries")

    async def classify_college_content(
        self,
        title: str,
        content: str,
        summary: Optional[str] = None,
        author: Optional[str] = None
    ) -> CollegeContentClassification:
        """
        Classify college basketball content and extract relevant entities

        Args:
            title: Content title
            content: Full content text
            summary: Content summary (optional)
            author: Content author (optional)

        Returns:
            CollegeContentClassification with detected type and entities
        """
        # Combine all text for analysis
        full_text = f"{title}\n{summary or ''}\n{content}".lower()

        # Classify content type
        content_type = self._classify_content_type(full_text)

        # Extract entities
        teams = self._extract_teams(full_text)
        players = self._extract_players(full_text)
        coaches = self._extract_coaches(full_text)
        conferences = self._extract_conferences(full_text)

        # Specialized classification based on content type
        injury_indicators = None
        recruiting_indicators = None
        coaching_indicators = None

        if content_type == CollegeContentType.INJURY_REPORT:
            injury_indicators = self._analyze_injury_content(full_text)
        elif content_type in [CollegeContentType.RECRUITING_NEWS, CollegeContentType.TRANSFER_PORTAL]:
            recruiting_indicators = self._analyze_recruiting_content(full_text)
        elif content_type == CollegeContentType.COACHING_NEWS:
            coaching_indicators = self._analyze_coaching_content(full_text)

        # Calculate sentiment and urgency
        sentiment_score = self._calculate_sentiment(full_text)
        urgency_score = self._calculate_urgency(full_text, content_type)

        # Calculate overall confidence
        confidence = self._calculate_confidence(content_type, teams, players)

        return CollegeContentClassification(
            content_type=content_type,
            teams=teams,
            players=players,
            coaches=coaches,
            conferences=conferences,
            injury_indicators=injury_indicators,
            recruiting_indicators=recruiting_indicators,
            coaching_indicators=coaching_indicators,
            sentiment_score=sentiment_score,
            urgency_score=urgency_score,
            confidence=confidence
        )

    def _classify_content_type(self, text: str) -> CollegeContentType:
        """Classify the primary content type based on text patterns"""
        scores = {}

        for content_type, patterns in self.content_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            scores[content_type] = score

        # Return the type with the highest score, default to GENERAL if no matches
        if not scores or max(scores.values()) == 0:
            return CollegeContentType.GENERAL

        return max(scores, key=scores.get)

    def _extract_teams(self, text: str) -> List[Tuple[UUID, float]]:
        """Extract team references from text"""
        teams = []

        for team_name, (team_id, full_name) in self._team_cache.items():
            if team_name in text:
                # Calculate relevance based on frequency and context
                count = text.count(team_name)
                relevance = min(0.3 + (count * 0.2), 1.0)
                teams.append((team_id, relevance))

        # Remove duplicates and sort by relevance
        team_dict = {}
        for team_id, relevance in teams:
            if team_id not in team_dict or relevance > team_dict[team_id]:
                team_dict[team_id] = relevance

        return [(team_id, relevance) for team_id, relevance in sorted(team_dict.items(), key=lambda x: x[1], reverse=True)]

    def _extract_players(self, text: str) -> List[Tuple[str, float]]:
        """Extract player references from text"""
        players = []

        for player_name, (player_id, team_name) in self._player_cache.items():
            if player_name in text:
                count = text.count(player_name)
                relevance = min(0.4 + (count * 0.3), 1.0)
                players.append((player_name.title(), relevance))

        # Remove duplicates and sort by relevance
        player_dict = {}
        for player_name, relevance in players:
            if player_name not in player_dict or relevance > player_dict[player_name]:
                player_dict[player_name] = relevance

        return [(player_name, relevance) for player_name, relevance in sorted(player_dict.items(), key=lambda x: x[1], reverse=True)]

    def _extract_coaches(self, text: str) -> List[Tuple[str, float]]:
        """Extract coach references from text"""
        # Common coaching titles and patterns
        coach_patterns = [
            r'\b(coach\s+\w+)',
            r'\b(\w+\s+coach)',
            r'\b(head coach\s+\w+)',
            r'\b(\w+\s+head coach)',
        ]

        coaches = []
        for pattern in coach_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                coach_name = match.strip().title()
                if len(coach_name) > 5:  # Filter out too short matches
                    coaches.append((coach_name, 0.7))

        # Remove duplicates
        coach_dict = {}
        for coach_name, relevance in coaches:
            if coach_name not in coach_dict:
                coach_dict[coach_name] = relevance

        return list(coach_dict.items())

    def _extract_conferences(self, text: str) -> List[str]:
        """Extract conference references from text"""
        conferences = []

        for conf_name, full_name in self._conference_cache.items():
            if conf_name in text:
                conferences.append(full_name)

        return list(set(conferences))

    def _analyze_injury_content(self, text: str) -> Dict[str, any]:
        """Analyze injury-specific content for details"""
        injury_info = {
            "injury_types": [],
            "severity": None,
            "body_parts": [],
            "timeline_indicators": []
        }

        # Detect injury types
        for injury_type, patterns in self.injury_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    injury_info["injury_types"].append(injury_type.value)

        # Detect severity
        for severity, patterns in self.severity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    injury_info["severity"] = severity.value
                    break
            if injury_info["severity"]:
                break

        # Extract timeline indicators
        timeline_patterns = [
            r'\b(\d+\s+(?:days?|weeks?|months?))\b',
            r'\b(indefinitely|immediately|soon)\b',
            r'\b(expected to return|return date|back by)\b'
        ]

        for pattern in timeline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            injury_info["timeline_indicators"].extend(matches)

        return injury_info

    def _analyze_recruiting_content(self, text: str) -> Dict[str, any]:
        """Analyze recruiting-specific content for details"""
        recruiting_info = {
            "event_types": [],
            "class_year": None,
            "star_rating": None,
            "position": None,
            "location": None
        }

        # Extract recruiting class year
        class_match = re.search(r'\bclass of (\d{4})\b', text, re.IGNORECASE)
        if class_match:
            recruiting_info["class_year"] = int(class_match.group(1))

        # Extract star rating
        star_match = re.search(r'\b(\d+)[\-\s]*star\b', text, re.IGNORECASE)
        if star_match:
            recruiting_info["star_rating"] = int(star_match.group(1))

        # Extract position
        position_patterns = [
            r'\b(point guard|pg)\b',
            r'\b(shooting guard|sg)\b',
            r'\b(small forward|sf)\b',
            r'\b(power forward|pf)\b',
            r'\b(center|c)\b',
            r'\b(guard|forward)\b'
        ]

        for pattern in position_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                recruiting_info["position"] = match.group(1).lower()
                break

        # Extract location indicators
        location_patterns = [
            r'\b([A-Z][a-z]+,\s*[A-Z]{2})\b',  # City, State
            r'\b(from [A-Z][a-z]+)\b'  # from Location
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                recruiting_info["location"] = matches[0]
                break

        return recruiting_info

    def _analyze_coaching_content(self, text: str) -> Dict[str, any]:
        """Analyze coaching-specific content for details"""
        coaching_info = {
            "change_types": [],
            "position_title": None,
            "contract_details": [],
            "previous_position": None
        }

        # Detect change types
        change_patterns = {
            CoachingChangeType.HIRE: [r'\bhired?\b', r'\bnew coach\b', r'\bnamed\b'],
            CoachingChangeType.FIRE: [r'\bfired?\b', r'\bdismissed?\b', r'\blet go\b'],
            CoachingChangeType.EXTENSION: [r'\bextension\b', r'\bextended\b', r'\bcontract extension\b'],
            CoachingChangeType.RESIGNATION: [r'\bresign\w*\b', r'\bstepping down\b'],
            CoachingChangeType.RETIREMENT: [r'\bretire\w*\b', r'\bretirement\b']
        }

        for change_type, patterns in change_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    coaching_info["change_types"].append(change_type.value)

        # Extract position title
        position_matches = re.findall(r'\b(head coach|assistant coach|associate head coach)\b', text, re.IGNORECASE)
        if position_matches:
            coaching_info["position_title"] = position_matches[0].title()

        # Extract contract details
        contract_patterns = [
            r'\b(\d+[\-\s]*year)\b',
            r'\$(\d+(?:\.\d+)?\s*(?:million|m))\b',
            r'\b(through \d{4})\b'
        ]

        for pattern in contract_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            coaching_info["contract_details"].extend(matches)

        return coaching_info

    def _calculate_sentiment(self, text: str) -> Optional[float]:
        """Calculate sentiment score for the content"""
        # Simple keyword-based sentiment analysis
        positive_words = [
            'win', 'victory', 'success', 'great', 'excellent', 'outstanding',
            'impressive', 'dominant', 'stellar', 'breakthrough', 'commit', 'signing'
        ]

        negative_words = [
            'loss', 'defeat', 'injury', 'injured', 'hurt', 'suspended', 'fired',
            'resign', 'disappointment', 'struggle', 'poor', 'terrible', 'decommit'
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0

        # Scale from -1 (negative) to 1 (positive)
        sentiment = (positive_count - negative_count) / total_sentiment_words
        return max(-1.0, min(1.0, sentiment))

    def _calculate_urgency(self, text: str, content_type: CollegeContentType) -> Optional[float]:
        """Calculate urgency score based on content type and keywords"""
        urgency_keywords = {
            'high': [
                'breaking', 'urgent', 'immediate', 'emergency', 'critical',
                'season-ending', 'fired', 'suspended', 'arrested'
            ],
            'medium': [
                'injured', 'questionable', 'doubtful', 'out', 'transfer',
                'commits', 'decommits', 'extension'
            ],
            'low': [
                'preview', 'analysis', 'outlook', 'prediction', 'recap'
            ]
        }

        high_count = sum(1 for word in urgency_keywords['high'] if word in text)
        medium_count = sum(1 for word in urgency_keywords['medium'] if word in text)
        low_count = sum(1 for word in urgency_keywords['low'] if word in text)

        # Base urgency on content type
        type_urgency = {
            CollegeContentType.INJURY_REPORT: 0.8,
            CollegeContentType.COACHING_NEWS: 0.7,
            CollegeContentType.TRANSFER_PORTAL: 0.6,
            CollegeContentType.RECRUITING_NEWS: 0.5,
            CollegeContentType.GAME_RECAP: 0.4,
            CollegeContentType.TOURNAMENT_NEWS: 0.6,
            CollegeContentType.GAME_PREVIEW: 0.3
        }.get(content_type, 0.4)

        # Adjust based on keywords
        keyword_adjustment = (high_count * 0.3) + (medium_count * 0.1) - (low_count * 0.1)
        urgency = max(0.0, min(1.0, type_urgency + keyword_adjustment))

        return urgency

    def _calculate_confidence(
        self,
        content_type: CollegeContentType,
        teams: List[Tuple[UUID, float]],
        players: List[Tuple[str, float]]
    ) -> float:
        """Calculate overall classification confidence"""
        base_confidence = 0.5

        # Boost confidence if we found relevant teams
        if teams:
            base_confidence += 0.2

        # Boost confidence if we found relevant players
        if players:
            base_confidence += 0.2

        # Content type specific confidence boosts
        type_boosts = {
            CollegeContentType.INJURY_REPORT: 0.1,
            CollegeContentType.RECRUITING_NEWS: 0.1,
            CollegeContentType.COACHING_NEWS: 0.1,
            CollegeContentType.GAME_PREVIEW: 0.05,
            CollegeContentType.GAME_RECAP: 0.05
        }

        base_confidence += type_boosts.get(content_type, 0.0)

        return min(1.0, base_confidence)


# Integration function for use with existing pipeline
async def create_college_basketball_classifier(session: AsyncSession) -> CollegeBasketballClassifier:
    """Factory function to create and initialize a college basketball classifier"""
    classifier = CollegeBasketballClassifier(session)
    await classifier.initialize_cache()
    return classifier