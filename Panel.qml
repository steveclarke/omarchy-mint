pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as Controls
import Quickshell
import qs.Commons
import qs.Ui
import qs.Ui as Ui
import "Model.js" as Model
Panel {
  id:root
  moduleName:"io.github.steveclarke.mint"
  manageIpc:false
  property var anchorItem:null
  property var hostWidget:null
  readonly property var service:bar && bar.shell ? bar.shell.serviceFor(moduleName) : null
  property string page:"main"
  property bool revealed:false
  readonly property bool busy:service ? service.busy : false
  readonly property string health:service ? service.health : "missing"
  readonly property color ink:Color.popups.text
  readonly property color dim:Qt.darker(ink,1.35)
  function back() {page="main";revealed=false;keys.forceActiveFocus()}
  function savePage() {page="save";revealed=false;if(service && !service.demo) service.request("vaults");Qt.callLater(titleField.forceActiveFocus)}
  function submit() {if(service && titleField.text.trim() && vault.value && !service.saveUncertain) service.save(titleField.text.trim(),vault.value,urlField.text,usernameField.text)}
  onOpenedChanged: {
    revealed=false;page="main"
    if(service) {if(opened) service.openPanel();else service.closePanel()}
  }
  component PlainLabel: Text {textFormat:Text.PlainText;color:root.ink;font.family:Style.font.family;font.pixelSize:Style.font.body;wrapMode:Text.Wrap}
  component Action: Ui.Button {focusable:true;bordered:true;foreground:root.ink;opacity:enabled?1:0.4}
  KeyboardPanel {
    id:popup
    anchorItem:root.anchorItem
    bar:root.bar
    owner:root.hostWidget || root;open:root.opened
    contentWidth:fittedContentWidth(Style.space(460))
    contentHeight:fittedContentHeight(content.implicitHeight)
    focusTarget:keys
    Item {
      id:keys;anchors.fill:parent;focus:true
      Keys.onPressed:function(event){
        if(event.key===Qt.Key_Escape) {if(root.page!=="main") root.back();else root.close();event.accepted=true}
        else if(root.page==="main" && event.modifiers & Qt.ControlModifier && event.key===Qt.Key_R) {if(root.service) root.service.generate();event.accepted=true}
        else if(root.page==="main" && event.modifiers & Qt.ControlModifier && event.key===Qt.Key_S) {root.savePage();event.accepted=true}
        else if(root.page==="main" && event.key===Qt.Key_Return && keys.activeFocus) {if(root.service) root.service.copy();event.accepted=true}
        else if(root.page==="main" && event.key===Qt.Key_V && keys.activeFocus) {root.revealed=!root.revealed;event.accepted=true}
      }
      Controls.ScrollView {
        anchors.fill:parent;clip:true;contentWidth:availableWidth
        Column {
          id:content;width:parent.width;spacing:Style.space(14)
          PanelHero {
            foreground:root.ink
            title:root.page==="settings" ? "Mint settings" : root.page==="save" ? (root.health==="saved"?"Saved to 1Password":"Save new password") : root.health==="missing"?"Install Mint":root.health==="generating"?"Making a password…":root.health==="copied"?"Copied":root.health==="saved"?"Saved to 1Password":"New password"
            meta:root.service && root.service.demo ? "Preview · actions disabled" : root.busy ? (root.service.action==="save"?"Approve in 1Password if asked":"Working…") : "Mint · password generator"
            iconComponent:Component {PlainLabel {text:"󰌆";font.pixelSize:Style.font.display;color:root.health==="failed"?Color.urgent:root.ink}}
            trailingControl:Component {Ui.PanelActionButton {iconText:root.page==="main"?"󰒓":"󰅁";foreground:root.ink;tooltipText:root.page==="main"?"Settings":"Back";onClicked:{if(root.page==="main") root.page="settings";else root.back()}}}
          }
          Rectangle {
            width:parent.width;height:notice.implicitHeight+Style.space(20);visible:notice.text!==""
            color:"transparent";border.width:1;border.color:root.health==="saved"?Color.accent:Color.urgent
            PlainLabel {id:notice;x:Style.space(10);y:x;width:parent.width-2*x;text:root.service?root.service.message:"Install Mint, then reopen this panel."}
          }
          Rectangle {
            visible:root.page==="main" && root.service && !!root.service.secret
            width:parent.width;height:passwordColumn.implicitHeight+Style.space(24)
            color:Style.selectedFillFor(root.ink,Color.accent)
            Column {
              id:passwordColumn;x:Style.space(12);y:x;width:parent.width-2*x;spacing:Style.space(10)
              Row {
                width:parent.width;spacing:Style.space(8)
                PlainLabel {width:parent.width-eye.width-parent.spacing; text:root.revealed && root.service ? root.service.secret : "••••••••••••••••";font.pixelSize:Style.font.heading;maximumLineCount:4;elide:Text.ElideRight;wrapMode:Text.WrapAnywhere;Accessible.name:"Generated password"}
                Action {id:eye;text:root.revealed?"Hide":"Show";onClicked:root.revealed=!root.revealed;enabled:!root.busy}
              }
              PlainLabel {width:parent.width;font.pixelSize:Style.font.caption;color:root.dim;text:root.service?root.service.length+" characters · "+root.service.bits.toFixed(1)+" bits":""}
            }
          }
          Column {
            width:parent.width;spacing:Style.space(12);visible:root.page==="main"
            enabled:!root.busy && root.service && !root.service.demo
            PanelSeparator {width:parent.width}
            PanelSectionHeader {text:"Password rules";foreground:root.ink}
            Row {
              width:parent.width;spacing:Style.space(12)
              PlainLabel {text:"Length";anchors.verticalCenter:parent.verticalCenter;width:Style.space(65)}
              PanelSlider {width:parent.width-lengthField.width-Style.space(89);minimum:4;maximum:64;step:1;integer:true;value:root.service?Math.min(root.service.wantedLength,64):24;bar:root.bar;onReleased:function(v){root.service.wantedLength=Math.round(v);root.service.preset="";root.service.generate()}}
              Ui.TextField {id:lengthField;width:Style.space(70);maximumLength:4;validator:IntValidator {bottom:1;top:4096} text:root.service?String(root.service.wantedLength):"24";onEditingFinished:{if(acceptableInput && root.service && Number(text)!==root.service.wantedLength){root.service.wantedLength=Number(text);root.service.preset="";root.service.generate()}}}
            }
            Row {
              width:parent.width;spacing:Style.space(6)
              Repeater {model:[{name:"upper",label:"A–Z"},{name:"lower",label:"a–z"},{name:"digits",label:"0–9"},{name:"symbols",label:"!#$"}]
                Action {required property var modelData;width:(content.width-Style.space(18))/4;text:modelData.label;selected:root.service && root.service.classes.indexOf(modelData.name)>=0;onClicked:root.service.setClass(modelData.name)}
              }
            }
            Ui.Dropdown {width:parent.width;label:"SITE RULE";value:root.service?root.service.preset:"";options:root.service?root.service.presets:[];onChanged:function(v){root.service.preset=v;root.service.generate()};onHovered:function(h){if(h && root.service && root.service.presets.length===1 && !root.service.busy) root.service.request("presets")}}
            Row {
              width:parent.width;spacing:Style.space(10)
              PlainLabel {text:"Allowed symbols";width:Style.space(130);anchors.verticalCenter:parent.verticalCenter}
              Ui.TextField {width:parent.width-Style.space(140);maximumLength:128;text:root.service?root.service.symbols:"";onEditingFinished:{if(root.service && text!==root.service.symbols){root.service.symbols=text;root.service.preset="";root.service.generate()}}}
            }
            Action {text:"Exclude look-alike characters";selected:root.service && root.service.noAmbiguous;onClicked:{root.service.noAmbiguous=!root.service.noAmbiguous;root.service.generate()}}
            PlainLabel {width:parent.width;font.pixelSize:Style.font.caption;color:root.dim;text:root.service?root.service.ruleSummary:""}
            PanelSeparator {width:parent.width}
          }
          Flow {
            width:parent.width;spacing:Style.space(8);visible:root.page==="main"
            Action {text:"New";enabled:!root.busy && root.service && !root.service.demo;onClicked:root.service.generate()}
            Action {text:"Copy";enabled:!root.busy && root.service && !!root.service.secret && !root.service.demo;onClicked:root.service.copy()}
            Action {text:"Save new…";enabled:!root.busy && root.service && !root.service.demo;onClicked:root.savePage()}
          }
          Column {
            width:parent.width;spacing:Style.space(10);visible:root.page==="save"
            PlainLabel {width:parent.width;text:"Generates a different password using these rules.";color:root.dim}
            PlainLabel {text:"Title"}
            Ui.TextField {id:titleField;width:parent.width;maximumLength:120;placeholderText:"Website or app name";enabled:!root.busy}
            Ui.Dropdown {id:vault;width:parent.width;label:"VAULT";options:root.service?root.service.vaults:[];value:root.service?(root.service.prefs.defaultVault || (root.service.vaults.length?root.service.vaults[0].value:"")):"";enabled:!root.busy;onChanged:function(v){value=v}}
            PlainLabel {text:"Website (optional)"}
            Ui.TextField {id:urlField;width:parent.width;maximumLength:2048;placeholderText:"https://example.com";enabled:!root.busy}
            PlainLabel {text:"Username (optional)"}
            Ui.TextField {id:usernameField;width:parent.width;maximumLength:120;enabled:!root.busy}
            Flow {
              width:parent.width;spacing:Style.space(8)
              Action {text:root.busy?"Cancel":"Back";onClicked:{if(root.busy) root.service.cancel();root.back()}}
              Action {text:root.busy && root.service.action==="save"?"Saving…":"Generate and save";enabled:!root.busy && root.service && !root.service.demo && !root.service.saveUncertain && !!titleField.text.trim() && !!vault.value && root.health!=="saved";onClicked:root.submit()}
              Action {text:"Reload vaults";enabled:!root.busy && root.service && !root.service.demo;onClicked:root.service.request("vaults")}
              Action {text:"Checked 1Password";visible:root.service && root.service.saveUncertain;enabled:!root.busy && root.service && !root.service.demo;onClicked:root.service.acknowledgeSave()}
            }
          }
          Column {
            width:parent.width;spacing:Style.space(10);visible:root.page==="settings"
            PlainLabel {width:parent.width;text:"Clipboard lifetime in seconds. Zero disables clearing."}
            Ui.TextField {width:parent.width;maximumLength:4;validator:IntValidator {bottom:0;top:3600} text:root.service?String(root.service.prefs.clearAfter):"45";onEditingFinished:if(acceptableInput && root.service && !root.service.demo)root.service.savePreferences({clearAfter:Number(text)})}
            PlainLabel {text:"Default site rule"}
            Ui.TextField {width:parent.width;maximumLength:80;text:root.service?root.service.prefs.defaultPreset:"";onEditingFinished:if(root.service && !root.service.demo)root.service.savePreferences({defaultPreset:text})}
            PlainLabel {text:"Default vault name or ID"}
            Ui.TextField {width:parent.width;maximumLength:120;text:root.service?root.service.prefs.defaultVault:"";onEditingFinished:if(root.service && !root.service.demo)root.service.savePreferences({defaultVault:text})}
            PlainLabel {width:parent.width;color:root.dim;text:"Passwords stay hidden until Show. Closing the panel removes the displayed password."}
          }
          PlainLabel {width:parent.width;visible:root.page==="main";font.pixelSize:Style.font.caption;color:root.dim;text:"enter copy · ctrl+r new · ctrl+s save · esc close"}
        }
      }
    }
  }
}
