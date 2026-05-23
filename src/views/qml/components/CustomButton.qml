import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control

    // =========================
    // Icon
    // =========================

    property url iconSource: ""
    property int iconSize: 18
    property int contentSpacing: 8

    // =========================
    // Visibility
    // =========================

    property bool showIcon: iconSource !== ""
    property bool showText: text !== ""

    // =========================
    // Colors
    // =========================

    property color backgroundColor: "#005ec3"
    property color hoverBackgroundColor: "#0069d9"
    property color pressedBackgroundColor: "#0051a8"
    property color foregroundColor: "#ffffff"
    property color borderColor: "transparent"

    // =========================
    // Style
    // =========================

    property int radius: 12

    // =========================
    // Layout
    // =========================

    implicitHeight: 44

    implicitWidth: Math.max(96, contentRow.implicitWidth + leftPadding + rightPadding)

    hoverEnabled: true

    // =========================
    // Typography
    // =========================

    // font.family: "Segoe UI"
    font.pixelSize: 14
    font.weight: Font.Bold

    // =========================
    // Content
    // =========================

    contentItem: Item {

        implicitWidth: contentRow.implicitWidth
        implicitHeight: contentRow.implicitHeight

        scale: control.down ? 0.97 : control.hovered ? 1.02 : 1.0

        Behavior on scale {
            NumberAnimation {
                duration: 100
                easing.type: Easing.OutCubic
            }
        }

        Row {
            id: contentRow

            anchors.centerIn: parent

            spacing: control.contentSpacing

            Image {

                visible: control.showIcon

                anchors.verticalCenter: parent.verticalCenter

                source: control.iconSource

                width: control.iconSize
                height: control.iconSize

                fillMode: Image.PreserveAspectFit

                smooth: true
                mipmap: true
            }

            Text {

                visible: control.showText

                anchors.verticalCenter: parent.verticalCenter

                text: control.text

                color: control.foregroundColor

                font.family: control.font.family
                font.pixelSize: control.font.pixelSize
                font.weight: control.font.weight

                elide: Text.ElideRight
            }
        }
    }

    // =========================
    // Background
    // =========================

    background: Rectangle {

        radius: control.radius

        border.color: control.borderColor
        border.width: control.borderColor === "transparent" ? 0 : 1

        color: control.down ? control.pressedBackgroundColor : control.hovered ? control.hoverBackgroundColor : control.backgroundColor

        scale: control.down ? 0.97 : control.hovered ? 1.02 : 1.0

        Behavior on scale {
            NumberAnimation {
                duration: 100
                easing.type: Easing.OutCubic
            }
        }

        Behavior on color {

            ColorAnimation {
                duration: 120
            }
        }
    }
}
