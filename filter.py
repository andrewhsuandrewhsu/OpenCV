import cv2
import numpy as np

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Set resolution
img_w, img_h = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, img_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, img_h)

# Variables
freeze_frame = None
scanning = False
i = 0
saved = False
scan_speed = 5  # Increase this number to make the scan faster

# Mouse callback function
def start_scan(event, x, y, flags, param):
    global scanning, i, freeze_frame, saved
    if event == cv2.EVENT_LBUTTONDOWN:
        scanning = True
        i = 0
        freeze_frame = None
        saved = False

# Create window
cv2.namedWindow('Time Warp Scan')
cv2.setMouseCallback('Time Warp Scan', start_scan)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Flip for mirror effect
    frame = cv2.flip(frame, 1)
    
    if not scanning:
        # Show start screen
        start_screen = frame.copy()
        cv2.putText(start_screen, "Click to Start Scan", (img_w//2-120, img_h//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(start_screen, "Left click anywhere to begin", (img_w//2-180, img_h//2+40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow('Time Warp Scan', start_screen)
    else:
        # Initialize freeze frame on first scan
        if freeze_frame is None:
            freeze_frame = np.zeros_like(frame)
        
        # Update multiple columns at once for faster scan
        if i < img_w:
            end_col = min(i + scan_speed, img_w)
            freeze_frame[:, i:end_col, :] = frame[:, i:end_col, :]
            i = end_col
        
        composite = freeze_frame.copy()
        if i < img_w: 
            cv2.line(composite, (i, 0), (i, img_h), (0, 0, 255), 2)
            composite[:, i:, :] = frame[:, i:, :] 
        
        if i >= img_w and not saved:
            cv2.putText(composite, "Press 's' to save", (img_w//2-100, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(composite, "Press 'r' to rescan", (img_w//2-100, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(composite, "Press 'q' to quit", (img_w//2-100, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        
        cv2.imshow('Time Warp Scan', composite)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s') and scanning and i >= img_w and not saved:
        filename = "time_warp_scan.jpg"
        cv2.imwrite(filename, freeze_frame)
        print(f"Image saved as {filename}")
        saved = True
    if key == ord('r'):
        scanning = False

    if cv2.getWindowProperty('Time Warp Scan', cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()