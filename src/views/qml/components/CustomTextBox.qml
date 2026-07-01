import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TextField {
    id: root

    Layout.fillWidth: true
    Layout.preferredHeight: 45

    property color textColor: "#ffffff"
    property color backgroundColor: "#151e29"
    property color backgroundHoverColor: "#1b2735"
    property color backgroundDisabledColor: "#101923"

    property color borderColor: "#2B3A52"
    property color borderFocusColor: "#005ec3"
    property color borderDisabledColor: "#233043"

    font.pixelSize: 16

    color: root.enabled ? root.textColor : "#70839b"
    placeholderTextColor: "#70839b"

    leftPadding: 18
    rightPadding: 18

    verticalAlignment: TextInput.AlignVCenter

    selectByMouse: true

    onAccepted: {
        root.focus = false;
    }

    background: Rectangle {
        color: !root.enabled ? root.backgroundDisabledColor : root.hovered ? root.backgroundHoverColor : root.backgroundColor
        radius: 10
        border.width: 2
        border.color: !root.enabled ? root.borderDisabledColor : root.focus ? root.borderFocusColor : root.borderColor

        Behavior on opacity {
            NumberAnimation {
                duration: 140
            }
        }

        Behavior on border.color {
            ColorAnimation {
                duration: 120
            }
        }
        Behavior on color {
            ColorAnimation {
                duration: 120
            }
        }
    }
}
