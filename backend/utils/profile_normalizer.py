from typing import Dict, Any, Optional, List
import re
import logging

from schemas.models import UserProfile, CareerBackground

logger = logging.getLogger(__name__)


class ProfileNormalizer:
    """Normalizes arbitrary user profile schemas to canonical format"""

    # Known career variant keywords for mapping
    CAREER_KEYWORDS = {
        'data_science': [
            'data scientist', 'data science', 'machine learning', 'ml engineer',
            'ai engineer', 'artificial intelligence', 'data analyst', 'analytics'
        ],
        'data_engineering': [
            'data engineer', 'data engineering', 'etl', 'data pipeline',
            'big data', 'hadoop', 'spark', 'kafka', 'data warehouse'
        ],
        'computer_vision': [
            'computer vision', 'cv engineer', 'image processing', 'opencv',
            'tensorflow', 'pytorch', 'deep learning', 'neural networks', 'cnn'
        ],
        'cto': [
            'cto', 'chief technology officer', 'technical leader', 'tech lead',
            'engineering manager', 'vp engineering', 'head of engineering',
            'director of engineering', 'technical director'
        ]
    }

    def normalize(self, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Normalize arbitrary profile data to canonical UserProfile format.

        Args:
            profile_data: Raw profile data in any format

        Returns:
            UserProfile: Normalized profile in canonical format
        """
        # Extract career background variants
        career_background = self._extract_career_background(profile_data)

        # Extract education background
        education_background = self._extract_education_background(profile_data)

        # Extract motivation
        motivation = self._extract_motivation(profile_data)

        return UserProfile(
            career_background=career_background,
            education_background=education_background,
            motivation=motivation
        )

    def _extract_career_background(self, profile_data: Dict[str, Any]) -> CareerBackground:
        """Extract and organize career background into variants"""

        # Initialize empty career background
        career_variants = {
            'data_science': None,
            'data_engineering': None,
            'computer_vision': None,
            'cto': None
        }

        # Look for explicit career sections
        career_data = self._find_career_data(profile_data)

        if career_data:
            # If career data is already structured with known keys
            if isinstance(career_data, dict):
                for variant, keywords in self.CAREER_KEYWORDS.items():
                    # Check if any keywords appear in the keys
                    matching_keys = [
                        key for key in career_data.keys()
                        if any(keyword in key.lower() for keyword in keywords)
                    ]

                    if matching_keys:
                        # Use the first matching section
                        career_variants[variant] = str(career_data[matching_keys[0]])

                    # Also check if the key itself matches the variant
                    elif variant in career_data:
                        career_variants[variant] = str(career_data[variant])

            # If career data is a list or string, try to split it
            elif isinstance(career_data, (list, tuple)):
                self._distribute_list_to_variants(career_data, career_variants)

            elif isinstance(career_data, str):
                self._distribute_text_to_variants(career_data, career_variants)

        # If no structured career data found, search the entire profile
        if not any(career_variants.values()):
            self._search_entire_profile(profile_data, career_variants)

        return CareerBackground(**career_variants)

    def _find_career_data(self, profile_data: Dict[str, Any]) -> Optional[Any]:
        """Find career-related data in the profile"""

        # Common career section names
        career_keys = [
            'career', 'career_background', 'background', 'experience',
            'work_experience', 'professional_experience', 'roles', 'positions'
        ]

        for key in career_keys:
            if key in profile_data:
                return profile_data[key]

        # Check nested structures
        for value in profile_data.values():
            if isinstance(value, dict) and 'career' in str(value).lower():
                return value

        return None

    def _distribute_list_to_variants(self, items: List[Any], variants: Dict[str, Optional[str]]):
        """Distribute list items to appropriate career variants"""
        items_text = [str(item) for item in items]

        # Group items by career variant based on keywords
        variant_items = {
            'data_science': [],
            'data_engineering': [],
            'computer_vision': [],
            'cto': []
        }

        unassigned_items = []

        for item in items_text:
            item_lower = item.lower()
            assigned = False

            for variant, keywords in self.CAREER_KEYWORDS.items():
                if any(keyword in item_lower for keyword in keywords):
                    variant_items[variant].append(item)
                    assigned = True
                    break

            if not assigned:
                unassigned_items.append(item)

        # Assign items to variants
        for variant, items_list in variant_items.items():
            if items_list:
                variants[variant] = '\n'.join(items_list)

        # If we have unassigned items and empty variants, distribute them
        empty_variants = [v for v, content in variants.items() if content is None]
        if unassigned_items and empty_variants:
            # Simple distribution: assign to first empty variant
            variants[empty_variants[0]] = '\n'.join(unassigned_items)

    def _distribute_text_to_variants(self, text: str, variants: Dict[str, Optional[str]]):
        """Distribute text content to appropriate career variants"""
        # Split text into sections (by double newlines or common separators)
        sections = re.split(r'\n\s*\n|;;|##', text)

        for section in sections:
            section_lower = section.lower()
            assigned = False

            for variant, keywords in self.CAREER_KEYWORDS.items():
                if any(keyword in section_lower for keyword in keywords):
                    variants[variant] = section.strip()
                    assigned = True
                    break

            # If no specific match and we have empty variants, assign to first empty
            if not assigned and not any(variants.values()):
                empty_variants = [v for v, content in variants.items() if content is None]
                if empty_variants:
                    variants[empty_variants[0]] = section.strip()

    def _search_entire_profile(self, profile_data: Dict[str, Any], variants: Dict[str, Optional[str]]):
        """Search entire profile for career-related content"""
        all_text = self._flatten_profile_to_text(profile_data)

        # Look for career sections within the text
        self._distribute_text_to_variants(all_text, variants)

    def _flatten_profile_to_text(self, profile_data: Dict[str, Any]) -> str:
        """Convert profile dict to flattened text"""
        text_parts = []

        def flatten(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        flatten(value, f"{prefix}{key}: ")
                    else:
                        text_parts.append(f"{prefix}{key}: {value}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        flatten(item, f"{prefix}Item {i+1}: ")
                    else:
                        text_parts.append(f"{prefix}Item {i+1}: {item}")
            else:
                text_parts.append(f"{prefix}{obj}")

        flatten(profile_data)
        return '\n'.join(text_parts)

    def _extract_education_background(self, profile_data: Dict[str, Any]) -> str:
        """Extract education background from profile"""

        # Common education keys
        education_keys = [
            'education', 'education_background', 'academic_background',
            'degrees', 'university', 'college', 'school'
        ]

        for key in education_keys:
            if key in profile_data:
                value = profile_data[key]
                if isinstance(value, (list, tuple)):
                    return '\n'.join(str(item) for item in value)
                return str(value)

        # Search in text content
        all_text = self._flatten_profile_to_text(profile_data)
        education_patterns = [
            r'Education:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Degree:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'University:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
        ]

        for pattern in education_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE | re.MULTILINE)
            if matches:
                return matches[0].strip()

        return "Education background not specified."

    def _extract_motivation(self, profile_data: Dict[str, Any]) -> str:
        """Extract motivation/goals from profile"""

        # Common motivation keys
        motivation_keys = [
            'motivation', 'goals', 'objectives', 'why', 'interest', 'passion',
            'career_goals', 'aspirations', 'purpose'
        ]

        for key in motivation_keys:
            if key in profile_data:
                value = profile_data[key]
                if isinstance(value, (list, tuple)):
                    return '\n'.join(str(item) for item in value)
                return str(value)

        # Search in text content
        all_text = self._flatten_profile_to_text(profile_data)
        motivation_patterns = [
            r'Motivation:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Goals:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Why:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
        ]

        for pattern in motivation_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE | re.MULTILINE)
            if matches:
                return matches[0].strip()

        return "Motivation not specified."



