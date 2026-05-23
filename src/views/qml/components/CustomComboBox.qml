import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ComboBox {
    id: control

    enabled: true

    Layout.fillWidth: true
    Layout.preferredHeight: 45

    implicitHeight: 45

    leftPadding: 20
    rightPadding: 42

    font.pixelSize: 14

    property int radiusValue: 10

    property color textColor: "#ffffff"
    property color backgroundColor: "#151e29"
    property color backgroundHoverColor: "#1b2735"
    property color backgroundDisabledColor: "#101923"

    property color borderColor: "#2B3A52"
    property color borderFocusColor: "#005ec3"
    property color borderDisabledColor: "#233043"

    property int borderWidthValue: 2

    property url indicatorSource: "qrc:/icon_arrow_down"

    property color popupBackgroundColor: "#151e29"
    property color popupBorderColor: "#2B3A52"
    property color delegateTextColor: "#ffffff"
    property color delegateHoverColor: "#172231"
    property color delegateHighlightedColor: "#1b2735"
    property int  horAlignment: Text.AlignLeft
    property Component popupDelegate

    contentItem: Text {
        text: control.displayText
        color: control.enabled ? control.textColor : "#70839b"
        font: control.font
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: control.horAlignment
        elide: Text.ElideRight
    }

    indicator: Image {
        width: 16
        height: 16
        x: control.width - width - 18
        y: (control.height - height) / 2
        source: control.indicatorSource
        smooth: true
        mipmap: true
        opacity: control.enabled ? 1.0 : 0.45
    }

    background: Rectangle {
        radius: control.radiusValue
        color: !control.enabled ? control.backgroundDisabledColor : control.hovered ? control.backgroundHoverColor : control.backgroundColor

        border.width: control.borderWidthValue
        border.color: !control.enabled ? control.borderDisabledColor : control.visualFocus ? control.borderFocusColor : control.borderColor

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

    popup: Popup {
        y: control.height + 4
        width: control.width
        implicitHeight: contentItem.implicitHeight
        padding: 0

        background: Rectangle {
            color: control.popupBackgroundColor
            radius: control.radiusValue
            border.color: control.popupBorderColor
            border.width: 1
        }

        contentItem: ListView {
            clip: true
            implicitHeight: Math.min(contentHeight, 240) + 5

            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex

            ScrollIndicator.vertical: ScrollIndicator {}
        }
    }
    delegate: popupDelegate ? popupDelegate : defaultDelegate
    
    Component {
        id: defaultDelegate

        ItemDelegate {
            id: itemDelegate
            width: control.width
            height: 42
            contentItem: Text {
                text: modelData
                color: control.delegateTextColor
                font: control.font
                verticalAlignment: Text.AlignVCenter
                leftPadding: 18
                rightPadding: 18
                elide: Text.ElideRight
            }
            background: Rectangle {
                radius: 10
                color: itemDelegate.highlighted ? control.delegateHighlightedColor : itemDelegate.hovered ? control.delegateHoverColor : "transparent"
            }
        }
    }
}
