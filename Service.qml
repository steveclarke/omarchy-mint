import QtQuick
import Quickshell.Io
import "Model.js" as Model

Item {
  id: root
  visible: false
  property var shell: null
  property var manifest: null
  property var entry: ({})
  readonly property var prefs: Model.preferences(entry)
  property string health: "idle"
  property string message: ""
  property string secret: ""
  property string ruleSummary: ""
  property int length: 24
  property real bits: 0
  property int wantedLength: 24
  property var classes: ["upper", "lower", "digits", "symbols"]
  property string preset: ""
  property string symbols: "!@#$%^&*-_=+?"
  property bool noAmbiguous: false
  property var presets: [
    {
      value: "",
      label: "Custom"
    }
  ]
  property var vaults: []
  property var activeRequest: null
  property var panelOwner: null
  property int generation: 0
  property bool busy: false
  property string action: ""
  property bool demo: false
  property bool saveUncertain: false
  property string savedTitle: ""
  property string savedVault: ""
  function savePreferences(values) {
    if (!shell)
      return;
    var merged = Object.assign({}, entry, values, {
      id: "io.github.steveclarke.mint"
    });
    if (shell.updateEntryInline("io.github.steveclarke.mint", merged))
      entry = merged;
  }
  function rules() {
    if (preset)
      return {
        preset: preset,
        clearAfter: prefs.clearAfter
      };
    return {
      length: wantedLength,
      classes: classes,
      preset: preset,
      symbols: symbols,
      noAmbiguous: noAmbiguous,
      clearAfter: prefs.clearAfter
    };
  }
  function discard() {
    secret = "";
    bits = 0;
    ruleSummary = "";
  }
  function cancel() {
    if (busy && action === "save") {
      saveUncertain = true;
      message = "A login may have been saved. Check 1Password before creating another.";
      health = "uncertain";
    }
    generation++;
    if (activeRequest) {
      activeRequest.cancel();
      activeRequest.destroy();
      activeRequest = null;
    }
    busy = false;
  }
  function closePanel(owner) {
    if (panelOwner !== owner)
      return;
    panelOwner = null;
    cancel();
    discard();
  }
  function request(op, extra) {
    if (demo || busy || (op === "save" && saveUncertain))
      return;
    busy = true;
    action = op;
    message = "";
    generation++;
    var token = generation;
    var task = requestFactory.createObject(root);
    activeRequest = task;
    task.completed.connect(function (result) {
      if (token !== root.generation) {
        task.destroy();
        return;
      }
      root.busy = false;
      root.activeRequest = null;
      if (!result.ok) {
        root.health = result.kind === "missing" ? "missing" : "failed";
        root.message = result.error || "Mint could not finish. Try again.";
        if (op === "save") {
          root.saveUncertain = true;
          root.health = "uncertain";
          root.message = "The save did not confirm. Check 1Password before creating another login.";
        }
      } else {
        try {
          var data = result.data;
          if (op === "generate" || op === "save") {
            var value = Model.password(data);
            root.secret = value.password;
            root.length = value.length;
            root.bits = value.entropy_bits;
            root.ruleSummary = value.rule;
            root.health = op === "save" ? "saved" : "ready";
            if (op === "generate" && root.presets.length === 1)
              Qt.callLater(function () {
                root.request("presets");
              });
            if (op === "save") {
              root.savedTitle = Model.clean(data.title, 100);
              root.savedVault = Model.clean(data.vault, 100);
            }
          }
          if (op === "copy") {
            root.health = "copied";
            root.message = root.prefs.clearAfter ? "Copied. Clears after " + root.prefs.clearAfter + " seconds if unchanged." : "Copied. Automatic clearing is disabled.";
          }
          if (op === "save")
            root.message = data.copied === false ? "Saved. Copy failed; use Copy to try again." : "Saved to 1Password.";
          if (op === "presets")
            root.presets = [
              {
                value: "",
                label: "Custom"
              }
            ].concat(Model.options(data, "preset"));
          if (op === "vaults")
            root.vaults = Model.options(data, "vault");
        } catch (e) {
          root.health = "failed";
          root.message = "Mint returned an unreadable response. Try again.";
          if (op === "save")
            root.saveUncertain = true;
        }
      }
      task.destroy();
    });
    var payload = op === "generate" || op === "save" ? rules() : ({});
    if (op === "generate")
      delete payload.clearAfter;
    if (op === "copy")
      payload.clearAfter = prefs.clearAfter;
    task.start(Object.assign(payload, extra || {}, {
      operation: op
    }));
  }
  function generate() {
    if (busy || demo)
      return;
    discard();
    health = "generating";
    request("generate");
  }
  function copy() {
    if (secret)
      request("copy", {
        password: secret
      });
  }
  function save(title, vault, url, username) {
    request("save", {
      title: title,
      vault: vault,
      url: url,
      username: username
    });
  }
  function setClass(name) {
    var next = classes.slice();
    var i = next.indexOf(name);
    if (i >= 0)
      next.splice(i, 1);
    else
      next.push(name);
    classes = next;
    preset = "";
    generate();
  }
  function openPanel(owner) {
    var previous = panelOwner;
    panelOwner = owner;
    if (previous && previous !== owner)
      previous.close();
    if (demo || busy || saveUncertain)
      return;
    preset = prefs.defaultPreset;
    generate();
  }
  function acknowledgeSave() {
    saveUncertain = false;
    message = "";
    health = secret ? "ready" : "idle";
  }
  function debugState(name) {
    if (["off", "ready", "copied", "saved", "copy-failed", "missing", "failed", "uncertain", "generating", "saving", "vaults"].indexOf(name) < 0)
      return;
    cancel();
    discard();
    demo = name !== "off";
    saveUncertain = false;
    if (!demo) {
      health = "idle";
      message = "";
      return;
    }
    health = name;
    wantedLength = 24;
    length = 24;
    bits = 141;
    ruleSummary = "24 characters, four classes";
    if (["ready", "copied", "saved", "copy-failed"].indexOf(name) >= 0)
      secret = "Example-Only-7!SampleText";
    message = name === "failed" ? "No password fits these rules. Switch on a character type." : name === "missing" ? "Install Mint, then reopen this panel." : name === "uncertain" ? "A login may have been saved. Check 1Password before creating another." : name === "copy-failed" ? "The clipboard did not take it. Try Copy again." : "";
    busy = ["generating", "saving", "vaults"].indexOf(name) >= 0;
    action = name === "saving" ? "save" : name === "vaults" ? "vaults" : "generate";
    saveUncertain = name === "uncertain";
    vaults = [
      {
        value: "example",
        label: "Example vault"
      }
    ];
  }
  Component {
    id: requestFactory
    Request {}
  }
  IpcHandler {
    target: "io.github.steveclarke.mint"
    function debugState(name: string): void {
      root.debugState(name);
    }
    function status(): string {
      return JSON.stringify({
        health: root.health,
        busy: root.busy,
        demo: root.demo,
        hasPassword: root.secret.length > 0
      });
    }
  }
}
