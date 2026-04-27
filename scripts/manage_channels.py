"""
TUI for managing config/channels.yaml
Keys:
  F5        – move selected channel up
  F6        – move selected channel down
  A         – add new channel (wizard)
  E         – edit selected channel
  D         – delete selected channel (with confirmation)
  S         – save to config/channels.yaml
  Q / Ctrl+C – quit (warns if unsaved changes)
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Grid, Vertical, Horizontal, ScrollableContainer
    from textual.screen import ModalScreen
    from textual.widgets import (
        Button,
        DataTable,
        Footer,
        Header,
        Input,
        Label,
        Select,
        Static,
    )
    from textual.reactive import reactive
except ImportError:
    sys.exit("textual is required: pip install textual")

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")

CHANNELS_PATH = "../channels.yaml"

AFFILIATIONS = [
    "independent",
    "fidesz-aligned",
    "tisza-aligned",
    "opposition",
]
DIRECTIONS = [
    "liberal",
    "centrist",
    "conservative",
    "far-right",
]

COLUMNS = [
    ("slug", "Slug", 22),
    ("display_name", "Display Name", 28),
    ("affiliation", "Affiliation", 18),
    ("direction", "Direction", 14),
    ("default_tags", "Default Tags", 22),
    ("id", "Channel ID", 26),
]


def load_channels(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("channels", [])


def save_channels(path: Path, channels: list[dict]) -> None:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["channels"] = channels
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def channel_row(ch: dict) -> tuple:
    tags = ", ".join(ch.get("default_tags") or [])
    return (
        ch.get("slug", ""),
        ch.get("display_name", ""),
        ch.get("affiliation", ""),
        ch.get("direction", ""),
        tags,
        ch.get("id", ""),
    )


# ── Confirmation dialog ────────────────────────────────────────────────────────

class ConfirmScreen(ModalScreen[bool]):
    CSS = """
    ConfirmScreen {
        align: center middle;
    }
    #dialog {
        width: 60;
        height: auto;
        border: thick $error 80%;
        background: $surface;
        padding: 1 2;
    }
    #buttons {
        margin-top: 1;
        align: center middle;
    }
    Button { margin: 0 1; }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self._message)
            with Horizontal(id="buttons"):
                yield Button("Yes", variant="error", id="yes")
                yield Button("No", variant="primary", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


# ── Channel edit / add form ────────────────────────────────────────────────────

class ChannelFormScreen(ModalScreen[dict | None]):
    CSS = """
    ChannelFormScreen {
        align: center middle;
    }
    #form-container {
        width: 72;
        height: auto;
        max-height: 90vh;
        border: thick $primary 80%;
        background: $surface;
        padding: 1 2;
    }
    .field-label {
        margin-top: 1;
        color: $text-muted;
    }
    Input { margin-bottom: 0; }
    Select { margin-bottom: 0; }
    #form-buttons {
        margin-top: 2;
        align: center middle;
    }
    Button { margin: 0 1; }
    #form-title {
        text-style: bold;
        margin-bottom: 1;
    }
    """

    def __init__(self, channel: dict | None = None, title: str = "Channel") -> None:
        super().__init__()
        self._channel = channel or {}
        self._title = title

    def compose(self) -> ComposeResult:
        ch = self._channel
        with ScrollableContainer(id="form-container"):
            yield Label(self._title, id="form-title")

            yield Label("Channel ID *", classes="field-label")
            yield Input(value=ch.get("id", ""), placeholder="UCxxxxxxxxxxxxxxxxxxxxxxxx", id="f-id")

            yield Label("Slug *", classes="field-label")
            yield Input(value=ch.get("slug", ""), placeholder="my-channel", id="f-slug")

            yield Label("Display Name *", classes="field-label")
            yield Input(value=ch.get("display_name", ""), placeholder="My Channel", id="f-display_name")

            yield Label("Affiliation", classes="field-label")
            yield Select(
                [(a, a) for a in AFFILIATIONS],
                value=ch.get("affiliation", AFFILIATIONS[0]),
                id="f-affiliation",
            )

            yield Label("Direction", classes="field-label")
            yield Select(
                [(d, d) for d in DIRECTIONS],
                value=ch.get("direction", DIRECTIONS[0]),
                id="f-direction",
            )

            yield Label("Default Tags (comma-separated)", classes="field-label")
            tags_str = ", ".join(ch.get("default_tags") or [])
            yield Input(value=tags_str, placeholder="közélet, interjú", id="f-default_tags")

            yield Label("Notes", classes="field-label")
            yield Input(value=ch.get("notes", ""), placeholder="Optional notes", id="f-notes")

            with Horizontal(id="form-buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return

        # Collect values
        def val(widget_id: str) -> str:
            return self.query_one(f"#{widget_id}", Input).value.strip()

        def sel(widget_id: str) -> str:
            w = self.query_one(f"#{widget_id}", Select)
            return str(w.value) if w.value is not None else ""

        channel_id = val("f-id")
        slug = val("f-slug")
        display_name = val("f-display_name")

        if not channel_id or not slug or not display_name:
            self.notify("Channel ID, Slug and Display Name are required.", severity="error")
            return

        tags_raw = val("f-default_tags")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

        notes = val("f-notes")

        result: dict = {
            "id": channel_id,
            "slug": slug,
            "display_name": display_name,
            "affiliation": sel("f-affiliation"),
            "direction": sel("f-direction"),
            "default_tags": tags,
        }
        if notes:
            result["notes"] = notes

        self.dismiss(result)


# ── Main app ───────────────────────────────────────────────────────────────────

class ChannelManagerApp(App):
    TITLE = "Channel Manager"
    CSS = """
    DataTable { height: 1fr; }
    #status-bar {
        height: 1;
        background: $primary-darken-2;
        color: $text;
        padding: 0 1;
    }
    """
    BINDINGS = [
        Binding("f5", "move_up", "Move Up"),
        Binding("f6", "move_down", "Move Down"),
        Binding("a", "add_channel", "Add"),
        Binding("e", "edit_channel", "Edit"),
        Binding("d", "delete_channel", "Delete"),
        Binding("s", "save", "Save"),
        Binding("q", "quit_app", "Quit"),
    ]

    dirty: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        super().__init__()
        self.channels: list[dict] = load_channels(CHANNELS_PATH)

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row", zebra_stripes=True)
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        for key, label, width in COLUMNS:
            table.add_column(label, width=width, key=key)
        self._refresh_table()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _refresh_table(self, keep_cursor: int | None = None) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for ch in self.channels:
            table.add_row(*channel_row(ch))
        if keep_cursor is not None:
            idx = max(0, min(keep_cursor, len(self.channels) - 1))
            table.move_cursor(row=idx)

    def _current_index(self) -> int:
        table = self.query_one(DataTable)
        return table.cursor_row

    def _set_dirty(self, value: bool = True) -> None:
        self.dirty = value
        status = self.query_one("#status-bar", Static)
        status.update("● Unsaved changes — press S to save" if value else "✓ All changes saved")

    # ── Actions ────────────────────────────────────────────────────────────────

    def action_move_up(self) -> None:
        idx = self._current_index()
        if idx <= 0:
            return
        self.channels[idx], self.channels[idx - 1] = self.channels[idx - 1], self.channels[idx]
        self._refresh_table(keep_cursor=idx - 1)
        self._set_dirty()

    def action_move_down(self) -> None:
        idx = self._current_index()
        if idx >= len(self.channels) - 1:
            return
        self.channels[idx], self.channels[idx + 1] = self.channels[idx + 1], self.channels[idx]
        self._refresh_table(keep_cursor=idx + 1)
        self._set_dirty()

    def action_add_channel(self) -> None:
        def handle_result(result: dict | None) -> None:
            if result is None:
                return
            self.channels.append(result)
            self._refresh_table(keep_cursor=len(self.channels) - 1)
            self._set_dirty()

        self.push_screen(ChannelFormScreen(title="Add New Channel"), handle_result)

    def action_edit_channel(self) -> None:
        idx = self._current_index()
        if not self.channels:
            return
        ch = self.channels[idx]

        def handle_result(result: dict | None) -> None:
            if result is None:
                return
            self.channels[idx] = result
            self._refresh_table(keep_cursor=idx)
            self._set_dirty()

        self.push_screen(ChannelFormScreen(channel=ch, title=f"Edit: {ch.get('display_name', '')}"), handle_result)

    def action_delete_channel(self) -> None:
        idx = self._current_index()
        if not self.channels:
            return
        ch = self.channels[idx]
        name = ch.get("display_name", ch.get("slug", "?"))

        def handle_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            self.channels.pop(idx)
            self._refresh_table(keep_cursor=idx)
            self._set_dirty()

        self.push_screen(ConfirmScreen(f"Delete channel '{name}'?"), handle_confirm)

    def action_save(self) -> None:
        try:
            save_channels(CHANNELS_PATH, self.channels)
            self._set_dirty(False)
            self.notify("Saved successfully.", severity="information")
        except Exception as exc:
            self.notify(f"Save failed: {exc}", severity="error")

    def action_quit_app(self) -> None:
        if not self.dirty:
            self.exit()
            return

        def handle_confirm(confirmed: bool) -> None:
            if confirmed:
                self.exit()

        self.push_screen(ConfirmScreen("You have unsaved changes. Quit anyway?"), handle_confirm)


if __name__ == "__main__":
    ChannelManagerApp().run()
