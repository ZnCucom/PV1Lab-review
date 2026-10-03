# Setup follow-up

User screenshot now shows Sandboxie Plus Global Settings / App Templates / App Compatibility, rather than the first-run Setup Wizard. Installation was already verified; screenshot does not itself qualify isolation.

Read-only checks: PV1Lab_NoLicense Enabled=n, RestrictDevices=y. No test/original process launched. GUI enumeration still returns only Sandboxie-Plus Notifications (397704), not the user's visible Global Settings. Per user's instruction stop GUI attempts rather than repeat the same failed activation loop.

Official SBIE6004 documentation confirms the 5-minute termination is conditional on a certificate-gated feature in the selected box. It is not a universal 5-minute restriction on personal/noncommercial standard use. Current exact-version driver source checks active certificate with opt_sec for RestrictDevices. Buying a certificate is not the only path: ordinary supported features may suffice after independent testing; an official eligible evaluation certificate can be a temporary test route. No certificate has been requested, read, installed, or purchased by the agent.

Do not enable global compatibility templates merely because detected. Current screenshot's unchecked entries need not be applied for our task. If no intentional unsaved settings were made, Cancel closes that dialog without applying changes. Then return to the normal sandbox list. Do not start PV1, enter its key, or re-enable the rejected box.

Next technical work: separately review standard-feature rules and inherited global templates; preserve project/private/control/run denial, offline behavior and virtualization; verify device/clipboard/desktop/input/IPC boundaries; eliminate timed termination before any GPU run; use formal native snapshot manager only after processes exit. Removing RestrictDevices or acquiring a certificate alone is not qualification.

Sources:
- https://sandboxie-plus.github.io/sandboxie-docs/Content/SBIE6004/
- https://sandboxie-plus.com/supporter-certificate/
- https://sandboxie-plus.github.io/sandboxie-docs/Content/FeatureComparison/
- https://github.com/sandboxie-plus/Sandboxie/blob/v1.18.5/Sandboxie/core/drv/process.c
