"""
iOS Pipeline — xcodebuild, notarytool, and Transporter CLI wrapper.

Requirements:
  - macOS 15+ host
  - Xcode 26+ with iOS 26 SDK installed
  - Apple Developer account ($99/year)
  - Valid keychain profile for notarytool

This module is intentionally a thin wrapper that shells out to Apple tooling.
It performs no magic — just orchestrates the standard Xcode workflow.

App Store hard constraints enforced:
  - §2.5.2: No runtime executable downloads (checked by Skeptic agent)
  - Archive export uses AdHoc or AppStore distribution method
"""

from __future__ import annotations

import asyncio
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

XCODE_BUILD_TIMEOUT = int(os.getenv("XCODE_BUILD_TIMEOUT", str(30 * 60)))  # 30 min
NOTARIZE_TIMEOUT = int(os.getenv("NOTARIZE_TIMEOUT", str(10 * 60)))  # 10 min


# ─── Result ───────────────────────────────────────────────────────────────────


@dataclass
class PipelineResult:
    success: bool
    message: str
    output: str = ""


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _is_macos() -> bool:
    return sys.platform == "darwin"


async def _run_command(
    *args: str,
    cwd: Path,
    timeout: int = XCODE_BUILD_TIMEOUT,
) -> tuple[str, str, int]:
    """Run a shell command and return (stdout, stderr, returncode)."""
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=float(timeout)
        )
        return stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace"), proc.returncode or 0
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return "", f"Command timed out after {timeout}s", -1


def _find_xcodeproj(project_path: Path) -> Path | None:
    """Find the .xcodeproj in the project directory."""
    matches = list(project_path.glob("*.xcodeproj"))
    return matches[0] if matches else None


def _find_scheme(xcodeproj: Path) -> str:
    """Derive scheme name from .xcodeproj name."""
    return xcodeproj.stem


def _export_options_plist(project_path: Path) -> Path:
    """Generate ExportOptions.plist if it doesn't exist."""
    plist_path = project_path / "ExportOptions.plist"
    if not plist_path.exists():
        plist_path.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>destination</key>
    <string>upload</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>stripSwiftSymbols</key>
    <true/>
    <key>uploadBitcode</key>
    <false/>
    <key>uploadSymbols</key>
    <true/>
</dict>
</plist>
""",
            encoding="utf-8",
        )
    return plist_path


# ─── Pipeline ─────────────────────────────────────────────────────────────────


class IOSPipeline:
    """Orchestrates the full iOS build → archive → notarize → submit pipeline."""

    async def build(self, project_path: Path) -> PipelineResult:
        """Build for iOS Simulator (fast iteration check)."""
        if not _is_macos():
            return PipelineResult(
                success=False,
                message="iOS builds require macOS. Linux/Windows not supported.",
            )

        xcodeproj = _find_xcodeproj(project_path)
        if not xcodeproj:
            return PipelineResult(
                success=False,
                message="No .xcodeproj found. Create one with Xcode first.",
            )

        scheme = _find_scheme(xcodeproj)
        logger.info("ios.build", scheme=scheme, project=str(xcodeproj))

        stdout, stderr, code = await _run_command(
            "xcodebuild",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "-destination", "generic/platform=iOS Simulator",
            "-configuration", "Debug",
            "build",
            cwd=project_path,
        )

        output = stdout + stderr
        if code == 0:
            return PipelineResult(success=True, message="Build succeeded", output=output)
        return PipelineResult(success=False, message="Build failed", output=output)

    async def archive(self, project_path: Path) -> PipelineResult:
        """Archive the app for distribution."""
        if not _is_macos():
            return PipelineResult(
                success=False,
                message="iOS archive requires macOS.",
            )

        xcodeproj = _find_xcodeproj(project_path)
        if not xcodeproj:
            return PipelineResult(
                success=False,
                message="No .xcodeproj found.",
            )

        scheme = _find_scheme(xcodeproj)
        archive_path = project_path / "build" / f"{scheme}.xcarchive"
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        export_plist = _export_options_plist(project_path)

        logger.info("ios.archive", scheme=scheme)

        # Step 1: Archive
        stdout, stderr, code = await _run_command(
            "xcodebuild",
            "archive",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "-archivePath", str(archive_path),
            "-configuration", "Release",
            "-allowProvisioningUpdates",
            cwd=project_path,
        )
        output = stdout + stderr
        if code != 0:
            return PipelineResult(
                success=False, message="Archive failed", output=output
            )

        # Step 2: Export IPA
        export_path = project_path / "build"
        stdout2, stderr2, code2 = await _run_command(
            "xcodebuild",
            "-exportArchive",
            "-archivePath", str(archive_path),
            "-exportOptionsPlist", str(export_plist),
            "-exportPath", str(export_path),
            "-allowProvisioningUpdates",
            cwd=project_path,
        )
        output += "\n" + stdout2 + stderr2
        if code2 != 0:
            return PipelineResult(
                success=False, message="IPA export failed", output=output
            )

        return PipelineResult(
            success=True, message="Archive + IPA export succeeded", output=output
        )

    async def notarize(self, project_path: Path, ipa_path: Path) -> PipelineResult:
        """Notarize the IPA using notarytool."""
        keychain_profile = os.getenv("APPLE_KEYCHAIN_PROFILE", "alkemist-notary")

        logger.info("ios.notarize", ipa=str(ipa_path))
        stdout, stderr, code = await _run_command(
            "xcrun",
            "notarytool",
            "submit",
            str(ipa_path),
            "--keychain-profile", keychain_profile,
            "--wait",
            cwd=project_path,
            timeout=NOTARIZE_TIMEOUT,
        )
        output = stdout + stderr
        if code == 0:
            return PipelineResult(success=True, message="Notarization succeeded", output=output)
        return PipelineResult(success=False, message="Notarization failed", output=output)

    async def submit(self, project_path: Path) -> PipelineResult:
        """Full pipeline: archive → notarize → upload to App Store."""
        if not _is_macos():
            return PipelineResult(
                success=False,
                message="App Store submission requires macOS + Apple Developer account.",
            )

        # Archive first
        archive_result = await self.archive(project_path)
        if not archive_result.success:
            return archive_result

        # Find IPA
        ipa_candidates = list((project_path / "build").glob("*.ipa"))
        if not ipa_candidates:
            return PipelineResult(
                success=False,
                message="No IPA found after archive. Check ExportOptions.plist.",
                output=archive_result.output,
            )
        ipa_path = ipa_candidates[0]

        # Notarize
        notarize_result = await self.notarize(project_path, ipa_path)
        if not notarize_result.success:
            return notarize_result

        # Upload via Transporter
        logger.info("ios.upload", ipa=str(ipa_path))
        stdout, stderr, code = await _run_command(
            "xcrun",
            "transporter",
            "upload",
            "-f", str(ipa_path),
            cwd=project_path,
            timeout=NOTARIZE_TIMEOUT,
        )
        output = archive_result.output + "\n" + notarize_result.output + "\n" + stdout + stderr

        if code == 0:
            return PipelineResult(
                success=True, message="App submitted to App Store Connect", output=output
            )
        return PipelineResult(
            success=False, message="Transporter upload failed", output=output
        )
