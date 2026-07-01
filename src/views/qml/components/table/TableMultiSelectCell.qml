import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

Item {
    id: root

    property var options: []
    property var selectedValues: []
    property string displayText: "---"
    property int rowHeight: 40
    property color popupBackgroundColor: "#151e29"
    property color popupBorderColor: "#2B3A52"

    signal valueToggled(var value, bool checked)

    anchors.fill: parent

    function isSelected(value) {
        for (var i = 0; i < root.selectedValues.length; i += 1) {
            if (String(root.selectedValues[i]) === String(value)) {
                return true;
            }
        }
        return false;
    }

    Item {
        id: multiSelectHost
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        height: Math.min(36, root.rowHeight - 8)

        BaseButton {
            anchors.fill: parent
            text: root.displayText
            variant: "outline"
            radius: 10
            font.pixelSize: 13
            onClicked: multiSelectPopup.open()
        }

        Popup {
            id: multiSelectPopup
            y: multiSelectHost.height + 4
            width: multiSelectHost.width
            modal: false
            focus: true
            padding: 8
            closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

            background: Rectangle {
                color: root.popupBackgroundColor
                radius: 8
                border.color: root.popupBorderColor
                border.width: 1
            }

            contentItem: ColumnLayout {
                spacing: 4

                Repeater {
                    model: root.options

                    delegate: CheckBox {
                        Layout.fillWidth: true
                        text: modelData
                        checked: root.isSelected(modelData)
                        onToggled: root.valueToggled(modelData, checked)
                    }
                }
            }
        }
    }
}
