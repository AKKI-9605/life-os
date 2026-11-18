// LIFE OS Flow layout for KDE Plasma.
// Generated configuration script.
// Apply only through a supported Plasma scripting interface.

var top = new Panel();
top.location = "top";
top.height = 32;

var topWidgets = ["org.kde.plasma.kickoff", "org.kde.plasma.panelspacer", "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock"];

for (var i = 0; i < topWidgets.length; i++) {
    top.addWidget(topWidgets[i]);
}

var dock = new Panel();
dock.location = "bottom";
dock.height = 52;

var dockWidgets = ["org.kde.plasma.icontasks"];

for (var j = 0; j < dockWidgets.length; j++) {
    dock.addWidget(dockWidgets[j]);
}
