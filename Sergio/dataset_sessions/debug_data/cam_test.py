
import cv2

for index in [0, 1]:
    print(f"\nTrying /dev/video{index} ...")
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("  Could not open this device at all.")
        continue

    # Force basic capture settings to something super common
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    ret, frame = cap.read()
    if not ret:
        print("  Opened but failed to read a frame.")
    else:
        print("  SUCCESS: got a frame with shape:", frame.shape)
        cv2.imwrite(f"test_frame_{index}.png", frame)
        print(f"  Saved test_frame_{index}.png")

    cap.release()
