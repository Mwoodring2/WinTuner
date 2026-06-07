"""Reusable dialogs with scroll areas and pinned action buttons."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.tweak_model import RiskLevel, Tweak


def _clamp_dialog_to_screen(dialog: QDialog) -> None:
    """Center dialog over parent and clamp to visible screen area."""
    parent = dialog.parentWidget()
    screen = dialog.screen() or QScreen.primaryScreen()
    if screen is None:
        return
    geo = screen.availableGeometry()
    if parent is not None:
        center = parent.frameGeometry().center()
    else:
        center = geo.center()
    dialog.adjustSize()
    w, h = dialog.width(), dialog.height()
    x = max(geo.x(), min(center.x() - w // 2, geo.right() - w))
    y = max(geo.y(), min(center.y() - h // 2, geo.bottom() - h))
    dialog.setGeometry(x, y, w, h)


class ScrollDialog(QDialog):
    """Base resizable dialog with scrollable content and pinned buttons."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(420, 280)
        self.resize(520, 400)
        self.setSizeGripEnabled(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll.setWidget(self._scroll_content)
        outer.addWidget(self._scroll, stretch=1)

        self._button_box = QDialogButtonBox()
        outer.addWidget(self._button_box)

    def scroll_layout(self) -> QVBoxLayout:
        return self._scroll_layout

    def add_button(self, role: QDialogButtonBox.ButtonRole, text: str) -> QPushButton:
        btn = self._button_box.addButton(text, role)
        return btn

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        _clamp_dialog_to_screen(self)


def _message_dialog(
    parent: QWidget | None,
    title: str,
    message: str,
    button_text: str = "OK",
) -> None:
    """Show a scrollable message dialog with a pinned OK button."""
    dlg = ScrollDialog(title, parent)
    layout = dlg.scroll_layout()
    lbl = QLabel(message)
    lbl.setWordWrap(True)
    lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    layout.addWidget(lbl)
    layout.addStretch()
    ok_btn = dlg.add_button(QDialogButtonBox.ButtonRole.AcceptRole, button_text)
    ok_btn.clicked.connect(dlg.accept)
    dlg.exec()


def show_info(parent: QWidget, title: str, message: str) -> None:
    _message_dialog(parent, title, message)


def show_warning(parent: QWidget, title: str, message: str) -> None:
    _message_dialog(parent, title, message)


def show_error(parent: QWidget, title: str, message: str) -> None:
    _message_dialog(parent, title, message)


def confirm_dialog(parent: QWidget, title: str, message: str) -> bool:
    """Show a scrollable Yes/No confirmation dialog."""
    dlg = ScrollDialog(title, parent)
    layout = dlg.scroll_layout()
    lbl = QLabel(message)
    lbl.setWordWrap(True)
    layout.addWidget(lbl)
    layout.addStretch()

    confirmed = [False]

    def on_yes() -> None:
        confirmed[0] = True
        dlg.accept()

    yes_btn = dlg.add_button(QDialogButtonBox.ButtonRole.YesRole, "Yes")
    yes_btn.clicked.connect(on_yes)
    no_btn = dlg.add_button(QDialogButtonBox.ButtonRole.NoRole, "No")
    no_btn.clicked.connect(dlg.reject)
    dlg.exec()
    return confirmed[0]


def _risk_label(level: RiskLevel) -> str:
    return level.value.capitalize()


def confirm_tweak_dialog(parent: QWidget, tweak: Tweak) -> bool:
    """Show tweak confirmation dialog. Returns True if user confirms."""
    dlg = ScrollDialog(f"Apply: {tweak.title}", parent)
    layout = dlg.scroll_layout()

    for text in (
        f"<b>{tweak.title}</b>",
        tweak.description,
        f"<b>Why use this?</b><br>{tweak.why_use}",
        f"<b>Risk level:</b> {_risk_label(tweak.risk_level)}",
        f"<b>Affected area:</b> {tweak.affected_area}",
        f"<b>How to undo:</b> {tweak.undo_instructions}",
    ):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

    badges: list[str] = []
    if tweak.requires_admin:
        badges.append("Needs Admin")
    if tweak.reversible:
        badges.append("Reversible")
    else:
        badges.append("Not Reversible")
    if tweak.opens_settings:
        badges.append("Opens Windows Settings")
    if tweak.changes_registry:
        badges.append("Changes Registry")
    if tweak.requires_restart:
        badges.append("Requires Restart")
    if tweak.requires_sign_out:
        badges.append("Requires Sign Out")
    layout.addWidget(QLabel("<b>Labels:</b> " + " · ".join(badges)))
    if tweak.notes:
        note = QLabel(f"<i>{tweak.notes}</i>")
        note.setWordWrap(True)
        layout.addWidget(note)
    layout.addStretch()

    confirmed = [False]

    def on_apply() -> None:
        confirmed[0] = True
        dlg.accept()

    apply_btn = dlg.add_button(QDialogButtonBox.ButtonRole.AcceptRole, "Apply")
    apply_btn.clicked.connect(on_apply)
    cancel_btn = dlg.add_button(QDialogButtonBox.ButtonRole.RejectRole, "Cancel")
    cancel_btn.clicked.connect(dlg.reject)

    dlg.exec()
    return confirmed[0]


def restore_point_prompt(parent: QWidget, on_open: Callable[[], None]) -> bool:
    """Ask user to create restore point before medium/high risk change."""
    dlg = ScrollDialog("Create a Restore Point First?", parent)
    layout = dlg.scroll_layout()
    lbl = QLabel(
        "This change is rated medium or high risk.\n\n"
        "We recommend creating a System Restore point before continuing. "
        "WinTuner will open System Protection settings — create a restore point "
        "manually, then return here."
    )
    lbl.setWordWrap(True)
    layout.addWidget(lbl)
    layout.addStretch()

    proceed = [False]

    def open_and_wait() -> None:
        on_open()
        proceed[0] = True
        dlg.accept()

    open_btn = dlg.add_button(QDialogButtonBox.ButtonRole.ActionRole, "Open System Protection")
    open_btn.clicked.connect(open_and_wait)
    skip_btn = dlg.add_button(QDialogButtonBox.ButtonRole.AcceptRole, "Continue Without")
    skip_btn.clicked.connect(lambda: (proceed.__setitem__(0, True), dlg.accept()))
    cancel_btn = dlg.add_button(QDialogButtonBox.ButtonRole.RejectRole, "Cancel")
    cancel_btn.clicked.connect(dlg.reject)

    dlg.exec()
    return proceed[0]
