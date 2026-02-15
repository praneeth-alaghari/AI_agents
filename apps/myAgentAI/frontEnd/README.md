# myAgentAI - Frontend

A scalable, modular Flutter application for the myAgentAI platform.

## 📱 Features

- **Dashboard**: Overview of AI activities.
- **Email Housekeeper**: AI-powered email management with reinforcement learning feedback loop.
- **API Key Management**: Securely store OpenAI and Gmail API keys.
- **Modular Architecture**: Feature-based folder structure for easy expansion.

## 🛠 Tech Stack

- **Flutter**: UI Framework
- **Riverpod**: State Management
- **Dio**: HTTP Client with Interceptors
- **GoRouter**: Navigation
- **Flutter Secure Storage**: Secure token storage
- **Google Fonts**: Typography

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   flutter pub get
   ```

2. **Run the App**
   Ensure an emulator is running or a device is connected.
   ```bash
   flutter run
   ```

3. **Backend Connection**
   - Default Base URL: `http://10.0.2.2:8000` (Android Emulator loopback)
   - Change in `lib/core/constants.dart` if running on physical device or iOS.

## 📂 Project Structure

```
lib/
├── core/                  # Core configuration (Auth, API, Theme, Routes)
├── features/              # Feature modules
│   ├── auth/              # Login screen
│   ├── dashboard/         # Dashboard & Drawer
│   ├── email_housekeeper/ # Email management utility
│   └── api_keys/          # API key management
├── shared/                # Reusable widgets
└── main.dart              # App entry point
```

## 📝 Setup for Android

Ensure you have the correct Android SDK installed as per `android/app/build.gradle`.
Min SDK: 21 (Flutter default usually, check config)
Target SDK: 34 (Android 14)
