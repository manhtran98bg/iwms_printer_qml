import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control

    property string variant: "primary"
    property double radius: 2
    implicitHeight: 44
    implicitWidth: Math.max(96, contentItem.implicitWidth + leftPadding + rightPadding)
    hoverEnabled: true
    font.pixelSize: 14
    font.weight: Font.Bold

    function backgroundColor() {
        if (!enabled) {
            return "#cbd5e1"
        }
        if (variant === "danger") {
            return down ? "#b91c1c" : hovered ? "#c82333" : "#dc3545"
        }
        if (variant === "secondary") {
            return down ? "#123A62" : hovered ? "#174C7D" : "#1B5D96"
        }
        if (variant === "outline" || variant === "ghost") {
            return down ? "#0D3566" : hovered ? "#102B47" : "transparent"
        }
        return down ? "#0051a8" : hovered ? "#0069d9" : "#005ec3"
    }

    function borderColor() {
        if (!enabled) {
            return "#cbd5e1"
        }
        if (variant === "outline") {
            return "#005ec3"
        }
        if (variant === "ghost") {
            return "transparent"
        }
        return backgroundColor()
    }

    function foregroundColor() {
        if (!enabled) {
            return "#64748b"
        }
        if (variant === "outline" || variant === "ghost") {
            return "#ffffff"
        }
        return "#ffffff"
    }

    contentItem: Text {
        text: control.text
        color: control.foregroundColor()
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: control.radius
        color: control.backgroundColor()
        border.width: control.variant === "outline" ? 1 : 0
        border.color: control.borderColor()
    }
}
