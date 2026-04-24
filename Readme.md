# 🛡️ SafeClass AI Moderator
**Fuzzy Logic Based Context-Aware Content Moderation**

Developed by: **Asad Ullah & Ahmad Raza** University: **GCUF, Chiniot Campus**

---

## 🚀 Introduction
SafeClass AI is an intelligent moderation system that goes beyond simple keyword filtering. It uses **Fuzzy Logic** to determine if a message should be allowed, flagged, or removed based on the surrounding context of the user and the message tone.

## 🧠 How it Works
The system evaluates three dynamic inputs:
* **Severity (0-10):** How offensive is the keyword?
* **Reputation (0-10):** How trustworthy is the user?
* **Sentiment (-1 to 1):** Is the tone positive, neutral, or negative?

### **Actions Taken:**
| Risk Score | Action | Description |
| :--- | :--- | :--- |
| **0 - 4** | ✅ NONE | Content is safe. |
| **4 - 7** | ⚠️ FLAG | Suspicious context (potential sarcasm). |
| **7 - 10** | 🚫 REMOVE | High-risk content deleted. |

## 🛠️ Installation & Usage
1. Clone this repository.
2. Install requirements:
   ```bash
   pip install streamlit scikit-fuzzy matplotlib numpy