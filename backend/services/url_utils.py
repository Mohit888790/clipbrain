"""URL canonicalization and platform detection utilities."""

import hashlib
import re
from urllib.parse import urlparse, parse_qs
from typing import Literal

Platform = Literal["youtube", "instagram", "tiktok", "facebook"]


class URLUtils:
    """Utilities for URL processing and platform detection."""
    
    # Platform domain patterns
    PLATFORM_PATTERNS = {
        "youtube": [
            r"youtube\.com",
            r"youtu\.be",
            r"m\.youtube\.com",
        ],
        "instagram": [
            r"instagram\.com",
            r"instagr\.am",
        ],
        "tiktok": [
            r"tiktok\.com",
            r"vm\.tiktok\.com",
        ],
        "facebook": [
            r"facebook\.com",
            r"fb\.watch",
            r"fb\.com",
        ],
    }
    
    @staticmethod
    def detect_platform(url: str) -> Platform | None:
        """
        Detect platform from URL.
        
        Args:
            url: Video URL
        
        Returns:
            Platform name or None if unsupported
        """
        url_lower = url.lower()
        
        for platform, patterns in URLUtils.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return platform
        
        return None
    
    @staticmethod
    def canonicalize_url(url: str, platform: Platform) -> str:
        """
        Convert URL to canonical format.
        
        Args:
            url: Original URL
            platform: Detected platform
        
        Returns:
            Canonical URL
        """
        if platform == "youtube":
            return URLUtils._canonicalize_youtube(url)
        elif platform == "instagram":
            return URLUtils._canonicalize_instagram(url)
        elif platform == "tiktok":
            return URLUtils._canonicalize_tiktok(url)
        elif platform == "facebook":
            return URLUtils._canonicalize_facebook(url)
        
        return url
    
    @staticmethod
    def _canonicalize_youtube(url: str) -> str:
        """Canonicalize YouTube URL to watch?v= format."""
        # Extract video ID
        video_id = None
        
        # youtu.be/VIDEO_ID
        match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
        if match:
            video_id = match.group(1)
        
        # youtube.com/watch?v=VIDEO_ID
        match = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
        if match:
            video_id = match.group(1)
        
        # youtube.com/shorts/VIDEO_ID
        match = re.search(r"/shorts/([a-zA-Z0-9_-]{11})", url)
        if match:
            video_id = match.group(1)
        
        # youtube.com/embed/VIDEO_ID
        match = re.search(r"/embed/([a-zA-Z0-9_-]{11})", url)
        if match:
            video_id = match.group(1)
        
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        
        return url
    
    @staticmethod
    def _canonicalize_instagram(url: str) -> str:
        """Canonicalize Instagram URL."""
        # Extract post/reel ID
        match = re.search(r"/(p|reel|tv)/([A-Za-z0-9_-]+)", url)
        if match:
            post_type = match.group(1)
            post_id = match.group(2)
            # Remove trailing slash and query params
            post_id = post_id.split("/")[0].split("?")[0]
            return f"https://www.instagram.com/{post_type}/{post_id}/"
        
        return url
    
    @staticmethod
    def _canonicalize_tiktok(url: str) -> str:
        """Canonicalize TikTok URL."""
        # Extract video ID
        match = re.search(r"/video/(\d+)", url)
        if match:
            video_id = match.group(1)
            return f"https://www.tiktok.com/@user/video/{video_id}"
        
        # Handle short URLs (vm.tiktok.com) - keep as is, yt-dlp will resolve
        if "vm.tiktok.com" in url:
            return url
        
        return url
    
    @staticmethod
    def _canonicalize_facebook(url: str) -> str:
        """Canonicalize Facebook URL."""
        # Extract video ID
        match = re.search(r"/videos?/(\d+)", url)
        if match:
            video_id = match.group(1)
            return f"https://www.facebook.com/watch/?v={video_id}"
        
        # fb.watch short URLs
        match = re.search(r"fb\.watch/([a-zA-Z0-9_-]+)", url)
        if match:
            # Keep as is, yt-dlp will resolve
            return url
        
        return url
    
    @staticmethod
    def generate_url_hash(canonical_url: str) -> str:
        """
        Generate SHA-256 hash of canonical URL.
        
        Args:
            canonical_url: Canonical URL
        
        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(canonical_url.encode()).hexdigest()
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if URL is valid.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_platform(platform: str, allowed_platforms: list[str]) -> bool:
        """
        Check if platform is in allowed list.
        
        Args:
            platform: Platform name
            allowed_platforms: List of allowed platforms
        
        Returns:
            True if allowed
        """
        return platform in allowed_platforms
