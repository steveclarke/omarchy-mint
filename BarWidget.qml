import QtQuick
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "io.github.steveclarke.mint"
  readonly property var service: bar && bar.shell ? bar.shell.serviceFor(moduleName) : null
  readonly property bool opened: panelLoader.item ? panelLoader.item.opened : false
  readonly property bool popoutSwitchClosing: panelLoader.item ? panelLoader.item.popoutSwitchClosing : false
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight
  function inject() {
    if (panelLoader.item) {
      panelLoader.item.bar = bar;
      panelLoader.item.anchorItem = button;
      panelLoader.item.hostWidget = root;
    }
  }
  function open() {
    if (panelLoader.item)
      panelLoader.item.open();
  }
  function close() {
    if (panelLoader.item)
      panelLoader.item.close();
  }
  function toggle() {
    if (panelLoader.item)
      panelLoader.item.toggle();
  }
  function closeForPopoutSwitch() {
    if (panelLoader.item)
      panelLoader.item.closeForPopoutSwitch();
  }
  function pushSettings() {
    if (service && settings)
      service.entry = settings;
  }
  onSettingsChanged: pushSettings()
  onServiceChanged: pushSettings()
  onBarChanged: inject()
  Loader {
    id: panelLoader
    source: Qt.resolvedUrl("Panel.qml")
    visible: false
    onLoaded: {
      root.inject();
      Qt.callLater(root.inject);
    }
  }
  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    hasVisualContent: true
    fixedWidth: root.vertical ? -1 : Style.bar.iconCanvas + Style.space(16)
    fixedHeight: root.vertical ? Style.bar.iconCanvas + Style.space(12) : -1
    labelVisible: false
    tooltipText: "Mint · generate a password"
    Accessible.role: Accessible.Button
    Accessible.name: "Mint. Generate a password."
    Accessible.onPressAction: root.toggle()
    onPressed: function (b) {
      if (b === Qt.LeftButton)
        root.toggle();
    }
    Text {
      anchors.centerIn: parent
      textFormat: Text.PlainText
      text: "󰌆"
      font.family: button.fontFamily
      font.pixelSize: Style.bar.iconFont
      color: root.service && ["failed", "uncertain", "copy-failed"].indexOf(root.service.health) >= 0 ? Color.urgent : button.foreground
      opacity: root.service && (root.service.busy || root.service.health === "missing") ? 0.55 : 1
      renderType: Text.NativeRendering
    }
  }
}
