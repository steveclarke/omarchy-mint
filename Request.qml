import QtQuick
import Quickshell.Io
import "Model.js" as Model

Item {
  id: root
  property var payload: ({})
  property bool accepting: false
  property string buffer: ""
  property int errorBytes: 0
  signal completed(var result)
  function start(request) {
    payload = request;
    accepting = true;
    deadline.start();
    worker.running = true;
  }
  function cancel() {
    accepting = false;
    buffer = "";
    payload = ({});
    worker.running = false;
    deadline.stop();
  }
  function reject() {
    if (!accepting)
      return;
    cancel();
    completed({
      ok: false,
      kind: "timeout",
      error: "The request did not finish. Check 1Password before repeating a save."
    });
  }
  Component.onDestruction: cancel()
  Timer {
    id: deadline
    // Bridge: 5 s input + 120 s save + 35 s copy, with cleanup margin.
    interval: 170000
    onTriggered: root.reject()
  }
  Process {
    id: worker
    command: ["/usr/bin/python3", "-I", "-S", decodeURIComponent(Qt.resolvedUrl("bin/mint-bridge").toString().replace(/^file:\/\//, ""))]
    stdinEnabled: true
    onStarted: {
      write(JSON.stringify(root.payload));
      stdinEnabled = false;
      root.payload = ({});
    }
    stdout: SplitParser {
      splitMarker: ""
      onRead: function (chunk) {
        if (!root.accepting)
          return;
        if (root.buffer.length + chunk.length > 65536) {
          root.reject();
          return;
        }
        root.buffer += chunk;
      }
    }
    stderr: SplitParser {
      splitMarker: ""
      onRead: function (chunk) {
        root.errorBytes += chunk.length;
        if (root.errorBytes > 8192)
          root.reject();
      }
    }
    onExited: function (code) {
      deadline.stop();
      if (!root.accepting)
        return;
      root.accepting = false;
      var result;
      try {
        result = Model.parse(root.buffer);
      } catch (e) {
        result = {
          ok: false,
          kind: "invalid",
          error: "Mint did not return a valid response. Try again."
        };
      }
      root.buffer = "";
      root.payload = ({});
      root.completed(result);
    }
  }
}
