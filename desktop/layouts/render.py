"""Generate native desktop scripts without executing them."""

from __future__ import annotations

import json
import shlex

from .engine import layout_plan


def render_xfce() -> str:
    commands = [
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels", "--create", "-t", "int", "-s", "1", "-t", "int", "-s", "2"],
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-1/position", "--create", "-t", "string", "-s", "p=6;x=0;y=0"],
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-1/size", "--create", "-t", "int", "-s", "30"],
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-2/position", "--create", "-t", "string", "-s", "p=10;x=0;y=0"],
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-2/size", "--create", "-t", "int", "-s", "48"],
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-2/length", "--create", "-t", "int", "-s", "45"],
    ]

    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Generated LIFE Flow XFCE configuration.",
        "# Preview only until tested against the target XFCE version.",
        "# Applying this changes existing panel configuration.",
        "",
    ]

    for command in commands:
        lines.append(shlex.join(command))

    return "\n".join(lines) + "\n"


def render_plasma() -> str:
    plan = layout_plan("life-standard", "flow")

    top_widgets = json.dumps(
        plan["top_panel"]["widgets"]
    )
    dock_widgets = json.dumps(
        plan["dock"]["widgets"]
    )

    return f"""// LIFE OS Flow layout for KDE Plasma.
// Generated configuration script.
// Apply only through a supported Plasma scripting interface.

var top = new Panel();
top.location = "top";
top.height = 32;

var topWidgets = {top_widgets};

for (var i = 0; i < topWidgets.length; i++) {{
    top.addWidget(topWidgets[i]);
}}

var dock = new Panel();
dock.location = "bottom";
dock.height = 52;

var dockWidgets = {dock_widgets};

for (var j = 0; j < dockWidgets.length; j++) {{
    dock.addWidget(dockWidgets[j]);
}}
"""


def render(edition: str, layout: str) -> str:
    layout_plan(edition, layout)

    if edition == "life-lite":
        return render_xfce()

    return render_plasma()
