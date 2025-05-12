import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
screen_w, screen_h = pyautogui.size()

# Capture webcam
cap = cv2.VideoCapture(0)

prev_click_time = time.time()
click_delay = 1  # seconds

# Finger tip landmarks
tips_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    h, w, _ = img.shape

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            if lm_list:
                # Draw landmarks
                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

                # Cursor control - move to index finger
                x, y = lm_list[8]  # Index fingertip
                screen_x = int((x / w) * screen_w)
                screen_y = int((y / h) * screen_h)
                pyautogui.moveTo(screen_x, screen_y)

                # Finger detection
                fingers = []

                # Thumb
                if lm_list[tips_ids[0]][0] > lm_list[tips_ids[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # Other fingers
                for i in range(1, 5):
                    if lm_list[tips_ids[i]][1] < lm_list[tips_ids[i] - 2][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                total_fingers = sum(fingers)
                now = time.time()

                # Click actions
                if now - prev_click_time > click_delay:
                    if fingers[1] == 1 and sum(fingers) == 1:
                        print("Single Click")
                        pyautogui.click()
                        prev_click_time = now

                    elif fingers[1] == 1 and fingers[2] == 1 and sum(fingers) == 2:
                        print("Double Click")
                        pyautogui.doubleClick()
                        prev_click_time = now

                    elif total_fingers >= 4:
                        print("Right Click")
                        pyautogui.rightClick()
                        prev_click_time = now

    # Display
    cv2.imshow("Virtual Mouse - Hand Controlled", img)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
