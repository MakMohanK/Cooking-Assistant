#!/usr/bin/env python3
"""
Calibration Script for Chef Assistant
Helps calibrate camera, measuring spoons, and containers for accurate quantity detection.
"""

import sys
import cv2
import numpy as np
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def calibrate_camera_scale():
    """Calibrate pixels-per-cm using an A4 paper or ArUco marker."""
    print("\n" + "="*60)
    print("Camera Scale Calibration")
    print("="*60)
    print("\nPlace an A4 paper (21cm x 29.7cm) flat in front of the camera.")
    print("Make sure the entire paper is visible.")
    print("\nPress SPACE to capture, ESC to skip.")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return None
    
    pixels_per_cm = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Display frame
        display = frame.copy()
        cv2.putText(display, "Position A4 paper, press SPACE to capture", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Calibration", display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest rectangular contour (should be the paper)
                largest = max(contours, key=cv2.contourArea)
                
                # Approximate to polygon
                epsilon = 0.02 * cv2.arcLength(largest, True)
                approx = cv2.approxPolyDP(largest, epsilon, True)
                
                if len(approx) == 4:
                    # Calculate width in pixels
                    pts = approx.reshape(4, 2)
                    width_px = np.linalg.norm(pts[0] - pts[1])
                    
                    # A4 width is 21cm
                    pixels_per_cm = width_px / 21.0
                    
                    print(f"\n✓ Calibration successful!")
                    print(f"  Detected width: {width_px:.1f} pixels")
                    print(f"  Pixels per cm: {pixels_per_cm:.2f}")
                    break
                else:
                    print("\n✗ Could not detect paper rectangle. Try again.")
            else:
                print("\n✗ No contours detected. Ensure good lighting and contrast.")
    
    cap.release()
    cv2.destroyAllWindows()
    
    return pixels_per_cm


def calibrate_measuring_spoons(pixels_per_cm):
    """Calibrate measuring spoon dimensions."""
    print("\n" + "="*60)
    print("Measuring Spoon Calibration")
    print("="*60)
    
    spoon_data = {}
    spoon_types = ["teaspoon", "tablespoon"]
    
    cap = cv2.VideoCapture(0)
    
    for spoon_type in spoon_types:
        print(f"\nPlace an empty {spoon_type} in view.")
        print("Position it flat and centered.")
        print("Press SPACE to capture, ESC to skip.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            display = frame.copy()
            cv2.putText(display, f"Position {spoon_type}, press SPACE", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Calibration", display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                # Simple bowl detection (find largest ellipse/circle)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (9, 9), 2)
                circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 50,
                                          param1=100, param2=30, minRadius=20, maxRadius=100)
                
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    # Take the largest circle
                    largest = max(circles[0], key=lambda c: c[2])
                    x, y, r = largest
                    
                    # Calculate diameter in pixels and cm
                    diameter_px = r * 2
                    
                    if pixels_per_cm:
                        diameter_cm = diameter_px / pixels_per_cm
                        area_cm2 = np.pi * (diameter_cm / 2) ** 2
                    else:
                        # Use default estimates
                        diameter_cm = 3.2 if spoon_type == "teaspoon" else 3.9
                        area_cm2 = 8.0 if spoon_type == "teaspoon" else 12.3
                    
                    spoon_data[spoon_type] = {
                        "bowl_diameter_cm": float(diameter_cm),
                        "bowl_area_cm2": float(area_cm2),
                        "bowl_diameter_px": float(diameter_px)
                    }
                    
                    print(f"\n✓ {spoon_type.capitalize()} calibrated!")
                    print(f"  Diameter: {diameter_cm:.2f} cm")
                    print(f"  Area: {area_cm2:.2f} cm²")
                    break
                else:
                    print("\n✗ Could not detect spoon bowl. Try again with better lighting.")
        
        if key == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    return spoon_data


def save_calibration(pixels_per_cm, spoon_data):
    """Save calibration data to YAML file."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    calibration = {
        "pixels_per_cm": float(pixels_per_cm) if pixels_per_cm else 35.0,
        "spoons": spoon_data if spoon_data else {
            "teaspoon": {"bowl_diameter_cm": 3.2, "bowl_area_cm2": 8.0},
            "tablespoon": {"bowl_diameter_cm": 3.9, "bowl_area_cm2": 12.3}
        }
    }
    
    calib_file = config_dir / "calibration.yaml"
    
    with open(calib_file, 'w') as f:
        yaml.dump(calibration, f, default_flow_style=False)
    
    print(f"\n✓ Calibration saved to: {calib_file}")
    return calib_file


def main():
    """Main calibration workflow."""
    print("="*60)
    print("Chef Assistant - Calibration Tool")
    print("="*60)
    print("\nThis tool helps calibrate:")
    print("  1. Camera scale (pixels to cm)")
    print("  2. Measuring spoon dimensions")
    print("\nCalibration improves quantity detection accuracy.")
    print()
    
    # Check if OpenCV is available
    try:
        import cv2
    except ImportError:
        print("Error: OpenCV (cv2) is required for calibration.")
        print("Install with: pip install opencv-python")
        sys.exit(1)
    
    # Step 1: Camera scale
    print("\n" + "-"*60)
    choice = input("Calibrate camera scale? (y/n): ").lower().strip()
    
    pixels_per_cm = None
    if choice == 'y':
        pixels_per_cm = calibrate_camera_scale()
    
    # Step 2: Measuring spoons
    print("\n" + "-"*60)
    choice = input("Calibrate measuring spoons? (y/n): ").lower().strip()
    
    spoon_data = {}
    if choice == 'y':
        spoon_data = calibrate_measuring_spoons(pixels_per_cm)
    
    # Save calibration
    if pixels_per_cm or spoon_data:
        calib_file = save_calibration(pixels_per_cm, spoon_data)
        
        print("\n" + "="*60)
        print("Calibration Complete!")
        print("="*60)
        print(f"\nCalibration file: {calib_file}")
        print("\nTo use this calibration, set environment variable:")
        print(f"  export CALIB_FILE={calib_file}")
        print("\nOr update run_chef.sh to include:")
        print(f"  export CALIB_FILE=\"{calib_file}\"")
    else:
        print("\nNo calibration performed. Using default values.")
    
    print()


if __name__ == '__main__':
    main()
