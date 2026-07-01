import QtQuick 2.15
import ".."

Item {
    id: root

    property var options: []
    property string currentValue: ""
    property int rowHeight: 40
    property color textColor: "#ffffff"
    property color backgroundColor: "#101923"
    property color borderColor: "#2B3A52"
    property color popupBackgroundColor: "#151e29"

    signal valueSelected(var value)

    anchors.fill: parent

    function optionIndex(value) {
        for (var i = 0; i < root.options.length; i += 1) {
            if (String(root.options[i]) === String(value)) {
                return i;
            }
        }
        return 0;
    }

    CustomComboBox {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        height: Math.min(36, root.rowHeight - 8)
        model: root.options
        currentIndex: root.optionIndex(root.currentValue)
        textColor: root.textColor
        backgroundColor: root.backgroundColor
        backgroundHoverColor: "#172231"
        borderColor: root.borderColor
        popupBackgroundColor: root.popupBackgroundColor
        popupBorderColor: root.borderColor
        delegateTextColor: root.textColor
        delegateHoverColor: "#172231"
        delegateHighlightedColor: "#1b2735"
        horAlignment: Text.AlignHCenter
        onActivated: root.valueSelected(currentText)
    }
}
