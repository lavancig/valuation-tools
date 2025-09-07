#!/usr/bin/env python3
"""
Test script to verify GUI startup works without errors
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_startup():
    """Test that GUI can start without errors"""
    
    print("Testing GUI startup...")
    print("="*30)
    
    try:
        # Import GUI components
        from src.gui.guiMain import GuiMain
        print("✓ Successfully imported GuiMain")
        
        # Create GUI instance
        gui = GuiMain()
        print("✓ Successfully created GUI instance")
        
        # Check that sensitivity tab was created
        if hasattr(gui, '_sensitivityTab'):
            print("✓ Sensitivity tab created successfully")
            
            # Check initial state
            if hasattr(gui._sensitivityTab, 'run_button'):
                button_state = gui._sensitivityTab.run_button['state']
                print(f"✓ Run button initial state: {button_state}")
            
            if hasattr(gui._sensitivityTab, 'status_label'):
                status_text = gui._sensitivityTab.status_label['text']
                print(f"✓ Status label initial text: {status_text}")
        else:
            print("✗ Sensitivity tab not found")
        
        # Test controller registration (mock)
        class MockController:
            def __init__(self):
                self._modelObj = None
        
        mock_controller = MockController()
        gui.registerController(mock_controller)
        print("✓ Controller registration completed without errors")
        
        print("\n✓ GUI startup test passed!")
        print("The application should now start without errors.")
        
    except Exception as e:
        print(f"✗ GUI startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_gui_startup()
