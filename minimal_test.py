#!/usr/bin/env python3
print("Starting minimal test...")

try:
    print("Testing basic imports...")
    import os
    import sys
    print("Basic imports successful")
    
    print("Testing GroomRoom import...")
    from groomroom.core import GroomRoom
    print("GroomRoom import successful")
    
    print("Testing GroomRoom initialization...")
    groomroom = GroomRoom()
    print("GroomRoom initialization successful")
    
    print("Testing methods...")
    methods = ['generate_groom_analysis', 'get_groom_level_prompt']
    for method in methods:
        if hasattr(groomroom, method):
            print(f"Method {method} exists")
        else:
            print(f"Method {method} missing")
    
    print("Minimal test completed successfully!")
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
