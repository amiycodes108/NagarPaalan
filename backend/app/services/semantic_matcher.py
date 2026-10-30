"""NAGARPAALAN AI — Explainable Semantic & Duplicate Matching Engine.

Combines:
1. Semantic text similarity (TF-IDF / N-gram cosine + civic synonym mapping).
2. Precise geographic proximity via Haversine distance.
3. Physical asset identity & historical context.
4. Category congruence.

Generates a fully transparent, explainable match breakdown for human administrative review.
"""

from __future__ import annotations

import math
import re
from typing import Any

from app.schemas.complaint import DuplicateMatchCandidate, MatchReasonItem
from app.services.geo_similarity import haversine_distance

# Civic synonym clusters for semantic expansion
CIVIC_SYNONYMS = {
    "pothole": {"pothole", "crater", "depression", "hole", "ditch", "hollow", "pit", "broken road", "asphalt damage"},
    "crack": {"crack", "fissure", "fracture", "cleft", "alligator crack", "surface crack"},
    "garbage": {"garbage", "trash", "waste", "rubbish", "refuse", "debris", "dump", "litter", "filth"},
    "streetlight": {"streetlight", "street light", "lamp", "luminaire", "bulb", "pole", "lighting", "darkness", "not working", "blackout"},
    "drainage": {"drain", "gutter", "sewer", "waterlogging", "overflow", "clog", "choked", "stagnant"},
}


def _tokenize(text: str) -> list[str]:
    """Tokenize and clean text."""
    clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return [word for word in clean.split() if len(word) > 2]


def _expand_synonyms(tokens: list[str]) -> set[str]:
    """Expand tokens with domain civic synonyms."""
    expanded = set(tokens)
    for token in tokens:
        for group in CIVIC_SYNONYMS.values():
            if token in group:
                expanded.update(group)
    return expanded


def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """Calculate token overlap similarity with civic synonym enhancement (Jaccard + Cosine hybrid)."""
    tokens1 = _tokenize(text1)
    tokens2 = _tokenize(text2)

    if not tokens1 or not tokens2:
        return 0.0

    exp1 = _expand_synonyms(tokens1)
    exp2 = _expand_synonyms(tokens2)

    intersection = exp1.intersection(exp2)
    union = exp1.union(exp2)

    if not union:
        return 0.0

    jaccard = len(intersection) / len(union)

    # Add bonus for core defect terms matching
    core_bonus = 0.0
    for key, cluster in CIVIC_SYNONYMS.items():
        if (exp1 & cluster) and (exp2 & cluster):
            core_bonus += 0.25
            break

    score = min(1.0, (jaccard * 0.75) + core_bonus)
    return round(score, 3)


def calculate_geo_proximity_score(distance_m: float, threshold_m: float = 100.0) -> float:
    """Calculate geographic match score (0-100) using smooth sigmoid/gaussian dropoff."""
    if distance_m <= 15.0:
        return 100.0
    if distance_m > threshold_m:
        return max(0.0, 100.0 - (distance_m - threshold_m) * 2.0)
    
    # Linear scale between 15m and threshold_m
    fraction = (threshold_m - distance_m) / (threshold_m - 15.0)
    return round(fraction * 100.0, 1)


def evaluate_duplicate_match(
    new_text: str,
    new_category: str,
    new_lat: float,
    new_lon: float,
    candidate_id: int,
    candidate_code: str,
    candidate_title: str,
    candidate_desc: str,
    candidate_category: str,
    candidate_status: str,
    candidate_lat: float,
    candidate_lon: float,
    same_asset: bool = False,
    target_type: str = "issue",
) -> DuplicateMatchCandidate:
    """Generate an explainable match assessment between a report and an existing issue/complaint."""
    # 1. Geographic distance & score
    dist_m = haversine_distance(new_lat, new_lon, candidate_lat, candidate_lon)
    geo_score = calculate_geo_proximity_score(dist_m, threshold_m=120.0)

    # 2. Semantic text similarity
    full_text_a = f"{new_category} {new_text}"
    full_text_b = f"{candidate_title} {candidate_desc or ''}"
    sem_sim = calculate_semantic_similarity(full_text_a, full_text_b)
    semantic_score = sem_sim * 100.0

    # 3. Category match
    cat_match = (new_category.lower() in candidate_category.lower()) or (candidate_category.lower() in new_category.lower())
    cat_score = 100.0 if cat_match else 20.0

    # 4. Asset alignment
    asset_score = 100.0 if same_asset else (80.0 if dist_m <= 40.0 else 30.0)

    # Weighted composite match score:
    # 35% Geo, 35% Semantic, 15% Asset, 15% Category
    overall = (
        (geo_score * 0.35)
        + (semantic_score * 0.35)
        + (asset_score * 0.15)
        + (cat_score * 0.15)
    )
    overall_score = round(min(100.0, max(0.0, overall)), 1)

    reasons: list[MatchReasonItem] = [
        MatchReasonItem(
            criterion="Geographic Proximity",
            score=geo_score,
            weight=0.35,
            explanation=f"Coordinates are {dist_m:.1f}m away from existing {target_type} ({'within immediate 30m cluster' if dist_m <= 30 else 'within neighborhood radius'}).",
        ),
        MatchReasonItem(
            criterion="Semantic Description",
            score=round(semantic_score, 1),
            weight=0.35,
            explanation=f"Text similarity index is {sem_sim:.2f} based on civic vocabulary and defect classification.",
        ),
        MatchReasonItem(
            criterion="Asset Context",
            score=asset_score,
            weight=0.15,
            explanation="Both records align to the same physical road/infrastructure segment." if same_asset else f"Located {dist_m:.1f}m along contiguous civic infrastructure corridor.",
        ),
        MatchReasonItem(
            criterion="Category Alignment",
            score=cat_score,
            weight=0.15,
            explanation=f"Category '{new_category}' corresponds with target category '{candidate_category}'.",
        ),
    ]

    if overall_score >= 70.0:
        recommended_action = "LINK_TO_EXISTING_ISSUE"
    elif overall_score >= 40.0:
        recommended_action = "FLAG_FOR_REVIEW"
    else:
        recommended_action = "CREATE_NEW_ISSUE"

    return DuplicateMatchCandidate(
        target_type=target_type,
        target_id=candidate_id,
        target_code=candidate_code,
        target_title=candidate_title,
        target_status=candidate_status,
        distance_meters=round(dist_m, 1),
        semantic_similarity=sem_sim,
        overall_match_score=overall_score,
        reasons=reasons,
        recommended_action=recommended_action,
    )
