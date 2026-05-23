import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    property string textValue: ""
    property string inputMode: "text"
    property int rowHeight: 40
    property color textColor: "#ffffff"
    property color backgroundColor: "#101923"
    property color borderColor: "#2B3A52"

    signal editorFocused()
    signal editorBlurred()
    signal valueCommitted(var value)

    anchors.fill: parent

    TextField {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        height: Math.min(36, root.rowHeight - 8)
        text: root.textValue
        inputMethodHints: root.inputMode === "digit" ? Qt.ImhDigitsOnly : Qt.ImhNone
        selectByMouse: true
        horizontalAlignment: TextInput.AlignHCenter
        color: root.textColor
        onActiveFocusChanged: activeFocus ? root.editorFocused() : root.editorBlurred()
        onEditingFinished: root.valueCommitted(text)
        background: Rectangle {
            color: root.backgroundColor
            radius: 6
            border.color: root.borderColor
            border.width: 1
        }
    }
}
