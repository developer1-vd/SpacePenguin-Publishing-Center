# SpacePenguin on the App Store (iPhone)

The App Store listing for the iPhone app (`mobile/` in SpacePenguin), in the
folder layout [fastlane](https://docs.fastlane.tools/actions/deliver/) reads:

| File | What it is | Apple's limit |
| ---- | ---------- | ------------- |
| `fastlane/metadata/en-US/name.txt` | SpacePenguin Browser | 30 characters |
| `fastlane/metadata/en-US/subtitle.txt` | under the name | 30 characters |
| `fastlane/metadata/en-US/description.txt` | the store page text | 4000 characters |
| `fastlane/metadata/en-US/keywords.txt` | search keywords, comma-separated | 100 characters |
| `fastlane/metadata/en-US/promotional_text.txt` | changeable without a new version | 170 characters |
| `fastlane/metadata/en-US/release_notes.txt` | What's New | 4000 characters |
| `fastlane/metadata/en-US/*_url.txt` | support, marketing and privacy pages | |
| `fastlane/metadata/primary_category.txt` | Utilities (where browsers go) | |
| `fastlane/metadata/secondary_category.txt` | Productivity | |

The description says what the iPhone app really does, limits included: iOS lets
no app block a web view's requests, so ads are hidden and skipped, not blocked.

## What Apple needs that cannot be in this folder

1. **An Apple Developer Program membership** ($99 a year) in your name.
2. **The bundle ID** `org.spacepenguin.SpacePenguin` registered in your account
   (Certificates, Identifiers & Profiles), and an app record for it in
   [App Store Connect](https://appstoreconnect.apple.com).
3. **A signed build.** The `.ipa` in each release is unsigned. Build a signed one
   on a Mac with Xcode: `./build-ios.sh --team <your team ID>` in SpacePenguin,
   then upload it with Xcode's Organizer or Apple's Transporter app.
4. **Screenshots**, at least for the 6.9-inch iPhone (1320 × 2868), taken in the
   iOS Simulator or on an iPhone. They go in `fastlane/screenshots/en-US/`.
5. **Answers only you can give**, in App Store Connect:
   - *App Privacy:* SpacePenguin collects no data, so **Data Not Collected**.
   - *Age rating:* a browser has **unrestricted web access**, which Apple rates
     for adults only (18+).
   - *App Review contact* (name, phone, email): yours, not stored here.

The app shows pages with iOS's own engine (WKWebView), as Apple requires of every
iPhone browser, so it meets App Review's rule 2.5.6.

## Uploading the listing

With fastlane installed (`brew install fastlane`) and signed in to App Store
Connect, from this folder:

```sh
fastlane deliver --app-identifier org.spacepenguin.SpacePenguin \
    --skip-binary-upload --skip-screenshots --force
```

That sends the text and categories; drop `--skip-screenshots` once the
screenshots are in. The build itself goes up from Xcode or Transporter, and you
submit it for review in App Store Connect.
