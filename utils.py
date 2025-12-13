"""
Utility functions for the scraper.
Includes rate limiting with jitter for anti-fingerprinting.
"""
import time
import random


def sleep_with_jitter(base, jitter=0.3):
    """
    Sleep for a base duration plus random jitter.
    This helps avoid robotic timing patterns that could be detected.
    
    Args:
        base (float): Base sleep duration in seconds
        jitter (float): Maximum random jitter to add (0 to jitter seconds)
        
    Example:
        sleep_with_jitter(1.5, 0.3)  # Sleeps 1.5-1.8 seconds
    """
    sleep_time = base + random.uniform(0, jitter)
    time.sleep(sleep_time)


def format_number(num):
    """Format a number with commas for readability"""
    if num is None:
        return "0"
    return f"{num:,}"


def estimate_time_remaining(novels_remaining, rate_per_novel=0.7):
    """
    Estimate time remaining for scraping.
    
    Args:
        novels_remaining (int): Number of novels left to scrape
        rate_per_novel (float): Average seconds per novel (default: 0.7s)
        
    Returns:
        str: Human-readable time estimate
    """
    seconds = novels_remaining * rate_per_novel
    
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds / 60)}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"
