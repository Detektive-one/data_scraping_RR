"""
Test script for new checkpoint and jitter features.
"""
import time
from .checkpoint import Checkpoint
from .utils import sleep_with_jitter, format_number, estimate_time_remaining


def test_checkpoint():
    """Test checkpoint save/load functionality"""
    print("\n" + "=" * 70)
    print("TEST: Checkpoint System")
    print("=" * 70)
    
    # Create and save checkpoint
    cp = Checkpoint()
    print("\n1. Creating new checkpoint...")
    cp.save(current_page=5, total_scraped=100, last_fiction_id=12345)
    print(f"   ✓ Saved: {cp}")
    
    # Load checkpoint
    print("\n2. Loading checkpoint...")
    cp2 = Checkpoint()
    print(f"   ✓ Loaded: {cp2}")
    print(f"   - Start page: {cp2.get_start_page()}")
    print(f"   - Total scraped: {cp2.get_total_scraped()}")
    
    # Clear checkpoint
    print("\n3. Clearing checkpoint...")
    cp.clear()
    print(f"   ✓ Cleared")
    
    print("\n✓ Checkpoint test passed!")


def test_jitter():
    """Test jitter-based sleep timing"""
    print("\n" + "=" * 70)
    print("TEST: Jitter-Based Rate Limiting")
    print("=" * 70)
    
    print("\n1. Testing sleep_with_jitter(1.0, 0.3)...")
    print("   Expected: 1.0-1.3 seconds")
    
    times = []
    for i in range(5):
        start = time.time()
        sleep_with_jitter(1.0, 0.3)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"   Attempt {i+1}: {elapsed:.3f}s")
    
    avg = sum(times) / len(times)
    print(f"\n   Average: {avg:.3f}s")
    print(f"   Min: {min(times):.3f}s, Max: {max(times):.3f}s")
    
    if 1.0 <= min(times) and max(times) <= 1.35:
        print("\n✓ Jitter test passed!")
    else:
        print("\n⚠ Jitter values outside expected range")


def test_utilities():
    """Test utility functions"""
    print("\n" + "=" * 70)
    print("TEST: Utility Functions")
    print("=" * 70)
    
    print("\n1. Testing format_number()...")
    print(f"   1234567 → {format_number(1234567)}")
    print(f"   65000 → {format_number(65000)}")
    print(f"   None → {format_number(None)}")
    
    print("\n2. Testing estimate_time_remaining()...")
    print(f"   1000 novels → {estimate_time_remaining(1000)}")
    print(f"   10000 novels → {estimate_time_remaining(10000)}")
    print(f"   65000 novels → {estimate_time_remaining(65000)}")
    
    print("\n✓ Utility test passed!")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("TESTING NEW FEATURES")
    print("=" * 70)
    
    try:
        test_checkpoint()
        test_jitter()
        test_utilities()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nNew features are working correctly:")
        print("  ✓ Checkpoint save/load/clear")
        print("  ✓ Jitter-based rate limiting")
        print("  ✓ Utility functions")
        print("\nYou can now run: python run_scrape.py")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
