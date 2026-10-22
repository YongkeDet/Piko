# Download dialogs remain English with “Ask every time”

- Reported against Chinese release `X.26.01`, using X `12.35.0-prod.01`.
- Piko source: `11ea728b9e0a907b2162b79445368cbcef21e783`.
- Reproduction: select “Ask every time” for photo and video/GIF quality, then tap a post’s download button. The resolution/quality chooser and multi-media picker still use English display labels.
- Cause: `ResolutionChooserDialog` and `MediaPickerDialog` use Java string literals rather than Android string resources. This is UI localization, not a resolver, bytecode, or APK compatibility failure.
- Fix in `X.26.02`: apply a focused source patch to those two dialog classes and add 14 English/Chinese string pairs. Reuse existing translations for Original/Large/Medium/Small. Translate media labels at display time so media classification, download URLs, quality keys, MIME types, and callbacks retain their original values.
- Validation: apply the patch to the pinned source; check all 487 translated resources and placeholders; compare media classification and callback code with the original; compile the extension and patch bundle in GitHub Actions. Phone interaction requires the user to install the rebuilt app and exercise the same flow; no device was controlled during this fix.
- Rollback: use the unchanged `X.26.01` Git tag and release bundle.
