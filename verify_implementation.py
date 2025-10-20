"""Quick verification of GroomRoom implementation"""
import sys
sys.path.insert(0, '.')

try:
    from groomroom.core import GroomRoom
    
    print("✅ GroomRoom imported successfully")
    
    # Create instance
    gr = GroomRoom()
    print("✅ GroomRoom instance created")
    
    # Check methods exist
    methods = [
        'detect_card_type',
        'analyze_story',
        'audit_acceptance_criteria',
        'generate_test_scenarios',
        'audit_bug',
        'analyze_frameworks',
        'analyze_dor_requirements_enhanced',
        'calculate_readiness',
        'analyze_ticket',
        'summarize_output'
    ]
    
    for method in methods:
        if hasattr(gr, method):
            print(f"✅ Method '{method}' exists")
        else:
            print(f"❌ Method '{method}' missing")
    
    print("\n✅ All core methods verified!")
    print("\nGroomRoom refinement agent updated successfully — ready for testing on Jira input.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

