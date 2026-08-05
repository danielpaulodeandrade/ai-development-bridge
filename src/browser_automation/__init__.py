"""
Browser Automation Framework
Milestone 4 - Media Studio AI
"""
from .browser_daemon import BrowserDaemon
from .clipboard_extractor import ClipboardExtractor
from .text_feeder import TextFeeder
from .adaptive_recovery import AdaptiveRecovery

__all__ = ["BrowserDaemon", "ClipboardExtractor", "TextFeeder", "AdaptiveRecovery"]
